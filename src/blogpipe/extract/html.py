from __future__ import annotations

import httpx
import trafilatura

from blogpipe.extract import ExtractResult

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

PAYWALL_SIGNALS = (
    "this post is for paid subscribers",
    "member-only story",
    "subscribe to continue",
)

MIN_WORDS = 300


def fetch_html(url: str) -> str:
    response = httpx.get(
        url,
        timeout=20.0,
        follow_redirects=True,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    return response.text


def extract_from_html(html: str, url: str) -> ExtractResult:
    markdown = trafilatura.extract(html, url=url, output_format="markdown")
    if not markdown:
        return ExtractResult(status="failed", reason="no extractable content")

    doc = trafilatura.bare_extraction(html, url=url, with_metadata=True)
    meta = doc.as_dict() if doc else {}

    words = len(markdown.split())
    lowered = markdown.lower()
    paywalled = any(signal in lowered for signal in PAYWALL_SIGNALS)

    if paywalled or words < MIN_WORDS:
        reason = "paywall signal detected" if paywalled else f"only {words} words (<{MIN_WORDS})"
        status = "partial"
    else:
        reason = None
        status = "ok"

    return ExtractResult(
        status=status,
        reason=reason,
        title=meta.get("title"),
        author=meta.get("author"),
        published=meta.get("date"),
        text=markdown,
        words=words,
    )


def extract_url(url: str) -> ExtractResult:
    try:
        html = fetch_html(url)
    except httpx.HTTPError as exc:
        return ExtractResult(status="failed", reason=str(exc))
    return extract_from_html(html, url)
