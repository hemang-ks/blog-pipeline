# Machine setup

## Prerequisites
- [Homebrew](https://brew.sh)
- [`uv`](https://docs.astral.sh/uv/): `brew install uv`
- [`gh`](https://cli.github.com/): `brew install gh`
- [Claude Code](https://claude.com/claude-code): `npm install -g @anthropic-ai/claude-code` (or see the install docs)

## Clone

> **Never clone into iCloud Drive** (`~/Library/Mobile Documents/...`). iCloud sync corrupts `.git` directories and creates "conflicted copy" files. Git and GitHub are the sync mechanism across machines — clone into a plain local folder instead.

```bash
mkdir -p ~/code && cd ~/code
gh repo clone <org-or-user>/blog-pipeline
cd blog-pipeline
uv sync
```

## Environment variables
None required in V1. All LLM work runs inside Claude Code; the Python CLI makes no external API calls.

## Logins
- `gh auth login` — GitHub CLI, needed for PRs and repo access.
- Claude Code: log in on first run (`claude` in the repo root, or via the desktop/IDE app).

## `style/confidential.yaml`
This file is local-only and **gitignored** — it never travels through git. On each new machine, recreate it from the template:

```bash
cp style/confidential.example.yaml style/confidential.yaml
```

Then fill it in with client names, abbreviations, project codenames, and partner names that must never appear in a post. Claude Code is denied read/edit/write access to this file; only `blog lint` reads it.

## Verify

Run this after `uv sync` on any machine to confirm the setup works:

```bash
uv sync && uv run blog --version && uv run pytest -q && uv run ruff check .
```

All four should succeed, with `blog --version` printing `0.1.0`.
