from __future__ import annotations

import asyncio
import random
import re
import time
from pathlib import Path

from playwright.async_api import Browser, BrowserContext, Page, Playwright, async_playwright

from app.core.config import get_settings
from app.core.logging import get_logger

log = get_logger("browser")

CHALLENGE_URL_MARKERS = (
    "/checkpoint",
    "/authwall",
    "/login",
    "/uas/",
    "captcha",
    "challenge",
    "cf-chl",
)
CHALLENGE_TEXT_MARKERS = (
    "just a moment",
    "tunggu sebentar",
    "verify you are human",
    "access denied",
    "unusual activity",
    "aktivitas tidak biasa",
    "verifikasi",
    "recaptcha",
    "hcaptcha",
    "turnstile",
)


def detect_challenge(html: str, url: str) -> bool:
    lowered_url = (url or "").lower()
    if any(marker in lowered_url for marker in CHALLENGE_URL_MARKERS):
        return True
    head = (html or "")[:60_000].lower()
    return any(marker in head for marker in CHALLENGE_TEXT_MARKERS)


class BrowserPool:
    """Satu Chromium per aplikasi, satu context per platform per run.

    Browser dibuat lazily agar test offline tidak memerlukan binary Chromium.
    `channel="chromium"` memakai Chromium penuh (new headless); headless-shell
    bawaan default terdeteksi sebagai bot oleh sebagian platform.
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.headless = settings.playwright_headless
        self.nav_timeout_ms = settings.nav_timeout_ms
        self.action_timeout_ms = settings.action_timeout_ms
        self._pw: Playwright | None = None
        self._browser: Browser | None = None
        self._contexts: dict[str, BrowserContext] = {}
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        async with self._lock:
            if self._browser is not None:
                return
            self._pw = await async_playwright().start()
            try:
                self._browser = await self._pw.chromium.launch(
                    headless=self.headless, channel="chromium"
                )
            except Exception:  # pragma: no cover - fallback bila channel tidak ada
                self._browser = await self._pw.chromium.launch(headless=self.headless)

    async def context(self, platform: str, *, storage_state: str | None = None) -> BrowserContext:
        if self._browser is None:
            await self.start()
        existing = self._contexts.get(platform)
        if existing is not None:
            return existing
        assert self._browser is not None
        context = await self._browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            storage_state=storage_state,
        )
        context.set_default_navigation_timeout(self.nav_timeout_ms)
        context.set_default_timeout(self.action_timeout_ms)
        self._contexts[platform] = context
        return context

    async def new_page(self, platform: str, *, storage_state: str | None = None) -> Page:
        context = await self.context(platform, storage_state=storage_state)
        return await context.new_page()

    async def reset_context(self, platform: str) -> None:
        context = self._contexts.pop(platform, None)
        if context is not None:
            await context.close()

    async def stop(self) -> None:
        async with self._lock:
            for context in self._contexts.values():
                await context.close()
            self._contexts.clear()
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            if self._pw is not None:
                await self._pw.stop()
                self._pw = None


def jitter(delay_ms: tuple[int, int] | list[int]) -> float:
    low, high = delay_ms
    return random.uniform(low, high) / 1000.0


async def save_debug_snapshot(
    page: Page, run_id: str, platform: str, reason: str = "error"
) -> Path | None:
    """Screenshot + HTML ke data/debug/<run_id>/, dengan rotasi jumlah file."""
    try:
        root = Path("data/debug")
        outdir = root / run_id
        outdir.mkdir(parents=True, exist_ok=True)
        safe_reason = re.sub(r"[^a-z0-9_-]+", "_", reason.lower())[:40]
        stamp = time.strftime("%Y%m%d_%H%M%S")
        prefix = f"{platform}_{stamp}_{safe_reason}"
        await page.screenshot(path=str(outdir / f"{prefix}.png"), full_page=False)
        (outdir / f"{prefix}.html").write_text(await page.content(), encoding="utf-8")
        _prune_debug_files(root)
        return outdir / f"{prefix}.html"
    except Exception:  # pragma: no cover - snapshot tidak boleh menjatuhkan run
        log.warning("debug_snapshot_failed", platform=platform, run_id=run_id)
        return None


def _prune_debug_files(root: Path) -> None:
    limit = get_settings().debug_snapshot_max_files
    files = sorted(root.rglob("*.*"), key=lambda p: p.stat().st_mtime)
    for path in files[: max(0, len(files) - limit)]:
        try:
            path.unlink()
        except OSError:  # pragma: no cover
            pass
