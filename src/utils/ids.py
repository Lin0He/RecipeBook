import hashlib
from pathlib import Path


def stable_id(value: str, prefix: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]
    return f"{prefix}_{digest}"


def file_id(path: str | Path, prefix: str) -> str:
    p = Path(path)
    return stable_id(str(p.resolve()), prefix)
