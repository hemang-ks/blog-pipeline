from __future__ import annotations

from pathlib import Path

import pymupdf
import pymupdf4llm

from blogpipe.extract import ExtractResult


def extract_pdf(path: Path) -> ExtractResult:
    try:
        markdown = pymupdf4llm.to_markdown(str(path))
    except (RuntimeError, ValueError, OSError) as exc:
        return ExtractResult(status="failed", reason=str(exc))

    if not markdown or not markdown.strip():
        return ExtractResult(status="failed", reason="no extractable text")

    with pymupdf.open(str(path)) as doc:
        pages = doc.page_count

    words = len(markdown.split())
    return ExtractResult(status="ok", text=markdown, words=words, pages=pages)
