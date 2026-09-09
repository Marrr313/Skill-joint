"""Cheap token estimation (~4 chars per token rule)."""
from __future__ import annotations
from pathlib import Path


def estimate(text_or_path) -> int:
    if isinstance(text_or_path, (str, bytes)):
        if isinstance(text_or_path, bytes):
            chars = len(text_or_path)
        else:
            chars = len(text_or_path)
        return max(1, chars // 4)
    if isinstance(text_or_path, Path):
        try:
            return max(1, text_or_path.stat().st_size // 4)
        except FileNotFoundError:
            return 0
    raise TypeError(f"estimate() got unsupported type: {type(text_or_path)}")
