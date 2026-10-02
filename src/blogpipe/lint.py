from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_RULES_PATH = Path("style/lint-rules.yaml")
DEFAULT_CONFIDENTIAL_PATH = Path("style/confidential.yaml")
DEFAULT_EXEMPLARS_DIR = Path("style/exemplars/corpus")
DEFAULT_POSITIONS_PATH = Path("style/positions.md")

MARKER_RE = re.compile(r"\[(S|W)(\d+)\]")
ME_MARKER_RE = re.compile(r"\[ME(:([A-Za-z0-9_]+))?\]")
POSITION_ID_RE = re.compile(r"^P(\d+)\s*[·\-:]", re.MULTILINE)
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z0-9']+")


@dataclass
class Finding:
    rule: str
    severity: str  # "hard" | "soft" | "info"
    line: int
    snippet: str
    hint: str


def load_rules(path: Path = DEFAULT_RULES_PATH) -> dict:
    return yaml.safe_load(path.read_text())


# --- preprocessing -------------------------------------------------------


def _strip_frontmatter(lines: list[str]) -> set[int]:
    """Return the 0-based line indices that belong to a leading YAML frontmatter block."""
    if not lines or lines[0].strip() != "---":
        return set()
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return set(range(i + 1))
    return set()


def _code_line_indices(lines: list[str]) -> set[int]:
    """Return 0-based line indices that are inside (or delimit) a fenced code block."""
    code_lines: set[int] = set()
    in_fence = False
    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            code_lines.add(i)
            in_fence = not in_fence
            continue
        if in_fence:
            code_lines.add(i)
    return code_lines


def _clean_prose_line(line: str) -> str:
    """Strip inline code spans and URLs from a line, for word/phrase/citation checks."""
    line = re.sub(r"`[^`]*`", " ", line)
    line = re.sub(r"https?://\S+", " ", line)
    line = re.sub(r"\]\(([^)]+)\)", "]", line)  # drop markdown link targets, keep link text
    return line


def _prose_lines(lines: list[str]) -> list[tuple[int, str]]:
    """(1-based line number, cleaned text) pairs for every non-frontmatter, non-code line."""
    skip = _strip_frontmatter(lines) | _code_line_indices(lines)
    return [(i + 1, _clean_prose_line(line)) for i, line in enumerate(lines) if i not in skip]


def _normalize_words(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


# --- word / phrase / pattern rules ---------------------------------------


def _context_allowed(
    text: str, match_start: int, match_end: int, allow_contexts: list[str]
) -> bool:
    window = text[max(0, match_start - 20) : match_end + 20].lower()
    return any(ctx.lower() in window for ctx in allow_contexts)


def _check_word_list(
    prose: list[tuple[int, str]],
    words: list[str],
    severity: str,
    allow_contexts: list[str],
) -> list[Finding]:
    findings = []
    for lineno, text in prose:
        for word in words:
            pattern = re.compile(r"(?<![\w-])" + re.escape(word) + r"(?![\w-])", re.IGNORECASE)
            for m in pattern.finditer(text):
                if allow_contexts and _context_allowed(text, m.start(), m.end(), allow_contexts):
                    continue
                findings.append(
                    Finding(
                        rule=f"banned-word:{word}",
                        severity=severity,
                        line=lineno,
                        snippet=text.strip()[:120],
                        hint=f'Avoid "{word}" — see writing-rules.md.',
                    )
                )
    return findings


def _check_phrase_list(
    prose: list[tuple[int, str]], phrases: list[str], severity: str
) -> list[Finding]:
    findings = []
    for lineno, text in prose:
        lowered = text.lower()
        for phrase in phrases:
            if phrase.lower() in lowered:
                findings.append(
                    Finding(
                        rule=f"banned-phrase:{phrase}",
                        severity=severity,
                        line=lineno,
                        snippet=text.strip()[:120],
                        hint=f'Avoid the phrase "{phrase}".',
                    )
                )
    return findings


def _check_pattern_list(
    prose: list[tuple[int, str]], patterns: list[str], severity: str
) -> list[Finding]:
    findings = []
    for lineno, text in prose:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                findings.append(
                    Finding(
                        rule=f"banned-pattern:{pattern}",
                        severity=severity,
                        line=lineno,
                        snippet=text.strip()[:120],
                        hint="Rewrite to avoid this construction.",
                    )
                )
    return findings


# --- structure rules (soft) ----------------------------------------------


def _check_structure(prose: list[tuple[int, str]], cfg: dict) -> list[Finding]:
    findings: list[Finding] = []
    paragraphs: list[list[tuple[int, str]]] = []
    current: list[tuple[int, str]] = []
    for lineno, text in prose:
        if text.strip() == "":
            if current:
                paragraphs.append(current)
                current = []
            continue
        if text.strip().startswith(("#", ">", "-", "*", "|")):
            if current:
                paragraphs.append(current)
                current = []
            continue
        current.append((lineno, text))
    if current:
        paragraphs.append(current)

    max_sentences = cfg.get("max_paragraph_sentences", 4)
    same_len_cfg = cfg.get("same_length_run", {})
    run_count = same_len_cfg.get("count", 3)
    tolerance = same_len_cfg.get("tolerance_words", 3)

    for para in paragraphs:
        joined = " ".join(text for _, text in para)
        sentences = [s.strip() for s in SENTENCE_SPLIT_RE.split(joined) if s.strip()]
        first_line = para[0][0]

        if len(sentences) > max_sentences:
            findings.append(
                Finding(
                    rule="structure:max_paragraph_sentences",
                    severity="soft",
                    line=first_line,
                    snippet=joined[:120],
                    hint=f"Paragraph has {len(sentences)} sentences (max {max_sentences}).",
                )
            )

        lengths = [len(_normalize_words(s)) for s in sentences]
        for i in range(len(lengths) - run_count + 1):
            window = lengths[i : i + run_count]
            if max(window) - min(window) <= tolerance:
                findings.append(
                    Finding(
                        rule="structure:same_length_run",
                        severity="soft",
                        line=first_line,
                        snippet=joined[:120],
                        hint=f"{run_count} consecutive sentences are nearly the same length — vary rhythm.",
                    )
                )
                break

        if cfg.get("rule_of_three") and re.search(r"\b\w+, \w+,? and \w+\b", joined):
            findings.append(
                Finding(
                    rule="structure:rule_of_three",
                    severity="soft",
                    line=first_line,
                    snippet=joined[:120],
                    hint='Possible "X, Y, and Z" triplet — make sure three is really the right number.',
                )
            )

    body_lines = [text for _, text in prose if text.strip() != ""]
    if body_lines:
        bullet_lines = sum(1 for text in body_lines if text.strip().startswith(("-", "*")))
        ratio = bullet_lines / len(body_lines)
        max_ratio = cfg.get("bullet_line_ratio_max", 0.25)
        if ratio > max_ratio:
            findings.append(
                Finding(
                    rule="structure:bullet_line_ratio",
                    severity="soft",
                    line=prose[0][0],
                    snippet="",
                    hint=f"{ratio:.0%} of lines are bullets (max {max_ratio:.0%}). Write more prose.",
                )
            )

    total_words = sum(len(_normalize_words(text)) for _, text in prose)
    bold_count = sum(len(re.findall(r"\*\*[^*]+\*\*", text)) for _, text in prose)
    max_bold = cfg.get("bold_per_300_words_max", 2)
    if total_words > 0:
        allowed = max_bold * max(1, total_words / 300)
        if bold_count > allowed:
            findings.append(
                Finding(
                    rule="structure:bold_per_300_words",
                    severity="soft",
                    line=prose[0][0],
                    snippet="",
                    hint=f"{bold_count} bolded spans for {total_words} words — emphasis is losing its force.",
                )
            )

    return findings


# --- mode length (soft) ---------------------------------------------------


def _check_mode_length(
    prose: list[tuple[int, str]], mode: str | None, modes_cfg: dict
) -> list[Finding]:
    if not mode or mode not in modes_cfg:
        return []
    total_words = sum(len(_normalize_words(text)) for _, text in prose)
    bounds = modes_cfg[mode]
    low, high = bounds.get("min_words", 0), bounds.get("max_words", 10**9)
    if total_words < low or total_words > high:
        return [
            Finding(
                rule="modes:word_range",
                severity="soft",
                line=1,
                snippet="",
                hint=f"{total_words} words is outside the {mode} range ({low}-{high}).",
            )
        ]
    return []


# --- citations -------------------------------------------------------------


QUOTE_RE = re.compile(r"[\"“]([^\"“”]{0,400})[\"”]")
NUMERIC_RE = re.compile(r"(?<!\[)(\$\d|\d+%|\b\d{2,})")


def _check_citations(
    prose: list[tuple[int, str]],
    sources_ids: set[str] | None,
    positions_ids: set[str],
) -> list[Finding]:
    findings: list[Finding] = []

    for lineno, text in prose:
        for m in QUOTE_RE.finditer(text):
            quote = m.group(1)
            if len(_normalize_words(quote)) >= 6:
                tail = text[m.end() : m.end() + 40]
                if not MARKER_RE.search(text) and not MARKER_RE.search(tail):
                    findings.append(
                        Finding(
                            rule="citations:unmarked_quote",
                            severity="hard",
                            line=lineno,
                            snippet=text.strip()[:120],
                            hint="Direct quote of 6+ words has no [S#]/[W#] marker.",
                        )
                    )

        for sentence in SENTENCE_SPLIT_RE.split(text):
            if NUMERIC_RE.search(sentence) and not MARKER_RE.search(sentence):
                findings.append(
                    Finding(
                        rule="citations:unmarked_number",
                        severity="soft",
                        line=lineno,
                        snippet=sentence.strip()[:120],
                        hint="Number/percentage/dollar amount with no [S#]/[W#] marker.",
                    )
                )

        if sources_ids is not None:
            for m in MARKER_RE.finditer(text):
                marker_id = f"{m.group(1)}{m.group(2)}"
                if marker_id not in sources_ids:
                    findings.append(
                        Finding(
                            rule="citations:unresolved_marker",
                            severity="hard",
                            line=lineno,
                            snippet=text.strip()[:120],
                            hint=f"[{marker_id}] does not resolve in sources.md.",
                        )
                    )

        for m in re.finditer(r"\[ME\]", text):
            findings.append(
                Finding(
                    rule="citations:bare_me",
                    severity="hard",
                    line=lineno,
                    snippet=text.strip()[:120],
                    hint="Bare [ME] — must be [ME:P#] or [ME:intake].",
                )
            )

        for m in re.finditer(r"\[ME:P(\d+)\]", text):
            pid = f"P{m.group(1)}"
            if pid not in positions_ids:
                findings.append(
                    Finding(
                        rule="citations:unresolved_position",
                        severity="hard",
                        line=lineno,
                        snippet=text.strip()[:120],
                        hint=f"[ME:{pid}] — {pid} is not defined in style/positions.md.",
                    )
                )

    return findings


def _load_position_ids(positions_path: Path) -> set[str]:
    if not positions_path.exists():
        return set()
    text = positions_path.read_text()
    return {f"P{m.group(1)}" for m in POSITION_ID_RE.finditer(text)}


def _load_source_ids(sources_path: Path | None) -> set[str] | None:
    if sources_path is None:
        return None
    if not sources_path.exists():
        return set()
    ids = set()
    for line in sources_path.read_text().splitlines():
        m = re.match(r"\|\s*((?:S|W)\d+)\s*\|", line)
        if m:
            ids.add(m.group(1))
    return ids


# --- platform rules --------------------------------------------------------


def _check_platform(lines: list[str]) -> list[Finding]:
    findings: list[Finding] = []
    frontmatter = _strip_frontmatter(lines)

    seen_first_content_line = False
    in_fence = False
    fence_lang = ""
    for i, line in enumerate(lines):
        if i in frontmatter:
            continue
        stripped = line.strip()

        if stripped.startswith("```"):
            if not in_fence:
                in_fence = True
                fence_lang = stripped[3:].strip().lower()
                if fence_lang == "mermaid":
                    findings.append(
                        Finding(
                            rule="platform:mermaid",
                            severity="hard",
                            line=i + 1,
                            snippet=stripped,
                            hint="Mermaid blocks don't render on Substack/Medium.",
                        )
                    )
            else:
                in_fence = False
            continue

        if in_fence:
            continue

        if re.search(r"\[\^[^\]]+\]", stripped):
            findings.append(
                Finding(
                    rule="platform:footnote",
                    severity="hard",
                    line=i + 1,
                    snippet=stripped[:120],
                    hint="Footnote syntax doesn't render — use an [S#]/[W#] marker instead.",
                )
            )

        if stripped.startswith("# ") and seen_first_content_line:
            findings.append(
                Finding(
                    rule="platform:h1_after_first_line",
                    severity="hard",
                    line=i + 1,
                    snippet=stripped[:120],
                    hint="Only the first line of a post may be an H1.",
                )
            )

        if stripped.startswith("|") and "---" not in stripped and "|" in stripped[1:]:
            findings.append(
                Finding(
                    rule="platform:markdown_table",
                    severity="soft",
                    line=i + 1,
                    snippet=stripped[:120],
                    hint="Markdown tables don't render — use a short list or flag for an image.",
                )
            )

        if stripped != "":
            seen_first_content_line = True

    return findings


# --- overlap rules -----------------------------------------------------------


def _ngrams(words: list[str], n: int) -> set[tuple[str, ...]]:
    return {tuple(words[i : i + n]) for i in range(len(words) - n + 1)}


def _corpus_ngrams(corpus_dir: Path, n: int) -> set[tuple[str, ...]]:
    grams: set[tuple[str, ...]] = set()
    if not corpus_dir.exists():
        return grams
    for f in corpus_dir.glob("*.md"):
        words = _normalize_words(f.read_text())
        grams |= _ngrams(words, n)
    return grams


def _check_overlap(
    prose: list[tuple[int, str]],
    corpus_dir: Path,
    n: int,
    rule_name: str,
    exempt_quoted_marked: bool,
) -> list[Finding]:
    reference_grams = _corpus_ngrams(corpus_dir, n)
    if not reference_grams:
        return []

    findings: list[Finding] = []
    seen_lines: set[int] = set()
    for lineno, text in prose:
        if lineno in seen_lines:
            continue
        words = _normalize_words(text)
        if len(words) < n:
            continue
        for i in range(len(words) - n + 1):
            gram = tuple(words[i : i + n])
            if gram not in reference_grams:
                continue
            if exempt_quoted_marked:
                is_quoted = bool(QUOTE_RE.search(text)) or text.strip().startswith(">")
                is_marked = bool(MARKER_RE.search(text))
                if is_quoted and is_marked:
                    continue
            findings.append(
                Finding(
                    rule=rule_name,
                    severity="hard",
                    line=lineno,
                    snippet=text.strip()[:120],
                    hint="12+ word sequence matches existing corpus text — quote and cite it, or rewrite.",
                )
            )
            seen_lines.add(lineno)
            break
    return findings


# --- confidential ------------------------------------------------------------


def _check_confidential(lines: list[str], confidential_path: Path) -> list[Finding]:
    if not confidential_path.exists():
        return [
            Finding(
                rule="confidential:missing_file",
                severity="info",
                line=1,
                snippet="",
                hint=f"{confidential_path} not found — confidentiality check skipped.",
            )
        ]

    data = yaml.safe_load(confidential_path.read_text()) or {}
    terms = (
        list(data.get("names", [])) + list(data.get("codenames", [])) + list(data.get("people", []))
    )
    patterns = list(data.get("patterns", []))

    findings: list[Finding] = []
    full_text = "\n".join(lines)
    for term in terms:
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        for m in pattern.finditer(full_text):
            lineno = full_text.count("\n", 0, m.start()) + 1
            findings.append(
                Finding(
                    rule="confidential:term",
                    severity="hard",
                    line=lineno,
                    snippet=f"matched: {term}",
                    hint=f'Remove or anonymize "{term}".',
                )
            )
    for pattern in patterns:
        for m in re.finditer(pattern, full_text, re.IGNORECASE):
            lineno = full_text.count("\n", 0, m.start()) + 1
            findings.append(
                Finding(
                    rule="confidential:pattern",
                    severity="hard",
                    line=lineno,
                    snippet=f"matched: {m.group(0)}",
                    hint=f'Remove or anonymize the match for pattern "{pattern}".',
                )
            )
    return findings


# --- orchestration -----------------------------------------------------------


def lint_text(
    text: str,
    mode: str | None = None,
    sources_path: Path | None = None,
    rules: dict | None = None,
    exemplars_dir: Path = DEFAULT_EXEMPLARS_DIR,
    positions_path: Path = DEFAULT_POSITIONS_PATH,
    confidential_path: Path = DEFAULT_CONFIDENTIAL_PATH,
    check_length: bool = True,
) -> list[Finding]:
    rules = rules if rules is not None else load_rules()
    lines = text.splitlines()
    prose = _prose_lines(lines)

    findings: list[Finding] = []
    findings += _check_word_list(prose, rules["hard"]["words"], "hard", [])
    findings += _check_phrase_list(prose, rules["hard"]["phrases"], "hard")
    findings += _check_pattern_list(prose, rules["hard"].get("patterns", []), "hard")
    findings += _check_word_list(
        prose, rules["soft"]["words"], "soft", rules.get("allow_contexts", [])
    )
    findings += _check_phrase_list(prose, rules["soft"].get("phrases", []), "soft")
    findings += _check_structure(prose, rules.get("structure", {}))
    if check_length:
        findings += _check_mode_length(prose, mode, rules.get("modes", {}))

    sources_ids = _load_source_ids(sources_path)
    positions_ids = _load_position_ids(positions_path)
    findings += _check_citations(prose, sources_ids, positions_ids)
    findings += _check_platform(lines)

    findings += _check_overlap(
        prose,
        exemplars_dir,
        rules["exemplar_overlap"]["min_shared_words"],
        "exemplar_overlap",
        exempt_quoted_marked=False,
    )
    if sources_path is not None:
        source_corpus_dir = sources_path.parent / "corpus"
        findings += _check_overlap(
            prose,
            source_corpus_dir,
            rules["source_overlap"]["min_shared_words"],
            "source_overlap",
            exempt_quoted_marked=True,
        )

    findings += _check_confidential(lines, confidential_path)

    return findings


def lint_file(
    path: Path,
    mode: str | None = None,
    sources_path: Path | None = None,
    rules_path: Path = DEFAULT_RULES_PATH,
    exemplars_dir: Path = DEFAULT_EXEMPLARS_DIR,
    positions_path: Path = DEFAULT_POSITIONS_PATH,
    confidential_path: Path = DEFAULT_CONFIDENTIAL_PATH,
    check_length: bool = True,
) -> list[Finding]:
    rules = load_rules(rules_path)
    return lint_text(
        path.read_text(),
        mode=mode,
        sources_path=sources_path,
        rules=rules,
        exemplars_dir=exemplars_dir,
        positions_path=positions_path,
        confidential_path=confidential_path,
        check_length=check_length,
    )


def format_report(path: Path, findings: list[Finding]) -> str:
    hard = [f for f in findings if f.severity == "hard"]
    soft = [f for f in findings if f.severity == "soft"]
    info = [f for f in findings if f.severity == "info"]

    lines = [f"# Lint report — {path}", ""]
    if any(f.rule.startswith("confidential:") for f in hard):
        lines.append(
            "**Contains confidential matches — don't paste this report outside the repo.**"
        )
        lines.append("")
    lines.append(f"hard={len(hard)} soft={len(soft)} info={len(info)}")
    lines.append("")

    for label, group in (("Hard", hard), ("Soft", soft), ("Info", info)):
        if not group:
            continue
        lines.append(f"## {label}")
        for f in sorted(group, key=lambda x: x.line):
            lines.append(f"- L{f.line} [{f.rule}] {f.hint}")
            if f.snippet:
                lines.append(f"  > {f.snippet}")
        lines.append("")

    return "\n".join(lines)
