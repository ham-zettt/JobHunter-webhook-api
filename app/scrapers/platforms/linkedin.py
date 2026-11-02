from __future__ import annotations

import asyncio
import re
from collections.abc import AsyncIterator
from pathlib import Path
from urllib.parse import urlencode

from selectolax.lexbor import LexborHTMLParser

from app.core.config import get_settings
from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.browser import detect_challenge, jitter, save_debug_snapshot
from app.scrapers.common.text import html_to_text, looks_truncated
from app.scrapers.exceptions import (
    AuthRequiredError,
    BlockedError,
    ParseError,
    SiteChangedError,
)

BASE = "https://www.linkedin.com"
JOBS_HOME = f"{BASE}/jobs/"
SEARCH_URL = f"{BASE}/jobs/search-results/"
DETAIL_URL = f"{BASE}/jobs/view/{{job_id}}"
AUTH_MESSAGE = "LinkedIn: sesi tidak valid. Jalankan scripts/linkedin_login.py"
CARD_SELECTOR = '[componentkey^="job-card-component-ref-"]'
DESC_BOX = '[data-testid="expandable-text-box"]'
EXPAND_BUTTON = '[data-testid="expandable-text-button"]'
ABOUT_JOB = ("Tentang pekerjaan ini", "About the job")
AUTH_URL_MARKERS = ("/login", "/checkpoint", "/authwall", "/uas/", "/signup")
NO_RESULTS_MARKERS = (
    "tidak ada lowongan",
    "tidak menemukan lowongan",
    "no matching jobs",
    "no results",
    "belum ada lowongan",
)
WORK_MODES = {
    "di kantor": "onsite",
    "di tempat": "onsite",
    "on-site": "onsite",
    "onsite": "onsite",
    "on site": "onsite",
    "jarak jauh": "remote",
    "remote": "remote",
    "hybrid": "hybrid",
    "hibrida": "hybrid",
    "gabungan": "hybrid",
}
EMPLOYMENT_TYPES = {
    "penuh waktu": "fulltime",
    "full-time": "fulltime",
    "full time": "fulltime",
    "paruh waktu": "parttime",
    "part-time": "parttime",
    "part time": "parttime",
    "kontrak": "contract",
    "contract": "contract",
    "temporary": "contract",
    "magang": "internship",
    "internship": "internship",
    "freelance": "freelance",
}
_TPR = ((1, "r86400"), (7, "r604800"), (30, "r2592000"))
_TIME_RE = re.compile(
    r"(lalu|ago|baru saja|just now|hari ini|today|minggu|bulan|jam|menit|"
    r"hour|minute|week|month|day)",
    re.I,
)
_SALARY_RE = re.compile(
    r"(?:rp|idr|\$|sgd|usd|myr)\s?[\d.,]+\s*[mkjtb]?\s*(?:/|per\s)\s*"
    r"(?:month|bulan|bln|year|tahun|hour|jam|day|hari|week|minggu)",
    re.I,
)


def search_url(term: str, max_age_days: int, *, start: int = 0, remote: bool = False) -> str:
    params = {
        "keywords": term,
        "location": "Indonesia",
        "f_TPR": _tpr(max_age_days),
        "sortBy": "DD",
        "start": start,
    }
    if remote:
        params["f_WT"] = "2"
    return f"{SEARCH_URL}?{urlencode(params)}"


def _tpr(max_age_days: int) -> str:
    for days, value in _TPR:
        if max_age_days <= days:
            return value
    return _TPR[-1][1]


def _work_mode(text: str | None) -> str | None:
    if not text:
        return None
    return WORK_MODES.get(text.strip().lower())


def _work_mode_from_card(text: str | None) -> str | None:
    if not text:
        return None
    match = re.search(r"\(([^)]+)\)", text)
    return _work_mode(match.group(1)) if match else None


def _inside_about_company(node) -> bool:
    parent = node.parent
    while parent is not None:
        if (parent.attributes.get("id") or "").startswith("JobDetails_AboutTheCompany_"):
            return True
        parent = parent.parent
    return False


def parse_listing_payload(
    html: str, *, page: int = 1, platform: str = "linkedin"
) -> list[RawListing]:
    tree = LexborHTMLParser(html)
    seen: set[str] = set()
    listings: list[RawListing] = []
    for card in tree.css(CARD_SELECTOR):
        key = card.attributes.get("componentkey") or ""
        job_id = key.rsplit("-", 1)[-1]
        if not job_id.isdigit() or job_id in seen:
            continue
        seen.add(job_id)

        spans = [s.text().strip() for s in card.css('span[aria-hidden="true"]')]
        spans = [text for text in spans if text]
        paragraphs = [p.text().strip() for p in card.css("p") if p.text().strip()]
        title = spans[0] if spans else (paragraphs[0] if paragraphs else "")
        company = paragraphs[1] if len(paragraphs) > 1 else None
        location = paragraphs[2] if len(paragraphs) > 2 else None
        posted = next((text for text in spans[1:] if _TIME_RE.search(text)), None)
        listings.append(
            RawListing(
                platform=platform,
                url=DETAIL_URL.format(job_id=job_id),
                external_id=job_id,
                title=title,
                company=company,
                location_raw=location,
                posted_raw=posted,
                extra={
                    "page": page,
                    "work_mode_raw": _work_mode_from_card(location),
                },
            )
        )
    return listings


def _text(tree: LexborHTMLParser, selector: str) -> str | None:
    node = tree.css_first(selector)
    if node is None:
        return None
    text = node.text().strip()
    return text or None


def _title_parts(html: str) -> tuple[str | None, str | None]:
    title = _text(LexborHTMLParser(html), "title") or ""
    parts = [part.strip() for part in title.split(" | ")]
    if len(parts) >= 2 and parts[-1].lower() == "linkedin":
        parts = parts[:-1]
    if not parts:
        return None, None
    return parts[0] or None, (parts[1] if len(parts) > 1 else None)


def _company_from_dom(tree: LexborHTMLParser) -> str | None:
    for anchor in tree.css('a[href^="/company/"]'):
        text = anchor.text().strip()
        if text:
            return text
    return None


def _location_and_posted(tree: LexborHTMLParser) -> tuple[str | None, str | None]:
    for node in tree.css("p"):
        text = node.text().strip()
        if "·" not in text or len(text) > 200:
            continue
        parts = [part.strip() for part in text.split("·") if part.strip()]
        if not parts:
            continue
        location = parts[0]
        posted = next((part for part in parts[1:] if _TIME_RE.search(part)), None)
        return location, posted
    return None, None


def _label(tree: LexborHTMLParser, mapping: dict[str, str]) -> str | None:
    for node in tree.css("span,p,li"):
        text = node.text().strip().lower()
        if text in mapping:
            return mapping[text]
    return None


def _salary(tree: LexborHTMLParser) -> str | None:
    for node in tree.css("span,p,li"):
        text = node.text().strip()
        if len(text) <= 120 and "premium" not in text.lower() and _SALARY_RE.search(text):
            return text
    return None


def _description_html(tree: LexborHTMLParser) -> str:
    for node in tree.css("h1,h2,h3"):
        if node.text().strip() not in ABOUT_JOB or node.parent is None:
            continue
        section = node.parent
        while section is not None and section.css_first(DESC_BOX) is None:
            section = section.parent
        if section is not None:
            heading = node.parent.html or ""
            html = section.html
            return html.replace(heading, "", 1) if heading else html
    for box in tree.css(DESC_BOX):
        if not _inside_about_company(box) and box.parent is not None:
            return box.parent.html
    return ""


def parse_detail_payload(html: str, listing: RawListing, platform: str = "linkedin") -> RawJob:
    tree = LexborHTMLParser(html)
    title, company = _title_parts(html)
    title = title or listing.title
    company = _company_from_dom(tree) or company or listing.company
    location, posted = _location_and_posted(tree)
    description_html = _description_html(tree)
    description_text = html_to_text(description_html)
    if not title or not description_text:
        raise SiteChangedError(
            "LinkedIn: halaman detail tidak memuat data yang dikenali", url=listing.url
        )

    return RawJob(
        platform=platform,
        url=DETAIL_URL.format(job_id=listing.external_id or ""),
        external_id=listing.external_id,
        title=title.strip(),
        company=company,
        location_raw=location or listing.location_raw,
        posted_raw=posted or listing.posted_raw,
        salary_raw=_salary(tree),
        work_mode_raw=_label(tree, WORK_MODES) or listing.extra.get("work_mode_raw"),
        employment_type_raw=_label(tree, EMPLOYMENT_TYPES),
        description_text=description_text,
        description_html=description_html or None,
        description_truncated=looks_truncated(description_text, len(description_html)),
    )


def _auth_url(url: str) -> bool:
    lowered = (url or "").lower()
    return any(marker in lowered for marker in AUTH_URL_MARKERS)


def _check_response(response, html: str, url: str) -> None:
    if response is not None and response.status in (403, 429, 999):
        raise BlockedError(f"LinkedIn menolak akses ({response.status})", url=url)
    if _auth_url(url):
        raise AuthRequiredError(AUTH_MESSAGE, url=url)
    if detect_challenge(html, url):
        raise BlockedError("LinkedIn menampilkan tantangan anti-bot", url=url)


async def _expand_and_wait(page) -> None:
    for _ in range(3):
        button = await page.query_selector(EXPAND_BUTTON)
        if button is None:
            break
        try:
            await button.click(force=True, timeout=2000)
        except Exception:
            break
        await page.wait_for_timeout(300)
    previous: str | None = None
    for _ in range(3):
        box = await page.query_selector(DESC_BOX)
        text = await box.inner_text() if box is not None else ""
        if text and text == previous:
            break
        previous = text
        await page.wait_for_timeout(300)


class LinkedInScraper(BaseScraper):
    platform = "linkedin"
    requires_auth = True

    def __init__(self, ctx) -> None:
        super().__init__(ctx)
        from app.scrapers.registry import platform_config

        config = platform_config().get(self.platform, {})
        settings = get_settings()
        self.delay_ms = config.get("delay_ms", [4000, 9000])
        self.max_pages = min(ctx.max_pages_per_term, int(config.get("max_pages_per_term", 4)))
        self.max_jobs = min(ctx.max_jobs, settings.linkedin_max_jobs_per_run)
        self.state_path = Path(settings.linkedin_state_path)

    def _storage_state(self) -> str:
        if not self.state_path.exists():
            raise AuthRequiredError(AUTH_MESSAGE)
        return str(self.state_path)

    async def _page(self):
        if self.ctx.browser is None:
            raise SiteChangedError("LinkedIn: BrowserPool tidak tersedia")
        return await self.ctx.browser.new_page(self.platform, storage_state=self._storage_state())

    async def check_session(self) -> None:
        state = self._storage_state()
        if self.ctx.browser is None:
            raise SiteChangedError("LinkedIn: BrowserPool tidak tersedia")
        page = await self.ctx.browser.new_page(self.platform, storage_state=state)
        try:
            response = await page.goto(JOBS_HOME, wait_until="domcontentloaded")
            _check_response(response, await page.content(), page.url)
        finally:
            await page.close()

    def _is_remote_term(self, term: str) -> bool:
        return term in list(self.ctx.search_terms)[:3]

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        yielded = 0
        for page_index in range(self.max_pages):
            if self.ctx.stop_requested or yielded >= self.max_jobs:
                return
            page = await self._page()
            try:
                url = search_url(
                    search_term,
                    self.ctx.max_age_days,
                    start=page_index * 25,
                    remote=self._is_remote_term(search_term),
                )
                await asyncio.sleep(jitter(self.delay_ms))
                response = await page.goto(url, wait_until="domcontentloaded")
                try:
                    await page.wait_for_selector(CARD_SELECTOR, timeout=15000)
                except Exception:
                    pass
                html = await page.content()
                _check_response(response, html, page.url)
                listings = parse_listing_payload(html, page=page_index + 1, platform=self.platform)
                if not listings:
                    if any(marker in html.lower() for marker in NO_RESULTS_MARKERS):
                        return
                    await save_debug_snapshot(page, self.ctx.run_id, self.platform, "no_cards")
                    raise SiteChangedError("LinkedIn: kartu lowongan tidak ditemukan", url=url)
            finally:
                await page.close()

            for listing in listings:
                if self.ctx.stop_requested or yielded >= self.max_jobs:
                    return
                yield listing
                yielded += 1
            if len(listings) < 25:
                return

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        page = await self._page()
        try:
            await asyncio.sleep(jitter(self.delay_ms))
            response = await page.goto(
                DETAIL_URL.format(job_id=listing.external_id), wait_until="domcontentloaded"
            )
            try:
                await page.wait_for_selector(DESC_BOX, timeout=15000)
            except Exception:
                pass
            await _expand_and_wait(page)
            html = await page.content()
            _check_response(response, html, page.url)
            return parse_detail_payload(html, listing, platform=self.platform)
        except (BlockedError, AuthRequiredError, SiteChangedError, ParseError):
            raise
        except Exception as exc:
            await save_debug_snapshot(page, self.ctx.run_id, self.platform, "parse_error")
            raise ParseError(f"LinkedIn detail gagal: {exc}", url=listing.url) from exc
        finally:
            await page.close()
