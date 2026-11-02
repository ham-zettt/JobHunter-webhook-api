from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass, field
from typing import Any

from app.scrapers.common.text import normalize_for_match

ROLE_PRIORITY = (
    "ai_automation",
    "ai_engineer",
    "fullstack",
    "backend",
    "frontend",
    "software_engineer",
    "other_it",
)


@dataclass(slots=True)
class KeywordSpec:
    term: str
    type: str
    strength: str | None = None
    scope: str = "both"
    role_category: str | None = None
    is_regex: bool = False

    @classmethod
    def from_row(cls, row: Any) -> KeywordSpec:
        return cls(
            term=row.term,
            type=row.type,
            strength=row.strength,
            scope=row.scope,
            role_category=row.role_category,
            is_regex=bool(row.is_regex),
        )


@dataclass(slots=True)
class Classification:
    accepted: bool
    score: int = 0
    matched: list[str] = field(default_factory=list)
    role_category: str | None = None
    reason: str | None = None


def _pattern(term: str, is_regex: bool = False) -> re.Pattern[str]:
    if is_regex:
        return re.compile(term, re.I)
    normalized = normalize_for_match(term)
    return re.compile(rf"(?<!\w){re.escape(normalized)}(?!\w)")


class Classifier:
    def __init__(self, rules: Iterable[KeywordSpec], *, threshold: int = 50) -> None:
        self.threshold = threshold
        self.includes: list[tuple[KeywordSpec, re.Pattern[str]]] = []
        self.excludes: list[tuple[KeywordSpec, re.Pattern[str]]] = []
        for rule in rules:
            if not rule.term:
                continue
            target = self.includes if rule.type == "include" else self.excludes
            if rule.type in ("include", "exclude"):
                target.append((rule, _pattern(rule.term, rule.is_regex)))

    @classmethod
    def from_rows(cls, rows: Iterable[Any], *, threshold: int = 50) -> Classifier:
        return cls((KeywordSpec.from_row(r) for r in rows), threshold=threshold)

    def is_title_excluded(self, title: str) -> bool:
        t = f" {normalize_for_match(title)} "
        return any(spec.scope in ("title", "both") and rx.search(t) for spec, rx in self.excludes)

    def classify(self, title: str, description: str) -> Classification:
        t = f" {normalize_for_match(title)} "
        d = f" {normalize_for_match(description)} "

        def hit(rx: re.Pattern[str], text: str) -> bool:
            return bool(rx.search(text))

        title_excluded = any(
            spec.scope in ("title", "both") and hit(rx, t) for spec, rx in self.excludes
        )
        if title_excluded:
            return Classification(accepted=False, reason="keyword")

        strong_title: list[KeywordSpec] = []
        weak_title: list[KeywordSpec] = []
        strong_desc: list[KeywordSpec] = []
        weak_desc: list[KeywordSpec] = []

        for spec, rx in self.includes:
            in_title = spec.scope in ("title", "both") and hit(rx, t)
            in_desc = spec.scope in ("description", "both") and hit(rx, d)
            if spec.strength == "strong":
                if in_title:
                    strong_title.append(spec)
                if in_desc:
                    strong_desc.append(spec)
            elif spec.strength == "weak":
                if in_title:
                    weak_title.append(spec)

        if strong_title:
            title_component = 100 + min(30, 10 * (len(strong_title) - 1))
        elif weak_title:
            title_component = 40
        else:
            title_component = 0

        desc_component = min(75, 25 * len(strong_desc)) + min(10, 5 * len(weak_desc))
        desc_excluded = [
            spec
            for spec, rx in self.excludes
            if spec.scope in ("description", "both") and hit(rx, d)
        ]
        penalty = min(45, 15 * len(desc_excluded))
        score = max(0, title_component + desc_component - penalty)

        accepted = title_component > 0 or score >= self.threshold
        if not accepted:
            return Classification(accepted=False, score=score, reason="keyword")

        matched: list[str] = []
        for spec in [*strong_title, *weak_title, *strong_desc]:
            if spec.term not in matched:
                matched.append(spec.term)

        return Classification(
            accepted=True,
            score=score,
            matched=matched[:20],
            role_category=self._role(strong_title + weak_title + strong_desc),
        )

    @staticmethod
    def _role(specs: list[KeywordSpec]) -> str | None:
        roles = {s.role_category for s in specs if s.role_category}
        if not roles:
            return "other_it" if specs else None
        if "ai_automation" in roles:
            return "ai_automation"
        if "ai_engineer" in roles:
            return "ai_engineer"
        if "fullstack" in roles or {"frontend", "backend"} <= roles:
            return "fullstack"
        for role in ("backend", "frontend", "software_engineer"):
            if role in roles:
                return role
        return "other_it"
