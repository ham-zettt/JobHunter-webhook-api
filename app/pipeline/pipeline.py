from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.core.timeutil import now_utc
from app.pipeline.age_filter import is_too_old
from app.pipeline.classifier import Classifier
from app.pipeline.deduper import DedupDecision, Deduper, compute_fingerprint
from app.pipeline.location import LocationNormalizer, LocationResult, accept_location
from app.pipeline.normalizer import NormalizedJob, Normalizer
from app.scrapers.base import RawJob


@dataclass(slots=True)
class PipelineResult:
    job: NormalizedJob
    accepted: bool
    filter_reason: str | None = None
    dedup: DedupDecision | None = None
    location: LocationResult = field(default_factory=LocationResult)


class Pipeline:
    def __init__(
        self,
        classifier: Classifier,
        locations: LocationNormalizer,
        *,
        keep_unverified_location: bool | None = None,
        max_age_days: int | None = None,
        deduper: Deduper | None = None,
        store_html: bool | None = None,
    ) -> None:
        settings = get_settings()
        self.classifier = classifier
        self.locations = locations
        self.keep_unverified = (
            settings.keep_unverified_location
            if keep_unverified_location is None
            else keep_unverified_location
        )
        self.max_age_days = settings.default_max_age_days if max_age_days is None else max_age_days
        self.deduper = deduper or Deduper()
        self.normalizer = Normalizer(
            store_html=settings.store_html if store_html is None else store_html
        )

    def prepare(
        self,
        raw: RawJob,
        *,
        first_seen: datetime | None = None,
    ) -> tuple[NormalizedJob, LocationResult]:
        job = self.normalizer.normalize(raw, first_seen=first_seen or now_utc())
        loc = self.locations.normalize(raw.location_raw)
        job.city = loc.city
        job.province = loc.province
        job.is_in_java = loc.is_in_java
        job.is_indonesia = loc.is_indonesia
        job.location_verified = int(loc.verified)
        job.fingerprint = compute_fingerprint(job)
        return job, loc

    def process(
        self,
        raw: RawJob,
        *,
        candidates: Iterable[Any] = (),
        first_seen: datetime | None = None,
    ) -> PipelineResult:
        job, loc = self.prepare(raw, first_seen=first_seen)

        if not accept_location(job.work_mode, loc, self.keep_unverified):
            return PipelineResult(job, False, "location", location=loc)

        classification = self.classifier.classify(job.title, job.description_text)
        if not classification.accepted:
            return PipelineResult(job, False, "keyword", location=loc)
        job.relevance_score = classification.score
        job.matched_keywords = classification.matched
        job.role_category = classification.role_category

        if is_too_old(job.effective_date, self.max_age_days):
            return PipelineResult(job, False, "age", location=loc)

        decision = self.deduper.decide(job, list(candidates))
        return PipelineResult(job, True, dedup=decision, location=loc)
