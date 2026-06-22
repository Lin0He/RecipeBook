from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import UploadFile

from recipebook.config import settings
from utils.ids import stable_id


class VideoLoader:
    def __init__(self, video_dir: str | None = None) -> None:
        self.video_dir = Path(video_dir or settings.video_dir)
        self.video_dir.mkdir(parents=True, exist_ok=True)

    def download_from_url(self, url: str) -> tuple[str, str]:
        try:
            import yt_dlp
        except ImportError as exc:
            raise RuntimeError("yt-dlp is not installed. Run: uv pip install -e '.[media]'") from exc

        video_id = stable_id(url, "video")
        output_template = str(self.video_dir / f"{video_id}.%(ext)s")

        options = {
            "outtmpl": output_template,
            "format": "mp4/bestvideo+bestaudio/best",
            "merge_output_format": "mp4",
            "quiet": True,
            "noplaylist": True,
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])

        candidates = list(self.video_dir.glob(f"{video_id}.*"))
        if not candidates:
            raise FileNotFoundError(f"Downloaded video not found for {url}")

        return video_id, str(candidates[0])

    async def save_upload(self, upload: UploadFile) -> tuple[str, str]:
        filename = upload.filename or "uploaded_video.mp4"
        suffix = Path(filename).suffix or ".mp4"
        video_id = stable_id(filename, "video")
        path = self.video_dir / f"{video_id}{suffix}"

        with path.open("wb") as target:
            while chunk := await upload.read(1024 * 1024):
                target.write(chunk)

        return video_id, str(path)

    def copy_local(self, source_path: str) -> tuple[str, str]:
        source = Path(source_path)
        if not source.exists():
            raise FileNotFoundError(source_path)

        video_id = stable_id(str(source.resolve()), "video")
        target = self.video_dir / f"{video_id}{source.suffix}"
        shutil.copy2(source, target)
        return video_id, str(target)
