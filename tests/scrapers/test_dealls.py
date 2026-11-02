from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from app.scrapers.base import RawListing, ScrapeContext
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import BlockedError, ParseError, SiteChangedError
from app.scrapers.platforms.dealls import (
    DeallsScraper,
    canonical_url,
    parse_detail_payload,
    parse_listing_payload,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "dealls"
DETAIL_CASES = {
    "detail_software-engineer-juniormiddle.json": ("onsite", "fulltime"),
    "detail_software-engineer-java-t24.json": ("onsite", "fulltime"),
    "detail_software-development-engineer-in-test-10.json": ("onsite", "contract"),
    "detail_software-engineer-fullstack-order-management.json": ("hybrid", "fulltime"),
    "detail_software-engineer-golang-1.json": ("hybrid", "contract"),
    "detail_part-time-pengajar-coding-kota.json": ("remote", "parttime"),
}


def payload(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def listing(**overrides) -> RawListing:
    data = {
        "platform": "dealls",
        "url": canonical_url("software-engineer-juniormiddle", "dexa-group"),
        "external_id": "6ae2f7aa23d8da0012111afc",
        "title": "Software Engineer (Junior/Middle)",
        "extra": {"api_slug": "software-engineer-juniormiddle"},
    }
    data.update(overrides)
    return RawListing(**data)


def test_listing_parsing_staff():
    listings = parse_listing_payload(payload("search_staff_p1.json"))
    assert len(listings) == 18
    first = listings[0]
    assert first.external_id == "6ae85714a4b0c800131241d9"
    assert first.title == "Staff Pajak"
    assert first.company == "Tazbiya Brands"
    assert first.location_raw == "Jakarta Selatan"
    assert first.posted_raw == "2026-11-02T09:25:40.039Z"
    assert first.url == "https://dealls.com/loker/staff-pajak-1~tazbiya-brands"
    assert first.extra["work_mode_raw"] == "onsite"
    assert first.extra["employment_type_raw"] == "fulltime"
    salary = parse_salary(first.extra["salary_raw"])
    assert (salary.minimum, salary.maximum) == (5_000_000, 6_000_000)


def test_listing_parsing_software_engineer():
    listings = parse_listing_payload(payload("search_software_engineer_p1.json"))
    assert len(listings) == 14
    assert all(item.url.startswith("https://dealls.com/loker/") for item in listings)
    assert all("?" not in item.url and "/en/" not in item.url for item in listings)
    assert all(item.posted_raw for item in listings)


def test_listing_empty_page():
    assert parse_listing_payload(payload("search_software_engineer_p2.json"), page=2) == []


def test_listing_missing_docs_raises():
    with pytest.raises(SiteChangedError):
        parse_listing_payload({"data": {}})


def test_listing_remote_salary_optional():
    listings = parse_listing_payload(payload("search_remote_p1.json"))
    assert len(listings) == 18
    assert all(item.extra["work_mode_raw"] == "remote" for item in listings)
    assert sum(item.extra["salary_raw"] is not None for item in listings) == 2


def test_detail_all_fixtures():
    for name, (work_mode, employment) in DETAIL_CASES.items():
        raw = parse_detail_payload(payload(name), listing())
        assert raw.title, name
        assert raw.company, name
        assert len(raw.description_text) > 200, name
        assert raw.description_truncated is False, name
        assert raw.work_mode_raw == work_mode, name
        assert raw.employment_type_raw == employment, name
        assert raw.url.startswith("https://dealls.com/loker/"), name
        assert "?" not in raw.url and "/en/" not in raw.url, name


def test_detail_salary_present():
    raw = parse_detail_payload(
        payload("detail_software-engineer-juniormiddle.json"), listing()
    )
    salary = parse_salary(raw.salary_raw)
    assert (salary.minimum, salary.maximum) == (10_000_000, 15_000_000)
    assert raw.posted_raw == "2026-10-29T07:37:14.497Z"


def test_detail_without_salary():
    raw = parse_detail_payload(payload("detail_software-engineer-java-t24.json"), listing())
    assert raw.salary_raw is None
    assert raw.employment_type_raw == "fulltime"


def test_recruiter_activity_is_not_posted_date():
    data = payload("detail_software-engineer-juniormiddle.json")
    data["data"]["result"].pop("publishedAt")
    assert data["data"]["result"]["lastActivelyHiringAt"]
    raw = parse_detail_payload(data, listing())
    assert raw.posted_raw is None


def test_missing_posting_date_is_none():
    data = payload("detail_software-engineer-java-t24.json")
    result = data["data"]["result"]
    result.pop("publishedAt")
    result.pop("lastActivelyHiringAt", None)
    assert parse_detail_payload(data, listing()).posted_raw is None


def test_detail_ssr_fallback():
    raw = parse_detail_payload(html("detail_ssr_dexa_group.html"), listing())
    assert raw.title == "Software Engineer (Junior/Middle)"
    assert raw.company == "Dexa Group"
    assert raw.posted_raw.startswith("2026-10-29")
    assert raw.url == "https://dealls.com/loker/software-engineer-juniormiddle~dexa-group"
    assert len(raw.description_text) > 500


def test_detail_contract_fields():
    for name in DETAIL_CASES:
        raw = parse_detail_payload(payload(name), listing())
        assert raw.platform == "dealls"
        assert raw.url and raw.title and raw.description_text
        assert raw.description_html


def test_detail_empty_description_raises():
    data = payload("detail_software-engineer-juniormiddle.json")
    result = data["data"]["result"]
    for field in ("description", "responsibilities", "requirements"):
        result.pop(field, None)
    with pytest.raises(ParseError):
        parse_detail_payload(data, listing())


def test_detail_malformed_payload_raises():
    with pytest.raises(SiteChangedError):
        parse_detail_payload({"data": {"result": None}}, listing())


def test_canonical_url_rules():
    assert canonical_url("staff-pajak-1", "tazbiya-brands") == (
        "https://dealls.com/loker/staff-pajak-1~tazbiya-brands"
    )
    assert canonical_url("staff-pajak-1~tazbiya-brands", "other") == (
        "https://dealls.com/loker/staff-pajak-1~tazbiya-brands"
    )
    assert canonical_url("", "x") == ""


def test_fixtures_are_not_challenge_pages():
    assert not detect_challenge(
        html("detail_ssr_dexa_group.html"),
        "https://dealls.com/loker/software-engineer-juniormiddle~dexa-group",
    )
    assert not detect_challenge(
        json.dumps(payload("search_staff_p1.json"))[:1000],
        "https://api.sejutacita.id/v1/explore-job/job",
    )


async def test_iter_listings_stops_on_empty_page(monkeypatch):
    calls: list[int] = []

    async def fake_search(client, term, page):
        calls.append(page)
        return payload("search_staff_p1.json" if page == 1 else "search_software_engineer_p2.json")

    scraper = DeallsScraper(
        ScrapeContext(run_id="test", max_age_days=30, max_jobs=100, max_pages_per_term=5)
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    items = [item async for item in scraper.iter_listings("staff")]
    assert len(items) == 18
    assert calls == [1, 2]


async def test_search_malformed_json_raises_site_changed(monkeypatch):
    scraper = DeallsScraper(ScrapeContext(run_id="test", max_age_days=30, max_jobs=10))
    response = httpx.Response(
        200,
        text="{not json",
        request=httpx.Request("GET", "https://api.sejutacita.id/v1/explore-job/job"),
    )

    async def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(scraper, "_get", fake_get)
    monkeypatch.setattr("app.scrapers.platforms.dealls._save_snapshot", lambda *a, **k: None)
    with pytest.raises(SiteChangedError):
        await scraper._search(None, "staff", 1)


async def test_search_challenge_raises_blocked(monkeypatch):
    scraper = DeallsScraper(ScrapeContext(run_id="test", max_age_days=30, max_jobs=10))
    response = httpx.Response(
        200,
        text="<html><title>Just a moment...</title></html>",
        request=httpx.Request("GET", "https://api.sejutacita.id/v1/explore-job/job"),
    )

    async def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(scraper, "_get", fake_get)
    monkeypatch.setattr("app.scrapers.platforms.dealls._save_snapshot", lambda *a, **k: None)
    with pytest.raises(BlockedError):
        await scraper._search(None, "staff", 1)


async def test_fetch_detail_falls_back_to_ssr(monkeypatch):
    urls: list[str] = []

    async def fake_get(client, url, **kwargs):
        urls.append(url)
        if "api.sejutacita.id" in url:
            raise SiteChangedError("API detail tidak tersedia")
        return httpx.Response(
            200,
            text=html("detail_ssr_dexa_group.html"),
            request=httpx.Request("GET", url),
        )

    scraper = DeallsScraper(ScrapeContext(run_id="test", max_age_days=30, max_jobs=10))
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_get", fake_get)
    raw = await scraper.fetch_detail(listing())
    assert raw.title == "Software Engineer (Junior/Middle)"
    assert urls[0].startswith("https://api.sejutacita.id/")
    assert urls[1].startswith("https://dealls.com/loker/")


@pytest.mark.live
async def test_dealls_live_smoke():
    ctx = ScrapeContext(
        run_id="live_dealls",
        max_age_days=30,
        max_jobs=20,
        fetch_details=True,
        max_pages_per_term=2,
    )
    scraper = DeallsScraper(ctx)
    listings = [item async for item in scraper.iter_listings("software engineer")][:3]
    assert listings, "tidak ada listing dari Dealls"
    assert listings[0].external_id and listings[0].title
    raw = await scraper.fetch_detail(listings[0])
    assert raw.title and len(raw.description_text) > 200
