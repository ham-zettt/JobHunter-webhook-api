from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from html import escape
from typing import Any

from selectolax.lexbor import LexborHTMLParser

from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.browser import detect_challenge, jitter, save_debug_snapshot
from app.scrapers.common.text import clean_text, looks_truncated
from app.scrapers.exceptions import (
    BlockedError,
    ParseError,
    ScraperError,
    SiteChangedError,
    TransientNetworkError,
)

BASE = "https://pintarnya.com"
API_URL = "https://api.pintarnya.com/api/v2/pk/job"
DETAIL_URL = f"{BASE}/lowongan/{{slug}}"
SEARCH_URL = f"{BASE}/q-{{term}}-lowongan"
PAGE_SIZE = 10
WORK_MODES = {
    "onsite": "onsite",
    "on-site": "onsite",
    "hybrid": "hybrid",
    "remote": "remote",
    "wfh": "remote",
}
EMPLOYMENT_TYPES = {
    "full-time": "fulltime",
    "full time": "fulltime",
    "fulltime": "fulltime",
    "part-time": "parttime",
    "part time": "parttime",
    "parttime": "parttime",
    "contract": "contract",
    "temporary": "contract",
    "internship": "internship",
    "freelance": "freelance",
}
SALARY_PERIODS = {"MONTH": "per month", "YEAR": "per year", "DAY": "per day", "HOUR": "per hour"}
_SCRIPT_STYLE_RE = re.compile(r"(?is)<(script|style)[^>]*>.*?</\1>")


def search_slug(term: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", (term or "").lower()).strip("-") or "lowongan"


def canonical_url(slug: str | None) -> str:
    return DETAIL_URL.format(slug=slug) if slug else ""


def _work_mode(value: str | None) -> str | None:
    return WORK_MODES.get((value or "").strip().lower())


def _employment_type(values: Any) -> str | None:
    if isinstance(values, str):
        values = [values]
    if not isinstance(values, list):
        return None
    mapped: list[str] = []
    for value in values:
        name = value.get("name") if isinstance(value, dict) else value
        key = str(name or "").strip().lower().replace("_", "-")
        mapped_type = EMPLOYMENT_TYPES.get(key)
        if mapped_type and mapped_type not in mapped:
            mapped.append(mapped_type)
    return ", ".join(mapped) or None


def _number(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def salary_text(
    low: Any, high: Any, *, currency: str = "IDR", unit: str = "MONTH"
) -> str | None:
    low_number = _number(low)
    high_number = _number(high)
    if low_number is None and high_number is None:
        return None
    if low_number is None:
        low_number = high_number
    if high_number is None:
        high_number = low_number
    amount = (
        f"{low_number:,} - {high_number:,}" if low_number != high_number else f"{low_number:,}"
    )
    period = SALARY_PERIODS.get((unit or "MONTH").upper(), "per month")
    return f"{currency} {amount} {period}"


def _location(city: Any, province: Any) -> str | None:
    parts = [
        part
        for part in (city, province)
        if isinstance(part, str) and part.strip()
    ]
    return ", ".join(parts) or None


def _items(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        rows = payload
    elif isinstance(payload, dict):
        container = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        rows = container.get("list") or container.get("initialJobList") or []
    else:
        rows = []
    jobs: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        sublist = row.get("sublist")
        job = sublist[0] if isinstance(sublist, list) and sublist else row
        if isinstance(job, dict):
            jobs.append(job)
    return jobs


def parse_list_payload(
    payload: Any, *, page: int = 1, platform: str = "pintarnya"
) -> list[RawListing]:
    listings: list[RawListing] = []
    for job in _items(payload):
        slug = str(job.get("slug") or "").strip()
        if not slug:
            continue
        city = job.get("city") if isinstance(job.get("city"), dict) else {}
        province = job.get("province") if isinstance(job.get("province"), dict) else {}
        employer = job.get("employer") if isinstance(job.get("employer"), dict) else {}
        education = (
            job.get("min_education_level")
            if isinstance(job.get("min_education_level"), dict)
            else {}
        )
        listings.append(
            RawListing(
                platform=platform,
                url=canonical_url(slug),
                external_id=slug,
                title=(job.get("title") or "").strip(),
                company=employer.get("name"),
                location_raw=_location(city.get("name"), province.get("name")),
                posted_raw=job.get("published_at"),
                extra={
                    "page": page,
                    "salary_raw": salary_text(job.get("min_salary"), job.get("max_salary")),
                    "work_mode_raw": _work_mode(
                        (job.get("type_of_work") or {}).get("name")
                        if isinstance(job.get("type_of_work"), dict)
                        else None
                    ),
                    "employment_type_raw": _employment_type(job.get("type_of_employments")),
                    "expires_raw": job.get("expired_at"),
                    "category_id": job.get("job_category_id"),
                    "education": education.get("name"),
                    "experience_years": job.get("years_of_experience"),
                    "promoted": bool(job.get("is_promoted") or job.get("is_highlighted")),
                },
            )
        )
    return listings


def total_pages(payload: Any) -> int:
    if not isinstance(payload, dict):
        return 1
    container = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    pagination = container.get("pagination") if isinstance(container, dict) else None
    if not isinstance(pagination, dict):
        return 1
    try:
        return max(1, int(pagination.get("total_page") or 1))
    except (TypeError, ValueError):
        return 1


def _next_data(html: str) -> dict[str, Any]:
    node = LexborHTMLParser(html).css_first("#__NEXT_DATA__")
    if node is None:
        return {}
    try:
        data = json.loads(node.text())
    except ValueError:
        return {}
    return data if isinstance(data, dict) else {}


def _job_ld(html: str) -> dict[str, Any]:
    tree = LexborHTMLParser(html)
    for node in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(node.text())
        except ValueError:
            continue
        candidates = data if isinstance(data, list) else [data]
        for candidate in candidates:
            if isinstance(candidate, dict) and candidate.get("@type") == "JobPosting":
                return candidate
    raise SiteChangedError("Pintarnya: JSON-LD JobPosting tidak ditemukan")


def _page_header(html: str) -> dict[str, Any]:
    props = _next_data(html).get("props", {})
    job_data = (props.get("pageProps") or {}).get("jobData") or {}
    header = job_data.get("page_header") if isinstance(job_data, dict) else None
    return header if isinstance(header, dict) else {}


def _ssr_payload(html: str, page: int = 1) -> dict[str, Any]:
    props = _next_data(html).get("props", {})
    jobs = (props.get("pageProps") or {}).get("initialJobList") or []
    return {
        "list": [{"sublist": [job]} for job in jobs if isinstance(job, dict)],
        "pagination": {"page": page, "total_page": page},
    }


def _description_html(text: str) -> str:
    paragraphs = [escape(part.strip()) for part in re.split(r"\n\s*\n", text) if part.strip()]
    return "\n".join(f"<p>{part.replace(chr(10), '<br>')}</p>" for part in paragraphs)


def parse_detail_payload(
    payload: dict[str, Any] | str,
    listing: RawListing | None = None,
    *,
    platform: str = "pintarnya",
) -> RawJob:
    if isinstance(payload, dict):
        ld = payload.get("json_ld") or {}
        header = payload.get("page_header") or {}
        fallback_url = payload.get("url")
    else:
        ld = _job_ld(payload)
        header = _page_header(payload)
        fallback_url = None

    title = str(ld.get("title") or header.get("title") or (listing.title if listing else ""))
    description_text = clean_text(str(ld.get("description") or ""))
    description_html = _description_html(description_text)
    if not description_text:
        raise ParseError("Pintarnya: deskripsi kosong pada halaman detail")

    values = ld.get("baseSalary") or {}
    unit = ((values.get("value") or {}).get("unitText") if isinstance(values, dict) else None) or ""
    salary = salary_text(
        (values.get("value") or {}).get("minValue") if isinstance(values, dict) else None,
        (values.get("value") or {}).get("maxValue") if isinstance(values, dict) else None,
        currency=values.get("currency") or "IDR" if isinstance(values, dict) else "IDR",
        unit=unit or "MONTH",
    )
    address = ((ld.get("jobLocation") or {}).get("address") or {}) if isinstance(
        ld.get("jobLocation"), dict
    ) else {}
    location = _location(
        header.get("city") or address.get("addressLocality"),
        header.get("district") or address.get("addressRegion"),
    ) or (listing.location_raw if listing else None)
    company = (ld.get("hiringOrganization") or {}).get("name") if isinstance(
        ld.get("hiringOrganization"), dict
    ) else None
    extra_listing = listing.extra if listing else {}
    url = str(fallback_url or (listing.url if listing else "")).split("?")[0]

    return RawJob(
        platform=platform,
        url=url,
        external_id=(listing.external_id if listing else None) or None,
        title=title.strip(),
        company=company or (listing.company if listing else None),
        location_raw=location,
        posted_raw=ld.get("datePosted") or (listing.posted_raw if listing else None),
        salary_raw=salary or extra_listing.get("salary_raw"),
        work_mode_raw=_work_mode(header.get("type_of_work"))
        or extra_listing.get("work_mode_raw"),
        employment_type_raw=_employment_type(
            ld.get("employmentType") or header.get("type_of_employments")
        )
        or extra_listing.get("employment_type_raw"),
        expires_raw=ld.get("validThrough") or extra_listing.get("expires_raw"),
        description_text=description_text,
        description_html=description_html,
        description_truncated=looks_truncated(description_text, len(description_html)),
        extra={
            "kategori": header.get("job_category") or extra_listing.get("category_id"),
            "pendidikan": extra_listing.get("education"),
            "pengalaman_tahun": extra_listing.get("experience_years"),
            "promoted": bool(header.get("is_highlighted") or extra_listing.get("promoted")),
        },
    )


def _is_challenge(html: str, url: str) -> bool:
    cleaned = _SCRIPT_STYLE_RE.sub("", html or "")
    return detect_challenge(cleaned, url)


class PintarnyaScraper(BaseScraper):
    platform = "pintarnya"
    requires_auth = False

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        self.delay_ms = config.get("delay_ms", [2000, 5000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 5)))
        self._page = None
        self._current_term: str | None = None

    async def _page_for(self, term: str):
        if self.ctx.browser is None:
            raise SiteChangedError("Pintarnya: browser pool tidak tersedia")
        context = await self.ctx.browser.context(self.platform)
        if self._page is None:
            self._page = await context.new_page()
        if self._current_term != term:
            url = SEARCH_URL.format(term=search_slug(term))
            await self._page.goto(url, wait_until="domcontentloaded")
            if _is_challenge(await self._page.content(), self._page.url):
                raise BlockedError("Pintarnya menampilkan tantangan anti-bot", url=url)
            self._current_term = term
        return context

    async def _search(self, term: str, page: int) -> dict[str, Any]:
        context = await self._page_for(term)
        params = {
            "city_id": -1,
            "province_id": -1,
            "search": term,
            "sort": "-published_at",
            "page": page,
            "page_size": PAGE_SIZE,
        }
        response = await context.request.get(API_URL, params=params)
        if response.status in (401, 403):
            raise BlockedError(
                f"Pintarnya menolak akses API ({response.status})", url=API_URL
            )
        if response.status == 429:
            raise TransientNetworkError("Pintarnya rate limit (429)", url=API_URL)
        if response.status == 410:
            return _ssr_payload(await self._page.content(), page)
        if response.status >= 500:
            raise TransientNetworkError(f"Pintarnya HTTP {response.status}", url=API_URL)
        if response.status != 200:
            raise SiteChangedError(f"Pintarnya HTTP {response.status}", url=API_URL)
        try:
            data = await response.json()
        except ValueError as exc:
            raise SiteChangedError("Pintarnya: respons API bukan JSON") from exc
        if not isinstance(data, dict):
            raise SiteChangedError("Pintarnya: respons API bukan objek JSON")
        return data

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        seen: set[str] = set()
        for page in range(1, self.max_pages + 1):
            payload = await self._search(search_term, page)
            listings = parse_list_payload(payload, page=page, platform=self.platform)
            if not listings:
                return
            for listing in listings:
                key = listing.external_id or listing.url
                if key in seen:
                    continue
                seen.add(key)
                if self.ctx.stop_requested:
                    return
                if len(seen) > self.ctx.max_jobs:
                    return
                yield listing
            if page >= total_pages(payload):
                return
            await asyncio.sleep(jitter(self.delay_ms))

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        if self.ctx.browser is None:
            raise ScraperError("Pintarnya: browser pool tidak tersedia", url=listing.url)
        context = await self.ctx.browser.context(self.platform)
        page = await context.new_page()
        await asyncio.sleep(jitter(self.delay_ms))
        try:
            await page.goto(listing.url, wait_until="domcontentloaded")
            html = await page.content()
            if _is_challenge(html, page.url):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "blocked")
                raise BlockedError("Pintarnya menampilkan tantangan anti-bot", url=listing.url)
            return parse_detail_payload(html, listing, platform=self.platform)
        except (BlockedError, SiteChangedError, ParseError):
            raise
        except Exception as exc:
            await save_debug_snapshot(page, self.ctx.run_id, self.platform, "parse")
            raise ParseError(f"Pintarnya detail gagal: {exc}", url=listing.url) from exc
        finally:
            await page.close()
