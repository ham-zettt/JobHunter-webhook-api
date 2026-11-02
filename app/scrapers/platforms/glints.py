from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from html import escape
from typing import Any

import httpx
from selectolax.lexbor import LexborHTMLParser

from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.browser import detect_challenge, jitter
from app.scrapers.common.text import looks_truncated
from app.scrapers.exceptions import (
    BlockedError,
    ParseError,
    SiteChangedError,
    TransientNetworkError,
)

BASE = "https://glints.com"
SEARCH_URL = f"{BASE}/id/opportunities/jobs/explore"
DETAIL_URL = f"{BASE}/id/opportunities/jobs/{{slug}}/{{uuid}}"
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/156.0.0.0 Safari/537.36"
)
WORK_MODES = {"REMOTE": "remote", "HYBRID": "hybrid", "ONSITE": "onsite"}
EMPLOYMENT_TYPES = {
    "FULL_TIME": "fulltime",
    "PART_TIME": "parttime",
    "CONTRACT": "contract",
    "PROJECT_BASED": "contract",
    "FREELANCE": "freelance",
    "INTERNSHIP": "internship",
}
SALARY_PERIODS = {
    "MONTH": "per month",
    "YEAR": "per year",
    "DAY": "per day",
    "HOUR": "per hour",
    "WEEK": "per week",
    "PROJECT": "per project",
}
BLOCK_TYPES = {
    "unstyled": "p",
    "header-one": "h1",
    "header-two": "h2",
    "header-three": "h3",
    "unordered-list-item": "li",
    "ordered-list-item": "li",
    "blockquote": "blockquote",
}


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (title or "").lower()).strip("-")
    return slug or "job"


def job_url(title: str, job_id: str) -> str:
    return DETAIL_URL.format(slug=slugify(title), uuid=job_id)


def _next_data(html: str) -> dict[str, Any]:
    tree = LexborHTMLParser(html)
    node = tree.css_first("#__NEXT_DATA__")
    if node is None:
        raise SiteChangedError("Glints: #__NEXT_DATA__ tidak ditemukan")
    try:
        return json.loads(node.text())
    except ValueError as exc:
        raise SiteChangedError("Glints: __NEXT_DATA__ bukan JSON") from exc


def location_label(location: dict[str, Any] | None) -> str | None:
    if not location:
        return None
    parts = [location.get("formattedName") or location.get("name")]
    for parent in location.get("parents") or []:
        level = parent.get("administrativeLevelName")
        if level in ("Kota", "Kabupaten", "Province", "Country"):
            name = parent.get("formattedName") or parent.get("name")
            if name and name not in parts:
                parts.append(name)
    return ", ".join(part for part in parts if part) or None


def salary_text(
    salaries: list[dict[str, Any]] | None, should_show: bool | None = True
) -> str | None:
    if not salaries or should_show is False:
        return None
    salary = salaries[0]
    currency = salary.get("CurrencyCode") or "IDR"
    low = salary.get("minAmount")
    high = salary.get("maxAmount")
    unit = SALARY_PERIODS.get(str(salary.get("salaryMode") or "").upper(), "")
    if low is None and high is None:
        return None
    low = int(low) if low is not None else None
    high = int(high) if high is not None else None
    if low is not None and high is not None and low != high:
        amount = f"{low:,} - {high:,}"
    else:
        amount = f"{(high or low):,}"
    return f"{currency} {amount} {unit}".strip()


def draft_to_parts(raw: str | None) -> tuple[str, str]:
    if not raw:
        return "", ""
    try:
        blocks = json.loads(raw).get("blocks", [])
    except (ValueError, AttributeError):
        return "", ""
    lines: list[str] = []
    html_parts: list[str] = []
    for block in blocks:
        text = (block.get("text") or "").strip()
        if not text:
            continue
        block_type = block.get("type") or "unstyled"
        if block_type in ("unordered-list-item", "ordered-list-item"):
            lines.append(f"- {text}")
            html_parts.append(f"<li>{escape(text)}</li>")
        else:
            lines.append(text)
            tag = BLOCK_TYPES.get(block_type, "p")
            html_parts.append(f"<{tag}>{escape(text)}</{tag}>")
    return "\n".join(lines), "\n".join(html_parts)


def parse_search_html(html: str, *, platform: str = "glints") -> list[RawListing]:
    data = _next_data(html)
    try:
        jobs = data["props"]["pageProps"]["initialJobs"]["jobsInPage"]
    except (KeyError, TypeError) as exc:
        raise SiteChangedError("Glints: initialJobs tidak ditemukan pada halaman eksplor") from exc
    listings: list[RawListing] = []
    for job in jobs:
        job_id = str(job.get("id") or "").strip()
        if not job_id:
            continue
        location = job.get("location") or {}
        company = job.get("company") or {}
        salaries = job.get("salaries") or []
        listings.append(
            RawListing(
                platform=platform,
                url=job_url(job.get("title") or "", job_id),
                external_id=job_id,
                title=(job.get("title") or "").strip(),
                company=company.get("name") or company.get("brandName"),
                location_raw=location_label(location) or job.get("city"),
                posted_raw=job.get("createdAt"),
                snippet=None,
                extra={
                    "salary_raw": salary_text(salaries, job.get("shouldShowSalary")),
                    "work_mode_raw": WORK_MODES.get(job.get("workArrangementOption") or ""),
                    "employment_type_raw": EMPLOYMENT_TYPES.get(job.get("type") or ""),
                    "category": (job.get("hierarchicalJobCategory") or {}).get("name"),
                },
            )
        )
    return listings


def parse_detail_html(html: str, listing: RawListing, platform: str = "glints") -> RawJob:
    data = _next_data(html)
    try:
        payload = data["props"]["pageProps"]["initialData"]
        job = payload["data"]
    except (KeyError, TypeError) as exc:
        raise SiteChangedError("Glints: initialData detail tidak ditemukan") from exc
    if not isinstance(job, dict) or not job.get("title"):
        raise SiteChangedError("Glints: payload detail kosong")

    description_text, description_html = draft_to_parts(job.get("descriptionJsonString"))
    if not description_text:
        raise ParseError("Glints: deskripsi kosong pada halaman detail", url=listing.url)

    company = job.get("company") or {}
    location = job.get("location") or {}
    provinces = [
        parent.get("name")
        for parent in (location.get("parents") or [])
        if parent.get("administrativeLevelName") == "Province"
    ]
    loc_label = location_label(location) or listing.location_raw
    if not loc_label and provinces:
        loc_label = provinces[0]

    return RawJob(
        platform=platform,
        url=listing.url,
        external_id=str(job.get("id") or listing.external_id or ""),
        title=(job.get("title") or listing.title or "").strip(),
        company=company.get("displayName") or company.get("name") or listing.company,
        location_raw=loc_label,
        posted_raw=job.get("createdAt") or listing.posted_raw,
        salary_raw=salary_text(job.get("salaries"), job.get("shouldShowSalary"))
        or listing.extra.get("salary_raw"),
        work_mode_raw=WORK_MODES.get(job.get("workArrangementOption") or "")
        or listing.extra.get("work_mode_raw"),
        employment_type_raw=EMPLOYMENT_TYPES.get(job.get("type") or "")
        or listing.extra.get("employment_type_raw"),
        expires_raw=job.get("expiryDate") or job.get("endDate"),
        description_text=description_text,
        description_html=description_html,
        description_truncated=looks_truncated(description_text, len(description_html)),
        extra={
            "category": (job.get("hierarchicalJobCategory") or {}).get("name"),
            "skills": [
                (s.get("skill") or {}).get("name")
                for s in (job.get("JobSkills") or [])
                if s.get("skill")
            ],
            "benefits": [b.get("title") for b in (job.get("benefits") or []) if b.get("title")],
            "education_level": job.get("educationLevel"),
            "min_years_experience": job.get("minYearsOfExperience"),
        },
    )


class GlintsScraper(BaseScraper):
    platform = "glints"
    requires_auth = False

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        self.delay_ms = config.get("delay_ms", [1500, 4000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 6)))
        self._headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
        }

    async def _get(self, client: httpx.AsyncClient, url: str, **kwargs: Any) -> httpx.Response:
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.get(url, headers=self._headers, **kwargs)
            except httpx.HTTPError as exc:
                last_error = exc
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code in (403, 999):
                raise BlockedError(
                    "Glints menolak akses (403/999) — hentikan platform", url=str(response.url)
                )
            if response.status_code == 429:
                await asyncio.sleep(60 if attempt >= 1 else 30)
                last_error = BlockedError("Glints rate limit (429)", url=str(response.url))
                continue
            if response.status_code >= 500:
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code != 200:
                raise SiteChangedError(f"Glints HTTP {response.status_code}", url=str(response.url))
            if "cf-mitigated" in response.headers or detect_challenge(
                response.text[:60_000], str(response.url)
            ):
                raise BlockedError("Glints menampilkan tantangan anti-bot", url=str(response.url))
            return response
        if isinstance(last_error, BlockedError):
            raise last_error
        raise TransientNetworkError(f"Glints request gagal: {last_error}")

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            params = {"keyword": search_term, "country": "ID"}
            response = await self._get(client, SEARCH_URL, params=params)
            listings = parse_search_html(response.text, platform=self.platform)
            for index, listing in enumerate(listings):
                if self.ctx.stop_requested or index >= self.ctx.max_jobs:
                    return
                listing.extra["page"] = 1
                yield listing
                if index + 1 < len(listings):
                    await asyncio.sleep(jitter(self.delay_ms) / 4)
            # Pagination klien memerlukan token/JS yang ditantang Cloudflare; lihat
            # docs/platform_notes/glints.md. Cakupan ditambah lewat banyak search term.

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            await asyncio.sleep(jitter(self.delay_ms))
            try:
                response = await self._get(client, listing.url)
            except (BlockedError, SiteChangedError):
                raise
            except Exception as exc:
                raise ParseError(f"Glints detail gagal: {exc}", url=listing.url) from exc
            raw = parse_detail_html(response.text, listing, platform=self.platform)
            raw.url = str(response.url).split("?")[0]
            return raw
