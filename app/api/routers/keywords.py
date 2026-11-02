from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.schemas.keyword import KeywordCreate, KeywordUpdate
from app.services import platform_service

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("")
async def list_keywords(
    type: str | None = Query(default=None), is_active: bool | None = Query(default=None)
) -> list[dict]:
    return await platform_service.list_keywords(type, is_active)


@router.post("", status_code=201)
async def create_keyword(body: KeywordCreate) -> dict:
    return await platform_service.create_keyword(body.to_row())


@router.patch("/{rule_id}")
async def patch_keyword(rule_id: int, body: KeywordUpdate) -> dict:
    return await platform_service.patch_keyword(rule_id, body.to_row())


@router.delete("/{rule_id}", status_code=204)
async def delete_keyword(rule_id: int) -> None:
    await platform_service.delete_keyword(rule_id)


@router.post("/reseed")
async def reseed() -> dict:
    return await platform_service.reseed_keywords()
