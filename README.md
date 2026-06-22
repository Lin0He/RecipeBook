# RecipeBook: Video-to-Recipe AI Assistant

RecipeBook is a useful AI tool that converts cooking videos into clean recipe documents.

Core flow:

```text
video URL / local video upload
        ↓
OCR from video frames + ASR from audio
        ↓
merged cooking context
        ↓
LLM / rule-based recipe structuring
        ↓
JSON + Markdown recipe files
```

No chatbot. No RAG. No recipe library.

## Install

```bash
brew install uv
brew install ffmpeg
```

Basic install, runnable with mock inference:

```bash
cp .env.example .env
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

Real OCR + ASR install:

```bash
uv pip install -e ".[dev,media]"
```

## Test

Default tests:

```bash
pytest
```

Real model loading checks, may download models:

```bash
USE_MOCK_INFERENCE=false RUN_MEDIA_TESTS=true pytest -m media
```

## Run API

```bash
uvicorn recipebook.main:app --reload
```

Open:

```text
http://127.0.0.1:8000/docs
```

## API

```text
GET  /health
POST /recipes/from-url
POST /recipes/from-video
```

## Project Layout

```text
src/recipebook/
  api.py              # FastAPI endpoints
  config.py           # app settings
  main.py             # app entrypoint
  pipeline.py         # end-to-end product pipeline
  renderer.py         # JSON / Markdown output
  schemas.py          # app-facing data schemas

src/inference/
  ocr.py              # OCR model loading and inference
  asr.py              # ASR model loading and inference
  recipe_structurer.py# LLM / fallback recipe structuring

src/utils/
  video_loader.py     # URL download / uploaded video save
  frame_extractor.py  # ffmpeg video frame extraction
  audio_extractor.py  # ffmpeg audio extraction
  ocr_extractor.py    # frame OCR orchestration
  context_builder.py  # OCR + ASR context fusion
  ids.py              # stable IDs
```
