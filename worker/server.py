"""Single-machine worker with persistent job directories. Run one process."""
import os
import secrets
import json
import uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import BoundedSemaphore
from fastapi import FastAPI, HTTPException, Header
from fastapi.responses import FileResponse
from pydantic import BaseModel
from gsplat_keras.youtube import canonical_url, generate

app = FastAPI()
root = Path(os.environ.get("JOB_DIR", "jobs")).resolve()
root.mkdir(parents=True, exist_ok=True)
pool = ThreadPoolExecutor(max_workers=1)
slots = BoundedSemaphore(3)

class Request(BaseModel):
    url: str
    authorized: bool = False

def auth(token):
    expected = os.environ.get("WORKER_TOKEN")
    if not expected or not secrets.compare_digest(token or "", expected):
        raise HTTPException(401, "Unauthorized")

def status(job, stage):
    path = root / job / "status.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps({"id": job, "status": stage}))
    tmp.replace(path)

def run(job, url):
    try:
        generate(url, root / job / "work", progress=lambda s: status(job, s))
        status(job, "completed")
    except Exception:
        import logging
        logging.exception("Job failed: %s", job)
        status(job, "failed")
    finally:
        slots.release()

@app.post("/jobs", status_code=202)
def submit(req: Request, x_worker_token: str = Header(default="")):
    auth(x_worker_token)
    if not req.authorized:
        raise HTTPException(400, "Confirm authorization")
    try:
        url = canonical_url(req.url)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not slots.acquire(blocking=False):
        raise HTTPException(429, "Worker busy")
    job = uuid.uuid4().hex
    try:
        (root / job).mkdir()
        status(job, "queued")
        pool.submit(run, job, url)
    except Exception:
        slots.release()
        raise
    return {"id": job, "status": "queued"}

def job_path(job):
    if len(job) != 32 or any(c not in "0123456789abcdef" for c in job):
        raise HTTPException(404)
    p = root / job
    if not (p / "status.json").is_file():
        raise HTTPException(404)
    return p

@app.get("/jobs/{job}")
def get_job(job: str, x_worker_token: str = Header(default="")):
    auth(x_worker_token)
    return json.loads((job_path(job) / "status.json").read_text())

@app.get("/jobs/{job}/{name}")
def artifact(job: str, name: str, x_worker_token: str = Header(default="")):
    auth(x_worker_token)
    if name not in ("scene.ply", "scene.splat", "viewer.html"):
        raise HTTPException(404)
    p = job_path(job) / "work" / "output" / name
    if not p.is_file():
        raise HTTPException(404)
    return FileResponse(p, filename=name if name != "viewer.html" else None)

@app.get("/health")
def health():
    return {"status": "ok", "configured": bool(os.getenv("WORKER_TOKEN"))}
