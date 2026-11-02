from __future__ import annotations

import csv
import io
import json
from collections.abc import AsyncIterator
from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.core.errors import NotFoundError, ValidationAppError
from app.core.timeutil import WIB
from app.db.repositories import job_repo
from app.db.repositories.job_repo import JobFilters, api_dict
from app.db.session import SessionLocal

CSV_FIELDS = [
    "id",
    "url",
    "tanggal_masuk",
    "tanggal_masuk_presisi",
    "sumber",
    "external_id",
    "perusahaan",
    "posisi",
    "lokasi",
    "kota",
    "provinsi",
    "sistem_kerja",
    "tipe_kerja",
    "gaji",
    "gaji_min",
    "gaji_max",
    "gaji_mata_uang",
    "gaji_periode",
    "deskripsi",
    "deskripsi_terpotong",
    "kategori_peran",
    "kata_kunci_cocok",
    "skor_relevansi",
    "is_duplikat",
    "duplikat_dari_id",
    "sumber_lain",
    "pertama_dilihat",
    "terakhir_dilihat",
    "status",
]


async def list_jobs(filters: JobFilters) -> dict[str, Any]:
    filters.limit = min(max(filters.limit, 1), 200)
    filters.page = max(filters.page, 1)
    async with SessionLocal() as session:
        rows, total = await job_repo.list_jobs(session, filters)
        items = [api_dict(row, include_description=filters.include_description) for row in rows]
    return {
        "items": items,
        "total": total,
        "page": filters.page,
        "limit": filters.limit,
        "has_more": filters.page * filters.limit < total,
    }


async def get_job(job_id: int) -> dict[str, Any]:
    async with SessionLocal() as session:
        row = await job_repo.get_job(session, job_id)
        if row is None:
            raise NotFoundError(f"Lowongan tidak ditemukan: {job_id}")
        siblings = await job_repo.sibling_count(session, job_id)
        return api_dict(row, siblings=siblings)


async def update_status(job_id: int, status: str) -> dict[str, Any]:
    if status not in ("active", "archived", "expired"):
        raise ValidationAppError("status harus active, archived, atau expired")
    async with SessionLocal() as session:
        row = await job_repo.set_status(session, job_id, status)
        if row is None:
            raise NotFoundError(f"Lowongan tidak ditemukan: {job_id}")
        await session.commit()
        return api_dict(row)


def _csv_cell(value: Any) -> Any:
    if isinstance(value, list):
        return ";".join("" if v is None else str(v) for v in value)
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def _csv_stream(rows: list[Any]) -> AsyncIterator[bytes]:
    buffer = io.StringIO()
    buffer.write("\ufeff")
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL, lineterminator="\r\n")
    writer.writerow(CSV_FIELDS)
    for row in rows:
        data = api_dict(row)
        writer.writerow([_csv_cell(data.get(field)) for field in CSV_FIELDS])
    yield buffer.getvalue().encode("utf-8")


def _jsonl_stream(rows: list[Any]) -> AsyncIterator[bytes]:
    for row in rows:
        yield (json.dumps(api_dict(row), ensure_ascii=False) + "\n").encode("utf-8")


def _json_stream(rows: list[Any]) -> AsyncIterator[bytes]:
    yield b'{"items": ['
    for index, row in enumerate(rows):
        prefix = b", " if index else b""
        yield prefix + json.dumps(api_dict(row), ensure_ascii=False).encode("utf-8")
    yield b"]}"


async def run_export(filters: JobFilters, fmt: str):
    from fastapi.responses import StreamingResponse

    if fmt not in ("json", "jsonl", "csv"):
        raise ValidationAppError("format harus json, jsonl, atau csv")
    settings = get_settings()
    async with SessionLocal() as session:
        rows = await job_repo.export_jobs(session, filters, settings.export_max_rows)
    streams = {"json": _json_stream, "jsonl": _jsonl_stream, "csv": _csv_stream}
    extension = {"json": "json", "jsonl": "jsonl", "csv": "csv"}[fmt]
    filename = f"jobs_{datetime.now(WIB).strftime('%Y%m%d_%H%M')}.{extension}"
    media = {
        "json": "application/json",
        "jsonl": "application/x-ndjson",
        "csv": "text/csv",
    }[fmt]
    return StreamingResponse(
        streams[fmt](rows),
        media_type=f"{media}; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
