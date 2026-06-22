from __future__ import annotations

from typing import Protocol

from recipebook.schemas import TranscriptSegment


class ASRModel(Protocol):
    def transcribe(self, audio_path: str) -> list[TranscriptSegment]:
        ...


class MockASRModel:
    def __init__(self) -> None:
        self.loaded = True

    def transcribe(self, audio_path: str) -> list[TranscriptSegment]:
        return [
            TranscriptSegment(
                start_sec=0.0,
                end_sec=8.0,
                text="Today we are making lemon garlic pasta.",
            ),
            TranscriptSegment(
                start_sec=8.0,
                end_sec=20.0,
                text="First boil the pasta for 10 minutes, then cook garlic in butter and add lemon.",
            ),
            TranscriptSegment(
                start_sec=20.0,
                end_sec=30.0,
                text="Finish with parmesan and do not burn the garlic.",
            ),
        ]


class FasterWhisperASRModel:
    def __init__(self, model_size: str, device: str = "cpu", compute_type: str = "int8") -> None:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Run: uv pip install -e '.[media]'"
            ) from exc

        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)
        self.loaded = True

    def transcribe(self, audio_path: str) -> list[TranscriptSegment]:
        segments, _info = self.model.transcribe(audio_path)
        return [
            TranscriptSegment(
                start_sec=float(segment.start),
                end_sec=float(segment.end),
                text=segment.text.strip(),
            )
            for segment in segments
            if segment.text.strip()
        ]


def load_asr_model(
    use_mock: bool,
    model_size: str,
    device: str = "cpu",
    compute_type: str = "int8",
) -> ASRModel:
    if use_mock:
        return MockASRModel()
    return FasterWhisperASRModel(
        model_size=model_size,
        device=device,
        compute_type=compute_type,
    )
