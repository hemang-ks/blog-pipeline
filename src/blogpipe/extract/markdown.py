from __future__ import annotations

from pathlib import Path

import yaml

from blogpipe.extract import ExtractResult


def extract_markdown(path: Path) -> ExtractResult:
    raw = path.read_text(encoding="utf-8")
    title: str | None = None
    author: str | None = None
    published: str | None = None
    body = raw

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {}
            if isinstance(frontmatter, dict):
                title = frontmatter.get("title")
                author = frontmatter.get("author")
                raw_published = frontmatter.get("date") or frontmatter.get("published")
                published = str(raw_published) if raw_published is not None else None
            body = parts[2].lstrip("\n")

    if not title:
        for line in body.splitlines():
            stripped = line.strip()
            if stripped.startswith("# "):
                title = stripped[2:].strip()
                break

    words = len(body.split())
    return ExtractResult(
        status="ok",
        title=title,
        author=author,
        published=published,
        text=body,
        words=words,
    )
