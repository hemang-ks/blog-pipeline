from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

HEADER = "| ID | type | title | origin | fetched | words | status | note |\n"
SEPARATOR = "|---|---|---|---|---|---|---|---|\n"


@dataclass
class SourceEntry:
    id: str
    type: str
    title: str
    origin: str
    fetched: str
    words: int
    status: str
    note: str = ""


def _escape(cell: str | None) -> str:
    return (cell or "").replace("|", "\\|").replace("\n", " ")


def load_entries(sources_path: Path) -> list[SourceEntry]:
    if not sources_path.exists():
        return []

    entries = []
    for line in sources_path.read_text().splitlines():
        if not line.startswith("|") or line.startswith(("| ID", "|---")):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        id_, type_, title, origin, fetched, words, status, note = cells[:8]
        entries.append(
            SourceEntry(
                id=id_,
                type=type_,
                title=title,
                origin=origin,
                fetched=fetched,
                words=int(words) if words.isdigit() else 0,
                status=status,
                note=note,
            )
        )
    return entries


def save_entries(sources_path: Path, entries: list[SourceEntry]) -> None:
    lines = [HEADER, SEPARATOR]
    for e in entries:
        lines.append(
            f"| {e.id} | {_escape(e.type)} | {_escape(e.title)} | {_escape(e.origin)} | "
            f"{_escape(e.fetched)} | {e.words} | {_escape(e.status)} | {_escape(e.note)} |\n"
        )
    sources_path.write_text("".join(lines))


def next_id(entries: list[SourceEntry], prefix: str) -> str:
    existing = [
        int(e.id[len(prefix) :])
        for e in entries
        if e.id.startswith(prefix) and e.id[len(prefix) :].isdigit()
    ]
    return f"{prefix}{max(existing, default=0) + 1}"


def find_by_origin(entries: list[SourceEntry], origin: str) -> SourceEntry | None:
    for e in entries:
        if e.origin == origin:
            return e
    return None


def upsert(entries: list[SourceEntry], entry: SourceEntry) -> None:
    for i, e in enumerate(entries):
        if e.id == entry.id:
            entries[i] = entry
            return
    entries.append(entry)
