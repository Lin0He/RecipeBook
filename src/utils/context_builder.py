from __future__ import annotations

import re
from pathlib import Path

from recipebook.config import settings
from recipebook.schemas import MergedContext, OCRSegment, TranscriptSegment

PLATFORM_NOISE_PATTERNS = [
    r"\btiktok\b",
    r"\binstagram\b",
    r"\byoutube\b",
    r"\bpinterest\b",
    r"\bsubscribe\b",
    r"\bfollow\b",
    r"\blike\s+and\s+subscribe\b",
    r"\blink\s+in\s+bio\b",
    r"\bfyp\b",
]

def normalize_text(text: str) -> str:
    text = text.strip()
    text = text.replace("♪", " ")
    text = text.replace("♫", " ")
    text = text.replace("•", " ")
    text = text.replace("|", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def deduplicate_nearby_events(
    events: list[tuple[float, str, str]],
    time_window_sec: float = 4.0,
) -> list[tuple[float, str, str]]:
    deduped: list[tuple[float, str, str]] = []

    for timestamp, source_type, text in events:
        normalized = _dedupe_key(text)

        duplicate = False
        for prev_timestamp, _, prev_text in deduped[-5:]:
            if abs(timestamp - prev_timestamp) > time_window_sec:
                continue

            prev_normalized = _dedupe_key(prev_text)
            if _text_similarity(normalized, prev_normalized) >= 0.88:
                duplicate = True
                break

        if not duplicate:
            deduped.append((timestamp, source_type, text))

    return deduped


def _dedupe_key(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _text_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0

    a_tokens = set(a.split())
    b_tokens = set(b.split())

    if not a_tokens or not b_tokens:
        return 0.0

    return len(a_tokens & b_tokens) / len(a_tokens | b_tokens)


def looks_like_noise(text: str, *, source_type: str) -> bool:
    text = normalize_text(text)
    lowered = text.lower()

    if not text:
        return True

    # Platform / UI watermark noise
    if any(re.search(pattern, lowered) for pattern in PLATFORM_NOISE_PATTERNS):
        return True

    # OCR often produces tiny random fragments.
    if source_type == "OCR" and len(text) < 5:
        return True

    alpha_count = sum(char.isalpha() for char in text)
    digit_count = sum(char.isdigit() for char in text)
    alnum_count = sum(char.isalnum() for char in text)
    total_count = len(text)

    alpha_ratio = alpha_count / max(total_count, 1)
    alnum_ratio = alnum_count / max(total_count, 1)

    # Mostly symbols, punctuation, or broken OCR.
    if alnum_ratio < 0.45:
        return True

    # Mostly numbers and symbols, e.g. "4 E wuldou) 4 79643'"
    if source_type == "OCR" and digit_count >= alpha_count:
        return True

    # Too many isolated one-character tokens usually means OCR garbage.
    tokens = text.split()
    if source_type == "OCR" and len(tokens) >= 3:
        one_char_tokens = sum(1 for token in tokens if len(token.strip(".,:;!?()[]{}")) <= 1)
        if one_char_tokens / len(tokens) > 0.5:
            return True

    # Repeated character garbage, e.g. "~~~~", "////", "aaaaaaa"
    if re.search(r"(.)\1{5,}", text):
        return True

    # ASR should be filtered less aggressively than OCR.
    # Do not apply semantic filtering here.
    if source_type == "ASR":
        return False

    # OCR text with almost no letters is likely bad.
    if source_type == "OCR" and alpha_ratio < 0.35:
        return True

    return False


def build_merged_context(
    video_id: str,
    source_video: str,
    ocr_segments: list,
    transcript_segments: list,
):
    events: list[tuple[float, str, str]] = []

    for segment in ocr_segments:
        text = normalize_text(segment.text)
        if looks_like_noise(text, source_type="OCR"):
            continue

        events.append(
            (
                float(segment.timestamp_sec),
                "OCR",
                text,
            )
        )

    for segment in transcript_segments:
        text = normalize_text(segment.text)
        if looks_like_noise(text, source_type="ASR"):
            continue

        events.append(
            (
                float(segment.start_sec),
                "ASR",
                text,
            )
        )

    events.sort(key=lambda item: item[0])

    events = deduplicate_nearby_events(events)

    lines = []
    for timestamp, source_type, text in events:
        lines.append(f"[{format_timestamp(timestamp)} {source_type}] {text}")

    merged_text = "\n".join(lines)

    return MergedContext(
        video_id=video_id,
        source_video=source_video,
        merged_text=merged_text,
    )

def format_timestamp(seconds: float) -> str:
    seconds = int(seconds)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"


def save_context(context: MergedContext) -> str:
    output_dir = Path(settings.context_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{context.video_id}_context.txt"
    path.write_text(context.merged_text, encoding="utf-8")
    return str(path)


def _fmt_time(seconds: float) -> str:
    seconds_i = int(seconds)
    minutes = seconds_i // 60
    remaining = seconds_i % 60
    return f"{minutes:02d}:{remaining:02d}"


def _timestamp_sort_key(line: str) -> int:
    try:
        timestamp = line.split("]", 1)[0].strip("[").split()[0].split("-")[0]
        minute, second = timestamp.split(":")
        return int(minute) * 60 + int(second)
    except Exception:
        return 0


def _dedupe_nearby_lines(text: str) -> str:
    seen: set[str] = set()
    cleaned: list[str] = []
    for line in text.splitlines():
        normalized = " ".join(line.lower().split())
        content = normalized.split("]", 1)[-1].strip()
        if content and content not in seen:
            seen.add(content)
            cleaned.append(line)
    return "\n".join(cleaned)
