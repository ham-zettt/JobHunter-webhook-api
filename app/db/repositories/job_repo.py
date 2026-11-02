from __future__ import annotations

import json
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any

from sqlalchemy import func, literal_column, or_, select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.timeutil import utc_iso, wib_today
from app.db.models import Job, JobRunLink
from app.pipeline.deduper import DedupDecision
from app.pipeline.normalizer import NormalizedJob
from app.pipeline.pipeline import PipelineResult

SORT_FIELDS = {
    "tanggal_masuk": Job.effective_date,
    "pertama_dilihat": Job.first_seen_at,
    "skor_relevansi": Job.relevance_score,
    "gaji_max": Job.salary_max,
}
PRECISION_RANK = {"exact": 3, "date": 2, "relative": 1, "unknown": 0}


@dataclass(slots=True)
class JobFilters:
    q: str | None = None
    platform: list[str] = field(default_factory=list)
    sistem_kerja: list[str] = field(default_factory=list)
    tipe_kerja: list[str] = field(default_factory=list)
    provinsi: list[str] = field(default_factory=list)
    kota: list[str] = field(default_factory=list)
    kategori_peran: list[str] = field(default_factory=list)
    max_age_days: int | None = None
    has_gaji: bool | None = None
    min_gaji: int | None = None
    first_seen_after: str | None = None
    run_id: str | None = None
    only_new: bool = False
    include_duplicates: bool = False
    include_description: bool = True
    status: str = "active"
    sort: str = "-tanggal_masuk"
    page: int = 1
    limit: int = 50


def _csv(values: Sequence[str] | str | None) -> list[str]:
    if not values:
        return []
    if isinstance(values, str):
        values = [values]
    out: list[str] = []
    for value in values:
        out.extend(part.strip() for part in value.split(",") if part.strip())
    return out


def api_dict(job: Job, *, include_description: bool = True, siblings: int = 0) -> dict[str, Any]:
    return {
        "id": job.id,
        "url": job.url,
        "tanggal_masuk": job.posted_at,
        "tanggal_masuk_presisi": job.posted_at_precision,
        "sumber": job.platform,
        "external_id": job.external_id,
        "perusahaan": job.company_name,
        "posisi": job.title,
        "lokasi": job.location_raw,
        "kota": job.city,
        "provinsi": job.province,
        "sistem_kerja": job.work_mode,
        "tipe_kerja": job.employment_type,
        "gaji": job.salary_raw,
        "gaji_min": job.salary_min,
        "gaji_max": job.salary_max,
        "gaji_mata_uang": job.salary_currency,
        "gaji_periode": job.salary_period,
        "deskripsi": job.description_text if include_description else "",
        "deskripsi_terpotong": bool(job.description_truncated),
        "kategori_peran": job.role_category,
        "kata_kunci_cocok": _load_keywords(job.matched_keywords),
        "skor_relevansi": job.relevance_score,
        "is_duplikat": bool(job.is_duplicate),
        "duplikat_dari_id": job.duplicate_of_id,
        "sumber_lain": siblings,
        "pertama_dilihat": job.first_seen_at,
        "terakhir_dilihat": job.last_seen_at,
        "status": job.status,
    }


def _load_keywords(raw: str | None) -> list[str]:
    try:
        value = json.loads(raw or "[]")
        return value if isinstance(value, list) else []
    except (ValueError, TypeError):
        return []


def build_query(filters: JobFilters, *, use_fts: bool = True):
    stmt = select(Job)
    conditions = []

    if filters.status != "all":
        conditions.append(Job.status == filters.status)
    if not filters.include_duplicates:
        conditions.append(Job.is_duplicate == 0)
    for column, values in (
        (Job.platform, filters.platform),
        (Job.work_mode, filters.sistem_kerja),
        (Job.employment_type, filters.tipe_kerja),
        (Job.role_category, filters.kategori_peran),
    ):
        if values:
            conditions.append(column.in_(values))
    if filters.provinsi:
        conditions.append(func.lower(Job.province).in_([v.lower() for v in filters.provinsi]))
    if filters.kota:
        conditions.append(func.lower(Job.city).in_([v.lower() for v in filters.kota]))
    if filters.max_age_days is not None:
        cutoff = wib_today() - timedelta(days=filters.max_age_days)
        conditions.append(Job.effective_date >= cutoff.isoformat())
    if filters.has_gaji is True:
        conditions.append(Job.salary_max.is_not(None))
    elif filters.has_gaji is False:
        conditions.append(Job.salary_max.is_(None))
    if filters.min_gaji is not None:
        conditions.extend(
            [
                Job.salary_max >= filters.min_gaji,
                Job.salary_currency == "IDR",
                Job.salary_period == "month",
            ]
        )
    if filters.first_seen_after:
        conditions.append(Job.first_seen_at >= filters.first_seen_after)
    if filters.run_id:
        link_stmt = select(JobRunLink.job_id).where(JobRunLink.run_id == filters.run_id)
        if filters.only_new:
            link_stmt = link_stmt.where(JobRunLink.action == "new")
        conditions.append(Job.id.in_(link_stmt))

    if filters.q:
        tokens = [t for t in _sanitize_q(filters.q).split() if t]
        if tokens and use_fts:
            fts_query = " AND ".join(f'"{t}"*' for t in tokens)
            fts = (
                select(literal_column("rowid"))
                .select_from(text("jobs_fts"))
                .where(text("jobs_fts MATCH :fts_q"))
            )
            stmt = stmt.where(Job.id.in_(fts)).params(fts_q=fts_query)
        elif tokens:
            conditions.append(_like_condition(tokens))

    stmt = stmt.where(*conditions)
    return stmt


def _sanitize_q(raw: str) -> str:
    cleaned = "".join(ch for ch in raw if ch not in '"*:()')
    return " ".join(part for part in cleaned.replace("-", " ").split() if part)


def _like_condition(tokens: list[str]):
    clauses = []
    for token in tokens:
        pattern = f"%{token}%"
        clauses.append(
            or_(
                Job.title.ilike(pattern),
                Job.company_name.ilike(pattern),
                Job.description_text.ilike(pattern),
            )
        )
    return or_(*clauses)


def _order(stmt, sort: str):
    descending = sort.startswith("-")
    name = sort.lstrip("-")
    column = SORT_FIELDS.get(name, Job.effective_date)
    return stmt.order_by(column.desc() if descending else column.asc(), Job.id.desc())


async def _run_list(session: AsyncSession, filters: JobFilters, *, max_rows: int | None):
    for use_fts in (True, False):
        stmt = _order(build_query(filters, use_fts=use_fts), filters.sort)
        try:
            total = await session.scalar(select(func.count()).select_from(stmt.subquery()))
            stmt = stmt.limit(max_rows or filters.limit)
            if max_rows is None:
                stmt = stmt.offset((filters.page - 1) * filters.limit)
            rows = list((await session.scalars(stmt)).all())
            return rows, int(total or 0)
        except OperationalError:
            if not use_fts:
                raise
    return [], 0


async def list_jobs(session: AsyncSession, filters: JobFilters) -> tuple[list[Job], int]:
    return await _run_list(session, filters, max_rows=None)


async def export_jobs(session: AsyncSession, filters: JobFilters, max_rows: int) -> list[Job]:
    rows, _ = await _run_list(session, filters, max_rows=max_rows)
    return rows


async def get_job(session: AsyncSession, job_id: int) -> Job | None:
    return await session.get(Job, job_id)


async def sibling_count(session: AsyncSession, job_id: int) -> int:
    return int(
        await session.scalar(
            select(func.count()).select_from(Job).where(Job.duplicate_of_id == job_id)
        )
        or 0
    )


async def find_known(
    session: AsyncSession, platform: str, external_id: str | None, url_canonical: str
) -> Job | None:
    conditions = [Job.url_canonical == url_canonical]
    if external_id:
        conditions.append(Job.external_id == external_id)
    stmt = select(Job).where(Job.platform == platform, or_(*conditions)).limit(1)
    return await session.scalar(stmt)


async def find_candidates(session: AsyncSession, job: NormalizedJob) -> list[Job]:
    conditions = [Job.fingerprint == job.fingerprint, Job.is_duplicate == 0]
    if job.company_normalized:
        conditions.append(Job.company_normalized == job.company_normalized)
        stmt = select(Job).where(or_(*conditions))
    else:
        stmt = select(Job).where(
            Job.title_normalized == job.title_normalized,
            Job.fingerprint == job.fingerprint,
            Job.is_duplicate == 0,
        )
    return list((await session.scalars(stmt.limit(50))).all())


def _apply_richer(target: Job, source: NormalizedJob) -> None:
    def richer(attr: str, unknown: Any = None) -> None:
        new = getattr(source, attr, None)
        old = getattr(target, attr)
        if new is None or new == "" or new == unknown:
            return
        if old is None or old == "" or old == unknown:
            setattr(target, attr, new)

    for attr in (
        "external_id",
        "company_name",
        "company_normalized",
        "location_raw",
        "city",
        "province",
        "salary_raw",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_period",
        "description_html",
        "expires_at",
        "role_category",
        "matched_keywords",
        "relevance_score",
    ):
        richer(attr)
    for attr, unknown in (
        ("work_mode", "unknown"),
        ("employment_type", "unknown"),
        ("is_in_java", None),
        ("is_indonesia", None),
    ):
        richer(attr, unknown)
    if source.description_text and len(source.description_text) > len(
        target.description_text or ""
    ):
        target.description_text = source.description_text
        target.description_hash = source.description_hash
        target.description_truncated = source.description_truncated
    if source.posted_at and PRECISION_RANK.get(source.posted_at_precision, 0) > PRECISION_RANK.get(
        target.posted_at_precision, 0
    ):
        target.posted_at = source.posted_at
        target.posted_at_precision = source.posted_at_precision
        target.effective_date = source.effective_date
    target.fingerprint = source.fingerprint or target.fingerprint


async def insert_new(
    session: AsyncSession, result: PipelineResult, run_id: str, now: str | None = None
) -> Job:
    now = now or utc_iso()
    job = result.job
    row = Job(
        platform=job.platform,
        external_id=job.external_id,
        url=job.url,
        url_canonical=job.url_canonical,
        title=job.title,
        title_normalized=job.title_normalized,
        company_name=job.company_name,
        company_normalized=job.company_normalized,
        location_raw=job.location_raw,
        city=job.city,
        province=job.province,
        is_in_java=job.is_in_java,
        is_indonesia=job.is_indonesia,
        location_verified=job.location_verified,
        work_mode=job.work_mode,
        employment_type=job.employment_type,
        salary_raw=job.salary_raw,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        description_text=job.description_text,
        description_html=job.description_html,
        description_hash=job.description_hash,
        description_truncated=job.description_truncated,
        posted_at=job.posted_at,
        posted_at_precision=job.posted_at_precision,
        expires_at=job.expires_at,
        effective_date=job.effective_date,
        role_category=job.role_category,
        matched_keywords=json.dumps(job.matched_keywords or []),
        relevance_score=job.relevance_score,
        fingerprint=job.fingerprint,
        is_duplicate=0,
        status="active",
        first_seen_at=now,
        last_seen_at=now,
        detail_fetched_at=now,
        first_run_id=run_id,
        last_run_id=run_id,
        created_at=now,
        updated_at=now,
    )
    session.add(row)
    await session.flush()
    return row


async def insert_duplicate(
    session: AsyncSession, result: PipelineResult, run_id: str, now: str | None = None
) -> Job:
    now = now or utc_iso()
    row = await insert_new(session, result, run_id, now)
    decision: DedupDecision = result.dedup  # type: ignore[assignment]
    target_id = decision.of_id
    if not target_id:
        return row
    target = await session.get(Job, target_id)
    if target and target.duplicate_of_id:
        target_id = target.duplicate_of_id
    if target and decision.reason == "repost":
        target.repost_count += 1
    row.is_duplicate = 1
    row.duplicate_of_id = target_id
    row.duplicate_reason = decision.reason
    row.status = "active"
    return row


async def update_existing(
    session: AsyncSession,
    row: Job,
    result: PipelineResult,
    run_id: str,
    now: str | None = None,
) -> Job:
    now = now or utc_iso()
    _apply_richer(row, result.job)
    row.last_seen_at = now
    row.last_run_id = run_id
    row.missed_runs = 0
    row.status = "active"
    row.detail_fetched_at = now
    row.updated_at = now
    return row


async def touch_existing(
    session: AsyncSession, row: Job, run_id: str, now: str | None = None
) -> Job:
    now = now or utc_iso()
    row.last_seen_at = now
    row.last_run_id = run_id
    row.missed_runs = 0
    row.status = "active"
    return row


async def add_link(
    session: AsyncSession, run_id: str, job_id: int, action: str, now: str | None = None
) -> None:
    session.add(
        JobRunLink(run_id=run_id, job_id=job_id, action=action, created_at=now or utc_iso())
    )


async def set_status(session: AsyncSession, job_id: int, status: str) -> Job | None:
    row = await session.get(Job, job_id)
    if row:
        row.status = status
        row.updated_at = utc_iso()
    return row


async def count_jobs_by_platform(session: AsyncSession) -> dict[str, int]:
    rows = await session.execute(
        select(Job.platform, func.count())
        .where(Job.is_duplicate == 0, Job.status == "active")
        .group_by(Job.platform)
    )
    return {platform: count for platform, count in rows.all()}


def to_filters(**kwargs: Any) -> JobFilters:
    platform = _csv(kwargs.pop("platform", None))
    sistem_kerja = _csv(kwargs.pop("sistem_kerja", None))
    tipe_kerja = _csv(kwargs.pop("tipe_kerja", None))
    provinsi = _csv(kwargs.pop("provinsi", None))
    kota = _csv(kwargs.pop("kota", None))
    kategori_peran = _csv(kwargs.pop("kategori_peran", None))
    return JobFilters(
        platform=platform,
        sistem_kerja=sistem_kerja,
        tipe_kerja=tipe_kerja,
        provinsi=provinsi,
        kota=kota,
        kategori_peran=kategori_peran,
        **kwargs,
    )


def iter_jsonl(rows: Iterable[dict[str, Any]]):
    for row in rows:
        yield json.dumps(row, ensure_ascii=False) + "\n"
