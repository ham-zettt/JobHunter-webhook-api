from __future__ import annotations

import time

from app.core.config import get_settings

_cache: tuple[float, bool, str] | None = None
_TTL = 60.0


async def check_browser() -> tuple[bool, str]:
    global _cache
    now = time.monotonic()
    if _cache and now - _cache[0] < _TTL:
        return _cache[1], _cache[2]
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=get_settings().playwright_headless)
            await browser.close()
        result = (True, "ok")
    except Exception as exc:  # pragma: no cover - environment dependent
        result = (False, f"error: {type(exc).__name__}")
    _cache = (now, *result)
    return result
