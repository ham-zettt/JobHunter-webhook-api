from __future__ import annotations

import hashlib
import re

from selectolax.lexbor import LexborHTMLParser as HTMLParser

MAX_DESCRIPTION_CHARS = 100_000

_WS_RE = re.compile(r"[ \t\u00a0]+")
_MULTI_NL_RE = re.compile(r"\n{3,}")
_ENTITY_MAP = {"&amp;": "&", "&lt;": "<", "&gt;": ">", "&quot;": '"', "&#39;": "'", "&nbsp;": " "}


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    out = text
    for ent, char in _ENTITY_MAP.items():
        out = out.replace(ent, char)
    out = _WS_RE.sub(" ", out)
    out = "\n".join(line.strip() for line in out.splitlines())
    out = _MULTI_NL_RE.sub("\n\n", out)
    return out.strip()


def normalize_for_match(text: str | None) -> str:
    if not text:
        return ""
    out = text.lower()
    out = out.replace("-", " ").replace("_", " ").replace("/", " ")
    out = re.sub(r"[^\w\s+#.]", " ", out)
    return _WS_RE.sub(" ", out).strip()


def normalize_company(name: str | None) -> str | None:
    if not name:
        return None
    out = name.lower()
    out = re.sub(r"\b(pt|cv|tbk|persero|perseroan|terbatas|inc|ltd|llc|corp|co)\b", " ", out)
    out = re.sub(r"[^\w\s]", " ", out)
    out = _WS_RE.sub(" ", out).strip()
    return out or None


def description_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()


def html_to_text(html: str | None) -> str:
    if not html:
        return ""
    prepared = re.sub(r"(?i)<br\s*/?>", "\n", html)
    prepared = re.sub(
        r"(?i)</(?:p|div|section|article|ul|ol|table|tr|blockquote|h[1-6])>", "\n", prepared
    )
    prepared = re.sub(r"(?i)<li[^>]*>", "\n- ", prepared)
    prepared = re.sub(r"(?i)</t[dh]>", " | ", prepared)
    tree = HTMLParser(prepared)
    for node in tree.css("script, style, noscript, button, form, nav, footer, iframe"):
        node.decompose()
    body = tree.body or tree.root
    text = body.text(separator="") if body else ""
    text = clean_text(text)
    text = re.sub(r" *\| *\n", "\n", text)
    text = re.sub(r"\n *\|", "", text)
    return text[:MAX_DESCRIPTION_CHARS]


def looks_truncated(text: str, html_len: int | None = None) -> bool:
    if not text:
        return True
    tail = text.rstrip().lower()
    if tail.endswith(("...", "…", "selengkapnya", "see more", "baca selengkapnya")):
        return True
    if len(text) < 200 and html_len is not None and html_len > 2000:
        return True
    return False
