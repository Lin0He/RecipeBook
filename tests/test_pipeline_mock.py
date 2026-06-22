from pathlib import Path

from recipebook.pipeline import RecipeBookPipeline
from utils.ids import stable_id


def test_pipeline_with_mock_inference(tmp_path: Path, monkeypatch) -> None:
    video_path = tmp_path / "demo.mp4"
    video_path.write_text("not a real video, mock mode does not decode it", encoding="utf-8")

    monkeypatch.setenv("USE_MOCK_INFERENCE", "true")

    pipeline = RecipeBookPipeline()
    video_id = stable_id(str(video_path), "video")
    response = pipeline.run_from_video_path(video_id=video_id, video_path=str(video_path))

    assert response.recipe.title
    assert response.ocr_segments >= 1
    assert response.transcript_segments >= 1
