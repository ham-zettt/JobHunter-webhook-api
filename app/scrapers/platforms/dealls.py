from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

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

BASE = "https://dealls.com"
API_BASE = "https://api.sejutacita.id"
SEARCH_API = f"{API_BASE}/v1/explore-job/job"
DETAIL_API = f"{API_BASE}/v1/job-portal/job/slug/{{slug}}"
PAGE_SIZE = 18
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/156.0.0.0 Safari/537.36"
)
WORK_MODES = {"onsite": "onsite", "hybrid": "hybrid", "remote": "remote"}
EMPLOYMENT_TYPES = {
    "fulltime": "fulltime",
    "parttime": "parttime",
    "internship": "internship",
    "contract": "contract",
    "freelance": "freelance",
}
DESCRIPTION_FIELDS = ("responsibilities", "requirements", "description")


def _work_mode(value: str | None) -> str | None:
    return WORK_MODES.get((value or "").strip().lower())


def _employment_type(values: Any) -> str | None:
    if not isinstance(values, list):
        return None
    mapped = [
        EMPLOYMENT_TYPES[value.strip().lower()]
        for value in values
        if isinstance(value, str) and value.strip().lower() in EMPLOYMENT_TYPES
    ]
    return ", ".join(mapped) or None


def _number(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def salary_text(salary_type: str | None, salary_range: Any) -> str | None:
    if salary_type and salary_type != "paid":
        return None
    if not isinstance(salary_range, dict):
        return None
    start = _number(salary_range.get("start"))
    end = _number(salary_range.get("end"))
    if start is None and end is None:
        return None
    low = start if start is not None else end
    high = end if end is not None else start
    if low == high:
        return f"IDR {low:,}"
    return f"IDR {low:,} - {high:,}"


def _full_slug(slug: str | None, company_slug: str | None = None) -> str:
    slug = (slug or "").strip().strip("/")
    if not slug or "~" in slug or not company_slug:
        return slug
    return f"{slug}~{company_slug}"


def canonical_url(slug: str | None, company_slug: str | None = None) -> str:
    full = _full_slug(slug, company_slug)
    return f"{BASE}/loker/{full}" if full else ""


def _clean_url(url: str) -> str:
    parts = urlsplit(url)
    path = parts.path
    if "/en/loker/" in path:
        path = path.replace("/en/loker/", "/loker/", 1)
    elif path.startswith("/en/"):
        path = path[3:]
    return urlunsplit(
        (parts.scheme or "https", parts.netloc or "dealls.com", path.rstrip("/"), "", "")
    )


def _next_data(html: str) -> dict[str, Any]:
    node = LexborHTMLParser(html).css_first("#__NEXT_DATA__")
    if node is None:
        raise SiteChangedError("Dealls: #__NEXT_DATA__ tidak ditemukan")
    try:
        return json.loads(node.text())
    except ValueError as exc:
        raise SiteChangedError("Dealls: __NEXT_DATA__ bukan JSON") from exc


def _canonical(html: str) -> str | None:
    node = LexborHTMLParser(html).css_first('link[rel="canonical"]')
    href = node.attributes.get("href") if node is not None else None
    return _clean_url(href) if href else None


def _json_ld_date(html: str) -> str | None:
    for node in LexborHTMLParser(html).css('script[type="application/ld+json"]'):
        try:
            data = json.loads(node.text())
        except ValueError:
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "JobPosting":
                return item.get("datePosted")
    return None


def _find(node: Any, key: str) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if isinstance(node.get(key), list):
            return node
        for value in node.values():
            found = _find(value, key)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find(value, key)
            if found is not None:
                return found
    return None


def _find_job(node: Any) -> dict[str, Any] | None:
    if isinstance(node, dict):
        if "role" in node and ("company" in node or "slug" in node):
            return node
        for value in node.values():
            found = _find_job(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for value in node:
            found = _find_job(value)
            if found is not None:
                return found
    return None


def _decode(payload: dict[str, Any] | str) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    try:
        data = json.loads(payload)
    except ValueError:
        data = _next_data(payload)
    if not isinstance(data, dict):
        raise SiteChangedError("Dealls: payload bukan objek JSON")
    return data


def parse_listing_payload(
    payload: dict[str, Any] | str, *, page: int = 1, platform: str = "dealls"
) -> list[RawListing]:
    data = _decode(payload)
    container = _find(data, "docs")
    if container is None:
        raise SiteChangedError("Dealls: field docs tidak ditemukan pada respons search")
    listings: list[RawListing] = []
    for row in container["docs"]:
        if not isinstance(row, dict):
            continue
        job_id = str(row.get("id") or "").strip()
        slug = str(row.get("slug") or "").strip()
        company = row.get("company") if isinstance(row.get("company"), dict) else {}
        company_slug = company.get("slug")
        url = canonical_url(slug, company_slug)
        if not url:
            continue
        city = row.get("city") if isinstance(row.get("city"), dict) else {}
        country = row.get("country") if isinstance(row.get("country"), dict) else {}
        listings.append(
            RawListing(
                platform=platform,
                url=url,
                external_id=job_id or _full_slug(slug, company_slug),
                title=(row.get("role") or "").strip(),
                company=company.get("name"),
                location_raw=city.get("name") or country.get("name"),
                posted_raw=row.get("publishedAt"),
                extra={
                    "page": page,
                    "api_slug": slug,
                    "salary_raw": salary_text(row.get("salaryType"), row.get("salaryRange")),
                    "work_mode_raw": _work_mode(row.get("workplaceType")),
                    "employment_type_raw": _employment_type(row.get("employmentTypes")),
                    "status": row.get("status"),
                },
            )
        )
    return listings


def _detail_job(data: dict[str, Any]) -> dict[str, Any]:
    inner = data.get("data")
    if isinstance(inner, dict) and isinstance(inner.get("result"), dict):
        return inner["result"]
    job = _find_job(data)
    if job is None:
        raise SiteChangedError("Dealls: payload detail tidak memuat data lowongan")
    return job


def parse_detail_payload(
    payload: dict[str, Any] | str,
    listing: RawListing | None = None,
    *,
    platform: str = "dealls",
) -> RawJob:
    canonical = None
    jsonld_date = None
    if isinstance(payload, str):
        stripped = payload.lstrip()
        if stripped.startswith("{"):
            try:
                data = json.loads(stripped)
            except ValueError as exc:
                raise SiteChangedError("Dealls: payload detail bukan JSON") from exc
            if not isinstance(data, dict):
                raise SiteChangedError("Dealls: payload detail bukan objek JSON")
        else:
            data = _next_data(stripped)
            canonical = _canonical(stripped)
            jsonld_date = _json_ld_date(stripped)
    else:
        data = payload

    job = _detail_job(data)
    company = job.get("company") if isinstance(job.get("company"), dict) else {}
    title = (job.get("role") or (listing.title if listing else "") or "").strip()
    if not title:
        raise SiteChangedError("Dealls: payload detail tanpa role")

    description_html = "\n".join(
        job[field]
        for field in DESCRIPTION_FIELDS
        if isinstance(job.get(field), str) and job[field].strip()
    )
    description_text = html_to_text(description_html)
    fallback_url = _clean_url(listing.url) if listing else ""
    url = canonical or canonical_url(job.get("slug"), company.get("slug")) or fallback_url
    if not description_text:
        raise ParseError("Dealls: deskripsi kosong pada detail", url=url)

    location = job.get("location") if isinstance(job.get("location"), dict) else {}
    city = location.get("city") if isinstance(location.get("city"), dict) else {}
    country = location.get("country") if isinstance(location.get("country"), dict) else {}
    extra = listing.extra if listing else {}

    return RawJob(
        platform=platform,
        url=url,
        external_id=str(job.get("id") or (listing.external_id if listing else "") or ""),
        title=title,
        company=company.get("name") or (listing.company if listing else None),
        location_raw=city.get("name")
        or country.get("name")
        or (listing.location_raw if listing else None),
        posted_raw=job.get("publishedAt")
        or jsonld_date
        or (listing.posted_raw if listing else None),
        salary_raw=salary_text(job.get("salaryType"), job.get("salaryRange"))
        or extra.get("salary_raw"),
        work_mode_raw=_work_mode(job.get("workplaceType")) or extra.get("work_mode_raw"),
        employment_type_raw=_employment_type(job.get("employmentTypes"))
        or extra.get("employment_type_raw"),
        description_text=description_text,
        description_html=description_html or None,
        description_truncated=looks_truncated(description_text, len(description_html)),
        extra={
            "job_role": (job.get("jobRole") or {}).get("name")
            if isinstance(job.get("jobRole"), dict)
            else None,
            "skills": [
                skill.get("name")
                for skill in (job.get("skills") or [])
                if isinstance(skill, dict) and skill.get("name")
            ],
        },
    )


def _save_snapshot(html: str, run_id: str, reason: str) -> None:
    try:
        outdir = Path("data/debug") / run_id
        outdir.mkdir(parents=True, exist_ok=True)
        name = f"dealls_{int(time.time())}_{reason}.html"
        (outdir / name).write_text(html, encoding="utf-8")
    except OSError:
        pass


class DeallsScraper(BaseScraper):
    platform = "dealls"
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
            "Referer": f"{BASE}/loker",
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
                raise BlockedError("Dealls menolak akses (403/999)", url=str(response.url))
            if response.status_code == 429:
                await asyncio.sleep(60 if attempt >= 1 else 30)
                last_error = BlockedError("Dealls rate limit (429)", url=str(response.url))
                continue
            if response.status_code >= 500:
                last_error = TransientNetworkError(
                    f"Dealls HTTP {response.status_code}", url=str(response.url)
                )
                await asyncio.sleep(2 * (2**attempt))
                continue
            if response.status_code != 200:
                raise SiteChangedError(
                    f"Dealls HTTP {response.status_code}", url=str(response.url)
                )
            if "cf-mitigated" in response.headers:
                raise BlockedError("Dealls menampilkan tantangan anti-bot", url=str(response.url))
            if check_challenge and detect_challenge(response.text, str(response.url)):
                raise BlockedError("Dealls menampilkan tantangan anti-bot", url=str(response.url))
            return response
        if isinstance(last_error, BlockedError):
            raise last_error
        raise TransientNetworkError(f"Dealls request gagal: {last_error}")

    async def _search(
        self, client: httpx.AsyncClient, term: str, page: int
    ) -> dict[str, Any]:
        response = await self._get(
            client,
            SEARCH_API,
            params={
                "page": page,
                "limit": PAGE_SIZE,
                "search": term,
                "sortParam": "publishedAt",
                "sortBy": "desc",
            },
        )
        try:
            payload = response.json()
        except ValueError as exc:
            _save_snapshot(response.text, self.ctx.run_id, "search_parse_error")
            if detect_challenge(response.text, str(response.url)):
                raise BlockedError(
                    "Dealls menampilkan tantangan anti-bot", url=str(response.url)
                ) from exc
            raise SiteChangedError("Dealls search bukan JSON", url=str(response.url)) from exc
        if not isinstance(payload, dict):
            raise SiteChangedError("Dealls search bukan objek JSON", url=str(response.url))
        return payload

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        yielded = 0
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
            for page in range(1, self.max_pages + 1):
                if self.ctx.stop_requested or yielded >= self.ctx.max_jobs:
                    return
                payload = await self._search(client, search_term, page)
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
                total_pages = (payload.get("data") or {}).get("totalPages")
                if isinstance(total_pages, int) and page >= total_pages:
                    return
                await asyncio.sleep(jitter(self.delay_ms))

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        await asyncio.sleep(jitter(self.delay_ms))
        async with httpx.AsyncClient(timeout=45, follow_redirects=True) as client:
            slug = str(listing.extra.get("api_slug") or "").strip()
            if slug:
                try:
                    response = await self._get(client, DETAIL_API.format(slug=slug))
                    return parse_detail_payload(
                        response.json(), listing, platform=self.platform
                    )
                except BlockedError:
                    raise
                except (SiteChangedError, TransientNetworkError, ValueError):
                    pass
            try:
                response = await self._get(client, listing.url, check_challenge=True)
            except (BlockedError, SiteChangedError, TransientNetworkError):
                raise
            except Exception as exc:
                raise ParseError(f"Dealls detail gagal: {exc}", url=listing.url) from exc
            try:
                return parse_detail_payload(response.text, listing, platform=self.platform)
            except (SiteChangedError, ParseError):
                _save_snapshot(response.text, self.ctx.run_id, "parse_error")
                raise
