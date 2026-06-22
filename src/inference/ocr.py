from __future__ import annotations

from pathlib import Path
from typing import Protocol

from recipebook.schemas import OCRSegment


class OCRModel(Protocol):
    def extract_text(self, frame_path: str, timestamp_sec: float) -> OCRSegment:
        ...


class MockOCRModel:
    def __init__(self) -> None:
        self.loaded = True

    def extract_text(self, frame_path: str, timestamp_sec: float) -> OCRSegment:
        name = Path(frame_path).name
        return OCRSegment(
            frame_path=frame_path,
            timestamp_sec=timestamp_sec,
            text=f"Mock OCR text from {name}: Ingredients pasta garlic butter lemon parmesan. Cook 10 minutes.",
            confidence=1.0,
        )


class EasyOCRModel:
    def __init__(self, languages: list[str], gpu: bool = False) -> None:
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "easyocr is not installed. Run: uv pip install -e '.[media]'"
            ) from exc

        self.reader = easyocr.Reader(languages, gpu=gpu)
        self.loaded = True

    def extract_text(self, frame_path: str, timestamp_sec: float) -> OCRSegment:
        results = self.reader.readtext(frame_path)
        texts: list[str] = []
        confidences: list[float] = []

        for item in results:
            if len(item) >= 3:
                text = str(item[1]).strip()
                confidence = float(item[2])
                if text:
                    texts.append(text)
                    confidences.append(confidence)

        avg_confidence = sum(confidences) / len(confidences) if confidences else None
        return OCRSegment(
            frame_path=frame_path,
            timestamp_sec=timestamp_sec,
            text=" ".join(texts),
            confidence=avg_confidence,
        )


def load_ocr_model(use_mock: bool, languages: list[str], gpu: bool = False) -> OCRModel:
    if use_mock:
        return MockOCRModel()
    return EasyOCRModel(languages=languages, gpu=gpu)
