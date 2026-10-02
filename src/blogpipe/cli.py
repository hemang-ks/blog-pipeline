import hashlib
from datetime import UTC, datetime
from pathlib import Path

import typer

from blogpipe import __version__
from blogpipe.ingest import ingest as run_ingest
from blogpipe.lint import format_report
from blogpipe.lint import lint_file as run_lint
from blogpipe.post import APPROVAL_STAGE, STAGES, Post, load_post, save_post, topic_dir

app = typer.Typer()


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(__version__)
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", callback=_version_callback, is_eager=True),
) -> None:
    pass


INTAKE_TEMPLATE = """# Intake — <working title>

Mode: auto            # auto | technical | strategy
Audience: <who, specifically — e.g., "platform leads at banks standing up their first shared inference cluster">
Reader walks away with: <one sentence>
My angle (optional): <what I think most people get wrong here>
Position to use (optional): <P# from style/positions.md>
Stories I could use (optional, anonymized; Claude appends any story you tell it in-session here, dated):
-
Must include:
-
Must avoid:
-
Length override (optional): <e.g., 1,500 words>
Publish target: substack | medium | both
"""

URLS_TEMPLATE = (
    '# One URL per line. Optional note after " | ". Lines starting with # are ignored.\n'
)

APPROVAL_STATE_LABEL = {"missing": "missing", "valid": "valid", "stale": "STALE"}

_SIMPLE_NEXT_COMMAND = {
    "intake": "uv run blog ingest topics/{slug}",
    "ingested": "type /blog-research {slug}",
    "drafted": "type /blog-finish {slug}",
    "final": "ready to publish — see PLAYBOOK.md §2 step 9",
}


@app.command("new")
def new(slug: str) -> None:
    tdir = topic_dir(slug)
    if tdir.exists():
        typer.echo(f"Error: topics/{slug} already exists.", err=True)
        raise typer.Exit(code=1)

    (tdir / "inputs" / "files").mkdir(parents=True)
    (tdir / "corpus").mkdir()
    (tdir / "research").mkdir()
    (tdir / "out").mkdir()

    (tdir / "intake.md").write_text(INTAKE_TEMPLATE)
    (tdir / "inputs" / "urls.txt").write_text(URLS_TEMPLATE)
    (tdir / "inputs" / "files" / ".gitkeep").write_text("")

    save_post(Post(slug=slug))

    typer.echo(f"Created topics/{slug}/")


def _next_command(post: Post) -> str:
    if post.stage in _SIMPLE_NEXT_COMMAND:
        return _SIMPLE_NEXT_COMMAND[post.stage].format(slug=post.slug)

    name = "brief" if post.stage == "brief_review" else "outline"
    state = post.approval_state(name, topic_dir(post.slug))
    if state == "valid":
        target = "outline" if name == "brief" else "draft"
        return f"type /blog-write {post.slug} ({target})"
    if state == "stale":
        return f"{name} approval is STALE — review {name}.md and re-approve"
    return f'review {name}.md, then say "{name} approved"'


@app.command("status")
def status(
    slug: str,
    set_: str = typer.Option(None, "--set"),
    published_url: str = typer.Option(None, "--published-url"),
) -> None:
    post = load_post(slug)

    changed = False
    if set_ is not None:
        post.set_stage(set_)
        changed = True
    if published_url is not None:
        post.published_url = published_url
        changed = True
    if changed:
        save_post(post)

    tdir = topic_dir(slug)
    typer.echo(f"slug: {post.slug}")
    typer.echo(f"stage: {post.stage}")
    for name in ("brief", "outline"):
        state = post.approval_state(name, tdir)
        typer.echo(f"approval[{name}]: {APPROVAL_STATE_LABEL[state]}")

    candidate_files = [
        "intake.md",
        "brief.md",
        "outline.md",
        "draft.md",
        "edited.md",
        "factcheck.md",
        "lint-report.md",
        "out/final.md",
        "out/final.html",
        "out/meta.md",
    ]
    present = [f for f in candidate_files if (tdir / f).exists()]
    typer.echo(f"files present: {', '.join(present) if present else '(none)'}")
    typer.echo(f"published_url: {post.published_url or '(none)'}")
    typer.echo(f"next: {_next_command(post)}")


@app.command("approve")
def approve(slug: str, name: str) -> None:
    if name not in APPROVAL_STAGE:
        typer.echo(f"Error: unknown approval '{name}'; expected brief or outline.", err=True)
        raise typer.Exit(code=1)

    post = load_post(slug)
    tdir = topic_dir(slug)
    file_path = tdir / f"{name}.md"
    required_stage = APPROVAL_STAGE[name]

    if not file_path.exists():
        typer.echo(f"Error: {file_path} does not exist.", err=True)
        raise typer.Exit(code=1)
    if post.stage != required_stage:
        typer.echo(
            f"Error: cannot approve {name} — stage is '{post.stage}', expected '{required_stage}'.",
            err=True,
        )
        raise typer.Exit(code=1)

    digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
    post.approvals[name] = {"date": datetime.now(UTC).date().isoformat(), "sha256": digest}
    save_post(post)
    typer.echo(f"Approved {name} for {slug} ({digest[:12]}...)")


@app.command("reset")
def reset(slug: str, stage: str) -> None:
    if stage not in STAGES:
        typer.echo(f"Error: unknown stage '{stage}'.", err=True)
        raise typer.Exit(code=1)

    post = load_post(slug)
    cleared = post.reset_to(stage)
    save_post(post)

    typer.echo(f"Reset {slug} to stage '{stage}'.")
    typer.echo(f"Cleared approvals: {', '.join(cleared)}" if cleared else "No approvals cleared.")


@app.command("ingest")
def ingest_cmd(directory: str, force: bool = typer.Option(False, "--force")) -> None:
    summary = run_ingest(Path(directory), force=force)

    typer.echo(f"{'ID':<5} {'status':<8} origin / reason")
    for row in summary.rows:
        typer.echo(f"{row['id']:<5} {row['status']:<8} {row['origin']}")
        if row["reason"]:
            typer.echo(f"      ↳ {row['reason']}")

    typer.echo(
        f"\nok={summary.ok} partial={summary.partial} "
        f"failed={summary.failed} skipped={summary.skipped}"
    )


@app.command("lint")
def lint_cmd(
    file: str,
    mode: str = typer.Option(None, "--mode"),
    sources: str = typer.Option(None, "--sources"),
    report: str = typer.Option(None, "--report"),
    no_length: bool = typer.Option(False, "--no-length"),
) -> None:
    path = Path(file)
    sources_path = Path(sources) if sources else None
    findings = run_lint(path, mode=mode, sources_path=sources_path, check_length=not no_length)

    text = format_report(path, findings)
    typer.echo(text)
    if report:
        Path(report).write_text(text)

    hard_count = sum(1 for f in findings if f.severity == "hard")
    if hard_count > 0:
        raise typer.Exit(code=1)
