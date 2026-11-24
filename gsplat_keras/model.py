import numpy as np
import tensorflow as tf
from tensorflow import keras

class GaussianScene(keras.Model):
    # Trainable 3D means, anisotropic scales, quaternions, opacity and RGB.
    def __init__(self, positions, colors=None, initial_scale=0.02, name="gaussian_scene"):
        super().__init__(name=name)
        positions = np.asarray(positions,np.float32)
        if positions.ndim != 2 or positions.shape[1] != 3 or len(positions) == 0:
            raise ValueError("positions must have shape [N,3] and N > 0")
        n = len(positions)
        if colors is None: colors = np.full((n,3),0.5,np.float32)
        colors = np.clip(np.asarray(colors,np.float32),1e-4,1-1e-4)
        q = np.zeros((n,4),np.float32); q[:,0] = 1.0
        self.means = self.add_weight(name="means",shape=(n,3),initializer=keras.initializers.Constant(positions))
        self.log_scales = self.add_weight(name="log_scales",shape=(n,3),initializer=keras.initializers.Constant(np.log(initial_scale)))
        self.quaternions = self.add_weight(name="quaternions",shape=(n,4),initializer=keras.initializers.Constant(q))
        self.opacity_logits = self.add_weight(name="opacity_logits",shape=(n,1),initializer="zeros")
        self.color_logits = self.add_weight(name="color_logits",shape=(n,3),
            initializer=keras.initializers.Constant(np.log(colors/(1-colors))))
    def parameters(self):
        return {"means":self.means,"scales":tf.exp(tf.clip_by_value(self.log_scales,-8.,3.)),
                "rotations":tf.math.l2_normalize(self.quaternions,axis=-1),
                "opacity":tf.sigmoid(self.opacity_logits),"colors":tf.sigmoid(self.color_logits)}
    @classmethod
    def from_point_cloud(cls, points, colors, max_gaussians=12000):
        if len(points)>max_gaussians:
            idx=np.linspace(0,len(points)-1,max_gaussians).astype(int)
            points,colors=points[idx],colors[idx]
        return cls(points,colors)
