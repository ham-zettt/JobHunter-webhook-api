from __future__ import annotations

from fastapi import APIRouter

from app.db.session import engine
from app.services.health_service import check_browser

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    from starlette.responses import JSONResponse

    components: dict[str, str] = {"db": "ok", "browser": "ok"}
    version = "1.0.0"

    try:
        async with engine.connect() as conn:
            await conn.exec_driver_sql("SELECT 1")
    except Exception:
        components["db"] = "error"

    ok, browser_state = await check_browser()
    if not ok:
        components["browser"] = browser_state

    healthy = all(v == "ok" for v in components.values())
    body = {"status": "ok" if healthy else "error", **components, "version": version}
    if not healthy:
        return JSONResponse(status_code=503, content=body)
    return body
