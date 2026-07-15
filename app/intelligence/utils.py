"""Small dependency-free helpers used by the intelligence engines."""

import html
import re
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urlparse

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "was",
    "with",
    "you",
    "your",
    "our",
    "we",
    "can",
    "will",
    "more",
    "shop",
    "buy",
}


class SEOHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.headings: list[tuple[str, str]] = []
        self.images: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self._heading: str | None = None
        self._heading_text: list[str] = []
        self._link: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading, self._heading_text = tag, []
        elif tag == "img":
            self.images.append({"url": values.get("src", ""), "alt": values.get("alt", "")})
        elif tag == "a":
            self._link = {"url": values.get("href", ""), "anchor": ""}

    def handle_data(self, data: str) -> None:
        if self._heading:
            self._heading_text.append(data)
        if self._link is not None:
            self._link["anchor"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading:
            self.headings.append((tag, " ".join(self._heading_text).strip()))
            self._heading, self._heading_text = None, []
        elif tag == "a" and self._link is not None:
            self.links.append(self._link)
            self._link = None


def strip_html(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", value))).strip()


def words(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+(?:['-][a-z0-9]+)?", strip_html(value).lower())


def meaningful_terms(value: str, limit: int = 20) -> list[str]:
    counts = Counter(word for word in words(value) if len(word) > 2 and word not in STOP_WORDS)
    return [term for term, _ in counts.most_common(limit)]


def url_depth(url: str) -> int:
    return len([part for part in urlparse(url).path.split("/") if part])


def truncate_at_word(value: str, maximum: int) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    if len(value) <= maximum:
        return value
    shortened = value[: maximum + 1].rsplit(" ", 1)[0].rstrip(" ,;:-")
    return shortened or value[:maximum]


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left | right else 0.0
