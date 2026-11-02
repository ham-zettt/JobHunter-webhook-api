from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from typing import Any

import httpx
from selectolax.lexbor import LexborHTMLParser

from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.browser import detect_challenge, jitter, save_debug_snapshot
from app.scrapers.common.text import html_to_text, looks_truncated
from app.scrapers.exceptions import (
    BlockedError,
    ParseError,
    SiteChangedError,
    TransientNetworkError,
)

BASE = "https://id.jobstreet.com"
SEARCH_API = f"{BASE}/api/jobsearch/v5/search"
REDUX_MARKER = "window.SEEK_REDUX_DATA = "
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/156.0.0.0 Safari/537.36"
)
WORK_MODES = {
    "remote": "remote",
    "hibrid": "hybrid",
    "hybrid": "hybrid",
    "on-site": "onsite",
    "onsite": "onsite",
    "di kantor": "onsite",
}
EMPLOYMENT_TYPES = {
    "full time": "fulltime",
    "full-time": "fulltime",
    "penuh waktu": "fulltime",
    "part time": "parttime",
    "part-time": "parttime",
    "paruh waktu": "parttime",
    "contract/temp": "contract",
    "kontrak/temporer": "contract",
    "contract": "contract",
    "kontrak": "contract",
    "casual/vacation": "freelance",
    "internship": "internship",
    "magang": "internship",
}


def _extract_assignment(script: str, marker: str) -> dict[str, Any] | None:
    start = script.find(marker)
    if start < 0:
        return None
    index = start + len(marker)
    depth = 0
    in_string = False
    escaped = False
    for pos in range(index, len(script)):
        char = script[pos]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(script[index : pos + 1])
                except ValueError:
                    return None
    return None


def extract_redux_state(html: str) -> dict[str, Any] | None:
    tree = LexborHTMLParser(html)
    node = tree.css_first('script[data-automation="server-state"]')
    if node is None:
        return None
    return _extract_assignment(node.text(), REDUX_MARKER)


def _work_mode(value: str | None) -> str | None:
    if not value:
        return None
    return WORK_MODES.get(value.strip().lower())


def _employment_type(value: str | None) -> str | None:
    if not value:
        return None
    return EMPLOYMENT_TYPES.get(value.strip().lower())


def parse_search_payload(
    payload: dict[str, Any], *, page: int = 1, platform: str = "jobstreet"
) -> list[RawListing]:
    rows = payload.get("data")
    if not isinstance(rows, list):
        raise SiteChangedError("JobStreet: field data tidak ditemukan pada respons search")
    listings: list[RawListing] = []
    for row in rows:
        job_id = str(row.get("id") or "").strip()
        if not job_id:
            continue
        locations = row.get("locations") or []
        arrangements = (row.get("workArrangements") or {}).get("data") or []
        work_mode_label = arrangements[0].get("label", {}).get("text") if arrangements else None
        listings.append(
            RawListing(
                platform=platform,
                url=f"{BASE}/id/job/{job_id}",
                external_id=job_id,
                title=(row.get("title") or "").strip(),
                company=(
                    row.get("companyName") or (row.get("advertiser") or {}).get("description")
                ),
                location_raw=(locations[0].get("label") if locations else None),
                posted_raw=row.get("listingDate"),
                snippet=row.get("teaser"),
                extra={
                    "page": page,
                    "salary_raw": row.get("salaryLabel"),
                    "work_mode_raw": work_mode_label,
                    "employment_type_raw": ", ".join(row.get("workTypes") or []),
                    "listing_date_display": row.get("listingDateDisplay"),
                },
            )
        )
    return listings


def _dom_text(tree: LexborHTMLParser, automation: str) -> str | None:
    node = tree.css_first(f'[data-automation="{automation}"]')
    if node is None:
        return None
    text = node.text(separator="\n").strip()
    return text or None


def parse_detail_html(html: str, listing: RawListing, platform: str = "jobstreet") -> RawJob:
    state = extract_redux_state(html)
    tree = LexborHTMLParser(html)

    job = None
    if state is not None:
        try:
            result = state["jobdetails"]["result"]
            job = result["job"]
        except (KeyError, TypeError):
            job = None

    if job is not None:
        content_html = job.get("content2") or job.get("content") or ""
        text = html_to_text(content_html) or (_dom_text(tree, "jobAdDetails") or "")
        listed = job.get("listedAt") or {}
        work_label = (result.get("workArrangements") or {}).get("label")
        employment_label = (job.get("workTypes") or {}).get("label")
        salary_label = (job.get("salary") or {}).get("label")
        expires = job.get("expiresAt") or {}
        return RawJob(
            platform=platform,
            url=listing.url,
            external_id=str(job.get("id") or listing.external_id or ""),
            title=(job.get("title") or listing.title or "").strip(),
            company=((job.get("advertiser") or {}).get("name") or listing.company),
            location_raw=listing.location_raw or (job.get("location") or {}).get("label"),
            posted_raw=listed.get("dateTimeUtc") or listed.get("label") or listing.posted_raw,
            salary_raw=salary_label or listing.extra.get("salary_raw"),
            work_mode_raw=_work_mode(work_label) or _work_mode(listing.extra.get("work_mode_raw")),
            employment_type_raw=_employment_type(employment_label)
            or _employment_type(listing.extra.get("employment_type_raw")),
            expires_raw=expires.get("dateTimeUtc"),
            description_text=text,
            description_html=content_html or None,
            description_truncated=looks_truncated(text, len(content_html or "")),
            extra={
                "classifications": [
                    c.get("label") for c in (job.get("classifications") or []) if c.get("label")
                ],
                "abstract": job.get("abstract"),
                "is_expired": job.get("isExpired"),
            },
            raw_payload=None,
        )

    title = _dom_text(tree, "job-detail-title") or listing.title
    description_html = None
    node = tree.css_first('[data-automation="jobAdDetails"]')
    if node is not None:
        description_html = node.html or node.text(separator="\n")
    text = html_to_text(description_html)
    if not title or not text:
        raise SiteChangedError("JobStreet: halaman detail tidak memuat data yang dikenali")
    posted_match = re.search(r"(?:Diposting|Posted)\s+([^<\n]+)", html)
    return RawJob(
        platform=platform,
        url=listing.url,
        external_id=listing.external_id,
        title=title,
        company=_dom_text(tree, "advertiser-name") or listing.company,
        location_raw=listing.location_raw or _dom_text(tree, "job-detail-location"),
        posted_raw=posted_match.group(1).strip() if posted_match else listing.posted_raw,
        salary_raw=_dom_text(tree, "job-detail-salary") or listing.extra.get("salary_raw"),
        work_mode_raw=listing.extra.get("work_mode_raw"),
        employment_type_raw=_employment_type(_dom_text(tree, "job-detail-work-type"))
        or listing.extra.get("employment_type_raw"),
        description_text=text,
        description_html=description_html,
        description_truncated=looks_truncated(text, len(description_html or "")),
    )


class JobStreetScraper(BaseScraper):
    platform = "jobstreet"
    requires_auth = False

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        self.delay_ms = config.get("delay_ms", [1500, 4000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 8)))
        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
            "Referer": f"{BASE}/id/software-engineer-jobs",
        }

    async def _search_page(self, client: httpx.AsyncClient, term: str, page: int) -> dict[str, Any]:
        params = {
            "siteKey": "ID",
            "sourcesystem": "houston",
            "keywords": term,
            "page": page,
            "daterange": self.ctx.max_age_days,
            "sortmode": "ListedDate",
        }
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.get(SEARCH_API, params=params, headers=self._headers)
            except httpx.HTTPError as exc:
                last_error = exc
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code in (403, 999):
                raise BlockedError(
                    "JobStreet menolak akses (403/999) — hentikan platform", url=str(response.url)
                )
            if response.status_code == 429:
                await asyncio.sleep(60 if attempt >= 1 else 30)
                last_error = BlockedError("JobStreet rate limit (429)", url=str(response.url))
                continue
            if response.status_code >= 500:
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code != 200:
                raise SiteChangedError(
                    f"JobStreet search HTTP {response.status_code}", url=str(response.url)
                )
            try:
                return response.json()
            except ValueError as exc:
                raise SiteChangedError(
                    "JobStreet search bukan JSON", url=str(response.url)
                ) from exc
        if isinstance(last_error, BlockedError):
            raise last_error
        raise TransientNetworkError(f"JobStreet search gagal: {last_error}")

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        yielded = 0
        async with httpx.AsyncClient(timeout=30) as client:
            for page in range(1, self.max_pages + 1):
                if self.ctx.stop_requested or yielded >= self.ctx.max_jobs:
                    return
                payload = await self._search_page(client, search_term, page)
                listings = parse_search_payload(payload, page=page, platform=self.platform)
                if not listings:
                    return
                for listing in listings:
                    yield listing
                    yielded += 1
                    if yielded >= self.ctx.max_jobs:
                        return
                if len(listings) < 20:
                    return
                await asyncio.sleep(jitter(self.delay_ms))

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        if self.ctx.browser is None:
            raise SiteChangedError("JobStreet: BrowserPool tidak tersedia")
        page = await self.ctx.browser.new_page(self.platform)
        try:
            await asyncio.sleep(jitter(self.delay_ms))
            response = await page.goto(listing.url, wait_until="domcontentloaded")
            html = await page.content()
            if response is not None and response.status in (403, 429, 999):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "blocked")
                raise BlockedError(f"JobStreet detail HTTP {response.status}", url=listing.url)
            if detect_challenge(html, page.url):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "challenge")
                raise BlockedError("JobStreet menampilkan tantangan anti-bot", url=listing.url)
            return parse_detail_html(html, listing, platform=self.platform)
        except (BlockedError, SiteChangedError, ParseError):
            raise
        except Exception as exc:
            await save_debug_snapshot(page, self.ctx.run_id, self.platform, "parse_error")
            raise ParseError(f"JobStreet detail gagal: {exc}", url=listing.url) from exc
        finally:
            await page.close()
