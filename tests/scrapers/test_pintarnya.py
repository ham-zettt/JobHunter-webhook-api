from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.scrapers.base import RawJob, RawListing, ScrapeContext
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import BlockedError, ParseError, SiteChangedError
from app.scrapers.platforms._placeholder import DiscoveryPendingScraper
from app.scrapers.platforms.pintarnya import (
    PintarnyaScraper,
    _is_challenge,
    canonical_url,
    parse_detail_payload,
    parse_list_payload,
    salary_text,
    total_pages,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "pintarnya"
LIST_FILES = ("list_page_1.json", "list_page_2.json", "list_page_3.json")


def payload(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def listing(slug: str = "it-support-1160847", **extra) -> RawListing:
    return RawListing(
        platform="pintarnya",
        url=canonical_url(slug),
        external_id=slug,
        title="IT Support",
        extra=extra,
    )


def test_scraper_replaces_placeholder():
    assert not issubclass(PintarnyaScraper, DiscoveryPendingScraper)


def test_list_page_1_mapping():
    listings = parse_list_payload(payload("list_page_1.json"))
    assert len(listings) == 12
    first = listings[0]
    assert first.external_id == "it-support-1160847"
    assert first.url == "https://pintarnya.com/lowongan/it-support-1160847"
    assert first.title == "IT Support"
    assert first.company == "PT Kobus Smart Service"
    assert first.location_raw == "Kota Adm. Jakarta Utara, DKI Jakarta"
    assert first.posted_raw == "2026-11-02T14:05:19.316Z"
    assert first.extra["work_mode_raw"] == "hybrid"
    assert first.extra["employment_type_raw"] == "fulltime"
    assert first.extra["category_id"] == 17
    salary = parse_salary(first.extra["salary_raw"])
    assert (salary.minimum, salary.maximum) == (4_100_000, 4_250_000)


def test_list_pages_2_and_3():
    second = parse_list_payload(payload("list_page_2.json"), page=2)
    third = parse_list_payload(payload("list_page_3.json"), page=3)
    assert (len(second), len(third)) == (10, 3)
    assert {item.extra["page"] for item in second} == {2}
    assert {item.extra["page"] for item in third} == {3}


def test_list_api_and_ssr_shapes():
    fixture = payload("list_page_1.json")
    assert len(parse_list_payload({"data": fixture})) == 12
    jobs = [row["sublist"][0] for row in fixture["list"]]
    assert len(parse_list_payload({"list": [{"sublist": [job]} for job in jobs]})) == 12
    assert len(parse_list_payload(jobs)) == 12
    assert total_pages({"data": fixture}) == 3
    assert total_pages(jobs) == 1


def test_list_skips_rows_without_slug():
    data = {
        "list": [
            {"sublist": []},
            {"sublist": [{"title": "tanpa slug"}]},
            "rusak",
            {"sublist": [{"slug": "valid-1", "title": "Valid"}]},
        ]
    }
    listings = parse_list_payload(data)
    assert [item.external_id for item in listings] == ["valid-1"]


def test_salary_text_formats_and_ignores_empty():
    assert salary_text(4_100_000, 4_250_000) == "IDR 4,100,000 - 4,250,000 per month"
    assert salary_text(5_000_000, None) == "IDR 5,000,000 per month"
    assert salary_text(None, None) is None


EXPECTED_SALARY = {
    "detail_it-support-1160847.json": (4_100_000, 4_250_000),
    "detail_it-support-1133693.json": (8_000_000, 10_000_000),
    "detail_it-support-1046482.json": (5_000_000, 6_000_000),
    "detail_it-programmer-762180.json": (3_500_000, 6_000_000),
    "detail_it-programmer-1154844.json": (4_000_000, 7_000_000),
}


@pytest.mark.parametrize(
    ("name", "slug", "work_mode", "employment"),
    [
        ("detail_it-support-1160847.json", "it-support-1160847", "hybrid", "fulltime"),
        ("detail_it-support-1133693.json", "it-support-1133693", "onsite", "fulltime"),
        ("detail_it-support-1046482.json", "it-support-1046482", "onsite", "contract"),
        ("detail_it-programmer-762180.json", "it-programmer-762180", "onsite", "fulltime"),
        ("detail_it-programmer-1154844.json", "it-programmer-1154844", "onsite", "fulltime"),
    ],
)
def test_detail_fixtures_contract(name, slug, work_mode, employment):
    job = parse_detail_payload(payload(name), listing(slug))
    assert isinstance(job, RawJob)
    assert job.external_id == slug
    assert job.url == canonical_url(slug)
    assert job.title
    assert job.company
    assert job.location_raw
    assert job.posted_raw
    assert job.expires_raw
    assert job.work_mode_raw == work_mode
    assert job.employment_type_raw == employment
    assert job.extra["kategori"] == "IT dan Teknisi"
    assert len(job.description_text) >= 400
    assert job.description_html.startswith("<p>")
    assert not job.description_truncated
    parsed = parse_salary(job.salary_raw)
    assert (parsed.minimum, parsed.maximum) == EXPECTED_SALARY[name]


def test_detail_html_with_json_ld_and_next_data():
    fixture = payload("detail_it-support-1160847.json")
    html = (
        "<html><head><script type=\"application/ld+json\">"
        + json.dumps(fixture["json_ld"])
        + "</script></head><body><script id=\"__NEXT_DATA__\" "
        "type=\"application/json\">"
        + json.dumps({"props": {"pageProps": {"jobData": {"page_header": fixture["page_header"]}}}})
        + "</script></body></html>"
    )
    job = parse_detail_payload(html, listing())
    assert job.title == "IT Support"
    assert job.work_mode_raw == "hybrid"
    assert job.employment_type_raw == "fulltime"
    assert job.extra["kategori"] == "IT dan Teknisi"
    assert job.description_text


def test_detail_missing_json_ld_raises_site_changed():
    with pytest.raises(SiteChangedError):
        parse_detail_payload("<html><body>kosong</body></html>", listing())


def test_detail_empty_description_raises_parse_error():
    fixture = payload("detail_it-support-1160847.json")
    fixture["json_ld"]["description"] = ""
    with pytest.raises(ParseError):
        parse_detail_payload(fixture, listing())


def test_challenge_detection_ignores_recaptcha_script():
    assert detect_challenge("<title>Just a moment...</title>", "https://pintarnya.com/")
    assert not _is_challenge(
        '<html><head><script>window.recaptchaSiteKey="abc"</script></head></html>',
        "https://pintarnya.com/lowongan/it-support-1160847",
    )
    assert _is_challenge("<title>Just a moment...</title>", "https://pintarnya.com/")


async def test_iter_listings_paginates_and_dedupes(monkeypatch):
    calls: list[int] = []

    async def fake_search(term, page):
        calls.append(page)
        return payload(f"list_page_{page}.json")

    scraper = PintarnyaScraper(
        ScrapeContext(run_id="test", max_age_days=30, max_jobs=100, max_pages_per_term=5)
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    items = [item async for item in scraper.iter_listings("it support")]
    assert calls == [1, 2, 3]
    assert len(items) == 23
    assert len({item.external_id for item in items}) == 23


async def test_iter_listings_stops_on_empty_page(monkeypatch):
    calls: list[int] = []

    async def fake_search(term, page):
        calls.append(page)
        if page == 1:
            return payload("list_page_1.json")
        return {"list": [], "pagination": {"total_page": 3}}

    scraper = PintarnyaScraper(
        ScrapeContext(run_id="test", max_age_days=30, max_jobs=100, max_pages_per_term=5)
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    items = [item async for item in scraper.iter_listings("it support")]
    assert len(items) == 12
    assert calls == [1, 2]


async def test_iter_listings_respects_max_pages_and_max_jobs(monkeypatch):
    calls: list[int] = []

    async def fake_search(term, page):
        calls.append(page)
        return payload(f"list_page_{page}.json")

    scraper = PintarnyaScraper(
        ScrapeContext(run_id="test", max_age_days=30, max_jobs=100, max_pages_per_term=1)
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    assert len([item async for item in scraper.iter_listings("it support")]) == 12
    assert calls == [1]

    calls.clear()
    scraper = PintarnyaScraper(
        ScrapeContext(run_id="test", max_age_days=30, max_jobs=5, max_pages_per_term=5)
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    assert len([item async for item in scraper.iter_listings("it support")]) == 5


class FakePage:
    def __init__(self, html: str = "<html><body>ok</body></html>") -> None:
        self._html = html
        self.url = "https://pintarnya.com/q-it-support-lowongan"

    async def goto(self, url: str, **kwargs) -> None:
        self.url = url

    async def content(self) -> str:
        return self._html


class FakeResponse:
    def __init__(self, status: int) -> None:
        self.status = status

    async def json(self):
        return {"data": {"list": [], "pagination": {"total_page": 1}}}


class FakeRequest:
    def __init__(self, status: int) -> None:
        self.status = status

    async def get(self, url: str, **kwargs) -> FakeResponse:
        return FakeResponse(self.status)


class FakeContext:
    def __init__(self, status: int = 200, html: str = "<html><body>ok</body></html>") -> None:
        self.request = FakeRequest(status)
        self._html = html

    async def new_page(self) -> FakePage:
        return FakePage(self._html)


class FakeBrowser:
    def __init__(self, status: int = 200, html: str = "<html><body>ok</body></html>") -> None:
        self._context = FakeContext(status, html)

    async def context(self, platform: str) -> FakeContext:
        return self._context


@pytest.mark.parametrize("status", [401, 403])
async def test_search_blocked_status(status):
    ctx = ScrapeContext(run_id="test", max_age_days=30, max_jobs=10, browser=FakeBrowser(status))
    scraper = PintarnyaScraper(ctx)
    with pytest.raises(BlockedError):
        await scraper._search("it support", 1)


async def test_search_challenge_raises_blocked():
    ctx = ScrapeContext(
        run_id="test",
        max_age_days=30,
        max_jobs=10,
        browser=FakeBrowser(html="<title>Just a moment...</title>"),
    )
    scraper = PintarnyaScraper(ctx)
    with pytest.raises(BlockedError):
        await scraper._search("it support", 1)
