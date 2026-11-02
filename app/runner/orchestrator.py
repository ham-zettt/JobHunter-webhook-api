from __future__ import annotations

import asyncio
import json
import statistics
import time
from datetime import UTC, datetime, timedelta
from datetime import time as day_time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.logging import get_logger
from app.core.timeutil import WIB, parse_posted, utc_iso, wib_today
from app.db.repositories import job_repo, keyword_repo, run_repo
from app.db.session import SessionLocal
from app.pipeline.age_filter import is_too_old
from app.pipeline.classifier import Classifier
from app.pipeline.deduper import DedupDecision
from app.pipeline.location import LocationNormalizer, accept_location
from app.pipeline.normalizer import canonical_url, detect_work_mode
from app.pipeline.pipeline import Pipeline
from app.scrapers.base import RawJob, ScrapeContext
from app.scrapers.exceptions import (
    AuthRequiredError,
    BlockedError,
    ScraperError,
    SiteChangedError,
)
from app.scrapers.platforms._placeholder import DISCOVERY_MESSAGE
from app.scrapers.registry import SCRAPERS, platform_config

log = get_logger("orchestrator")

DEGRADED_AFTER_CONSECUTIVE_ERRORS = 5


class Orchestrator:
    async def run(
        self, run_id: str, cancel_event: asyncio.Event | None = None, browser_pool: Any = None
    ) -> None:
        async with SessionLocal() as session:
            run = await run_repo.get_run(session, run_id)
            if run is None or run.status in ("cancelled", "completed", "partial", "failed"):
                return
            params = json.loads(run.params or "{}")
            platforms = json.loads(run.requested_platforms or "[]")
            await run_repo.start_run(session, run)

            pipeline = await self._build_pipeline(session, params)
            for platform in platforms:
                if cancel_event and cancel_event.is_set():
                    source = await run_repo.get_source(session, run_id, platform)
                    await run_repo.finish_source(session, source, "cancelled")
                    continue
                await self._run_platform(
                    session, run, platform, params, pipeline, cancel_event, browser_pool
                )

            await self._aggregate(session, run)
            status = await self._final_status(run, session)
            await run_repo.finish_run(session, run, status)

    async def _build_pipeline(self, session: AsyncSession, params: dict[str, Any]) -> Pipeline:
        settings = get_settings()
        rules = await keyword_repo.active_rules(session)
        classifier = Classifier.from_rows(rules, threshold=settings.relevance_threshold)
        locations = LocationNormalizer(f"{settings.config_dir}/locations_java.yaml")
        return Pipeline(
            classifier,
            locations,
            max_age_days=int(params.get("max_age_days") or settings.default_max_age_days),
        )

    async def _run_platform(
        self,
        session: AsyncSession,
        run: Any,
        platform: str,
        params: dict[str, Any],
        pipeline: Pipeline,
        cancel_event: asyncio.Event | None,
        browser_pool: Any = None,
    ) -> None:
        source = await run_repo.get_source(session, run.id, platform)
        scraper_cls = SCRAPERS.get(platform)
        cfg = platform_config().get(platform, {})
        if scraper_cls is None or not cfg.get("enabled", True):
            await run_repo.finish_source(session, source, "skipped")
            return

        settings = get_settings()
        max_age = int(params.get("max_age_days") or settings.default_max_age_days)
        max_jobs = int(
            params.get("max_jobs_per_platform")
            or cfg.get("max_details_per_run", settings.max_jobs_per_platform)
        )
        if platform == "linkedin":
            day_start = datetime.combine(wib_today(), day_time.min, tzinfo=WIB)
            used = await run_repo.details_fetched_since(
                session, platform, utc_iso(day_start)
            )
            remaining = settings.linkedin_max_jobs_per_day - used
            if remaining <= 0:
                run_repo.add_error(source, "DAILY_CAP", "Batas harian LinkedIn tercapai")
                await run_repo.finish_source(session, source, "skipped")
                return
            max_jobs = min(max_jobs, settings.linkedin_max_jobs_per_run, remaining)
        terms = params.get("keywords") or await keyword_repo.search_terms(
            session, int(cfg.get("search_terms_limit", 10))
        )
        ctx = ScrapeContext(
            run_id=run.id,
            max_age_days=max_age,
            max_jobs=max_jobs,
            fetch_details=bool(params.get("fetch_details", True)),
            search_terms=list(terms),
            max_pages_per_term=int(cfg.get("max_pages_per_term", 6)),
            browser=browser_pool,
        )
        scraper = scraper_cls(ctx)
        await run_repo.start_source(session, source)
        source.search_terms = json.dumps(list(terms))

        deadline = time.monotonic() + float(cfg.get("max_duration_sec", 1500))
        status = "completed"
        descriptions: list[int] = []
        missing_required = 0
        detail_count = 0
        old_streak = 0
        consecutive_errors = 0
        pages_seen = 0

        try:
            await scraper.check_session()
        except AuthRequiredError as exc:
            run_repo.add_error(source, exc.code, exc.message)
            await run_repo.finish_source(session, source, "auth_required")
            return
        except BlockedError as exc:
            run_repo.add_error(source, exc.code, exc.message)
            await run_repo.finish_source(session, source, "blocked")
            return

        try:
            for term in terms:
                if status != "completed" or source.detail_fetched >= max_jobs:
                    break
                if cancel_event and cancel_event.is_set():
                    status = "cancelled"
                    break
                if time.monotonic() > deadline:
                    break
                try:
                    async for listing in scraper.iter_listings(term):
                        if cancel_event and cancel_event.is_set():
                            status = "cancelled"
                            break
                        if time.monotonic() > deadline:
                            break
                        if source.detail_fetched >= max_jobs:
                            break
                        source.found_count += 1
                        pages_seen = max(pages_seen, int(listing.extra.get("page", 0)))

                        post = parse_posted(listing.posted_raw)
                        if post.value and is_too_old(post.value, max_age):
                            source.filtered_age += 1
                            old_streak += 1
                            await session.commit()
                            if old_streak >= 5:
                                break
                            continue
                        old_streak = 0

                        if pipeline.classifier.is_title_excluded(listing.title):
                            source.filtered_keyword += 1
                            await session.commit()
                            continue
                        work_mode = detect_work_mode(listing.title, listing.location_raw)
                        loc = pipeline.locations.normalize(listing.location_raw)
                        if not accept_location(work_mode, loc, pipeline.keep_unverified):
                            source.filtered_location += 1
                            await session.commit()
                            continue

                        known = await job_repo.find_known(
                            session,
                            platform,
                            listing.external_id,
                            canonical_url(listing.url),
                        )
                        if known is not None and self._is_fresh(known, settings):
                            await job_repo.touch_existing(session, known, run.id)
                            await job_repo.add_link(session, run.id, known.id, "seen")
                            await session.commit()
                            continue

                        try:
                            raw = await self._fetch(scraper, listing, ctx)
                        except (BlockedError, AuthRequiredError):
                            raise
                        except Exception as exc:
                            code = getattr(exc, "code", "PARSE_ERROR")
                            run_repo.add_error(source, code, str(exc), listing.url)
                            consecutive_errors += 1
                            await session.commit()
                            if consecutive_errors >= DEGRADED_AFTER_CONSECUTIVE_ERRORS:
                                status = "degraded"
                                break
                            continue

                        detail_count += 1
                        source.detail_fetched += 1
                        consecutive_errors = 0
                        descriptions.append(len(raw.description_text))
                        if not raw.title or not raw.url or not raw.description_text:
                            missing_required += 1

                        prepared, _ = pipeline.prepare(raw)
                        candidates = await job_repo.find_candidates(session, prepared)
                        result = pipeline.process(raw, candidates=candidates)
                        if known is not None and result.accepted:
                            result.dedup = DedupDecision("update", known.id)
                        await self._persist(session, source, result, run.id)
                        await session.commit()
                except BlockedError as exc:
                    run_repo.add_error(source, exc.code, exc.message)
                    status = "blocked"
                    break
                except AuthRequiredError as exc:
                    run_repo.add_error(source, exc.code, exc.message)
                    status = "auth_required"
                    break
                except (SiteChangedError, ScraperError) as exc:
                    run_repo.add_error(source, exc.code, exc.message)
                    status = "degraded"
                    break
        except Exception as exc:  # pragma: no cover - safety net
            log.exception("platform_run_failed", run_id=run.id, platform=platform)
            run_repo.add_error(source, "INTERNAL_ERROR", str(exc))
            status = "failed"

        source.pages_visited = pages_seen
        if status == "completed":
            status = self._canary(status, source, descriptions, detail_count, missing_required)
            if ctx.fetch_details and source.found_count > 0 and detail_count == 0:
                status = "degraded"
        await run_repo.finish_source(session, source, status)

    async def _fetch(self, scraper: Any, listing: Any, ctx: ScrapeContext) -> RawJob:
        if ctx.fetch_details:
            return await scraper.fetch_detail(listing)
        return RawJob(
            platform=listing.platform,
            url=listing.url,
            title=listing.title,
            description_text=listing.snippet or "",
            external_id=listing.external_id,
            company=listing.company,
            location_raw=listing.location_raw,
            posted_raw=listing.posted_raw,
            description_truncated=True,
        )

    async def _persist(self, session: AsyncSession, source: Any, result: Any, run_id: str) -> None:
        if not result.accepted:
            if result.filter_reason == "keyword":
                source.filtered_keyword += 1
            elif result.filter_reason == "location":
                source.filtered_location += 1
            elif result.filter_reason == "age":
                source.filtered_age += 1
            return

        decision = result.dedup
        if decision.action == "new":
            row = await job_repo.insert_new(session, result, run_id)
            source.new_count += 1
            action = "new"
        elif decision.action == "update":
            row = await job_repo.get_job(session, decision.of_id or 0)
            if row is None:
                row = await job_repo.insert_new(session, result, run_id)
                source.new_count += 1
                action = "new"
            else:
                await job_repo.update_existing(session, row, result, run_id)
                source.updated_count += 1
                action = "updated"
        else:
            row = await job_repo.insert_duplicate(session, result, run_id)
            source.duplicate_count += 1
            action = "repost" if decision.reason == "repost" else "duplicate"
        await job_repo.add_link(session, run_id, row.id, action)

    @staticmethod
    def _is_fresh(job: Any, settings: Any) -> bool:
        if not job.detail_fetched_at:
            return False
        try:
            fetched = datetime.fromisoformat(job.detail_fetched_at)
        except ValueError:
            return False
        if fetched.tzinfo is None:
            fetched = fetched.replace(tzinfo=UTC)
        return datetime.now(UTC) - fetched < timedelta(days=settings.detail_refresh_days)

    @staticmethod
    def _canary(
        status: str, source: Any, descriptions: list[int], detail_count: int, missing_required: int
    ) -> str:
        if source.found_count == 0:
            return "degraded"
        if detail_count and missing_required / detail_count > 0.30:
            return "degraded"
        if descriptions and statistics.median(descriptions) < 150:
            return "degraded"
        if source.error_count and source.error_count >= DEGRADED_AFTER_CONSECUTIVE_ERRORS:
            return "degraded"
        return status

    async def _aggregate(self, session: AsyncSession, run: Any) -> None:
        sources = await run_repo.sources_for(session, run.id)
        run.found_count = sum(s.found_count for s in sources)
        run.new_count = sum(s.new_count for s in sources)
        run.updated_count = sum(s.updated_count for s in sources)
        run.duplicate_count = sum(s.duplicate_count for s in sources)
        run.filtered_keyword = sum(s.filtered_keyword for s in sources)
        run.filtered_location = sum(s.filtered_location for s in sources)
        run.filtered_age = sum(s.filtered_age for s in sources)
        await session.commit()

    @staticmethod
    async def _final_status(run: Any, session: AsyncSession) -> str:
        sources = await run_repo.sources_for(session, run.id)
        statuses = [s.status for s in sources]
        if not statuses:
            return "failed"
        if all(s in ("cancelled",) for s in statuses):
            return "cancelled"
        if all(s in ("completed", "skipped") for s in statuses):
            return "completed"
        if all(s in ("failed",) for s in statuses):
            return "failed"
        return "partial"


def discovery_stub_message(platform: str) -> str:
    return DISCOVERY_MESSAGE.format(platform=platform)
