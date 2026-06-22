from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class VideoInputType(str, Enum):
    URL = "url"
    UPLOAD = "upload"


class Ingredient(BaseModel):
    name: str
    quantity: str | None = None
    note: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Ingredient name cannot be empty.")
        return value


class RecipeStep(BaseModel):
    order: int = Field(..., ge=1)
    instruction: str
    timing: str | None = None

    @field_validator("instruction")
    @classmethod
    def validate_instruction(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Step instruction cannot be empty.")
        return value


class OCRSegment(BaseModel):
    frame_path: str
    timestamp_sec: float
    text: str
    confidence: float | None = None


class TranscriptSegment(BaseModel):
    start_sec: float
    end_sec: float
    text: str


class MergedContext(BaseModel):
    video_id: str
    source_video: str
    merged_text: str


class RecipeDocument(BaseModel):
    recipe_id: str
    title: str
    description: str | None = None
    ingredients: list[Ingredient] = Field(default_factory=list)
    steps: list[RecipeStep] = Field(default_factory=list)
    total_time: str | None = None
    tools: list[str] = Field(default_factory=list)
    tips: list[str] = Field(default_factory=list)
    source_video: str | None = None
    extracted_text: str

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Recipe title cannot be empty.")
        return value


class RecipeFromUrlRequest(BaseModel):
    url: str


class RecipePipelineResponse(BaseModel):
    recipe: RecipeDocument
    video_id: str
    context_path: str
    json_path: str
    markdown_path: str
    ocr_segments: int
    transcript_segments: int
