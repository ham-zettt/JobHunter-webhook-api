from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urlsplit, urlunsplit

from app.core.timeutil import (
    PRECISION_UNKNOWN,
    ParsedDate,
    parse_posted,
    utc_iso,
    wib_date,
)
from app.scrapers.base import RawJob
from app.scrapers.common.salary import SalaryInfo, parse_salary
from app.scrapers.common.text import (
    clean_text,
    description_hash,
    html_to_text,
    looks_truncated,
    normalize_company,
    normalize_for_match,
)

_REMOTE_RE = re.compile(r"\b(remote|wfh|work from home|kerja dari rumah|fully remote)\b", re.I)
_HYBRID_RE = re.compile(r"\b(hybrid|hibrida)\b", re.I)
_ONSITE_RE = re.compile(r"\b(onsite|on-site|on site|wfo|work from office|di kantor)\b", re.I)
_TYPE_PATTERNS = [
    ("internship", re.compile(r"\b(internship|intern|magang|pemagangan)\b", re.I)),
    ("freelance", re.compile(r"\b(freelance|freelancer|lepas)\b", re.I)),
    ("parttime", re.compile(r"\b(part[\s-]?time|paruh waktu)\b", re.I)),
    ("contract", re.compile(r"\b(contract|kontrak|temporary|project[\s-]?based|pkwt)\b", re.I)),
    ("fulltime", re.compile(r"\b(full[\s-]?time|fulltime|permanent|tetap|pkwtt)\b", re.I)),
]


def canonical_url(url: str) -> str:
    parts = urlsplit(url.strip())
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, "", ""))


def detect_work_mode(*values: str | None) -> str:
    text = " ".join(v for v in values if v)
    if _HYBRID_RE.search(text):
        return "hybrid"
    if _REMOTE_RE.search(text):
        return "remote"
    if _ONSITE_RE.search(text):
        return "onsite"
    return "unknown"


def detect_employment_type(*values: str | None) -> str:
    text = " ".join(v for v in values if v)
    for name, rx in _TYPE_PATTERNS:
        if rx.search(text):
            return name
    return "unknown"


@dataclass(slots=True)
class NormalizedJob:
    platform: str
    url: str
    url_canonical: str
    title: str
    title_normalized: str
    description_text: str
    description_hash: str
    effective_date: str
    external_id: str | None = None
    company_name: str | None = None
    company_normalized: str | None = None
    location_raw: str | None = None
    city: str | None = None
    province: str | None = None
    is_in_java: int | None = None
    is_indonesia: int | None = None
    location_verified: int = 0
    work_mode: str = "unknown"
    employment_type: str = "unknown"
    salary_raw: str | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    salary_currency: str | None = None
    salary_period: str | None = None
    description_html: str | None = None
    description_truncated: int = 0
    posted_at: str | None = None
    posted_at_precision: str = PRECISION_UNKNOWN
    expires_at: str | None = None
    role_category: str | None = None
    matched_keywords: list[str] | None = None
    relevance_score: int = 0
    fingerprint: str = ""
    first_seen_at: str = ""
    last_seen_at: str = ""


class Normalizer:
    def __init__(self, store_html: bool = True) -> None:
        self.store_html = store_html

    def normalize(self, raw: RawJob, *, first_seen: datetime | None = None) -> NormalizedJob:
        text = clean_text(raw.description_text) or html_to_text(raw.description_html)
        if not text:
            text = clean_text(raw.extra.get("snippet")) or ""
        html = raw.description_html if self.store_html else None

        parsed: ParsedDate = parse_posted(raw.posted_raw)
        first_seen_date = wib_date(first_seen)
        effective = parsed.value or first_seen_date

        salary: SalaryInfo = parse_salary(raw.salary_raw)
        expires = parse_posted(raw.expires_raw)

        location_text = raw.location_raw
        work_mode = detect_work_mode(raw.work_mode_raw, raw.title, location_text, text[:600])
        employment = detect_employment_type(raw.employment_type_raw, raw.title, text[:600])

        return NormalizedJob(
            platform=raw.platform,
            url=raw.url,
            url_canonical=canonical_url(raw.url),
            title=clean_text(raw.title),
            title_normalized=normalize_for_match(raw.title),
            description_text=text[:100_000],
            description_hash=description_hash(text),
            description_html=html,
            description_truncated=int(
                raw.description_truncated or looks_truncated(text, len(html or ""))
            ),
            external_id=raw.external_id,
            company_name=clean_text(raw.company) or None,
            company_normalized=normalize_company(raw.company),
            location_raw=clean_text(location_text) or None,
            work_mode=work_mode,
            employment_type=employment,
            salary_raw=salary.raw,
            salary_min=salary.minimum,
            salary_max=salary.maximum,
            salary_currency=salary.currency,
            salary_period=salary.period,
            posted_at=parsed.value,
            posted_at_precision=parsed.precision,
            expires_at=expires.value if expires.value else None,
            effective_date=effective,
            first_seen_at=utc_iso(first_seen),
            last_seen_at=utc_iso(first_seen),
        )
