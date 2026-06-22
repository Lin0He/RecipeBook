from recipebook.renderer import render_markdown
from recipebook.schemas import Ingredient, RecipeDocument, RecipeStep


def test_render_markdown() -> None:
    recipe = RecipeDocument(
        recipe_id="recipe_test",
        title="Lemon Garlic Pasta",
        ingredients=[Ingredient(name="pasta"), Ingredient(name="garlic")],
        steps=[RecipeStep(order=1, instruction="Boil pasta.")],
        source_video="test.mp4",
        extracted_text="mock extracted text",
    )

    markdown = render_markdown(recipe)

    assert "# Lemon Garlic Pasta" in markdown
    assert "## Ingredients" in markdown
    assert "## Steps" in markdown
