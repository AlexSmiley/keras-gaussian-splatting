# Keras Gaussian Splatting

TensorFlow/Keras-first educational 3D Gaussian Splatting project. Accepts images or video, uses COLMAP for camera calibration and sparse reconstruction, optimizes a Gaussian scene, and exports PLY, `.splat`, and an HTML viewer.

**Important scope:** this is a readable reference implementation, not a performance-equivalent replacement for the original CUDA rasterizer. The dense differentiable renderer has O(number of Gaussians × image pixels) cost. Start with a small scene, low resolution, and a GPU. COLMAP is an external executable. The HTML viewer loads a browser library from a CDN.

## Install
Python 3.10–3.12 recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```
Install COLMAP separately and ensure `colmap` is on PATH.

## Input preparation

Put photos in `data/scene/images/`, or extract video frames:

```bash
python -m gsplat_keras.cli extract-video --video data/input.mp4 --output data/scene/images --every 8
```

Run camera calibration and sparse reconstruction:

```bash
python -m gsplat_keras.cli colmap --images data/scene/images --workspace data/scene/colmap --camera-model OPENCV
```

Train:

```bash
python -m gsplat_keras.cli train --images data/scene/images --colmap-model data/scene/colmap/dense/sparse --output runs/scene --iterations 3000 --resolution 256
```

Open the viewer by serving the output directory:

```bash
cd runs/scene
python -m http.server 8000
# http://localhost:8000/viewer.html
```

Optional local PLY viewer: `python -m gsplat_keras.cli view-ply --ply runs/scene/scene.ply`

## Python API

```python
from gsplat_keras.colmap import load_colmap_scene
from gsplat_keras.model import GaussianScene
from gsplat_keras.trainer import Trainer, TrainingConfig

data = load_colmap_scene("data/scene/colmap/dense/sparse")
scene = GaussianScene.from_point_cloud(data.points, data.colors)
Trainer(scene, data, TrainingConfig(iterations=1000)).fit("runs/scene", "data/scene/images")
```

## Included
- Video frame extraction with OpenCV
- COLMAP feature extraction, matching, mapping, undistortion and text model conversion
- COLMAP camera parsing and sparse point initialization
- Keras trainable means, scales, quaternions, opacity and RGB
- TensorFlow projection, Gaussian footprints, depth sorting and front-to-back alpha compositing
- L1 + SSIM loss, training loop, PLY and `.splat` export, browser viewer
- Unit tests

## Known limitations
This first version omits adaptive densification/pruning, spherical harmonics, exact anisotropic projected covariance, anti-aliasing, and tile-based CUDA rasterization. The renderer currently uses isotropic screen-space footprints derived from mean scale; quaternions are retained and exported but do not yet affect the footprint. For research-grade quality and large scenes, add densification/pruning, view-dependent SH color, and a custom TensorFlow op/CUDA rasterizer. One image cannot uniquely recover hidden geometry; multi-view input is strongly recommended.
