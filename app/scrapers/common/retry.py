from __future__ import annotations

import asyncio
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
    wait_random,
)

from app.scrapers.browser import detect_challenge
from app.scrapers.exceptions import BlockedError, SiteChangedError, TransientNetworkError

RETRY_ATTEMPTS = 3
MAX_RATE_LIMIT_RETRIES = 2
RATE_LIMIT_FALLBACK_SEC = 60.0
WAIT = wait_exponential(multiplier=2, min=2, max=8) + wait_random(0, 1)


class _RateLimited(Exception):
    def __init__(self, retry_after: float | None) -> None:
        super().__init__("rate limited")
        self.retry_after = retry_after


def _retry_after_seconds(response: httpx.Response) -> float | None:
    raw = response.headers.get("Retry-After")
    if not raw:
        return None
    try:
        # ponytail: hanya detik; Retry-After HTTP-date diabaikan (fallback 60 dtk).
        return max(0.0, float(raw))
    except ValueError:
        return None


async def _attempt(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None,
    check_challenge: bool,
    **kwargs: Any,
) -> httpx.Response:
    try:
        response = await client.request(method, url, headers=headers, **kwargs)
    except httpx.HTTPError as exc:
        raise TransientNetworkError(f"request gagal: {exc}", url=url) from exc
    status = response.status_code
    if status in (403, 999):
        raise BlockedError(f"akses ditolak ({status})", url=str(response.url))
    if status == 429:
        raise _RateLimited(_retry_after_seconds(response))
    if status >= 500:
        raise TransientNetworkError(f"HTTP {status}", url=str(response.url))
    if status != 200:
        raise SiteChangedError(f"HTTP {status}", url=str(response.url))
    if "cf-mitigated" in response.headers or (
        check_challenge and detect_challenge(response.text[:60_000], str(response.url))
    ):
        raise BlockedError("menampilkan tantangan anti-bot", url=str(response.url))
    return response


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    check_challenge: bool = False,
    **kwargs: Any,
) -> httpx.Response:
    """GET dengan retry terpusat (SCRAPER_SPEC §4.2).

    Transient/5xx: tenacity 3 percobaan backoff 2→4→8 dtk + jitter.
    429: tunggu Retry-After/60 dtk, maks 2 kali lalu ``BlockedError``.
    403/999/CAPTCHA/challenge: langsung ``BlockedError`` (tanpa retry).
    """
    rate_limited = 0
    while True:
        try:
            async for attempt in AsyncRetrying(
                stop=stop_after_attempt(RETRY_ATTEMPTS),
                wait=WAIT,
                retry=retry_if_exception_type(TransientNetworkError),
                reraise=True,
            ):
                with attempt:
                    return await _attempt(
                        client,
                        method,
                        url,
                        headers=headers,
                        check_challenge=check_challenge,
                        **kwargs,
                    )
        except _RateLimited as exc:
            if rate_limited >= MAX_RATE_LIMIT_RETRIES:
                raise BlockedError("rate limit (429) berulang", url=url) from exc
            rate_limited += 1
            await asyncio.sleep(
                exc.retry_after if exc.retry_after is not None else RATE_LIMIT_FALLBACK_SEC
            )
