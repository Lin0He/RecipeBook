from __future__ import annotations

import json
import re

from recipebook.config import settings
from recipebook.schemas import Ingredient, RecipeDocument, RecipeStep
from utils.ids import stable_id


class RecipeStructurer:
    def __init__(self) -> None:
        self.use_llm = bool(settings.llm_api_key)
        self.client = None
        if self.use_llm:
            try:
                from openai import OpenAI
            except ImportError as exc:
                raise RuntimeError("openai is not installed. Run: uv pip install -e '.[dev]'") from exc

            kwargs = {"api_key": settings.llm_api_key}
            if settings.llm_base_url:
                kwargs["base_url"] = settings.llm_base_url
            self.client = OpenAI(**kwargs)

    def structure_recipe(self, merged_text: str, source_video: str | None = None) -> RecipeDocument:
        if self.client is None:
            return self._fallback_structure(merged_text=merged_text, source_video=source_video)

        prompt = self._build_prompt(merged_text)
        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        data["recipe_id"] = data.get("recipe_id") or stable_id(merged_text, "recipe")
        data["source_video"] = source_video
        data["extracted_text"] = merged_text
        return RecipeDocument.model_validate(data)

    @staticmethod
    def _build_prompt(merged_text: str) -> str:
        return f"""
You are RecipeBook, an AI tool that turns cooking video OCR and audio transcripts into a clean recipe document.

Return only valid JSON with this structure:
{{
  "title": "string",
  "description": "string or null",
  "ingredients": [{{"name": "string", "quantity": "string or null", "note": "string or null"}}],
  "steps": [{{"order": 1, "instruction": "string", "timing": "string or null"}}],
  "total_time": "string or null",
  "tools": ["string"],
  "tips": ["string"]
}}

Rules:
- Use only information supported by the OCR/ASR context.
- If quantity or timing is unclear, use null.
- Keep instructions practical and concise.

OCR + ASR context:
{merged_text}
""".strip()

    @staticmethod
    def _fallback_structure(merged_text: str, source_video: str | None = None) -> RecipeDocument:
        lowered = merged_text.lower()
        title = "Generated Recipe"
        title_match = re.search(r"(?:making|make) ([a-zA-Z\s]+?)(?:\.|\n|$)", lowered)
        if title_match:
            title = title_match.group(1).strip().title()

        known_ingredients = [
            "pasta",
            "garlic",
            "butter",
            "lemon",
            "parmesan",
            "olive oil",
            "salt",
            "pepper",
            "tomato",
            "onion",
        ]
        ingredients = [Ingredient(name=item) for item in known_ingredients if item in lowered]

        sentences = re.split(r"(?<=[.!?])\s+", merged_text.replace("\n", " "))
        action_words = ("boil", "cook", "add", "mix", "heat", "serve", "bake", "stir", "finish")
        step_sentences = [s.strip() for s in sentences if any(word in s.lower() for word in action_words)]
        if not step_sentences:
            step_sentences = ["Review the extracted video text and prepare the recipe manually."]

        steps = [
            RecipeStep(order=index, instruction=sentence, timing=_extract_timing(sentence))
            for index, sentence in enumerate(step_sentences[:8], start=1)
        ]

        tools = [tool for tool in ["pan", "pot", "oven", "knife", "bowl"] if tool in lowered]
        tips = []
        if "do not burn" in lowered or "don't burn" in lowered:
            tips.append("Do not burn the garlic or aromatics; it can make the dish bitter.")

        return RecipeDocument(
            recipe_id=stable_id(merged_text, "recipe"),
            title=title,
            description="Recipe structured from video OCR and audio transcript.",
            ingredients=ingredients,
            steps=steps,
            total_time=_extract_timing(merged_text),
            tools=tools,
            tips=tips,
            source_video=source_video,
            extracted_text=merged_text,
        )


def _extract_timing(text: str) -> str | None:
    match = re.search(r"(\d+\s?(minutes?|mins?|hours?|hrs?))", text.lower())
    return match.group(1) if match else None
