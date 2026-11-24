"""Authorized YouTube video ingestion and reconstruction."""
import re
from pathlib import Path
from urllib.parse import urlsplit, parse_qs

def canonical_url(url):
    p = urlsplit(url)
    if p.scheme != "https" or p.username or p.password or p.port:
        raise ValueError("Use an HTTPS YouTube video URL")
    if p.hostname == "youtu.be":
        video = p.path.strip("/")
    elif p.hostname in ("youtube.com", "www.youtube.com", "m.youtube.com"):
        video = parse_qs(p.query).get("v", [""])[0] if p.path == "/watch" else (
            p.path.split("/")[2] if re.fullmatch(r"/(?:shorts|live)/[^/]+", p.path) else "")
    else:
        raise ValueError("Unsupported YouTube host")
    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video):
        raise ValueError("Invalid YouTube video ID")
    return "https://www.youtube.com/watch?v=" + video

def generate(url, workspace, *, every=15, max_frames=120, iterations=1000,
             resolution=96, max_gaussians=2000, progress=lambda stage: None):
    url = canonical_url(url)
    from yt_dlp import YoutubeDL
    from .video import extract_frames
    from .colmap import run_colmap, load_colmap_scene
    from .model import GaussianScene
    from .trainer import Trainer, TrainingConfig
    root = Path(workspace)
    root.mkdir(parents=True, exist_ok=False)
    progress("downloading")
    with YoutubeDL({"format": "best[height<=720][ext=mp4]/best[height<=720]",
                    "outtmpl": str(root / "video.%(ext)s"), "noplaylist": True,
                    "max_filesize": 250_000_000, "socket_timeout": 30,
                    "match_filter": lambda info, **kw: "Video exceeds 10 minutes" if
                    (info.get("duration") or 0) > 600 or info.get("is_live") else None}) as downloader:
        downloader.download([url])
    videos = [p for p in root.glob("video.*") if p.suffix not in (".part", ".ytdl")]
    if len(videos) != 1:
        raise RuntimeError("No complete video downloaded")
    progress("extracting")
    extract_frames(videos[0], root / "frames", every, max_frames)
    progress("reconstructing")
    model = run_colmap(root / "frames", root / "colmap")
    data = load_colmap_scene(model)
    if len(data.cameras) < 3:
        raise RuntimeError("Insufficient registered views")
    progress("training")
    scene = GaussianScene.from_point_cloud(data.points, data.colors, max_gaussians)
    return Trainer(scene, data, TrainingConfig(iterations=iterations, resolution=resolution)).fit(
        root / "output", model.parent / "images")

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("url", nargs="?", default="https://www.youtube.com/watch?v=oxxucX4dr5k", help="YouTube URL (defaults to the example test video)")
    p.add_argument("--workspace", required=True)
    p.add_argument("--authorized", action="store_true", required=True)
    args = p.parse_args()
    print(generate(args.url, args.workspace, progress=print))

if __name__ == "__main__":
    main()
