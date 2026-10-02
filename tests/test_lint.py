from pathlib import Path

import pytest
from typer.testing import CliRunner

from blogpipe.cli import app
from blogpipe.lint import DEFAULT_RULES_PATH, format_report, lint_text, load_rules

RULES = load_rules(DEFAULT_RULES_PATH)
NOWHERE = Path("/nonexistent-exemplars-dir")
runner = CliRunner()


def _severities(findings, rule_prefix):
    return [f.severity for f in findings if f.rule.startswith(rule_prefix)]


def lint(text, **kwargs):
    kwargs.setdefault("rules", RULES)
    kwargs.setdefault("exemplars_dir", NOWHERE)
    kwargs.setdefault("confidential_path", Path("/nonexistent-confidential.yaml"))
    return lint_text(text, **kwargs)


# --- hard word/phrase rules -------------------------------------------------


def test_hard_word_fires_on_positive_sample():
    findings = lint("We need to delve into this topic.")
    assert _severities(findings, "banned-word:delve")


def test_hard_word_quiet_on_negative_sample():
    findings = lint("We need to look closely at this topic.")
    assert not _severities(findings, "banned-word:delve")


def test_hard_phrase_fires():
    findings = lint("In conclusion, this approach works.")
    assert _severities(findings, "banned-phrase:in conclusion")


def test_hard_phrase_quiet_on_negative_sample():
    findings = lint("This approach works because the cache hit rate improved.")
    assert not any(f.rule.startswith("banned-phrase:") for f in findings)


def test_hard_pattern_not_only_but_also():
    findings = lint("It is not only fast but also cheap to run.")
    assert any(f.rule.startswith("banned-pattern:") and f.severity == "hard" for f in findings)


# --- soft word rules + allow_contexts ---------------------------------------


def test_soft_word_fires_on_positive_sample():
    findings = lint("The key insight here is caching.")
    hits = [f for f in findings if f.rule == "banned-word:key"]
    assert hits and hits[0].severity == "soft"


def test_allow_context_suppresses_soft_word():
    findings = lint("Rotate your API key regularly.")
    assert not any(f.rule == "banned-word:key" for f in findings)


def test_allow_context_robust_to():
    findings = lint("This design is robust to node failures.")
    assert not any(f.rule == "banned-word:robust" for f in findings)


def test_soft_word_without_allow_context_still_fires():
    findings = lint("This is a robust solution to the problem.")
    assert any(f.rule == "banned-word:robust" for f in findings)


# --- code block / inline code / frontmatter skipping -------------------------


def test_code_block_is_skipped():
    text = "Intro text.\n\n```python\ndelve_into_this = True  # delve\n```\n\nMore text.\n"
    findings = lint(text)
    assert not any(f.rule == "banned-word:delve" for f in findings)


def test_inline_code_is_skipped():
    text = "Call `delve_into()` to start."
    findings = lint(text)
    assert not any(f.rule == "banned-word:delve" for f in findings)


def test_frontmatter_is_skipped():
    text = "---\nnote: delve into this\n---\n\nReal content here.\n"
    findings = lint(text)
    assert not any(f.rule == "banned-word:delve" for f in findings)


# --- structure (soft) ---------------------------------------------------------


def test_max_paragraph_sentences():
    para = "One. Two. Three. Four. Five."
    findings = lint(para)
    assert any(f.rule == "structure:max_paragraph_sentences" for f in findings)


def test_same_length_run_flagged():
    para = "The cat sat there. The dog ran fast. The bird flew high."
    findings = lint(para)
    assert any(f.rule == "structure:same_length_run" for f in findings)


# --- mode length (soft, never hard) -------------------------------------------


def test_mode_length_warning_is_soft_not_hard():
    short_text = "Short post. " * 10
    findings = lint(short_text, mode="technical")
    length_findings = [f for f in findings if f.rule == "modes:word_range"]
    assert length_findings
    assert all(f.severity == "soft" for f in length_findings)
    assert all(f.severity != "hard" for f in findings if f.rule == "modes:word_range")


def test_no_length_flag_skips_mode_check():
    short_text = "Short post. " * 10
    findings = lint(short_text, mode="technical", check_length=False)
    assert not any(f.rule == "modes:word_range" for f in findings)


def test_mode_length_in_range_is_quiet():
    words = ("word " * 1500).strip()
    findings = lint(words, mode="technical")
    assert not any(f.rule == "modes:word_range" for f in findings)


# --- citations -----------------------------------------------------------------


def test_unmarked_long_quote_is_hard():
    text = '"this architecture handles ten thousand requests per second reliably" she said.'
    findings = lint(text)
    assert any(f.rule == "citations:unmarked_quote" and f.severity == "hard" for f in findings)


def test_marked_long_quote_is_allowed():
    text = '"this architecture handles ten thousand requests per second reliably" [S1]'
    findings = lint(text)
    assert not any(f.rule == "citations:unmarked_quote" for f in findings)


def test_unmarked_number_is_soft():
    findings = lint("Revenue grew 40% last quarter.")
    assert any(f.rule == "citations:unmarked_number" and f.severity == "soft" for f in findings)


def test_unresolved_marker_is_hard_when_sources_given(tmp_path):
    sources_path = tmp_path / "sources.md"
    sources_path.write_text(
        "| ID | type | title | origin | fetched | words | status | note |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| S1 | html | x | https://example.com | 2026-10-02 | 10 | ok |  |\n"
    )
    findings = lint("A claim backed by [S2].", sources_path=sources_path)
    assert any(f.rule == "citations:unresolved_marker" for f in findings)


def test_resolved_marker_is_quiet_when_sources_given(tmp_path):
    sources_path = tmp_path / "sources.md"
    sources_path.write_text(
        "| ID | type | title | origin | fetched | words | status | note |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| S1 | html | x | https://example.com | 2026-10-02 | 10 | ok |  |\n"
    )
    findings = lint("A claim backed by [S1].", sources_path=sources_path)
    assert not any(f.rule == "citations:unresolved_marker" for f in findings)


def test_bare_me_marker_is_hard():
    findings = lint("This happened to me. [ME]")
    assert any(f.rule == "citations:bare_me" and f.severity == "hard" for f in findings)


def test_me_intake_marker_is_not_bare():
    findings = lint("This happened to me. [ME:intake]")
    assert not any(f.rule == "citations:bare_me" for f in findings)


def test_me_position_not_in_positions_md_is_hard(tmp_path):
    positions_path = tmp_path / "positions.md"
    positions_path.write_text("P1 · Some stance\n")
    findings = lint("As I've argued. [ME:P9]", positions_path=positions_path)
    assert any(f.rule == "citations:unresolved_position" for f in findings)


def test_me_position_defined_in_positions_md_is_quiet(tmp_path):
    positions_path = tmp_path / "positions.md"
    positions_path.write_text("P1 · Some stance\n")
    findings = lint("As I've argued. [ME:P1]", positions_path=positions_path)
    assert not any(f.rule == "citations:unresolved_position" for f in findings)


# --- platform -------------------------------------------------------------------


def test_mermaid_block_is_hard():
    text = "Intro.\n\n```mermaid\ngraph TD; A-->B;\n```\n"
    findings = lint(text)
    assert any(f.rule == "platform:mermaid" and f.severity == "hard" for f in findings)


def test_footnote_syntax_is_hard():
    findings = lint("A claim with a footnote[^1] reference.")
    assert any(f.rule == "platform:footnote" and f.severity == "hard" for f in findings)


def test_h1_after_first_line_is_hard():
    text = "# Title\n\nBody text.\n\n# Another H1\n"
    findings = lint(text)
    assert any(f.rule == "platform:h1_after_first_line" for f in findings)


def test_first_line_h1_is_allowed():
    text = "# Title\n\nBody text here.\n"
    findings = lint(text)
    assert not any(f.rule == "platform:h1_after_first_line" for f in findings)


def test_markdown_table_is_soft():
    text = "| A | B |\n| 1 | 2 |\n"
    findings = lint(text)
    hits = [f for f in findings if f.rule == "platform:markdown_table"]
    assert hits
    assert all(f.severity == "soft" for f in hits)


# --- exemplar overlap -------------------------------------------------------------


def test_exemplar_overlap_hard(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "E1-x.md").write_text(
        "the scheduler had no concept of priority beyond arrival order in the queue today"
    )
    text = "The scheduler had no concept of priority beyond arrival order in the queue today."
    findings = lint(text, exemplars_dir=corpus_dir)
    assert any(f.rule == "exemplar_overlap" and f.severity == "hard" for f in findings)


def test_no_exemplar_overlap_when_text_is_original(tmp_path):
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "E1-x.md").write_text(
        "the scheduler had no concept of priority beyond arrival order in the queue today"
    )
    findings = lint(
        "A completely unrelated sentence about GPU memory fragmentation.", exemplars_dir=corpus_dir
    )
    assert not any(f.rule == "exemplar_overlap" for f in findings)


# --- source/corpus overlap --------------------------------------------------------


def test_source_overlap_unquoted_copy_is_hard(tmp_path):
    sources_path = tmp_path / "sources.md"
    sources_path.write_text(
        "| ID | type | title | origin | fetched | words | status | note |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| S1 | html | x | https://example.com | 2026-10-02 | 10 | ok |  |\n"
    )
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "S1-x.md").write_text(
        "the scheduler had no concept of priority beyond arrival order in this cluster setup today"
    )
    text = (
        "The scheduler had no concept of priority beyond arrival order in this cluster setup today."
    )
    findings = lint(text, sources_path=sources_path)
    assert any(f.rule == "source_overlap" and f.severity == "hard" for f in findings)


def test_source_overlap_quoted_and_marked_is_allowed(tmp_path):
    sources_path = tmp_path / "sources.md"
    sources_path.write_text(
        "| ID | type | title | origin | fetched | words | status | note |\n"
        "|---|---|---|---|---|---|---|---|\n"
        "| S1 | html | x | https://example.com | 2026-10-02 | 10 | ok |  |\n"
    )
    corpus_dir = tmp_path / "corpus"
    corpus_dir.mkdir()
    (corpus_dir / "S1-x.md").write_text(
        "the scheduler had no concept of priority beyond arrival order in this cluster setup today"
    )
    text = (
        '"The scheduler had no concept of priority beyond arrival order in this '
        'cluster setup today." [S1]'
    )
    findings = lint(text, sources_path=sources_path)
    assert not any(f.rule == "source_overlap" for f in findings)


def test_source_overlap_only_runs_when_sources_given(tmp_path):
    text = "Some text that would overlap if sources were checked."
    findings = lint(text)
    assert not any(f.rule == "source_overlap" for f in findings)


# --- confidential ------------------------------------------------------------------


def test_planted_confidential_term_is_hard(tmp_path):
    conf_path = tmp_path / "confidential.yaml"
    conf_path.write_text('names:\n  - "Example Bank"\n')
    findings = lint("We worked with Example Bank on this project.", confidential_path=conf_path)
    assert any(f.rule == "confidential:term" and f.severity == "hard" for f in findings)


def test_confidential_pattern_is_hard(tmp_path):
    conf_path = tmp_path / "confidential.yaml"
    conf_path.write_text('patterns:\n  - "\\\\bex-prod-\\\\d+\\\\b"\n')
    findings = lint("The host ex-prod-42 failed overnight.", confidential_path=conf_path)
    assert any(f.rule == "confidential:pattern" and f.severity == "hard" for f in findings)


def test_missing_confidential_file_is_info_not_failure(tmp_path):
    conf_path = tmp_path / "does-not-exist.yaml"
    findings = lint("Nothing sensitive here.", confidential_path=conf_path)
    assert any(f.rule == "confidential:missing_file" and f.severity == "info" for f in findings)
    assert not any(f.severity == "hard" for f in findings)


def test_confidential_report_header_warns_not_to_paste_outside(tmp_path):
    conf_path = tmp_path / "confidential.yaml"
    conf_path.write_text('names:\n  - "Example Bank"\n')
    findings = lint("We worked with Example Bank on this project.", confidential_path=conf_path)
    report = format_report(Path("draft.md"), findings)
    assert "don't paste this report outside the repo" in report


# --- exit-code behavior (via the CLI layer) ----------------------------------------


def test_exit_code_reflects_hard_count():
    hard_findings = lint("We need to delve into this topic.")
    soft_only_findings = lint("The key insight here is caching.")
    assert any(f.severity == "hard" for f in hard_findings)
    assert not any(f.severity == "hard" for f in soft_only_findings)


@pytest.mark.parametrize("mode", ["technical", "strategy"])
def test_rules_file_has_both_modes_configured(mode):
    assert mode in RULES["modes"]
    assert "min_words" in RULES["modes"][mode]
    assert "max_words" in RULES["modes"][mode]


# --- CLI exit code ------------------------------------------------------------------


def test_cli_lint_exits_nonzero_on_hard_finding(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "style").mkdir()
    (DEFAULT_RULES_PATH).parent.mkdir(exist_ok=True)
    import shutil

    shutil.copy(
        Path(__file__).parent.parent / "style" / "lint-rules.yaml",
        tmp_path / "style" / "lint-rules.yaml",
    )
    draft = tmp_path / "draft.md"
    draft.write_text("We need to delve into this topic.\n")

    result = runner.invoke(app, ["lint", str(draft)])
    assert result.exit_code == 1
    assert "delve" in result.output


def test_cli_lint_exits_zero_when_clean(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "style").mkdir()
    import shutil

    shutil.copy(
        Path(__file__).parent.parent / "style" / "lint-rules.yaml",
        tmp_path / "style" / "lint-rules.yaml",
    )
    draft = tmp_path / "draft.md"
    draft.write_text("This sentence is clean and specific.\n")

    result = runner.invoke(app, ["lint", str(draft)])
    assert result.exit_code == 0
