from pathlib import Path
import numpy as np

def _arrays(params):
    return {k:np.asarray(v.numpy()) for k,v in params.items()}

def export_ply(path,params):
    a=_arrays(params); n=len(a["means"]); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("w") as f:
        f.write("ply\nformat ascii 1.0\n"+f"element vertex {n}\n")
        props=[("x","float"),("y","float"),("z","float"),("red","uchar"),("green","uchar"),("blue","uchar"),
               ("opacity","float"),("scale_0","float"),("scale_1","float"),("scale_2","float"),
               ("rot_0","float"),("rot_1","float"),("rot_2","float"),("rot_3","float")]
        for typ,name in props: f.write(f"property {typ} {name}\n")
        f.write("end_header\n")
        rgb=np.clip(a["colors"]*255,0,255).astype(np.uint8)
        for i in range(n):
            vals=[*a["means"][i],*rgb[i],float(a["opacity"][i,0]),*a["scales"][i],*a["rotations"][i]]
            f.write(" ".join(map(str,vals))+"\n")
    return path

def export_splat(path,params):
    # 32-byte records: xyz float32, log-scale float32, RGBA uint8, quaternion uint8.
    a=_arrays(params); path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("wb") as f:
        for i in range(len(a["means"])):
            xyz=np.asarray(a["means"][i],dtype="<f4")
            scale=np.log(np.maximum(a["scales"][i],1e-8)).astype("<f4")
            rgba=np.r_[np.clip(a["colors"][i]*255,0,255),np.clip(a["opacity"][i,0]*255,0,255)].astype(np.uint8)
            q=a["rotations"][i][[1,2,3,0]]
            qbytes=np.clip((q*.5+.5)*255,0,255).astype(np.uint8)
            f.write(xyz.tobytes()+scale.tobytes()+rgba.tobytes()+qbytes.tobytes())
    return path

def write_viewer(path,splat_filename):
    html=f'''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Keras Gaussian Splatting Viewer</title><style>html,body,#app{{margin:0;width:100%;height:100%;overflow:hidden;background:#111}}#hint{{position:absolute;top:12px;left:14px;color:white;background:#0009;padding:10px}}</style></head>
<body><div id="app"></div><div id="hint">Drag to orbit · Scroll to zoom · Right-drag to pan</div>
<script type="module">
import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';
import {{ Viewer }} from 'https://unpkg.com/@mkkellogg/gaussian-splats-3d@0.4.7/build/gaussian-splats-3d.module.js';
const viewer=new Viewer({{rootElement:document.getElementById('app'),THREE}});
viewer.addSplatScene('./{splat_filename}',{{showLoadingUI:true}}).then(()=>viewer.start());
</script></body></html>'''
    Path(path).write_text(html,encoding="utf-8")
