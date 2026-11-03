from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_iso
from app.db.models import ScrapeRun, ScrapeRunSource


async def create_run(
    session: AsyncSession,
    *,
    run_id: str,
    platforms: list[str],
    params: dict[str, Any],
    trigger: str = "api",
    callback_url: str | None = None,
) -> ScrapeRun:
    now = utc_iso()
    run = ScrapeRun(
        id=run_id,
        trigger=trigger,
        status="queued",
        requested_platforms=json.dumps(platforms),
        params=json.dumps(params),
        callback_url=callback_url,
        callback_status="pending" if callback_url else None,
        created_at=now,
    )
    session.add(run)
    for platform in platforms:
        session.add(ScrapeRunSource(run_id=run_id, platform=platform, status="queued", errors="[]"))
    await session.commit()
    return run


async def get_run(session: AsyncSession, run_id: str) -> ScrapeRun | None:
    return await session.get(ScrapeRun, run_id)


async def list_runs(
    session: AsyncSession, *, status: str | None = None, limit: int = 20, page: int = 1
) -> tuple[list[ScrapeRun], int]:
    from sqlalchemy import func

    stmt = select(ScrapeRun)
    if status:
        stmt = stmt.where(ScrapeRun.status == status)
    total = int(await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0)
    rows = list(
        (
            await session.scalars(
                stmt.order_by(ScrapeRun.created_at.desc()).limit(limit).offset((page - 1) * limit)
            )
        ).all()
    )
    return rows, total


async def sources_for(session: AsyncSession, run_id: str) -> list[ScrapeRunSource]:
    return list(
        (
            await session.scalars(
                select(ScrapeRunSource)
                .where(ScrapeRunSource.run_id == run_id)
                .order_by(ScrapeRunSource.id)
            )
        ).all()
    )


async def get_source(session: AsyncSession, run_id: str, platform: str) -> ScrapeRunSource:
    row = await session.scalar(
        select(ScrapeRunSource).where(
            ScrapeRunSource.run_id == run_id, ScrapeRunSource.platform == platform
        )
    )
    assert row is not None
    return row


async def start_run(session: AsyncSession, run: ScrapeRun) -> None:
    run.status = "running"
    run.started_at = utc_iso()
    await session.commit()


async def finish_run(
    session: AsyncSession, run: ScrapeRun, status: str, error: str | None = None
) -> None:
    run.status = status
    run.finished_at = utc_iso()
    run.error = error
    await session.commit()


async def start_source(session: AsyncSession, source: ScrapeRunSource) -> None:
    source.status = "running"
    source.started_at = utc_iso()
    await session.commit()


async def finish_source(session: AsyncSession, source: ScrapeRunSource, status: str) -> None:
    source.status = status
    source.finished_at = utc_iso()
    await session.commit()


def add_error(source: ScrapeRunSource, code: str, message: str, url: str | None = None) -> None:
    try:
        errors = json.loads(source.errors or "[]")
    except ValueError:
        errors = []
    if len(errors) < 50:
        errors.append({"code": code, "message": message, "url": url, "at": utc_iso()})
    source.errors = json.dumps(errors, ensure_ascii=False)
    source.error_count = int(source.error_count or 0) + 1


async def recover(session: AsyncSession) -> list[str]:
    interrupted = list(
        (await session.scalars(select(ScrapeRun).where(ScrapeRun.status == "running"))).all()
    )
    for run in interrupted:
        run.status = "failed"
        run.error = "interrupted by restart"
        run.finished_at = utc_iso()
    queued = list(
        (
            await session.scalars(
                select(ScrapeRun.id)
                .where(ScrapeRun.status == "queued")
                .order_by(ScrapeRun.created_at)
            )
        ).all()
    )
    await session.commit()
    return queued


async def cancel_run(session: AsyncSession, run: ScrapeRun) -> None:
    run.status = "cancelled"
    run.finished_at = utc_iso()
    await session.commit()


async def details_fetched_since(
    session: AsyncSession, platform: str, since_iso: str
) -> int:
    from sqlalchemy import func

    total = await session.scalar(
        select(func.coalesce(func.sum(ScrapeRunSource.detail_fetched), 0)).where(
            ScrapeRunSource.platform == platform,
            ScrapeRunSource.started_at >= since_iso,
        )
    )
    return int(total or 0)


async def productive_terms(session: AsyncSession, platform: str, terms: list[str]) -> set[str]:
    """Term yang pernah menghasilkan listing pada sub-run sukses (canary §5.3)."""
    if not terms:
        return set()
    wanted = set(terms)
    rows = (
        await session.scalars(
            select(ScrapeRunSource.search_terms).where(
                ScrapeRunSource.platform == platform,
                ScrapeRunSource.status == "completed",
                ScrapeRunSource.found_count > 0,
                ScrapeRunSource.search_terms.is_not(None),
            )
        )
    ).all()
    out: set[str] = set()
    for raw in rows:
        try:
            past = json.loads(raw)
        except (ValueError, TypeError):
            continue
        if isinstance(past, list):
            out.update(t for t in past if t in wanted)
    return out


async def last_source_by_platform(session: AsyncSession) -> dict[str, ScrapeRunSource]:
    rows = list(
        (
            await session.scalars(
                select(ScrapeRunSource)
                .where(ScrapeRunSource.finished_at.is_not(None))
                .order_by(ScrapeRunSource.finished_at.desc())
            )
        ).all()
    )
    out: dict[str, ScrapeRunSource] = {}
    for row in rows:
        out.setdefault(row.platform, row)
    return out


def source_dict(source: ScrapeRunSource) -> dict[str, Any]:
    return {
        "platform": source.platform,
        "status": source.status,
        "found": source.found_count,
        "new": source.new_count,
        "updated": source.updated_count,
        "duplicate": source.duplicate_count,
        "filtered": {
            "keyword": source.filtered_keyword,
            "location": source.filtered_location,
            "age": source.filtered_age,
        },
        "pages": source.pages_visited,
        "detail_fetched": source.detail_fetched,
        "duration_sec": _duration(source.started_at, source.finished_at),
        "errors": json.loads(source.errors or "[]"),
    }


def run_dict(run: ScrapeRun, sources: list[ScrapeRunSource]) -> dict[str, Any]:
    return {
        "run_id": run.id,
        "status": run.status,
        "trigger": run.trigger,
        "params": json.loads(run.params or "{}"),
        "created_at": run.created_at,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "totals": {
            "found": run.found_count,
            "new": run.new_count,
            "updated": run.updated_count,
            "duplicate": run.duplicate_count,
            "filtered": {
                "keyword": run.filtered_keyword,
                "location": run.filtered_location,
                "age": run.filtered_age,
            },
        },
        "errors": [{"code": "INTERNAL_ERROR", "message": run.error}] if run.error else [],
        "platforms": [source_dict(s) for s in sources],
    }


def _duration(started: str | None, finished: str | None) -> int:
    from datetime import datetime

    if not started or not finished:
        return 0
    try:
        return int(
            (datetime.fromisoformat(finished) - datetime.fromisoformat(started)).total_seconds()
        )
    except ValueError:
        return 0
