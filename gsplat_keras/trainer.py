from dataclasses import dataclass
from pathlib import Path
import numpy as np
import tensorflow as tf
from PIL import Image
from tqdm import trange
from .losses import photometric_loss
from .renderer import render_gaussians
from .export import export_ply,export_splat,write_viewer
from .camera import Camera

@dataclass
class TrainingConfig:
    iterations:int=3000
    resolution:int=256
    learning_rate:float=0.001
    ssim_weight:float=0.2
    log_every:int=100

class Trainer:
    def __init__(self,scene,scene_data,config=None):
        self.scene,self.data=scene,scene_data
        self.config=config or TrainingConfig()
    def _load_target(self,cam,image_root):
        path=Path(image_root)/cam.image_path
        if not path.exists(): raise FileNotFoundError(f"COLMAP image not found: {path}")
        im=Image.open(path).convert("RGB").resize((self.config.resolution,self.config.resolution),Image.Resampling.LANCZOS)
        arr=np.asarray(im,np.float32)/255.
        sx=self.config.resolution/cam.width; sy=self.config.resolution/cam.height
        scaled=Camera(self.config.resolution,self.config.resolution,cam.fx*sx,cam.fy*sy,
                      cam.cx*sx,cam.cy*sy,cam.rotation,cam.translation,cam.image_path)
        return arr,scaled
    def fit(self,output_dir,image_root):
        out=Path(output_dir); out.mkdir(parents=True,exist_ok=True)
        prepared=[self._load_target(c,image_root) for c in self.data.cameras]
        if not prepared: raise RuntimeError("No registered COLMAP images")
        opt=tf.keras.optimizers.Adam(self.config.learning_rate)
        @tf.function
        def step(target,camera):
            with tf.GradientTape() as tape:
                pred=render_gaussians(self.scene.parameters(),camera,self.config.resolution,self.config.resolution)
                loss=photometric_loss(target,pred,self.config.ssim_weight)
            grads=tape.gradient(loss,self.scene.trainable_variables)
            opt.apply_gradients([(g,v) for g,v in zip(grads,self.scene.trainable_variables) if g is not None])
            return loss
        for it in trange(self.config.iterations,desc="Training"):
            target,cam=prepared[it%len(prepared)]
            loss=step(tf.convert_to_tensor(target),cam.tensors())
            if (it+1)%self.config.log_every==0: print(f"iteration {it+1}: loss={float(loss):.6f}")
        params=self.scene.parameters()
        export_ply(out/"scene.ply",params); export_splat(out/"scene.splat",params)
        write_viewer(out/"viewer.html","scene.splat")
        self.scene.save_weights(out/"weights.weights.h5")
        return out
