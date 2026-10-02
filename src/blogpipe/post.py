from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path

import yaml

STAGES = ["intake", "ingested", "brief_review", "outline_review", "drafted", "final"]

APPROVAL_STAGE = {"brief": "brief_review", "outline": "outline_review"}


@dataclass
class Post:
    slug: str
    title_working: str = ""
    mode: str = "auto"
    stage: str = "intake"
    approvals: dict[str, dict | None] = field(
        default_factory=lambda: {"brief": None, "outline": None}
    )
    waivers: list[dict] = field(default_factory=list)
    published_url: str | None = None
    created: str = field(default_factory=lambda: datetime.now(UTC).date().isoformat())

    def stage_index(self) -> int:
        return STAGES.index(self.stage)

    def set_stage(self, new_stage: str) -> None:
        if new_stage not in STAGES:
            raise ValueError(f"unknown stage: {new_stage}")
        if STAGES.index(new_stage) < self.stage_index():
            raise ValueError(
                f"cannot move backward from '{self.stage}' to '{new_stage}'; use reset_to()"
            )
        self.stage = new_stage

    def reset_to(self, stage: str) -> list[str]:
        if stage not in STAGES:
            raise ValueError(f"unknown stage: {stage}")
        target_index = STAGES.index(stage)
        cleared = []
        for name, approval_stage in APPROVAL_STAGE.items():
            if STAGES.index(approval_stage) >= target_index and self.approvals.get(name):
                self.approvals[name] = None
                cleared.append(name)
        self.stage = stage
        return cleared

    def approval_state(self, name: str, topic_dir: Path) -> str:
        approval = self.approvals.get(name)
        if not approval:
            return "missing"
        file_path = topic_dir / f"{name}.md"
        if not file_path.exists():
            return "missing"
        current_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        return "valid" if current_hash == approval["sha256"] else "stale"

    def to_dict(self) -> dict:
        return {
            "slug": self.slug,
            "title_working": self.title_working,
            "mode": self.mode,
            "stage": self.stage,
            "approvals": self.approvals,
            "waivers": self.waivers,
            "published_url": self.published_url,
            "created": self.created,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Post:
        return cls(
            slug=data["slug"],
            title_working=data.get("title_working", ""),
            mode=data.get("mode", "auto"),
            stage=data.get("stage", "intake"),
            approvals=data.get("approvals") or {"brief": None, "outline": None},
            waivers=data.get("waivers") or [],
            published_url=data.get("published_url"),
            created=data.get("created", datetime.now(UTC).date().isoformat()),
        )


def _root() -> Path:
    return Path(os.environ.get("BLOG_ROOT", "."))


def topic_dir(slug: str) -> Path:
    return _root() / "topics" / slug


def post_path(slug: str) -> Path:
    return topic_dir(slug) / "post.yaml"


def load_post(slug: str) -> Post:
    path = post_path(slug)
    data = yaml.safe_load(path.read_text())
    return Post.from_dict(data)


def save_post(post: Post) -> None:
    path = post_path(post.slug)
    path.write_text(yaml.safe_dump(post.to_dict(), sort_keys=False, default_flow_style=False))
