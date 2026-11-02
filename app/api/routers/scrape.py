from __future__ import annotations

from fastapi import APIRouter, Body, Query
from fastapi.responses import JSONResponse

from app.api.schemas.scrape import ScrapeRequest
from app.services import scrape_service

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("/all", status_code=202)
async def scrape_all(body: ScrapeRequest | None = Body(default=None)) -> JSONResponse:
    payload = body.model_dump() if body else {}
    result = await scrape_service.start_scrape(None, payload)
    return JSONResponse(status_code=202, content=result)


@router.post("/{platform}", status_code=202)
async def scrape_platform(
    platform: str, body: ScrapeRequest | None = Body(default=None)
) -> JSONResponse:
    payload = body.model_dump() if body else {}
    result = await scrape_service.start_scrape(platform, payload)
    return JSONResponse(status_code=202, content=result)


@router.get("/runs")
async def list_runs(
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=200),
    page: int = Query(default=1, ge=1),
) -> dict:
    return await scrape_service.list_runs(status=status, limit=limit, page=page)


@router.get("/runs/{run_id}")
async def get_run(run_id: str) -> dict:
    return await scrape_service.get_run(run_id)


@router.post("/runs/{run_id}/cancel")
async def cancel_run(run_id: str) -> dict:
    return await scrape_service.cancel_run(run_id)
