from dataclasses import dataclass
import numpy as np
import tensorflow as tf

@dataclass
class Camera:
    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    rotation: np.ndarray
    translation: np.ndarray
    image_path: str = ""

    def tensors(self):
        return {"rotation": tf.convert_to_tensor(self.rotation, tf.float32),
                "translation": tf.convert_to_tensor(self.translation, tf.float32),
                "fx": tf.constant(self.fx, tf.float32), "fy": tf.constant(self.fy, tf.float32),
                "cx": tf.constant(self.cx, tf.float32), "cy": tf.constant(self.cy, tf.float32)}

def qvec_to_rotmat(q):
    qw, qx, qy, qz = np.asarray(q, dtype=np.float64)
    return np.array([
        [1-2*(qy*qy+qz*qz), 2*(qx*qy-qz*qw), 2*(qx*qz+qy*qw)],
        [2*(qx*qy+qz*qw), 1-2*(qx*qx+qz*qz), 2*(qy*qz-qx*qw)],
        [2*(qx*qz-qy*qw), 2*(qy*qz+qx*qw), 1-2*(qx*qx+qy*qy)]], dtype=np.float32)

def project_points(points, camera):
    p = np.asarray(points) @ camera.rotation.T + camera.translation
    z = np.maximum(p[:, 2], 1e-8)
    return np.stack([camera.fx*p[:, 0]/z+camera.cx, camera.fy*p[:, 1]/z+camera.cy], axis=-1), p[:, 2]
