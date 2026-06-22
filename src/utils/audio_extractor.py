from __future__ import annotations

import subprocess
from pathlib import Path

from recipebook.config import settings


def extract_audio(video_path: str, video_id: str, audio_root: str | None = None) -> str:
    output_dir = Path(audio_root or settings.audio_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    audio_path = output_dir / f"{video_id}.wav"

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vn",
        "-acodec",
        "pcm_s16le",
        "-ar",
        "16000",
        "-ac",
        "1",
        str(audio_path),
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return str(audio_path)
