from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExtractResult:
    status: str  # ok | failed | partial
    reason: str | None = None
    title: str | None = None
    author: str | None = None
    published: str | None = None
    text: str = ""
    words: int = 0
    pages: int | None = None
