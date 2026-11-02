from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Query

from app.db.repositories.job_repo import JobFilters, to_filters
from app.services import job_service

router = APIRouter(prefix="/jobs", tags=["jobs"])

Common = Annotated[str | None, Query()]


def _filters(
    q: Common = None,
    platform: Common = None,
    sistem_kerja: Common = None,
    tipe_kerja: Common = None,
    provinsi: Common = None,
    kota: Common = None,
    kategori_peran: Common = None,
    max_age_days: int | None = Query(default=None, ge=1),
    has_gaji: bool | None = Query(default=None),
    min_gaji: int | None = Query(default=None, ge=0),
    first_seen_after: str | None = Query(default=None),
    run_id: str | None = Query(default=None),
    only_new: bool = Query(default=False),
    include_duplicates: bool = Query(default=False),
    include_description: bool = Query(default=True),
    status: str = Query(default="active"),
    sort: str = Query(default="-tanggal_masuk"),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=50, ge=1, le=200),
):
    return to_filters(
        q=q,
        platform=platform,
        sistem_kerja=sistem_kerja,
        tipe_kerja=tipe_kerja,
        provinsi=provinsi,
        kota=kota,
        kategori_peran=kategori_peran,
        max_age_days=max_age_days,
        has_gaji=has_gaji,
        min_gaji=min_gaji,
        first_seen_after=first_seen_after,
        run_id=run_id,
        only_new=only_new,
        include_duplicates=include_duplicates,
        include_description=include_description,
        status=status,
        sort=sort,
        page=page,
        limit=limit,
    )


Filters = Annotated[JobFilters, Depends(_filters)]


@router.get("")
async def list_jobs(filters: Filters):
    return await job_service.list_jobs(filters)


@router.get("/export")
async def export_jobs(filters: Filters, format: str = Query(default="json")):
    return await job_service.run_export(filters, format)


@router.get("/{job_id}")
async def get_job(job_id: int) -> dict:
    return await job_service.get_job(job_id)


@router.patch("/{job_id}")
async def patch_job(job_id: int, status: str = Body(embed=True)) -> dict:
    return await job_service.update_status(job_id, status)
