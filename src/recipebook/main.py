from __future__ import annotations

from fastapi import FastAPI

from recipebook.api import router
from recipebook.config import settings


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.3.0",
        description="Video-to-recipe AI tool using OCR, ASR, and recipe structuring.",
    )
    app.include_router(router)
    return app


app = create_app()
