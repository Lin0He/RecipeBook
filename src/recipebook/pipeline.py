from __future__ import annotations

from pathlib import Path

from inference.asr import load_asr_model
from inference.ocr import load_ocr_model
from inference.context_refiner import ContextRefiner
from inference.recipe_structurer import RecipeStructurer
from recipebook.config import settings
from recipebook.renderer import save_recipe_outputs
from recipebook.schemas import RecipePipelineResponse
from utils.audio_extractor import extract_audio
from utils.context_builder import build_merged_context, save_context
from utils.frame_extractor import extract_frames
from utils.ocr_extractor import run_ocr_on_frames
from utils.video_loader import VideoLoader


class RecipeBookPipeline:
    def __init__(self) -> None:
        self.video_loader = VideoLoader()

    def run_from_url(self, url: str) -> RecipePipelineResponse:
        video_id, video_path = self.video_loader.download_from_url(url)
        return self.run_from_video_path(video_id=video_id, video_path=video_path)

    async def run_from_upload(self, upload) -> RecipePipelineResponse:
        video_id, video_path = await self.video_loader.save_upload(upload)
        return self.run_from_video_path(video_id=video_id, video_path=video_path)

    def run_from_video_path(self, video_id: str, video_path: str) -> RecipePipelineResponse:
        if settings.use_mock_inference:
            frames = [(video_path, 0.0)]
            audio_path = video_path
        else:
            _ensure_file_exists(video_path)
            frames = extract_frames(video_path=video_path, video_id=video_id)
            audio_path = extract_audio(video_path=video_path, video_id=video_id)

        ocr_model = load_ocr_model(
            use_mock=settings.use_mock_inference,
            languages=settings.ocr_language_list,
            gpu=settings.ocr_gpu,
        )
        asr_model = load_asr_model(
            use_mock=settings.use_mock_inference,
            model_size=settings.asr_model_size,
            device=settings.asr_device,
            compute_type=settings.asr_compute_type,
        )

        ocr_segments = run_ocr_on_frames(frames=frames, model=ocr_model)
        transcript_segments = asr_model.transcribe(audio_path)

        context = build_merged_context(
            video_id=video_id,
            source_video=video_path,
            ocr_segments=ocr_segments,
            transcript_segments=transcript_segments,
        )
        context_path = save_context(context)

        refiner = ContextRefiner()
        clean_cooking_notes = refiner.refine(context.merged_text)

        structurer = RecipeStructurer()
        recipe = structurer.structure_recipe(
            merged_text=clean_cooking_notes,
            source_video=video_path,
        )
        json_path, markdown_path = save_recipe_outputs(recipe)

        return RecipePipelineResponse(
            recipe=recipe,
            video_id=video_id,
            context_path=context_path,
            json_path=json_path,
            markdown_path=markdown_path,
            ocr_segments=len(ocr_segments),
            transcript_segments=len(transcript_segments),
        )


def _ensure_file_exists(path: str) -> None:
    if not Path(path).exists():
        raise FileNotFoundError(path)
