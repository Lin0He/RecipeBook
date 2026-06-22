from __future__ import annotations

from inference.ocr import OCRModel
from recipebook.schemas import OCRSegment


def run_ocr_on_frames(
    frames: list[tuple[str, float]],
    model: OCRModel,
    min_text_length: int = 2,
) -> list[OCRSegment]:
    segments: list[OCRSegment] = []
    for frame_path, timestamp_sec in frames:
        segment = model.extract_text(frame_path=frame_path, timestamp_sec=timestamp_sec)
        if len(segment.text.strip()) >= min_text_length:
            segments.append(segment)
    return segments
