from __future__ import annotations

import secrets
from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.core.errors import (
    PlatformDisabledError,
    PlatformNotFoundError,
    RunNotCancellableError,
    RunNotFoundError,
    ValidationAppError,
)
from app.core.timeutil import WIB
from app.db.repositories import run_repo
from app.db.session import SessionLocal
from app.runner.run_manager import CallbackRejectedError, run_manager, validate_callback_url
from app.scrapers.registry import SCRAPERS, enabled_platforms, platform_config


def new_run_id() -> str:
    stamp = datetime.now(WIB).strftime("%Y%m%d_%H%M%S")
    return f"r_{stamp}_{secrets.token_hex(2)}"


def _validate_request(platforms: list[str], body: dict[str, Any]) -> dict[str, Any]:
    settings = get_settings()
    config = platform_config()
    for platform in platforms:
        if platform not in SCRAPERS:
            raise PlatformNotFoundError(f"Platform tidak dikenal: {platform}")
        if not config.get(platform, {}).get("enabled", True):
            raise PlatformDisabledError(f"Platform dinonaktifkan: {platform}")

    max_age = body.get("max_age_days")
    if max_age is not None and not (1 <= int(max_age) <= settings.max_age_days_limit):
        raise ValidationAppError(
            f"max_age_days harus 1..{settings.max_age_days_limit}",
            details=[{"field": "max_age_days", "issue": "range"}],
        )
    max_jobs = body.get("max_jobs_per_platform")
    if max_jobs is not None and int(max_jobs) < 1:
        raise ValidationAppError("max_jobs_per_platform harus > 0")

    callback_url = body.get("callback_url")
    if callback_url:
        try:
            validate_callback_url(str(callback_url))
        except CallbackRejectedError as exc:
            raise ValidationAppError(
                str(exc), details=[{"field": "callback_url", "issue": "url"}]
            ) from exc

    params = {
        "keywords": body.get("keywords"),
        "max_age_days": int(max_age) if max_age is not None else settings.default_max_age_days,
        "max_jobs_per_platform": int(max_jobs)
        if max_jobs is not None
        else settings.max_jobs_per_platform,
        "fetch_details": bool(body.get("fetch_details", True)),
        "callback_url": callback_url,
    }
    return params


async def start_scrape(platform: str | None, body: dict[str, Any]) -> dict[str, Any]:
    platforms = enabled_platforms() if platform is None else [platform]
    params = _validate_request(platforms, body)
    run_id = new_run_id()
    await run_manager.enqueue(
        run_id=run_id,
        platforms=platforms,
        params=params,
        callback_url=params["callback_url"],
    )
    return {"run_id": run_id, "status": "queued", "platforms": platforms}


async def get_run(run_id: str) -> dict[str, Any]:
    async with SessionLocal() as session:
        run = await run_repo.get_run(session, run_id)
        if run is None:
            raise RunNotFoundError(f"Run tidak ditemukan: {run_id}")
        sources = await run_repo.sources_for(session, run_id)
        return run_repo.run_dict(run, sources)


async def list_runs(*, status: str | None, limit: int, page: int) -> dict[str, Any]:
    async with SessionLocal() as session:
        rows, total = await run_repo.list_runs(session, status=status, limit=limit, page=page)
        return {
            "items": [
                {
                    "run_id": run.id,
                    "status": run.status,
                    "trigger": run.trigger,
                    "created_at": run.created_at,
                    "finished_at": run.finished_at,
                }
                for run in rows
            ],
            "total": total,
            "page": page,
            "limit": limit,
            "has_more": page * limit < total,
        }


async def cancel_run(run_id: str) -> dict[str, Any]:
    async with SessionLocal() as session:
        run = await run_repo.get_run(session, run_id)
        if run is None:
            raise RunNotFoundError(f"Run tidak ditemukan: {run_id}")
        previous = run.status
    if previous not in ("queued", "running"):
        raise RunNotCancellableError(f"Run berstatus {previous} tidak dapat dibatalkan")
    await run_manager.cancel(run_id)
    return {"run_id": run_id, "status": "cancelling"}
