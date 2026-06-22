from __future__ import annotations

from openai import OpenAI

from recipebook.config import settings


class LLMClient:
    def __init__(self) -> None:
        if not settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required when using LLM inference.")

        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
        )

    def complete_text(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float | None = None,
    ) -> str:
        response = self.client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.llm_temperature if temperature is None else temperature,
        )

        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("LLM returned empty response.")

        return content.strip()