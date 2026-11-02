from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import httpx
from selectolax.lexbor import LexborHTMLParser

from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.browser import detect_challenge, jitter
from app.scrapers.common.text import html_to_text, looks_truncated
from app.scrapers.exceptions import (
    BlockedError,
    ParseError,
    SiteChangedError,
    TransientNetworkError,
)

BASE = "https://www.kalibrr.com"
SEARCH_API = f"{BASE}/kjs/job_board/search"
PAGE_SIZE = 15
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/156.0.0.0 Safari/537.36"
)
DESCRIPTION_FIELDS = (
    "description",
    "qualifications",
    "duties",
    "responsibilities",
    "requirements",
)


def _location(components: dict[str, Any] | None) -> str | None:
    if not isinstance(components, dict):
        return None
    parts: list[str] = []
    for key in ("city", "region", "country"):
        value = components.get(key)
        if value and value not in parts:
            parts.append(str(value).strip())
    return ", ".join(parts) or None


def _work_mode(work_from_home: bool | None, hybrid: bool | None) -> str | None:
    if work_from_home is True:
        return "Remote"
    if hybrid is True:
        return "Hybrid"
    if work_from_home is False or hybrid is False:
        return "On-site"
    return None


def _salary_text(
    shown: bool | None,
    minimum: int | None,
    maximum: int | None,
    currency: str | None,
    interval: str | None,
) -> str | None:
    if not shown or (minimum is None and maximum is None):
        return None
    low = int(minimum) if minimum is not None else None
    high = int(maximum) if maximum is not None else None
    if low is not None and high is not None and low != high:
        amount = f"{low:,} - {high:,}"
    else:
        amount = f"{(high if high is not None else low):,}"
    suffix = f" per {interval}" if interval else ""
    return f"{currency or 'IDR'} {amount}{suffix}"


def _job_url(company_code: str, job_id: str, slug: str) -> str:
    return f"{BASE}/c/{company_code}/jobs/{job_id}/{slug}"


def parse_listing_payload(
    payload: dict[str, Any], *, page: int = 1, platform: str = "kalibrr"
) -> list[RawListing]:
    rows = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(rows, list):
        raise SiteChangedError("Kalibrr: field jobs tidak ditemukan pada respons search")
    listings: list[RawListing] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        job_id = str(row.get("id") or "").strip()
        company = row.get("company") or row.get("company_info") or {}
        company_code = str(company.get("code") or "").strip()
        slug = str(row.get("slug") or "").strip()
        if not job_id or not company_code or not slug:
            continue
        listings.append(
            RawListing(
                platform=platform,
                url=_job_url(company_code, job_id, slug),
                external_id=job_id,
                title=(row.get("name") or "").strip(),
                company=row.get("company_name") or company.get("name"),
                location_raw=_location(
                    (row.get("google_location") or {}).get("address_components")
                ),
                posted_raw=row.get("activation_date"),
                extra={
                    "page": page,
                    "salary_raw": _salary_text(
                        row.get("salary_shown"),
                        row.get("minimum_salary"),
                        row.get("maximum_salary"),
                        row.get("salary_currency"),
                        row.get("salary_interval"),
                    ),
                    "work_mode_raw": _work_mode(
                        row.get("is_work_from_home"), row.get("is_hybrid")
                    ),
                    "employment_type_raw": row.get("tenure"),
                    "expires_raw": row.get("application_end_date"),
                    "function": row.get("function"),
                    "education_level": row.get("education_level"),
                    "work_experience": row.get("work_experience"),
                },
            )
        )
    return listings


def _next_data(html: str) -> dict[str, Any]:
    node = LexborHTMLParser(html).css_first("script#__NEXT_DATA__")
    if node is None:
        raise SiteChangedError("Kalibrr: #__NEXT_DATA__ tidak ditemukan")
    try:
        return json.loads(node.text())
    except ValueError as exc:
        raise SiteChangedError("Kalibrr: __NEXT_DATA__ bukan JSON") from exc


def _canonical(html: str) -> str | None:
    node = LexborHTMLParser(html).css_first('link[rel="canonical"]')
    href = node.attributes.get("href") if node is not None else None
    return href.split("?")[0] if href else None


def parse_detail_payload(
    payload: str | dict[str, Any], listing: RawListing, *, platform: str = "kalibrr"
) -> RawJob:
    if isinstance(payload, str):
        data = _next_data(payload)
        canonical = _canonical(payload)
    else:
        data = payload
        canonical = None
    try:
        if isinstance(data, dict) and "props" not in data:
            job = data
        else:
            job = data["props"]["pageProps"]["job"]
    except (KeyError, TypeError) as exc:
        raise SiteChangedError("Kalibrr: props.pageProps.job tidak ditemukan") from exc
    if not isinstance(job, dict) or not job.get("name"):
        raise SiteChangedError("Kalibrr: payload detail kosong")

    description_html = "\n".join(
        job[field]
        for field in DESCRIPTION_FIELDS
        if isinstance(job.get(field), str) and job[field].strip()
    )
    description_text = html_to_text(description_html)
    if not description_text:
        raise ParseError("Kalibrr: deskripsi kosong pada halaman detail", url=listing.url)

    company_info = job.get("companyInfo") or {}
    location = job.get("googleLocation") or {}
    return RawJob(
        platform=platform,
        url=canonical or listing.url.split("?")[0],
        external_id=str(job.get("id") or listing.external_id or ""),
        title=(job.get("name") or listing.title or "").strip(),
        company=company_info.get("name") or listing.company,
        location_raw=_location(location.get("addressComponents"))
        or location.get("formattedAddress")
        or listing.location_raw,
        posted_raw=job.get("activationDate") or listing.posted_raw,
        salary_raw=_salary_text(
            job.get("salaryShown"),
            job.get("minimumSalary"),
            job.get("maximumSalary"),
            job.get("salaryCurrency"),
            job.get("salaryInterval"),
        )
        or listing.extra.get("salary_raw"),
        work_mode_raw=_work_mode(job.get("isWorkFromHome"), job.get("isHybrid"))
        or listing.extra.get("work_mode_raw"),
        employment_type_raw=job.get("tenure")
        or listing.extra.get("employment_type_raw"),
        expires_raw=job.get("applicationEndDate") or listing.extra.get("expires_raw"),
        description_text=description_text,
        description_html=description_html or None,
        description_truncated=looks_truncated(description_text, len(description_html)),
        extra={
            "function": job.get("function"),
            "education_level": job.get("educationLevel"),
            "work_experience": job.get("workExperience"),
            "perks": job.get("perks"),
        },
    )


def _is_challenge(html: str, url: str) -> bool:
    return detect_challenge(html, url)


def _save_snapshot(html: str, run_id: str, reason: str) -> None:
    try:
        outdir = Path("data/debug") / run_id
        outdir.mkdir(parents=True, exist_ok=True)
        name = f"kalibrr_{int(time.time())}_{reason}.html"
        (outdir / name).write_text(html, encoding="utf-8")
    except OSError:
        pass


class KalibrrScraper(BaseScraper):
    platform = "kalibrr"
    requires_auth = False

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        self.delay_ms = config.get("delay_ms", [1500, 4000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 6)))
        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
            "Referer": f"{BASE}/id-ID/home",
        }

    async def _get(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        check_challenge: bool = False,
        **kwargs: Any,
    ) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.get(url, headers=self._headers, **kwargs)
            except httpx.HTTPError as exc:
                last_error = exc
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code in (403, 999):
                raise BlockedError("Kalibrr menolak akses (403/999)", url=str(response.url))
            if response.status_code == 429:
                await asyncio.sleep(60 if attempt >= 1 else 30)
                last_error = BlockedError("Kalibrr rate limit (429)", url=str(response.url))
                continue
            if response.status_code >= 500:
                last_error = TransientNetworkError(
                    f"Kalibrr HTTP {response.status_code}", url=str(response.url)
                )
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code != 200:
                raise SiteChangedError(
                    f"Kalibrr HTTP {response.status_code}", url=str(response.url)
                )
            if "cf-mitigated" in response.headers:
                raise BlockedError("Kalibrr menampilkan tantangan anti-bot", url=str(response.url))
            if check_challenge and _is_challenge(response.text, str(response.url)):
                raise BlockedError("Kalibrr menampilkan tantangan anti-bot", url=str(response.url))
            return response
        if isinstance(last_error, BlockedError):
            raise last_error
        raise TransientNetworkError(f"Kalibrr request gagal: {last_error}")

    async def _search(
        self, client: httpx.AsyncClient, term: str, offset: int
    ) -> dict[str, Any]:
        response = await self._get(
            client,
            SEARCH_API,
            params={
                "limit": PAGE_SIZE,
                "offset": offset,
                "text": term,
                "country": "Indonesia",
            },
        )
        try:
            payload = response.json()
        except ValueError as exc:
            _save_snapshot(response.text, self.ctx.run_id, "search_parse_error")
            if _is_challenge(response.text, str(response.url)):
                raise BlockedError(
                    "Kalibrr menampilkan tantangan anti-bot", url=str(response.url)
                ) from exc
            raise SiteChangedError("Kalibrr search bukan JSON", url=str(response.url)) from exc
        if not isinstance(payload, dict):
            raise SiteChangedError("Kalibrr search bukan objek JSON", url=str(response.url))
        return payload

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        yielded = 0
        offset = 0
        total: int | None = None
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            for page in range(1, self.max_pages + 1):
                if self.ctx.stop_requested or yielded >= self.ctx.max_jobs:
                    return
                if total is not None and offset >= total:
                    return
                payload = await self._search(client, search_term, offset)
                if total is None and isinstance(payload.get("count"), int):
                    total = payload["count"]
                rows = payload.get("jobs")
                page_size = len(rows) if isinstance(rows, list) else 0
                listings = parse_listing_payload(payload, page=page, platform=self.platform)
                if not listings:
                    return
                for listing in listings:
                    if self.ctx.stop_requested:
                        return
                    yield listing
                    yielded += 1
                    if yielded >= self.ctx.max_jobs:
                        return
                offset += page_size
                if page_size < PAGE_SIZE:
                    return
                await asyncio.sleep(jitter(self.delay_ms))

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            await asyncio.sleep(jitter(self.delay_ms))
            try:
                response = await self._get(client, listing.url, check_challenge=True)
            except (BlockedError, SiteChangedError, TransientNetworkError):
                raise
            except Exception as exc:
                raise ParseError(f"Kalibrr detail gagal: {exc}", url=listing.url) from exc
            try:
                return parse_detail_payload(response.text, listing, platform=self.platform)
            except (SiteChangedError, ParseError):
                _save_snapshot(response.text, self.ctx.run_id, "parse_error")
                raise
