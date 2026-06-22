from __future__ import annotations

from fastapi import APIRouter, File, UploadFile

from recipebook.pipeline import RecipeBookPipeline
from recipebook.schemas import RecipeFromUrlRequest, RecipePipelineResponse

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": "RecipeBook"}


@router.post("/recipes/from-url", response_model=RecipePipelineResponse)
def create_recipe_from_url(payload: RecipeFromUrlRequest) -> RecipePipelineResponse:
    pipeline = RecipeBookPipeline()
    return pipeline.run_from_url(payload.url)


@router.post("/recipes/from-video", response_model=RecipePipelineResponse)
async def create_recipe_from_video(file: UploadFile = File(...)) -> RecipePipelineResponse:
    pipeline = RecipeBookPipeline()
    return await pipeline.run_from_upload(file)
