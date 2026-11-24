from dataclasses import dataclass
from pathlib import Path
import subprocess
import os
import numpy as np
from .camera import Camera, qvec_to_rotmat

@dataclass
class SceneData:
    cameras: list
    points: np.ndarray
    colors: np.ndarray

def _run(args):
    print("+", " ".join(map(str, args)))
    subprocess.run(list(map(str, args)), check=True)

def run_colmap(images_dir, workspace, executable="colmap", camera_model="OPENCV"):
    use_gpu = os.getenv("COLMAP_USE_GPU", "1")
    if use_gpu not in ("0", "1"):
        raise ValueError("COLMAP_USE_GPU must be 0 or 1")
    images_dir, workspace = Path(images_dir), Path(workspace)
    workspace.mkdir(parents=True, exist_ok=True)
    database, sparse = workspace/"database.db", workspace/"sparse"
    sparse.mkdir(exist_ok=True)
    _run([executable,"feature_extractor","--database_path",database,"--image_path",images_dir,
          "--ImageReader.camera_model",camera_model,"--SiftExtraction.use_gpu",use_gpu])
    matcher = "sequential_matcher" if len(list(images_dir.iterdir())) > 20 else "exhaustive_matcher"
    _run([executable,matcher,"--database_path",database,"--SiftMatching.use_gpu",use_gpu])
    _run([executable,"mapper","--database_path",database,"--image_path",images_dir,"--output_path",sparse])
    models = sorted(p for p in sparse.iterdir() if p.is_dir())
    if not models:
        raise RuntimeError("COLMAP did not produce a sparse model.")
    dense = workspace/"dense"
    _run([executable,"image_undistorter","--image_path",images_dir,"--input_path",models[0],
          "--output_path",dense,"--output_type","COLMAP"])
    text_model = dense/"sparse"
    _run([executable,"model_converter","--input_path",text_model,"--output_path",text_model,"--output_type","TXT"])
    return text_model

def load_colmap_scene(model_dir):
    model_dir = Path(model_dir)
    camera_defs = {}
    for line in (model_dir/"cameras.txt").read_text().splitlines():
        p = line.strip().split()
        if not p or p[0].startswith("#"): continue
        cid, model, w, h = int(p[0]), p[1], int(p[2]), int(p[3])
        v = list(map(float,p[4:]))
        if model in ("SIMPLE_PINHOLE","SIMPLE_RADIAL","RADIAL"):
            fx = fy = v[0]; cx,cy = v[1:3]
        elif model in ("PINHOLE","OPENCV","FULL_OPENCV","OPENCV_FISHEYE"):
            fx,fy,cx,cy = v[:4]
        else: raise ValueError(f"Unsupported camera model: {model}")
        camera_defs[cid] = (w,h,fx,fy,cx,cy)
    lines = (model_dir/"images.txt").read_text().splitlines()
    cameras, i = [], 0
    while i < len(lines):
        line = lines[i].strip(); i += 1
        if not line or line.startswith("#"): continue
        p = line.split()
        if len(p) < 10: continue
        q = list(map(float,p[1:5])); t = np.array(list(map(float,p[5:8])),np.float32)
        cid = int(p[8]); name = " ".join(p[9:])
        if i < len(lines): i += 1
        w,h,fx,fy,cx,cy = camera_defs[cid]
        cameras.append(Camera(w,h,fx,fy,cx,cy,qvec_to_rotmat(q),t,name))
    points, colors = [], []
    for line in (model_dir/"points3D.txt").read_text().splitlines():
        p = line.strip().split()
        if not p or p[0].startswith("#"): continue
        points.append(list(map(float,p[1:4])))
        colors.append(np.asarray(list(map(float,p[4:7])),np.float32)/255.0)
    if not cameras or not points:
        raise RuntimeError("COLMAP model must contain registered images and sparse points.")
    return SceneData(cameras,np.asarray(points,np.float32),np.asarray(colors,np.float32))
