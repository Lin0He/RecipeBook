from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RecipeBook"
    app_env: str = "local"

    use_mock_inference: bool = True

    ocr_languages: str = "en"
    ocr_gpu: bool = False

    asr_model_size: str = "tiny"
    asr_device: str = "cpu"
    asr_compute_type: str = "int8"

    llm_provider: str = "deepseek"
    llm_api_key: str | None = None
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-v4-flash"
    llm_temperature: float = 0.2

    video_dir: str = "data/videos"
    frame_dir: str = "data/frames"
    audio_dir: str = "data/audio"
    context_dir: str = "outputs/context"
    recipe_json_dir: str = "outputs/recipes/json"
    recipe_markdown_dir: str = "outputs/recipes/markdown"

    frame_interval_seconds: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def ocr_language_list(self) -> list[str]:
        return [item.strip() for item in self.ocr_languages.split(",") if item.strip()]

    def ensure_directories(self) -> None:
        for directory in [
            self.video_dir,
            self.frame_dir,
            self.audio_dir,
            self.context_dir,
            self.recipe_json_dir,
            self.recipe_markdown_dir,
        ]:
            Path(directory).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()
