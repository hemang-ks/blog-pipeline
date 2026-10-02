from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

from blogpipe.extract import ExtractResult
from blogpipe.extract.html import extract_url
from blogpipe.extract.markdown import extract_markdown
from blogpipe.extract.pdf import extract_pdf
from blogpipe.post import Post
from blogpipe.registry import (
    SourceEntry,
    find_by_origin,
    load_entries,
    next_id,
    save_entries,
    upsert,
)


def _kebab(text: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return text or "untitled"


def _read_url_lines(path: Path) -> list[tuple[str, str]]:
    if not path.exists():
        return []
    out = []
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            url, note = line.split("|", 1)
            out.append((url.strip(), note.strip()))
        else:
            out.append((line, ""))
    return out


def _file_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in (".md", ".markdown"):
        return "markdown"
    return "unsupported"


@dataclass
class IngestSummary:
    ok: int = 0
    partial: int = 0
    failed: int = 0
    skipped: int = 0
    rows: list[dict] = field(default_factory=list)


def _extract(kind: str, origin: str, topic_dir: Path) -> ExtractResult:
    if kind == "html":
        return extract_url(origin)
    if kind == "pdf":
        return extract_pdf(topic_dir / origin)
    if kind == "markdown":
        return extract_markdown(topic_dir / origin)
    return ExtractResult(status="failed", reason=f"unsupported source kind: {kind}")


def _ingest_one(
    topic_dir: Path,
    corpus_dir: Path,
    entries: list[SourceEntry],
    origin: str,
    kind: str,
    note: str,
    prefix: str,
    force: bool,
    summary: IngestSummary,
) -> None:
    existing = find_by_origin(entries, origin)
    already_ingested = (
        existing
        and existing.status in ("ok", "partial")
        and not force
        and list(corpus_dir.glob(f"{existing.id}-*.md"))
    )
    if already_ingested:
        summary.skipped += 1
        summary.rows.append(
            {"id": existing.id, "origin": origin, "status": "skipped", "reason": ""}
        )
        return

    source_id = existing.id if existing else next_id(entries, prefix)
    result = _extract(kind, origin, topic_dir)
    fetched = datetime.now(UTC).date().isoformat()
    title = result.title or origin

    if result.reason:
        combined_note = f"{note} — {result.reason}" if note else result.reason
    else:
        combined_note = note

    entry = SourceEntry(
        id=source_id,
        type=kind,
        title=title,
        origin=origin,
        fetched=fetched,
        words=result.words,
        status=result.status,
        note=combined_note,
    )
    upsert(entries, entry)

    if result.status in ("ok", "partial"):
        frontmatter = {
            "id": source_id,
            "title": title,
            "origin": origin,
            "author": result.author,
            "published": result.published,
            "fetched": fetched,
            "words": result.words,
            "status": result.status,
        }
        body = (
            "---\n"
            + yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False)
            + "---\n\n"
            + result.text
            + "\n"
        )
        (corpus_dir / f"{source_id}-{_kebab(title)}.md").write_text(body)
        if result.status == "ok":
            summary.ok += 1
        else:
            summary.partial += 1
    else:
        summary.failed += 1

    summary.rows.append(
        {"id": source_id, "origin": origin, "status": result.status, "reason": result.reason or ""}
    )


def _maybe_advance_stage(topic_dir: Path) -> None:
    post_yaml = topic_dir / "post.yaml"
    if not post_yaml.exists():
        return
    data = yaml.safe_load(post_yaml.read_text())
    post = Post.from_dict(data)
    if post.stage == "intake":
        post.set_stage("ingested")
        post_yaml.write_text(
            yaml.safe_dump(post.to_dict(), sort_keys=False, default_flow_style=False)
        )


def ingest(topic_dir: Path, force: bool = False) -> IngestSummary:
    inputs_dir = topic_dir / "inputs"
    corpus_dir = topic_dir / "corpus"
    corpus_dir.mkdir(parents=True, exist_ok=True)
    sources_path = topic_dir / "sources.md"

    entries = load_entries(sources_path)
    summary = IngestSummary()

    s_items: list[tuple[str, str, str]] = [
        (url, "html", note) for url, note in _read_url_lines(inputs_dir / "urls.txt")
    ]
    files_dir = inputs_dir / "files"
    if files_dir.exists():
        for f in sorted(files_dir.iterdir()):
            if f.is_dir() or f.name == ".gitkeep":
                continue
            s_items.append((str(f.relative_to(topic_dir)), _file_kind(f), ""))

    w_items: list[tuple[str, str, str]] = [
        (url, "html", note) for url, note in _read_url_lines(inputs_dir / "urls-web.txt")
    ]

    for origin, kind, note in s_items:
        _ingest_one(topic_dir, corpus_dir, entries, origin, kind, note, "S", force, summary)
    for origin, kind, note in w_items:
        _ingest_one(topic_dir, corpus_dir, entries, origin, kind, note, "W", force, summary)

    save_entries(sources_path, entries)
    _maybe_advance_stage(topic_dir)

    return summary
