from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from app.scrapers.base import RawListing, ScrapeContext
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import BlockedError, ParseError, SiteChangedError
from app.scrapers.platforms.kalibrr import (
    KalibrrScraper,
    parse_detail_payload,
    parse_listing_payload,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "kalibrr"

DETAIL_CASES = {
    "detail_263888.html": ("263888", "Android Engineer", "Full time", "Remote"),
    "detail_272018.html": ("272018", "QA Automation Engineer", "Contractual", "On-site"),
    "detail_272823.html": ("272823", "Data Platform Engineer", "Full time", "Hybrid"),
    "detail_275079.html": ("275079", "DevOps Engineer", "Full time", "On-site"),
    "detail_275125.html": ("275125", "Jr. QA Manual", "Contractual", "On-site"),
}


def payload(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def listing(job_id: str = "275125", **overrides) -> RawListing:
    data = {
        "platform": "kalibrr",
        "url": f"https://www.kalibrr.com/c/acme/jobs/{job_id}/job",
        "external_id": job_id,
        "title": "",
    }
    data.update(overrides)
    return RawListing(**data)


def job(**overrides) -> dict:
    data = {
        "id": 1,
        "name": "Engineer",
        "companyInfo": {"name": "Acme"},
        "description": "<p>Hello world</p>",
        "qualifications": "<ul><li>Python</li></ul>",
        "activationDate": "2026-11-01T00:00:00+00:00",
        "applicationEndDate": "2026-12-01T17:00:00+00:00",
        "tenure": "Full time",
        "isWorkFromHome": False,
        "isHybrid": False,
        "salaryShown": False,
    }
    data.update(overrides)
    return data


def detail_html(data: dict, canonical: str = "https://www.kalibrr.com/c/acme/jobs/1/job") -> str:
    next_data = json.dumps({"props": {"pageProps": {"job": data}}}, ensure_ascii=False)
    return (
        f'<html><head><link rel="canonical" href="{canonical}"></head><body>'
        f'<script id="__NEXT_DATA__" type="application/json">{next_data}</script>'
        "</body></html>"
    )


@pytest.mark.parametrize("name", ["search_p1.json", "search_p2.json", "search_p3.json"])
def test_listing_pages(name: str):
    listings = parse_listing_payload(payload(name), page=2)
    assert len(listings) == 15
    for item in listings:
        assert item.platform == "kalibrr"
        assert item.external_id and item.title and item.posted_raw
        assert item.url.startswith("https://www.kalibrr.com/c/")
        assert "?" not in item.url and "/id-ID/" not in item.url
        assert item.extra["page"] == 2
        assert item.extra["work_mode_raw"] in ("Remote", "Hybrid", "On-site")
        assert item.extra["employment_type_raw"] in ("Full time", "Contractual")


def test_listing_fields():
    first = parse_listing_payload(payload("search_p1.json"))[0]
    assert first.external_id == "275125"
    assert first.title == "Jr. QA Manual"
    assert first.company == "PT Adi Data Informatika"
    assert first.location_raw == "Central Jakarta, DKI Jakarta, Indonesia"
    assert first.posted_raw == "2026-11-02T06:39:13.540414+00:00"
    assert first.url.endswith("/c/pt-adi-data-informatika/jobs/275125/jr-qa-manual")
    assert first.extra["salary_raw"] is None
    assert first.extra["expires_raw"] == "2027-11-01T17:00:00+00:00"
    assert first.extra["function"] == "IT and Software"


def test_listing_missing_jobs():
    with pytest.raises(SiteChangedError):
        parse_listing_payload({})


@pytest.mark.parametrize(("name", "expected"), DETAIL_CASES.items())
def test_detail_fixtures(name: str, expected: tuple[str, str, str, str]):
    job_id, title, employment, work_mode = expected
    raw = parse_detail_payload(html(name), listing(job_id))
    assert raw.external_id == job_id
    assert raw.title == title
    assert raw.company
    assert raw.location_raw and raw.location_raw.endswith("Indonesia")
    assert raw.posted_raw and raw.expires_raw
    assert raw.employment_type_raw == employment
    assert raw.work_mode_raw == work_mode
    assert len(raw.description_text) > 500
    assert raw.description_truncated is False
    assert raw.extra["function"] == "IT and Software"


def test_detail_description_union_and_canonical():
    raw = parse_detail_payload(html("detail_275125.html"), listing())
    assert raw.url == (
        "https://www.kalibrr.com/c/pt-adi-data-informatika/jobs/275125/jr-qa-manual"
    )
    assert "<ul>" in raw.description_html
    assert "Menyusun skenario" in raw.description_html
    assert "Pendidikan minimal" in raw.description_html
    assert "Menyusun skenario" in raw.description_text
    assert "Pendidikan minimal" in raw.description_text


def test_detail_salary_rules():
    null_salary = parse_detail_payload(html("detail_275125.html"), listing())
    hidden_salary = parse_detail_payload(html("detail_275079.html"), listing())
    assert null_salary.salary_raw is None
    assert hidden_salary.salary_raw is None

    raw = parse_detail_payload(
        detail_html(
            job(
                salaryShown=True,
                minimumSalary=5_000_000,
                maximumSalary=10_000_000,
                salaryCurrency="IDR",
                salaryInterval="month",
            )
        ),
        listing("1"),
    )
    assert raw.salary_raw == "IDR 5,000,000 - 10,000,000 per month"
    salary = parse_salary(raw.salary_raw)
    assert (salary.minimum, salary.maximum, salary.currency) == (5_000_000, 10_000_000, "IDR")


def test_detail_edge_cases():
    raw = parse_detail_payload(
        detail_html(job(companyInfo={})),
        listing("1", company=None),
    )
    assert raw.title == "Engineer"
    assert raw.company is None

    long_text = "x" * 50_000
    raw = parse_detail_payload(
        detail_html(job(description=f"<p>{long_text}</p>", qualifications=None)),
        listing("1"),
    )
    assert len(raw.description_text) == 50_000
    assert raw.description_truncated is False

    raw = parse_detail_payload(
        detail_html(job(description="<p>Kami 🚀 butuh engineer ñ — oke</p>", qualifications=None)),
        listing("1"),
    )
    assert "🚀" in raw.description_text and "ñ" in raw.description_text


def test_detail_payload_errors():
    with pytest.raises(SiteChangedError):
        parse_detail_payload("<html><body>kosong</body></html>", listing())
    with pytest.raises(SiteChangedError):
        parse_detail_payload({"props": {"pageProps": {}}}, listing())
    with pytest.raises(ParseError):
        parse_detail_payload(
            detail_html(job(description=None, qualifications=None)), listing("1")
        )


def test_contract_raw_job():
    for name in DETAIL_CASES:
        raw = parse_detail_payload(html(name), listing(name.split("_", 1)[1].split(".")[0]))
        assert raw.platform == "kalibrr"
        assert raw.url and raw.title and raw.description_text
        assert raw.external_id and raw.posted_raw
        assert isinstance(raw.extra, dict)


def test_fixtures_are_not_challenge_pages():
    search_url = "https://www.kalibrr.com/id-ID/home/te/software+engineer"
    assert not detect_challenge(html("search_software_engineer.html"), search_url)
    api_url = "https://www.kalibrr.com/kjs/job_board/search"
    api_text = (FIXTURES / "search_p1.json").read_text(encoding="utf-8")[:1000]
    assert not detect_challenge(api_text, api_url)
    for name in DETAIL_CASES:
        assert not detect_challenge(
            html(name)[:1000], "https://www.kalibrr.com/c/acme/jobs/1/job"
        )


def test_detail_accepts_job_dict():
    raw = parse_detail_payload(job(), listing("1"))
    assert raw.external_id == "1"
    assert raw.title == "Engineer"


async def test_search_challenge_raises_blocked(monkeypatch):
    scraper = KalibrrScraper(ScrapeContext(run_id="test", max_age_days=30, max_jobs=10))
    response = httpx.Response(
        200,
        text="<html><title>Just a moment...</title></html>",
        request=httpx.Request("GET", "https://www.kalibrr.com/kjs/job_board/search"),
    )

    async def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(scraper, "_get", fake_get)
    monkeypatch.setattr("app.scrapers.platforms.kalibrr._save_snapshot", lambda *a, **k: None)
    with pytest.raises(BlockedError):
        await scraper._search(None, "engineer", 0)


async def test_search_malformed_json_raises_site_changed(monkeypatch):
    scraper = KalibrrScraper(ScrapeContext(run_id="test", max_age_days=30, max_jobs=10))
    response = httpx.Response(
        200,
        text="{not json",
        request=httpx.Request("GET", "https://www.kalibrr.com/kjs/job_board/search"),
    )

    async def fake_get(*args, **kwargs):
        return response

    monkeypatch.setattr(scraper, "_get", fake_get)
    monkeypatch.setattr("app.scrapers.platforms.kalibrr._save_snapshot", lambda *a, **k: None)
    with pytest.raises(SiteChangedError):
        await scraper._search(None, "engineer", 0)


async def test_iter_listings_guard_offset_against_count(monkeypatch):
    payload_page = payload("search_p1.json")
    payload_page["count"] = 15
    calls: list[int] = []

    async def fake_search(client, term, offset):
        calls.append(offset)
        return payload_page

    scraper = KalibrrScraper(
        ScrapeContext(
            run_id="test",
            max_age_days=30,
            max_jobs=100,
            max_pages_per_term=5,
        )
    )
    scraper.delay_ms = [0, 0]
    monkeypatch.setattr(scraper, "_search", fake_search)
    items = [item async for item in scraper.iter_listings("engineer")]
    assert len(items) == 15
    assert calls == [0]


@pytest.mark.live
async def test_kalibrr_live_smoke():
    ctx = ScrapeContext(
        run_id="live_kalibrr",
        max_age_days=30,
        max_jobs=30,
        fetch_details=True,
        max_pages_per_term=2,
    )
    scraper = KalibrrScraper(ctx)
    listings = [item async for item in scraper.iter_listings("software engineer")][:3]
    assert listings, "tidak ada listing dari Kalibrr"
    assert listings[0].external_id and listings[0].title
    raw = await scraper.fetch_detail(listings[0])
    assert raw.title and len(raw.description_text) > 200
    assert raw.work_mode_raw in ("Remote", "Hybrid", "On-site")
