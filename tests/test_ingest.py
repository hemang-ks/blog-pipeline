from pathlib import Path

import httpx
import pymupdf
import pytest

from blogpipe.extract.html import extract_from_html, extract_url
from blogpipe.extract.markdown import extract_markdown
from blogpipe.extract.pdf import extract_pdf
from blogpipe.ingest import ingest
from blogpipe.registry import SourceEntry, load_entries, save_entries

FIXTURES = Path(__file__).parent / "fixtures"


def _make_pdf(path: Path, pages: list[str]) -> None:
    doc = pymupdf.open()
    rect = pymupdf.Rect(50, 50, 550, 750)
    for text in pages:
        page = doc.new_page()
        page.insert_textbox(rect, text, fontsize=11, fontname="helv")
    doc.save(str(path))
    doc.close()


# --- extractors -------------------------------------------------------


def test_html_extraction_from_local_fixture():
    html = (FIXTURES / "article.html").read_text()
    result = extract_from_html(html, "https://example.com/article")
    assert result.status == "ok"
    assert result.words >= 300
    assert result.title == "How Shared Inference Clusters Actually Fail"
    assert result.author == "Jane Doe"


def test_paywall_detection_marks_partial():
    html = (FIXTURES / "paywall.html").read_text()
    result = extract_from_html(html, "https://example.com/paywall")
    assert result.status == "partial"
    assert "paywall" in result.reason.lower()


def test_extract_url_offline_via_monkeypatched_httpx(monkeypatch):
    html = (FIXTURES / "article.html").read_text()

    def fake_get(url, timeout=None, follow_redirects=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, text=html, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)
    result = extract_url("https://example.com/article")
    assert result.status == "ok"
    assert result.words >= 300


def test_extract_url_failure_is_recorded_not_raised(monkeypatch):
    def fake_get(url, timeout=None, follow_redirects=None, headers=None):
        raise httpx.ConnectError("boom")

    monkeypatch.setattr(httpx, "get", fake_get)
    result = extract_url("https://example.com/unreachable")
    assert result.status == "failed"
    assert result.reason


def test_pdf_extraction(tmp_path):
    pdf_path = tmp_path / "doc.pdf"
    _make_pdf(
        pdf_path,
        [
            "This is page one of a test PDF document used for extraction testing. " * 5,
            "This is page two of the same test PDF document. " * 5,
        ],
    )
    result = extract_pdf(pdf_path)
    assert result.status == "ok"
    assert result.pages == 2
    assert result.words > 0


def test_markdown_extraction_keeps_frontmatter():
    result = extract_markdown(FIXTURES / "notes.md")
    assert result.status == "ok"
    assert result.title == "My observations on cluster scheduling"
    assert result.author == "Hemang Shishir"
    assert result.published == "2026-01-20"


# --- registry ----------------------------------------------------------


def test_registry_round_trips_title_with_literal_pipe(tmp_path):
    sources_path = tmp_path / "sources.md"
    entries = [
        SourceEntry(
            id="S1",
            type="html",
            title="Page Title | Site Name",
            origin="https://example.com/a",
            fetched="2026-10-02",
            words=100,
            status="ok",
        )
    ]
    save_entries(sources_path, entries)

    loaded = load_entries(sources_path)
    assert len(loaded) == 1
    assert loaded[0].title == "Page Title | Site Name"
    assert loaded[0].origin == "https://example.com/a"


# --- ingest orchestration ----------------------------------------------


@pytest.fixture
def topic(tmp_path, monkeypatch):
    html = (FIXTURES / "article.html").read_text()

    def fake_get(url, timeout=None, follow_redirects=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, text=html, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)

    tdir = tmp_path / "g1"
    (tdir / "inputs" / "files").mkdir(parents=True)
    (tdir / "inputs" / "urls.txt").write_text(
        "https://example.com/a | primary source\nhttps://example.com/b\n"
    )
    import shutil

    shutil.copy(FIXTURES / "notes.md", tdir / "inputs" / "files" / "notes.md")
    return tdir


def test_ingest_creates_corpus_and_sources(topic):
    summary = ingest(topic)
    assert summary.ok == 3
    assert summary.failed == 0

    entries = load_entries(topic / "sources.md")
    ids = {e.id for e in entries}
    assert ids == {"S1", "S2", "S3"}

    corpus_files = list((topic / "corpus").glob("*.md"))
    assert len(corpus_files) == 3


def test_ingest_ids_stable_across_reruns(topic):
    ingest(topic)
    entries_before = {e.origin: e.id for e in load_entries(topic / "sources.md")}

    summary2 = ingest(topic)
    assert summary2.skipped == 3

    entries_after = {e.origin: e.id for e in load_entries(topic / "sources.md")}
    assert entries_before == entries_after


def test_ingest_stays_deduped_when_title_has_literal_pipe(tmp_path, monkeypatch):
    html = (
        """<html><head><title>Page Title | Site Name</title></head>
    <body><article><p>"""
        + ("word " * 320)
        + """</p></article></body></html>"""
    )

    def fake_get(url, timeout=None, follow_redirects=None, headers=None):
        request = httpx.Request("GET", url)
        return httpx.Response(200, text=html, request=request)

    monkeypatch.setattr(httpx, "get", fake_get)

    tdir = tmp_path / "g1"
    (tdir / "inputs" / "files").mkdir(parents=True)
    (tdir / "inputs" / "urls.txt").write_text("https://example.com/piped\n")

    ingest(tdir)
    entries_before = {e.origin: e.id for e in load_entries(tdir / "sources.md")}

    summary2 = ingest(tdir)
    assert summary2.skipped == 1

    entries_after = {e.origin: e.id for e in load_entries(tdir / "sources.md")}
    assert entries_before == entries_after


def test_ingest_new_input_gets_next_free_id(topic):
    ingest(topic)
    with (topic / "inputs" / "urls.txt").open("a") as f:
        f.write("https://example.com/c | a new one\n")

    ingest(topic)
    entries = load_entries(topic / "sources.md")
    new_entry = next(e for e in entries if e.origin == "https://example.com/c")
    assert new_entry.id == "S4"


def test_ingest_failure_recorded_without_aborting(topic, monkeypatch):
    def flaky_get(url, timeout=None, follow_redirects=None, headers=None):
        if url == "https://example.com/a":
            raise httpx.ConnectError("boom")
        request = httpx.Request("GET", url)
        return httpx.Response(200, text=(FIXTURES / "article.html").read_text(), request=request)

    monkeypatch.setattr(httpx, "get", flaky_get)
    summary = ingest(topic)

    assert summary.failed == 1
    assert summary.ok == 2

    entries = load_entries(topic / "sources.md")
    failed_entry = next(e for e in entries if e.origin == "https://example.com/a")
    assert failed_entry.status == "failed"
    assert failed_entry.note
    assert "boom" in failed_entry.note
    assert "primary source" in failed_entry.note


def test_ingest_w_sources_numbered_separately(topic):
    (topic / "inputs" / "urls-web.txt").write_text(
        "https://example.com/w1\nhttps://example.com/w2\n"
    )
    ingest(topic)
    entries = load_entries(topic / "sources.md")
    w_ids = sorted(e.id for e in entries if e.id.startswith("W"))
    assert w_ids == ["W1", "W2"]
    s_ids = sorted(e.id for e in entries if e.id.startswith("S"))
    assert s_ids == ["S1", "S2", "S3"]


def test_ingest_advances_stage_from_intake(topic):
    import yaml

    from blogpipe.post import Post

    post_yaml = topic / "post.yaml"
    post_yaml.write_text(yaml.safe_dump(Post(slug="g1").to_dict(), sort_keys=False))

    ingest(topic)
    data = yaml.safe_load(post_yaml.read_text())
    assert data["stage"] == "ingested"
