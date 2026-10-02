# Project Status — blog-pipeline
Last updated: 2026-10-02 · by: Me
Current module: M2
Status values: todo · in-progress · blocked · done · skipped
Rule: Claude Code may mark TASKS done (with evidence). Only Me marks a MODULE done, after verifying its success criteria.

## Resume Here
- Last session: 2026-10-02 · machine: <name> · branch: main
- Last completed: M0 (done), M1 (done), M2.1, M2.2, M2.3, M2.4
- Next action: M2.5 — positions interview (Claude Code, interactive via AskUserQuestion)
- Open questions for Me: G1 (done — llm-d-distributed-inference) and G2 topics (see PLAYBOOK §8)
- Uncommitted/WIP: none

## Modules
| Module | Status | Criteria met | Commit | Notes |
|--------|--------|--------------|--------|-------|
| M0 Setup | done | 6/6 | d81510f | Merged PR #1, #2 |
| M1 Ingest | done | 5/5 | 53a4ccc | Merged PR #3 |
| M2 Style System | in-progress | 3/7 | — | M2.1-M2.4 done; M2.5-M2.6 remain |
| M3 Research + Brief | todo | 0/5 | — | |
| M4 Outline + Draft | todo | 0/4 | — | |
| M5 Edit, Fact-check, Export | todo | 0/7 | — | |
| M6 Two-topic Validation | todo | 0/5 | — | |

## M0 — Setup
- [x] M0.1 Create private repo, clone, add PLAYBOOK.md · Owner: Me · Status: done · Evidence: repo `hemang-ks/blog-pipeline`, `PLAYBOOK.md` committed to main (commit `4468338`)
- [x] M0.2 Scaffold project, CLI stub, CI, CLAUDE.md, settings, machine-setup · Owner: Claude Code · Status: done · Evidence: `uv run blog --version` → `0.1.0`; `uv run pytest -q --cov=blogpipe --cov-fail-under=80` → 1 passed, 90.91% coverage; `uv run ruff check .` → All checks passed!; `uv run ruff format --check .` → 10 files already formatted. PR: https://github.com/hemang-ks/blog-pipeline/pull/1 (CI: pass)
- [x] M0.3 Copy writing-rules.md and about-me.md into style/ · Owner: Me · Status: done · Evidence: `style/writing-rules.md` (135 lines) and `style/about-me.md` (139 lines) present and committed (commit `06161bb`)
- [x] M0.4 Run verify command; confirm CI green · Owner: Me · Status: done · Evidence: Hemang ran `uv sync && uv run blog --version && uv run pytest -q && uv run ruff check .` and confirmed it passed; PR #1 CI green
Success criteria:
- [x] `uv run blog --version` prints 0.1.0
- [x] `uv run pytest -q` passes
- [x] `uv run ruff check .` clean
- [x] CI green on main
- [x] style/writing-rules.md and style/about-me.md committed
- [x] docs/machine-setup.md verify command passes on this machine

## M1 — Ingest
- [x] M1.1 `blog new`, `blog status`, `blog approve` (with fingerprint), `blog reset`, post.yaml model · Owner: Claude Code · Status: done · Evidence: `src/blogpipe/post.py`, `src/blogpipe/cli.py`, `tests/test_post.py` (15 tests, all passing); `uv run pytest -q --cov=blogpipe --cov-fail-under=80` → 90.68% coverage; `uv run ruff check .` → All checks passed!
- [x] M1.2 Extractors (URL/PDF/MD), ingest, sources.md registry · Owner: Claude Code · Status: done · Evidence: `src/blogpipe/extract/{html,pdf,markdown}.py`, `src/blogpipe/registry.py`, `src/blogpipe/ingest.py`, `blog ingest <dir> [--force]` CLI command; end-to-end smoke test (`blog new` → `blog ingest` → `blog status`) confirmed stage auto-advances intake→ingested
- [x] M1.3 Offline tests with fixtures · Owner: Claude Code · Status: done · Evidence: `tests/test_ingest.py` (12 tests, all offline via monkeypatched httpx + generated PDF), `tests/fixtures/{article.html,paywall.html,notes.md}`; full suite 27 passed; `uv run pytest -q --cov=blogpipe --cov-fail-under=80` → 89.64% coverage; `uv run ruff check .` → All checks passed! PR: https://github.com/hemang-ks/blog-pipeline/pull/3 (CI: pass)
- [x] M1.4 Provide G1 inputs + intake.md · Owner: Me · Status: done · Evidence: `topics/llm-d-distributed-inference/` — `intake.md` filled in (mode: technical, audience, angle, must include/avoid), 3 URLs in `inputs/urls.txt`, 1 PDF in `inputs/files/` (later swapped for a URL per M1.5 spot-check)
- [x] M1.5 Ingest G1, report failures; Me spot-checks corpus · Owner: Me + Claude Code · Status: done · Evidence: `uv run blog ingest topics/llm-d-distributed-inference` → ok=3 partial=1 failed=0 skipped=0; S1 Red Hat ok, S2 llm-d.ai/docs partial (thin landing page, 147 words, not a bug), S3 Google Cloud ok, S4 re-ingested from the Solo.io URL (https://www.solo.io/blog/llm-d-distributed-inference-serving-on-kubernetes) instead of the browser-printed PDF, which had nav/chat-widget text corrupting the article body. Re-ingest also surfaced and fixed a real registry bug: titles containing a literal `\|` (e.g. "Page Title \| Site Name") broke row parsing in `sources.md` and silently defeated dedup, producing duplicate S2–S5 rows. Fixed `_split_row` in `src/blogpipe/registry.py` to respect the `\|` escape; added regression tests. Confirmed stable re-run (`skipped=4`, no duplicates) and clean S4 extraction. Hemang confirmed the spot-check.
Success criteria:
- [x] pytest passes, with ingest tests running offline
- [x] `blog new demo` creates the full topic skeleton
- [x] Re-running ingest keeps IDs stable, and editing an approved file makes its approval stale (tests prove both)
- [x] G1 corpus has one file per input; failures listed with reason in sources.md
- [x] Me spot-checked 2 corpus files for extraction quality

## M2 — Style System
- [x] M2.1 Write exemplar urls.txt + notes.md · Owner: Me · Status: done · Evidence: `style/exemplars/inputs/urls.txt` (E1-E3), `style/exemplars/notes.md` with Observed lines (Claude) and What I like / Don't copy (Hemang) filled in for all three. Not a paid Pragmatic Engineer subscriber, so no E3 PDF — free portion used.
- [x] M2.2 Ingest exemplars; report truncation/paywall · Owner: Claude Code · Status: done · Evidence: `uv run blog ingest style/exemplars` → ok=1 (E3, 3002 words) failed=2 (E1, E2 — Medium 403, confirmed via both httpx and a WebFetch retry, no further workaround per instructions). Also fixed an ingest.py bug found along the way: a failure's reason was silently dropped from sources.md's note column whenever the input line also had a user note (e.g. "E1 technical"); now both are recorded. 29 tests pass, 89.83% coverage. PR: https://github.com/hemang-ks/blog-pipeline/pull/4 (CI: pass)
- [x] M2.3 Draft blog-craft.md (two modes) · Owner: Me + Claude Code · Status: done · Evidence: `style/blog-craft.md` drafted, 1259 words (limit 1800), approved by Hemang 2026-10-02.
- [x] M2.4 lint-rules.yaml + `blog lint` + calibration on exemplars · Owner: Me + Claude Code · Status: done · Evidence: hard/soft split approved by Hemang 2026-10-02. `style/lint-rules.yaml`, `src/blogpipe/lint.py`, `blog lint <file> [--mode] [--sources] [--report] [--no-length]`; `tests/test_lint.py` (45 tests: every rule's positive+negative sample, allow_contexts, code/frontmatter skipping, planted confidential term+pattern, exemplar overlap, source overlap quoted+marked exemption, bare/unresolved [ME], mode-length-is-soft, CLI exit code); full suite 74 passed, 93.03% coverage. Calibration: `style/exemplars/lint-calibration.md` (E3 only — E1/E2 have no corpus text). One real gap found: banned words inside a direct, attributed quote aren't exempted yet (recommendation in the calibration doc, not fixed — carried forward as a known gap). PR: https://github.com/hemang-ks/blog-pipeline/pull/4 (CI: pass)
- [ ] M2.5 Positions interview → positions.md · Owner: Me + Claude Code · Status: todo · Evidence:
- [ ] M2.6 Create confidential.yaml · Owner: Me · Status: todo · Evidence:
Success criteria:
- [ ] style/exemplars/corpus has E1–E3 (E3 marked partial or full) — **not met**: E1/E2 corpus missing (Medium 403, see M2.2); only E3 (ok, full-looking) present
- [x] blog-craft.md has an "Approved: <date>" line from Me
- [x] lint tests pass (hard, soft, allow-contexts, code-block skipping, confidential, exemplar overlap, source-corpus overlap, quoted-and-marked passage allowed)
- [x] Lint calibration report on exemplars reviewed by Me; hard/soft split approved
- [ ] positions.md has ≥6 positions and an "Approved: <date>" line
- [ ] `git check-ignore style/confidential.yaml` prints the path
- [x] `blog lint` flags a planted confidential term (test)

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
