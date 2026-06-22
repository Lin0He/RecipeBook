from __future__ import annotations

import subprocess
from pathlib import Path

from recipebook.config import settings


def extract_frames(
    video_path: str,
    video_id: str,
    interval_seconds: int | None = None,
    frame_root: str | None = None,
) -> list[tuple[str, float]]:
    interval = interval_seconds or settings.frame_interval_seconds
    output_dir = Path(frame_root or settings.frame_dir) / video_id
    output_dir.mkdir(parents=True, exist_ok=True)

    pattern = output_dir / "frame_%05d.jpg"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vf",
        f"fps=1/{interval}",
        str(pattern),
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    frames = sorted(output_dir.glob("frame_*.jpg"))
    return [(str(frame), float(index * interval)) for index, frame in enumerate(frames)]
