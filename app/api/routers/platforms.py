from __future__ import annotations

from fastapi import APIRouter

from app.services import platform_service

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("")
async def list_platforms() -> list[dict]:
    return await platform_service.list_platforms()
