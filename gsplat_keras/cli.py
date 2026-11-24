import argparse
from .video import extract_frames
from .colmap import run_colmap,load_colmap_scene
from .model import GaussianScene
from .trainer import Trainer,TrainingConfig

def main():
    p=argparse.ArgumentParser(prog="gsplat-keras")
    sub=p.add_subparsers(dest="command",required=True)
    v=sub.add_parser("extract-video"); v.add_argument("--video",required=True); v.add_argument("--output",required=True)
    v.add_argument("--every",type=int,default=8); v.add_argument("--max-frames",type=int,default=0)
    c=sub.add_parser("colmap"); c.add_argument("--images",required=True); c.add_argument("--workspace",required=True)
    c.add_argument("--colmap",default="colmap"); c.add_argument("--camera-model",default="OPENCV")
    t=sub.add_parser("train"); t.add_argument("--images",required=True); t.add_argument("--colmap-model",required=True)
    t.add_argument("--output",required=True); t.add_argument("--iterations",type=int,default=3000)
    t.add_argument("--resolution",type=int,default=256); t.add_argument("--max-gaussians",type=int,default=12000)
    t.add_argument("--learning-rate",type=float,default=.001)
    q=sub.add_parser("view-ply"); q.add_argument("--ply",required=True)
    a=p.parse_args()
    if a.command=="extract-video": print("Extracted",extract_frames(a.video,a.output,a.every,a.max_frames),"frames")
    elif a.command=="colmap": print("COLMAP text model:",run_colmap(a.images,a.workspace,a.colmap,a.camera_model))
    elif a.command=="train":
        data=load_colmap_scene(a.colmap_model)
        scene=GaussianScene.from_point_cloud(data.points,data.colors,a.max_gaussians)
        cfg=TrainingConfig(iterations=a.iterations,resolution=a.resolution,learning_rate=a.learning_rate)
        Trainer(scene,data,cfg).fit(a.output,a.images)
    elif a.command=="view-ply":
        import open3d as o3d
        o3d.visualization.draw_geometries([o3d.io.read_point_cloud(a.ply)])

if __name__=="__main__": main()
