import hashlib

import pytest
import yaml
from typer.testing import CliRunner

from blogpipe.cli import app
from blogpipe.post import Post, load_post, post_path, save_post, topic_dir

runner = CliRunner()


@pytest.fixture(autouse=True)
def blog_root(tmp_path, monkeypatch):
    monkeypatch.setenv("BLOG_ROOT", str(tmp_path))
    return tmp_path


def test_new_creates_topic_skeleton():
    result = runner.invoke(app, ["new", "g1"])
    assert result.exit_code == 0

    tdir = topic_dir("g1")
    assert (tdir / "post.yaml").exists()
    assert (tdir / "intake.md").exists()
    assert (tdir / "inputs" / "urls.txt").exists()
    assert (tdir / "inputs" / "files" / ".gitkeep").exists()
    assert (tdir / "corpus").is_dir()
    assert (tdir / "research").is_dir()
    assert (tdir / "out").is_dir()

    post = load_post("g1")
    assert post.slug == "g1"
    assert post.stage == "intake"
    assert post.approvals == {"brief": None, "outline": None}


def test_new_refuses_if_exists():
    runner.invoke(app, ["new", "g1"])
    result = runner.invoke(app, ["new", "g1"])
    assert result.exit_code == 1


def test_status_prints_stage_and_next_command():
    runner.invoke(app, ["new", "g1"])
    result = runner.invoke(app, ["status", "g1"])
    assert result.exit_code == 0
    assert "stage: intake" in result.output
    assert "approval[brief]: missing" in result.output
    assert "uv run blog ingest topics/g1" in result.output


def test_status_set_moves_stage_forward():
    runner.invoke(app, ["new", "g1"])
    result = runner.invoke(app, ["status", "g1", "--set", "ingested"])
    assert result.exit_code == 0
    assert load_post("g1").stage == "ingested"


def test_status_set_backward_fails():
    runner.invoke(app, ["new", "g1"])
    runner.invoke(app, ["status", "g1", "--set", "ingested"])
    result = runner.invoke(app, ["status", "g1", "--set", "intake"])
    assert result.exit_code != 0


def test_set_stage_forward_only_api():
    post = Post(slug="g1", stage="ingested")
    with pytest.raises(ValueError):
        post.set_stage("intake")
    post.set_stage("ingested")
    post.set_stage("brief_review")
    assert post.stage == "brief_review"


def test_published_url_stored_and_persists():
    runner.invoke(app, ["new", "g1"])
    result = runner.invoke(app, ["status", "g1", "--published-url", "https://example.com/post"])
    assert result.exit_code == 0
    assert load_post("g1").published_url == "https://example.com/post"

    result = runner.invoke(app, ["status", "g1"])
    assert "https://example.com/post" in result.output


def _advance_to(slug: str, stage: str) -> None:
    from blogpipe.post import STAGES

    post = load_post(slug)
    for s in STAGES[: STAGES.index(stage) + 1]:
        if STAGES.index(s) > post.stage_index():
            post.set_stage(s)
    save_post(post)


def test_approve_refuses_without_file():
    runner.invoke(app, ["new", "g1"])
    _advance_to("g1", "brief_review")
    result = runner.invoke(app, ["approve", "g1", "brief"])
    assert result.exit_code == 1


def test_approve_refuses_wrong_stage():
    runner.invoke(app, ["new", "g1"])
    (topic_dir("g1") / "brief.md").write_text("# Brief\n")
    result = runner.invoke(app, ["approve", "g1", "brief"])
    assert result.exit_code == 1


def test_approve_stores_fingerprint():
    runner.invoke(app, ["new", "g1"])
    _advance_to("g1", "brief_review")
    (topic_dir("g1") / "brief.md").write_text("# Brief\ncontent\n")
    result = runner.invoke(app, ["approve", "g1", "brief"])
    assert result.exit_code == 0

    post = load_post("g1")
    assert post.approvals["brief"] is not None
    expected = hashlib.sha256((topic_dir("g1") / "brief.md").read_bytes()).hexdigest()
    assert post.approvals["brief"]["sha256"] == expected
    assert post.approval_state("brief", topic_dir("g1")) == "valid"


def test_edit_after_approval_goes_stale_then_reapprove_is_valid():
    runner.invoke(app, ["new", "g1"])
    _advance_to("g1", "brief_review")
    brief = topic_dir("g1") / "brief.md"
    brief.write_text("# Brief\nv1\n")
    runner.invoke(app, ["approve", "g1", "brief"])

    brief.write_text("# Brief\nv2 edited\n")
    post = load_post("g1")
    assert post.approval_state("brief", topic_dir("g1")) == "stale"

    result = runner.invoke(app, ["approve", "g1", "brief"])
    assert result.exit_code == 0
    post = load_post("g1")
    assert post.approval_state("brief", topic_dir("g1")) == "valid"


def test_reset_clears_later_approvals_and_keeps_files():
    runner.invoke(app, ["new", "g1"])
    _advance_to("g1", "brief_review")
    (topic_dir("g1") / "brief.md").write_text("# Brief\n")
    runner.invoke(app, ["approve", "g1", "brief"])
    _advance_to("g1", "outline_review")
    (topic_dir("g1") / "outline.md").write_text("# Outline\n")
    runner.invoke(app, ["approve", "g1", "outline"])

    result = runner.invoke(app, ["reset", "g1", "brief_review"])
    assert result.exit_code == 0

    post = load_post("g1")
    assert post.stage == "brief_review"
    assert post.approvals["brief"] is None
    assert post.approvals["outline"] is None
    assert (topic_dir("g1") / "brief.md").exists()
    assert (topic_dir("g1") / "outline.md").exists()


def test_reset_to_outline_review_keeps_brief_approval():
    runner.invoke(app, ["new", "g1"])
    _advance_to("g1", "brief_review")
    (topic_dir("g1") / "brief.md").write_text("# Brief\n")
    runner.invoke(app, ["approve", "g1", "brief"])
    _advance_to("g1", "outline_review")
    (topic_dir("g1") / "outline.md").write_text("# Outline\n")
    runner.invoke(app, ["approve", "g1", "outline"])

    runner.invoke(app, ["reset", "g1", "outline_review"])
    post = load_post("g1")
    assert post.approvals["brief"] is not None
    assert post.approvals["outline"] is None


def test_post_yaml_is_human_readable_block_style():
    runner.invoke(app, ["new", "g1"])
    raw = post_path("g1").read_text()
    assert raw.startswith("slug:")
    data = yaml.safe_load(raw)
    assert data["slug"] == "g1"
