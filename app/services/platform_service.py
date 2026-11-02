from __future__ import annotations

from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.repositories import job_repo, keyword_repo, run_repo
from app.db.session import SessionLocal
from app.scrapers.registry import SCRAPERS, platform_config


async def list_keywords(type_: str | None, is_active: bool | None) -> list[dict[str, Any]]:
    async with SessionLocal() as session:
        return [
            keyword_repo.rule_dict(r)
            for r in await keyword_repo.list_rules(session, type_=type_, is_active=is_active)
        ]


async def create_keyword(data: dict[str, Any]) -> dict[str, Any]:
    async with SessionLocal() as session:
        return keyword_repo.rule_dict(await keyword_repo.create_rule(session, data))


async def patch_keyword(rule_id: int, data: dict[str, Any]) -> dict[str, Any]:
    async with SessionLocal() as session:
        return keyword_repo.rule_dict(await keyword_repo.update_rule(session, rule_id, data))


async def delete_keyword(rule_id: int) -> None:
    async with SessionLocal() as session:
        await keyword_repo.delete_rule(session, rule_id)


async def reseed_keywords() -> dict[str, int]:
    async with SessionLocal() as session:
        return await keyword_repo.reseed(session)


def _auth_state(platform: str) -> str | None:
    if not SCRAPERS[platform].requires_auth:
        return None
    path = Path(get_settings().linkedin_state_path)
    if not path.exists():
        return "missing"
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC)
    if datetime.now(UTC) - modified > timedelta(days=30):
        return "expired"
    return "valid"


async def list_platforms() -> list[dict[str, Any]]:
    config = platform_config()
    async with SessionLocal() as session:
        counts = await job_repo.count_jobs_by_platform(session)
        last_sources = await run_repo.last_source_by_platform(session)
    result = []
    for platform, scraper_cls in SCRAPERS.items():
        source = last_sources.get(platform)
        result.append(
            {
                "platform": platform,
                "enabled": bool(config.get(platform, {}).get("enabled", True)),
                "requires_auth": scraper_cls.requires_auth,
                "last_run": {
                    "run_id": source.run_id,
                    "status": source.status,
                    "finished_at": source.finished_at,
                    "found": source.found_count,
                    "new": source.new_count,
                }
                if source
                else None,
                "total_jobs": counts.get(platform, 0),
                "auth_state": _auth_state(platform),
            }
        )
    return result


async def keyword_rules_for_pipeline(session: AsyncSession) -> list[Any]:
    return await keyword_repo.active_rules(session)
