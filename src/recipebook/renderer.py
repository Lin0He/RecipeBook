from __future__ import annotations

import json
from pathlib import Path

from recipebook.config import settings
from recipebook.schemas import RecipeDocument


def render_markdown(recipe: RecipeDocument) -> str:
    ingredients = "\n".join(_format_ingredient(item) for item in recipe.ingredients)
    if not ingredients:
        ingredients = "- Not clearly detected"

    steps = "\n".join(
        f"{step.order}. {step.instruction}{f' _({step.timing})_' if step.timing else ''}"
        for step in recipe.steps
    )
    if not steps:
        steps = "No clear steps detected."

    tools = "\n".join(f"- {tool}" for tool in recipe.tools) or "- Not clearly detected"
    tips = "\n".join(f"- {tip}" for tip in recipe.tips) or "- None"

    return f"""# {recipe.title}

{recipe.description or ""}

## Ingredients

{ingredients}

## Steps

{steps}

## Time

- Total time: {recipe.total_time or "Not specified"}

## Tools

{tools}

## Tips

{tips}

## Source

- Source video: {recipe.source_video or "Not provided"}

## Extracted Video Text

```text
{recipe.extracted_text}
```
"""


def save_recipe_outputs(recipe: RecipeDocument) -> tuple[str, str]:
    json_dir = Path(settings.recipe_json_dir)
    markdown_dir = Path(settings.recipe_markdown_dir)
    json_dir.mkdir(parents=True, exist_ok=True)
    markdown_dir.mkdir(parents=True, exist_ok=True)

    json_path = json_dir / f"{recipe.recipe_id}.json"
    markdown_path = markdown_dir / f"{recipe.recipe_id}.md"

    json_path.write_text(json.dumps(recipe.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown(recipe), encoding="utf-8")

    return str(json_path), str(markdown_path)


def _format_ingredient(item) -> str:
    quantity = f"{item.quantity} " if item.quantity else ""
    note = f" — {item.note}" if item.note else ""
    return f"- {quantity}{item.name}{note}"
