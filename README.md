# Keras Gaussian Splatting

**Vercel frontend:** [https://keras-gaussian-splatting.vercel.app](https://keras-gaussian-splatting.vercel.app)

Reconstruction requires a running worker and configured Vercel environment variables.


Experimental TensorFlow/Keras reconstruction from images or video. The renderer is a dense, isotropic reference implementation, not production-quality 3DGS.

## YouTube to splat

Use only videos you have permission to download and process. Install FFmpeg and a compatible GPU-enabled COLMAP executable on PATH, then:

```sh
pip install -e ".[training,test]"
pip install yt-dlp
python -m gsplat_keras.youtube "https://www.youtube.com/watch?v=VIDEO_ID" --workspace jobs/example --authorized
```

Use a new workspace each time. Output is in jobs/example/output. Videos should show a static scene from overlapping viewpoints; edited footage and moving objects may fail.

## Worker API

```sh
pip install -e .
pip install -r worker/requirements.txt
export WORKER_TOKEN=replace-with-a-long-random-secret
uvicorn worker.server:app --host 0.0.0.0 --port 8000
```

Run one worker process with persistent JOB_DIR storage and HTTPS via a reverse proxy. POST /jobs with JSON {"url":"...","authorized":true} and X-Worker-Token header. Poll GET /jobs/{id}; download GET /jobs/{id}/scene.ply or scene.splat. Serve viewer.html alongside scene.splat using an authenticated local HTTP server. Queue is bounded and in-process; interrupted jobs require resubmission. Add storage quotas and cleanup before public deployment.

Vercel remains a lightweight health endpoint; do not install ML dependencies there. The worker is not automatically deployed by Vercel.

Run tests with pytest. Full reconstruction requires compatible COLMAP, TensorFlow and suitable hardware.
