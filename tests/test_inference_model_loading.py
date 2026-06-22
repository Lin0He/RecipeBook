import os

import pytest

from inference.asr import MockASRModel, load_asr_model
from inference.ocr import MockOCRModel, load_ocr_model


def test_mock_ocr_model_loads() -> None:
    model = load_ocr_model(use_mock=True, languages=["en"], gpu=False)

    assert isinstance(model, MockOCRModel)
    assert getattr(model, "loaded") is True


def test_mock_asr_model_loads() -> None:
    model = load_asr_model(
        use_mock=True,
        model_size="tiny",
        device="cpu",
        compute_type="int8",
    )

    assert isinstance(model, MockASRModel)
    assert getattr(model, "loaded") is True


@pytest.mark.media
def test_real_ocr_model_loads_when_enabled() -> None:
    if os.getenv("RUN_MEDIA_TESTS") != "true":
        pytest.skip("Set RUN_MEDIA_TESTS=true to run real OCR model loading check.")

    print("\n[media] Loading real OCR model...")
    model = load_ocr_model(use_mock=False, languages=["en"], gpu=False)
    print(f"[media] OCR model loaded: {type(model).__name__}")

    assert getattr(model, "loaded") is True


@pytest.mark.media
def test_real_asr_model_loads_when_enabled() -> None:
    if os.getenv("RUN_MEDIA_TESTS") != "true":
        pytest.skip("Set RUN_MEDIA_TESTS=true to run real ASR model loading check.")

    print("\n[media] Loading real ASR model...")
    model = load_asr_model(
        use_mock=False,
        model_size="tiny",
        device="cpu",
        compute_type="int8",
    )
    print(f"[media] ASR model loaded: {type(model).__name__}")

    assert getattr(model, "loaded") is True