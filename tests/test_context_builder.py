from recipebook.schemas import OCRSegment, TranscriptSegment
from utils.context_builder import build_merged_context
from utils.context_builder import looks_like_noise, normalize_text


def test_build_merged_context() -> None:
    context = build_merged_context(
        video_id="video_test",
        source_video="test.mp4",
        ocr_segments=[
            OCRSegment(frame_path="frame.jpg", timestamp_sec=3, text="Ingredients: pasta, garlic"),
        ],
        transcript_segments=[
            TranscriptSegment(start_sec=5, end_sec=9, text="Boil pasta for 10 minutes."),
        ],
    )

    assert "OCR" in context.merged_text
    assert "ASR" in context.merged_text
    assert "pasta" in context.merged_text.lower()


def test_filters_platform_watermark() -> None:
    assert looks_like_noise("J TikTok livs table", source_type="OCR") is True


def test_filters_symbol_heavy_ocr_noise() -> None:
    assert looks_like_noise("4 E wuldou) 4 79643'", source_type="OCR") is True


def test_keeps_imperfect_but_useful_ocr() -> None:
    assert looks_like_noise("~esto Pasta Salad with nmatoes & mozzarella", source_type="OCR") is False


def test_keeps_general_asr_text() -> None:
    text = "I personally love using my homemade kale Pesto, but you can always use your favorite instead."
    assert looks_like_noise(text, source_type="ASR") is False


def test_normalize_text() -> None:
    assert normalize_text("  hello   world  ") == "hello world"