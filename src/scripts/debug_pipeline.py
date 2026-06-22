from pathlib import Path

from recipebook.pipeline import RecipeBookPipeline

video_path = Path("data/videos/pinterest.mp4")
video_id = video_path.stem

pipeline = RecipeBookPipeline()

result = pipeline.run_from_video_path(
    video_id=video_id,
    video_path=str(video_path),
)

print("\n=== RecipeBook Pipeline Debug ===")
print("Video ID:", result.video_id)
print("Recipe ID:", result.recipe.recipe_id)
print("Title:", result.recipe.title)
print("JSON:", result.json_path)
print("Markdown:", result.markdown_path)
print("Context:", result.context_path)
print("OCR segments:", result.ocr_segments)
print("Transcript segments:", result.transcript_segments)