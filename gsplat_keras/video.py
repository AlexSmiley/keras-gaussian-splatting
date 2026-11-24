from pathlib import Path
import cv2

def extract_frames(video_path, output_dir, every=8, max_frames=0, image_format="jpg"):
    if every < 1:
        raise ValueError("every must be >= 1")
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    frame_idx = saved = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            if frame_idx % every == 0:
                path = out / f"frame_{saved:06d}.{image_format}"
                if not cv2.imwrite(str(path), frame):
                    raise RuntimeError(f"Could not write {path}")
                saved += 1
                if max_frames and saved >= max_frames:
                    break
            frame_idx += 1
    finally:
        cap.release()
    if saved < 2:
        raise RuntimeError("At least two frames are recommended.")
    return saved
