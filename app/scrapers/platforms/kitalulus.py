from __future__ import annotations

import asyncio
import json
import re
from collections.abc import AsyncIterator
from typing import Any
from urllib.parse import urlencode

from playwright.async_api import Error as PlaywrightError
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

BASE = "https://www.kitalulus.com"
DETAIL_PATH = "/lowongan/detail/"
CARD_SELECTOR = 'a[href^="/lowongan/detail/"]'
EXPAND_TEXTS = (
    r"lihat selengkapnya",
    r"baca selengkapnya",
    r"selengkapnya",
    r"lebih banyak",
    r"show more",
    r"see more",
)
SALARY_PERIODS = {
    "MONTH": "per month",
    "YEAR": "per year",
    "DAY": "per day",
    "HOUR": "per hour",
    "WEEK": "per week",
}
EMPLOYMENT_TYPES = {
    "full-time": "fulltime",
    "full time": "fulltime",
    "penuh waktu": "fulltime",
    "part-time": "parttime",
    "part time": "parttime",
    "paruh waktu": "parttime",
    "kontrak": "contract",
    "contract": "contract",
    "contractor": "contract",
    "temporary": "contract",
    "freelance": "freelance",
    "lepas": "freelance",
    "magang": "internship",
    "intern": "internship",
    "internship": "internship",
}


def _flight_text(html: str) -> str:
    decoder = json.JSONDecoder()
    parts: list[str] = []
    for match in re.finditer(r"self\.__next_f\.push\(", html):
        start = html.find("[", match.end())
        if start < 0:
            continue
        try:
            payload, _ = decoder.raw_decode(html[start:])
        except ValueError:
            continue
        if isinstance(payload, list) and len(payload) > 1 and isinstance(payload[1], str):
            parts.append(payload[1])
    return "".join(parts)


def _json_object_at(text: str, key: str) -> dict[str, Any] | None:
    decoder = json.JSONDecoder()
    needle = f'"{key}":'
    pos = 0
    while True:
        found = text.find(needle, pos)
        if found < 0:
            return None
        start = text.find("{", found + len(needle))
        if start < 0:
            return None
        try:
            value, _ = decoder.raw_decode(text[start:])
        except ValueError:
            pos = found + len(needle)
            continue
        if isinstance(value, dict):
            return value
        pos = found + len(needle)


def _num(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _bounds_salary(low: Any, high: Any, period: str | None = None) -> str | None:
    low_n = _num(low) or 0
    high_n = _num(high) or 0
    if low_n <= 0 and high_n <= 0:
        return None
    low_n = low_n or high_n
    high_n = high_n or low_n
    amount = f"IDR {low_n:,}" if low_n == high_n else f"IDR {low_n:,} - {high_n:,}"
    return f"{amount} {period}".strip() if period else amount


def _salary_from_ld(ld: dict[str, Any]) -> str | None:
    base = ld.get("baseSalary")
    if not isinstance(base, dict):
        return None
    value = base.get("value") if isinstance(base.get("value"), dict) else {}
    period = SALARY_PERIODS.get(str(value.get("unitText") or "").upper())
    return _bounds_salary(value.get("minValue"), value.get("maxValue"), period)


def _location(city: Any, province: Any) -> str | None:
    parts = [part for part in (city, province) if part]
    return ", ".join(dict.fromkeys(parts)) or None


def _slug_from_href(href: str) -> str:
    path = href.split("?", 1)[0].rstrip("/")
    return path.rsplit("/", 1)[-1] if path else ""


def _work_mode(value: str | None) -> str | None:
    text = (value or "").lower()
    if "remote" in text or "wfh" in text or "dari manapun" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    if "wfo" in text or "kantor" in text:
        return "onsite"
    return None


def _employment_type(value: str | None) -> str | None:
    key = (value or "").strip().lower().replace("_", "-")
    return EMPLOYMENT_TYPES.get(key)


def _dom_listings(tree: LexborHTMLParser, platform: str) -> list[RawListing]:
    listings: list[RawListing] = []
    seen: set[str] = set()
    for card in tree.css(CARD_SELECTOR):
        slug = _slug_from_href(card.attributes.get("href") or "")
        if not slug or slug in seen:
            continue
        seen.add(slug)
        titles = [
            (p.attributes.get("title") or "").strip()
            for p in card.css("p[title]")
            if p.attributes.get("title")
        ]
        heading = card.css_first("h3")
        text = card.text(separator="\n") or ""
        updated = re.search(r"Terakhir diperbarui[^\n]*", text)
        listings.append(
            RawListing(
                platform=platform,
                url=f"{BASE}{DETAIL_PATH}{slug}",
                external_id=slug,
                title=(heading.text() if heading else "").strip(),
                company=titles[0] if titles else None,
                location_raw=titles[1] if len(titles) > 1 else None,
                posted_raw=None,
                extra={
                    "pendidikan": titles[2] if len(titles) > 2 else None,
                    "salary_raw": titles[3] if len(titles) > 3 else None,
                    "updated_at_str": updated.group(0).strip() if updated else None,
                    "promoted": "Dipromosikan" in text,
                },
            )
        )
    return listings


def _flight_listings(flight: str, platform: str) -> list[RawListing]:
    payload = _json_object_at(flight, "vacancyList")
    rows = payload.get("list") if payload else None
    if not isinstance(rows, list):
        return []
    listings: list[RawListing] = []
    for row in rows:
        slug = str(row.get("slug") or "").strip()
        if not slug:
            continue
        company = row.get("company") or {}
        listings.append(
            RawListing(
                platform=platform,
                url=f"{BASE}{DETAIL_PATH}{slug}",
                external_id=slug,
                title=(row.get("positionName") or "").strip(),
                company=company.get("name"),
                location_raw=_location(
                    (row.get("city") or {}).get("name"),
                    (row.get("province") or {}).get("name"),
                ),
                posted_raw=None,
                extra={
                    "pendidikan": row.get("educationLevelStr"),
                    "salary_raw": _bounds_salary(
                        row.get("salaryLowerBound"), row.get("salaryUpperBound")
                    ),
                    "updated_at_str": row.get("updatedAtStr"),
                    "promoted": row.get("isHighlighted"),
                    "kategori": (row.get("jobRole") or {}).get("displayName"),
                    "employment_type_raw": row.get("typeStr"),
                },
            )
        )
    return listings


def parse_listing_payload(html: str, *, platform: str = "kitalulus") -> list[RawListing]:
    tree = LexborHTMLParser(html)
    listings = _dom_listings(tree, platform)
    if not listings:
        listings = _flight_listings(_flight_text(html), platform)
    if not listings:
        raise SiteChangedError("KitaLulus: daftar lowongan tidak dikenali")
    return listings


def _ld_jobposting(tree: LexborHTMLParser) -> dict[str, Any] | None:
    for node in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(node.text())
        except ValueError:
            continue
        if isinstance(data, dict) and data.get("@type") == "JobPosting":
            return data
    return None


def _canonical_slug(tree: LexborHTMLParser) -> str:
    node = tree.css_first('link[rel="canonical"]')
    href = node.attributes.get("href") if node else ""
    return _slug_from_href(href or "")


def _dom_description(tree: LexborHTMLParser) -> str | None:
    node = tree.css_first(".html-content")
    if node is None:
        return None
    return node.html or node.text(separator="\n") or None


def parse_detail_payload(html: str, *, platform: str = "kitalulus") -> RawJob:
    tree = LexborHTMLParser(html)
    ld = _ld_jobposting(tree)
    flight = _flight_text(html)
    vacancy = _json_object_at(flight, "vacancy") or {}
    slug = str(vacancy.get("slug") or "").strip() or _canonical_slug(tree)
    if ld is None and not vacancy:
        raise SiteChangedError("KitaLulus: halaman detail tidak memuat JobPosting")

    title = (ld.get("title") if ld else None) or vacancy.get("positionName") or ""
    description_html = (ld.get("description") if ld else None) or vacancy.get(
        "formattedDescription"
    )
    if not isinstance(description_html, str) or description_html.startswith("$"):
        description_html = _dom_description(tree)
    description_text = html_to_text(description_html)
    if not str(title).strip() or not description_text:
        raise ParseError("KitaLulus: judul/deskripsi detail kosong")

    experience = (ld.get("experienceRequirements") if ld else None) or {}
    education = (ld.get("educationRequirements") if ld else None) or {}
    address = ((ld.get("jobLocation") if ld else None) or {}).get("address") or {}
    location = _location(
        (vacancy.get("city") or {}).get("name") or address.get("addressLocality"),
        (vacancy.get("province") or {}).get("name") or address.get("addressRegion"),
    )
    benefits = vacancy.get("benefits")
    skills = vacancy.get("skillTags")

    return RawJob(
        platform=platform,
        url=f"{BASE}{DETAIL_PATH}{slug}" if slug else f"{BASE}{DETAIL_PATH}",
        external_id=slug or None,
        title=str(title).strip(),
        company=((ld.get("hiringOrganization") if ld else None) or {}).get("name")
        or (vacancy.get("company") or {}).get("name"),
        location_raw=location,
        posted_raw=ld.get("datePosted") if ld else None,
        salary_raw=_salary_from_ld(ld or {})
        or _bounds_salary(vacancy.get("salaryLowerBound"), vacancy.get("salaryUpperBound")),
        work_mode_raw=_work_mode(vacancy.get("locationSiteStr")),
        employment_type_raw=_employment_type(vacancy.get("typeStr"))
        or _employment_type(ld.get("employmentType") if ld else None),
        expires_raw=ld.get("validThrough") if ld else None,
        description_text=description_text,
        description_html=description_html,
        description_truncated=looks_truncated(description_text, len(description_html or "")),
        extra={
            "pendidikan": vacancy.get("educationLevelStr") or education.get("credentialCategory"),
            "pengalaman_bulan": experience.get("monthsOfExperience"),
            "skill": skills if isinstance(skills, list) else None,
            "benefit": [
                item.get("copy")
                for item in (benefits or [])
                if isinstance(item, dict) and item.get("copy")
            ]
            or None,
            "kategori": (vacancy.get("jobRole") or {}).get("displayName"),
            "promoted": vacancy.get("isHighlighted"),
        },
        raw_payload=None,
    )


async def _expand_description(page: Any) -> None:
    for _ in range(3):
        clicked = False
        for pattern in EXPAND_TEXTS:
            locator = page.get_by_role("button", name=re.compile(pattern, re.I))
            count = await locator.count()
            for index in range(min(count, 5)):
                try:
                    await locator.nth(index).click(timeout=1500)
                    clicked = True
                except Exception:
                    pass
        if not clicked:
            break
        await asyncio.sleep(0.3)
    previous = None
    for _ in range(3):
        node = await page.query_selector(".html-content")
        current = (await node.inner_text()) if node else ""
        if current == previous:
            break
        previous = current
        await asyncio.sleep(0.3)


async def _card_count(page: Any) -> int:
    return len(await page.query_selector_all(CARD_SELECTOR))


class KitaLulusScraper(BaseScraper):
    platform = "kitalulus"
    requires_auth = False

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        self.delay_ms = config.get("delay_ms", [2000, 5000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 6)))

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        if self.ctx.browser is None:
            raise SiteChangedError("KitaLulus: BrowserPool tidak tersedia")
        page = await self.ctx.browser.new_page(self.platform)
        url = f"{BASE}/lowongan?{urlencode({'sortBy': 'updatedAt', 'keyword': search_term})}"
        try:
            await asyncio.sleep(jitter(self.delay_ms) / 2)
            try:
                response = await page.goto(url, wait_until="domcontentloaded")
            except PlaywrightError as exc:
                raise TransientNetworkError(
                    f"KitaLulus: navigasi gagal: {exc}", url=url
                ) from exc
            html = await page.content()
            if response is not None and response.status in (403, 429):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "blocked")
                raise BlockedError(f"KitaLulus HTTP {response.status}", url=url)
            if detect_challenge(html, page.url):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "challenge")
                raise BlockedError("KitaLulus menampilkan tantangan anti-bot", url=url)

            seen: set[str] = set()
            yielded = 0
            page_index = 0
            while page_index < self.max_pages:
                if self.ctx.stop_requested or yielded >= self.ctx.max_jobs:
                    return
                listings = parse_listing_payload(await page.content(), platform=self.platform)
                fresh = [item for item in listings if item.external_id not in seen]
                if not fresh:
                    return
                for listing in fresh:
                    seen.add(listing.external_id or "")
                    listing.extra["page"] = page_index + 1
                    yield listing
                    yielded += 1
                    if yielded >= self.ctx.max_jobs:
                        return
                page_index += 1
                if page_index >= self.max_pages:
                    return
                button = page.get_by_role("button", name=re.compile(r"Lebih Banyak", re.I))
                if await button.count() == 0:
                    return
                before = await _card_count(page)
                await asyncio.sleep(jitter(self.delay_ms))
                try:
                    await button.first.click(timeout=5000)
                except Exception:
                    return
                for _ in range(20):
                    await asyncio.sleep(0.25)
                    if await _card_count(page) > before:
                        break
                else:
                    return
        finally:
            await page.close()

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        if self.ctx.browser is None:
            raise SiteChangedError("KitaLulus: BrowserPool tidak tersedia")
        page = await self.ctx.browser.new_page(self.platform)
        try:
            await asyncio.sleep(jitter(self.delay_ms))
            try:
                response = await page.goto(listing.url, wait_until="domcontentloaded")
            except PlaywrightError as exc:
                raise TransientNetworkError(
                    f"KitaLulus: navigasi gagal: {exc}", url=listing.url
                ) from exc
            if response is not None and response.status in (403, 429):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "blocked")
                raise BlockedError(f"KitaLulus detail HTTP {response.status}", url=listing.url)
            html = await page.content()
            if detect_challenge(html, page.url):
                await save_debug_snapshot(page, self.ctx.run_id, self.platform, "challenge")
                raise BlockedError("KitaLulus menampilkan tantangan anti-bot", url=listing.url)
            await _expand_description(page)
            return parse_detail_payload(await page.content(), platform=self.platform)
        except (BlockedError, SiteChangedError, ParseError, TransientNetworkError):
            raise
        except Exception as exc:
            await save_debug_snapshot(page, self.ctx.run_id, self.platform, "parse_error")
            raise ParseError(f"KitaLulus detail gagal: {exc}", url=listing.url) from exc
        finally:
            await page.close()
