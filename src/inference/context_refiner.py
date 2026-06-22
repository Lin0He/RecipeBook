from __future__ import annotations

from inference.llm_client import LLMClient


CONTEXT_REFINER_SYSTEM_PROMPT = """
You are RecipeBook's context refinement module.

You receive noisy OCR and ASR text extracted from a cooking video.

Your job:
- Remove timestamps.
- Remove platform watermarks, UI text, creator handles, and unrelated promotional text.
- Remove duplicated lines.
- Fix obvious OCR/ASR spelling errors only when the intended cooking meaning is clear.
- Rewrite fragmented OCR/ASR snippets into clean cooking notes.
- Keep recipe-relevant information: recipe name, ingredients, quantities, tools, timings, actions, tips, substitutions, serving notes.
- Do not invent missing quantities.
- Do not invent missing steps.
- Do not output a final recipe.
- Output clean cooking notes only.
""".strip()


class ContextRefiner:
    def __init__(self, llm_client: LLMClient | None = None) -> None:
        self.llm_client = llm_client or LLMClient()

    def refine(self, merged_text: str) -> str:
        if not merged_text.strip():
            return ""

        user_prompt = f"""
Clean and rewrite the following OCR/ASR evidence from a cooking video into coherent cooking notes.

OCR/ASR evidence:
{merged_text}

Return only the cleaned cooking notes.
""".strip()

        return self.llm_client.complete_text(
            system_prompt=CONTEXT_REFINER_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=0.1,
        )