from __future__ import annotations

import hashlib
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import date
from typing import Any

from rapidfuzz import fuzz

from app.pipeline.normalizer import NormalizedJob
from app.scrapers.common.text import normalize_for_match

SENIORITY_TOKENS = {
    "intern",
    "magang",
    "junior",
    "jr",
    "senior",
    "sr",
    "lead",
    "principal",
    "staff",
    "manager",
    "head",
    "chief",
    "vp",
    "director",
}
TECH_TOKENS = {
    "python",
    "java",
    "golang",
    "go",
    "php",
    "node",
    "nodejs",
    "react",
    "vue",
    "angular",
    "laravel",
    "django",
    "flask",
    "fastapi",
    "flutter",
    "kotlin",
    "swift",
    "rust",
    "ruby",
    "rails",
    "scala",
    "typescript",
    "javascript",
    "c#",
    ".net",
    "dotnet",
    "c++",
    "sql",
    "aws",
    "gcp",
    "azure",
    "kubernetes",
    "docker",
}
DEFAULT_SOURCE_PRIORITY = (
    "jobstreet",
    "glints",
    "linkedin",
    "kalibrr",
    "dealls",
    "kitalulus",
    "pintarnya",
)


@dataclass(slots=True)
class DedupDecision:
    action: str
    of_id: int | None = None
    reason: str | None = None


def _tokens(title: str, vocabulary: set[str]) -> set[str]:
    normalized = normalize_for_match(title)
    return {tok for tok in normalized.split() if tok in vocabulary}


def seniority_tokens(title: str) -> set[str]:
    return _tokens(title, SENIORITY_TOKENS)


def tech_tokens(title: str) -> set[str]:
    return _tokens(title, TECH_TOKENS)


def compute_fingerprint(job: NormalizedJob) -> str:
    location = (
        (job.city or "").lower() or "remote"
        if job.work_mode == "remote"
        else (job.city or "").lower() or (job.province or "").lower()
    )
    key = "|".join(
        [
            job.company_normalized or "",
            job.title_normalized,
            location,
        ]
    )
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def title_similarity(a: str, b: str) -> float:
    return fuzz.token_set_ratio(a, b) / 100


def description_similarity(a: str, b: str) -> float:
    return fuzz.token_sort_ratio((a or "")[:2000], (b or "")[:2000]) / 100


def _date(value: str | None) -> date | None:
    try:
        return date.fromisoformat(value) if value else None
    except ValueError:
        return None


def _posted_diff(a: str | None, b: str | None) -> int | None:
    da, db = _date(a), _date(b)
    return abs((da - db).days) if da and db else None


def location_compatible(a: NormalizedJob, b: Any) -> bool:
    a_remote = a.work_mode == "remote"
    b_remote = b.work_mode == "remote"
    if a_remote != b_remote:
        return False
    if a_remote:
        return True
    if a.city and b.city:
        return a.city.casefold() == b.city.casefold()
    if a.province and b.province:
        return a.province.casefold() == b.province.casefold()
    return False


def _company_match(a: NormalizedJob, b: Any) -> tuple[bool, bool]:
    if not a.company_normalized or not b.company_normalized:
        return False, True
    if a.company_normalized == b.company_normalized:
        return True, False
    return fuzz.ratio(a.company_normalized, b.company_normalized) >= 92, False


def _is_repost(a: NormalizedJob, b: Any) -> bool:
    if (
        a.company_normalized
        and b.company_normalized
        and a.company_normalized != b.company_normalized
    ):
        return False
    if (a.city or "").casefold() != (b.city or "").casefold():
        return False
    same_fp = bool(a.fingerprint) and a.fingerprint == getattr(b, "fingerprint", "")
    if not same_fp and title_similarity(a.title, b.title) < 0.95:
        return False
    if seniority_tokens(a.title) != seniority_tokens(b.title):
        return False
    if tech_tokens(a.title) != tech_tokens(b.title):
        return False
    if a.employment_type != b.employment_type and "unknown" not in (
        a.employment_type,
        b.employment_type,
    ):
        return False
    if a.description_hash == b.description_hash:
        return True
    sim = description_similarity(a.description_text, b.description_text)
    if sim >= 0.95:
        return True
    diff = _posted_diff(a.posted_at, b.posted_at)
    return sim >= 0.85 and diff is not None and diff <= 3


def _is_cross_platform(a: NormalizedJob, b: Any) -> bool:
    company_ok, strict = _company_match(a, b)
    if not company_ok and not strict:
        return False
    if not company_ok and strict:
        return (
            title_similarity(a.title, b.title) >= 0.95
            and description_similarity(a.description_text, b.description_text) >= 0.90
            and (a.city or "").casefold() == (b.city or "").casefold()
            and (a.province or "").casefold() == (b.province or "").casefold()
        )
    if title_similarity(a.title, b.title) < 0.90:
        return False
    if seniority_tokens(a.title) != seniority_tokens(b.title):
        return False
    ta, tb = tech_tokens(a.title), tech_tokens(b.title)
    if ta and tb and ta != tb:
        return False
    if a.employment_type != b.employment_type and "unknown" not in (
        a.employment_type,
        b.employment_type,
    ):
        return False
    if not location_compatible(a, b):
        return False
    diff = _posted_diff(a.posted_at, b.posted_at)
    if diff is not None and diff > 21:
        return False
    return description_similarity(a.description_text, b.description_text) >= 0.80


class Deduper:
    def __init__(self, source_priority: Sequence[str] = DEFAULT_SOURCE_PRIORITY) -> None:
        self.source_priority = list(source_priority)

    def _canonical_id(self, candidates: Iterable[Any]) -> int | None:
        def key(c: Any) -> tuple[str, int]:
            prio = (
                self.source_priority.index(c.platform)
                if c.platform in self.source_priority
                else len(self.source_priority)
            )
            return (c.posted_at or "9999-12-31", prio)

        items = list(candidates)
        if not items:
            return None
        by_id = {c.id: c for c in items}
        root = min(items, key=key)
        seen: set[int] = set()
        while getattr(root, "duplicate_of_id", None):
            if root.id in seen:
                break
            seen.add(root.id)
            duplicate_of = root.duplicate_of_id
            root = by_id.get(duplicate_of)
            if root is None:
                return duplicate_of
        return root.id

    def decide(self, job: NormalizedJob, candidates: Iterable[Any]) -> DedupDecision:
        same_platform = []
        cross_platform = []
        for candidate in candidates:
            if candidate.platform == job.platform:
                if (job.external_id and candidate.external_id == job.external_id) or (
                    candidate.url_canonical == job.url_canonical
                ):
                    return DedupDecision("update", candidate.id)
                same_platform.append(candidate)
            else:
                cross_platform.append(candidate)

        reposts = [c for c in same_platform if _is_repost(job, c)]
        if reposts:
            return DedupDecision("duplicate", self._canonical_id(reposts), "repost")

        crosses = [c for c in cross_platform if _is_cross_platform(job, c)]
        if crosses:
            return DedupDecision("duplicate", self._canonical_id(crosses), "cross_platform")

        return DedupDecision("new")
