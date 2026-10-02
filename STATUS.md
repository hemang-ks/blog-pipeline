# Project Status — blog-pipeline
Last updated: 2026-09-29 · by: Me
Current module: M0
Status values: todo · in-progress · blocked · done · skipped
Rule: Claude Code may mark TASKS done (with evidence). Only Me marks a MODULE done, after verifying its success criteria.

## Resume Here
- Last session: 2026-09-29 · machine: <name> · branch: main
- Last completed: none
- Next action: M0.1 — create GitHub repo, clone, place PLAYBOOK.md at root
- Open questions for Me: G1 and G2 topics (see PLAYBOOK §8)
- Uncommitted/WIP: none

## Modules
| Module | Status | Criteria met | Commit | Notes |
|--------|--------|--------------|--------|-------|
| M0 Setup | todo | 0/6 | — | |
| M1 Ingest | todo | 0/5 | — | |
| M2 Style System | todo | 0/7 | — | |
| M3 Research + Brief | todo | 0/5 | — | |
| M4 Outline + Draft | todo | 0/4 | — | |
| M5 Edit, Fact-check, Export | todo | 0/7 | — | |
| M6 Two-topic Validation | todo | 0/5 | — | |

## M0 — Setup
- [ ] M0.1 Create private repo, clone, add PLAYBOOK.md · Owner: Me · Status: todo · Evidence:
- [x] M0.2 Scaffold project, CLI stub, CI, CLAUDE.md, settings, machine-setup · Owner: Claude Code · Status: done · Evidence: `uv run blog --version` → `0.1.0`; `uv run pytest -q --cov=blogpipe --cov-fail-under=80` → 1 passed, 90.91% coverage; `uv run ruff check .` → All checks passed!; `uv run ruff format --check .` → 10 files already formatted. PR: https://github.com/hemang-ks/blog-pipeline/pull/1
- [ ] M0.3 Copy writing-rules.md and about-me.md into style/ · Owner: Me · Status: todo · Evidence:
- [ ] M0.4 Run verify command; confirm CI green · Owner: Me · Status: todo · Evidence:
Success criteria:
- [ ] `uv run blog --version` prints 0.1.0
- [ ] `uv run pytest -q` passes
- [ ] `uv run ruff check .` clean
- [ ] CI green on main
- [ ] style/writing-rules.md and style/about-me.md committed
- [ ] docs/machine-setup.md verify command passes on this machine

## M1 — Ingest
- [ ] M1.1 `blog new`, `blog status`, `blog approve` (with fingerprint), `blog reset`, post.yaml model · Owner: Claude Code · Status: todo · Evidence:
- [ ] M1.2 Extractors (URL/PDF/MD), ingest, sources.md registry · Owner: Claude Code · Status: todo · Evidence:
- [ ] M1.3 Offline tests with fixtures · Owner: Claude Code · Status: todo · Evidence:
- [ ] M1.4 Provide G1 inputs + intake.md · Owner: Me · Status: todo · Evidence:
- [ ] M1.5 Ingest G1, report failures; Me spot-checks corpus · Owner: Me + Claude Code · Status: todo · Evidence:
Success criteria:
- [ ] pytest passes, with ingest tests running offline
- [ ] `blog new demo` creates the full topic skeleton
- [ ] Re-running ingest keeps IDs stable, and editing an approved file makes its approval stale (tests prove both)
- [ ] G1 corpus has one file per input; failures listed with reason in sources.md
- [ ] Me spot-checked 2 corpus files for extraction quality

## M2 — Style System
- [ ] M2.1 Write exemplar urls.txt + notes.md · Owner: Me · Status: todo · Evidence:
- [ ] M2.2 Ingest exemplars; report truncation/paywall · Owner: Claude Code · Status: todo · Evidence:
- [ ] M2.3 Draft blog-craft.md (two modes) · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M2.4 lint-rules.yaml + `blog lint` + calibration on exemplars · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M2.5 Positions interview → positions.md · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M2.6 Create confidential.yaml · Owner: Me · Status: todo · Evidence:
Success criteria:
- [ ] style/exemplars/corpus has E1–E3 (E3 marked partial or full)
- [ ] blog-craft.md has an "Approved: <date>" line from Me
- [ ] lint tests pass (hard, soft, allow-contexts, code-block skipping, confidential, exemplar overlap, source-corpus overlap, quoted-and-marked passage allowed)
- [ ] Lint calibration report on exemplars reviewed by Me; hard/soft split approved
- [ ] positions.md has ≥6 positions and an "Approved: <date>" line
- [ ] `git check-ignore style/confidential.yaml` prints the path
- [ ] `blog lint` flags a planted confidential term (test)

## M3 — Research + Brief
- [ ] M3.1 researcher subagent · Owner: Claude Code · Status: todo · Evidence:
- [ ] M3.2 /blog-research skill + brief template · Owner: Claude Code · Status: todo · Evidence:
- [ ] M3.3 Run on G1; Me approves brief · Owner: Me + Claude Code · Status: todo · Evidence:
Success criteria:
- [ ] Both files exist and load (`/agents` lists researcher; `/blog-research` is in the / menu)
- [ ] G1 brief.md has every template field filled, including mode + reason
- [ ] Every key claim in brief.md has an S# or W# that resolves in sources.md
- [ ] brief has exactly one counterpoint backed by a W# source; research log shows ≤8 searches
- [ ] `blog status g1` shows the brief approved

## M4 — Outline + Draft
- [ ] M4.1 /blog-write skill · Owner: Claude Code · Status: todo · Evidence:
- [ ] M4.2 Run on G1: outline → Me approves → draft · Owner: Me + Claude Code · Status: todo · Evidence:
Success criteria:
- [ ] /blog-write refuses to draft without a valid outline approval (tested once by typing it before approving)
- [ ] G1 outline approved (`blog status`)
- [ ] G1 draft.md within the mode's word range; `blog lint` hard = 0
- [ ] Every numeric claim and direct quote in draft.md carries a marker

## M5 — Edit, Fact-check, Export
- [ ] M5.1 fact-checker subagent · Owner: Claude Code · Status: todo · Evidence:
- [ ] M5.2 `blog export`, `blog check-links`, gates, tests · Owner: Claude Code · Status: todo · Evidence:
- [ ] M5.3 /blog-finish skill · Owner: Claude Code · Status: todo · Evidence:
- [ ] M5.4 Run on G1; Me test-pastes into a Substack draft · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M5.5 Decide the AI-assistance disclosure policy (Substack + Medium) · Owner: Me · Status: todo · Evidence:
Success criteria:
- [ ] pytest passes, including tests that each gate blocks export (stale approval, unsupported, unmarked, unresolved marker, lint hard)
- [ ] G1 out/final.md, out/final.html, out/meta.md exist
- [ ] G1 factcheck.md: 0 unsupported and 0 unmarked (or waivers with reasons in post.yaml), and 0 experience-untraced
- [ ] `blog check-links g1` reports 0 dead links
- [ ] Pasted into a Substack draft (not published): headings, links, `[n]` citations, code blocks, and sources render correctly
- [ ] Me: "publishable with ≤15 min of edits"
- [ ] Disclosure decision recorded in the Decisions Log (and in blog-craft.md if a disclosure line is used)

## M6 — Two-topic Validation
- [ ] M6.1 Provide G2 inputs (strategy mode) · Owner: Me · Status: todo · Evidence:
- [ ] M6.2 Run the full pipeline on G2 + run report · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M6.3 Retro: propose style/pipeline fixes from my edits; apply the approved ones · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M6.4 docs/runbook.md + README · Owner: Claude Code · Status: todo · Evidence:
Success criteria:
- [ ] G2 reaches `final`, with mode = strategy and all gates passing
- [ ] G2 hands-on time for Me ≤ 90 minutes (logged in run report)
- [ ] Approved retro changes merged; pytest still passes
- [ ] runbook lets a fresh session produce a post with no other docs
- [ ] G1 or G2 published; URL recorded in its post.yaml (`published_url`) and in the Decisions Log

## Blockers
- (none)

## Decisions Log
| Date | Decision | Why |
|------|----------|-----|
| 2026-09-29 | Claude Code–native pipeline + small Python CLI | Simplest option at solo scale; built-in web research; checkpoints are natural |
| 2026-09-29 | Mode auto-proposed in brief, confirmed at checkpoint; overridable | Mode depends on topic, but Me keeps control |
| 2026-09-29 | Research = gap-fill + one counterpoint | Stays close to Me's sources; adds credibility |
| 2026-09-29 | Positions via multiple-choice interview | Faster than writing from scratch; brings out stories |
| 2026-09-29 | Manual publishing; Substack first, Medium via "Import a story" | Substack has no public posting API; Medium import sets the canonical link so the two copies don't compete in search |
| 2026-09-29 | Repo outside iCloud Drive | iCloud sync corrupts .git; git is the sync layer |
| 2026-09-30 | Models: main session Opus; researcher Sonnet; fact-checker pinned to Opus | Voice and verification need the strongest model; research is search-and-summarize |
