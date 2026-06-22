from inference.recipe_structurer import RecipeStructurer


def test_fallback_recipe_structurer() -> None:
    context = """
    [00:01 ASR] Today we are making lemon garlic pasta.
    [00:03 OCR] Ingredients: pasta garlic butter lemon parmesan.
    [00:10 ASR] Boil the pasta for 10 minutes. Add garlic and butter. Finish with parmesan.
    """

    structurer = RecipeStructurer()
    recipe = structurer.structure_recipe(context, source_video="demo.mp4")

    assert recipe.title
    assert len(recipe.ingredients) >= 2
    assert len(recipe.steps) >= 1
