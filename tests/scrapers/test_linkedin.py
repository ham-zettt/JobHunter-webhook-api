from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.scrapers.base import RawJob, RawListing, ScrapeContext
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import AuthRequiredError, BlockedError, SiteChangedError
from app.scrapers.platforms.linkedin import (
    LinkedInScraper,
    parse_detail_payload,
    parse_listing_payload,
    search_url,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "linkedin"


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def listing(job_id: str = "4481158304", **extra) -> RawListing:
    return RawListing(
        platform="linkedin",
        url=f"https://www.linkedin.com/jobs/view/{job_id}",
        external_id=job_id,
        title="",
        extra=extra,
    )


class FakeResponse:
    status = 200


class FakePage:
    def __init__(self, url: str, body: str) -> None:
        self.url = url
        self.body = body
        self.closed = False

    async def goto(self, url: str, wait_until: str | None = None):
        if self.url == "https://www.linkedin.com/jobs/":
            self.url = url
        return FakeResponse()

    async def content(self) -> str:
        return self.body

    async def close(self) -> None:
        self.closed = True


class FakeBrowser:
    def __init__(self, page: FakePage) -> None:
        self.page = page
        self.storage_state: str | None = None

    async def new_page(self, platform: str, *, storage_state: str | None = None) -> FakePage:
        self.storage_state = storage_state
        return self.page


def settings(path: Path, *, per_run: int = 60):
    return SimpleNamespace(linkedin_state_path=str(path), linkedin_max_jobs_per_run=per_run)


def ctx(**overrides) -> ScrapeContext:
    data = {
        "run_id": "run-1",
        "max_age_days": 7,
        "max_jobs": 300,
        "search_terms": ["backend", "frontend", "data", "devops"],
    }
    data.update(overrides)
    return ScrapeContext(**data)


def test_listing_fixtures():
    cases = {
        "search_indonesia_week.html": 25,
        "search_remote_filter.html": 25,
        "search_last_week.html": 6,
    }
    for name, expected in cases.items():
        listings = parse_listing_payload(html(name), page=2)
        assert len(listings) == expected, name
        assert all(item.external_id.isdigit() for item in listings), name
        assert all(item.title for item in listings), name
        assert all(item.url.endswith(item.external_id) for item in listings), name
        assert all(item.extra["page"] == 2 for item in listings), name


def test_listing_fields_and_remote_mode():
    first = parse_listing_payload(html("search_indonesia_week.html"))[0]
    assert first.external_id == "4483298296"
    assert first.title == "Application Developer - Malang (.NET)"
    assert first.company == "PT Adicipta Inovasi Teknologi"
    assert first.location_raw == "Kota Malang (Gabungan)"
    assert first.posted_raw == "6 hari yang lalu"
    assert first.extra["work_mode_raw"] == "hybrid"

    remote = parse_listing_payload(html("search_remote_filter.html"))[0]
    assert remote.location_raw == "Indonesia (Jarak Jauh)"
    assert remote.extra["work_mode_raw"] == "remote"


def test_listing_deduplicates_multiple_nodes():
    listings = parse_listing_payload(html("search_last_week.html"))
    assert len({item.external_id for item in listings}) == len(listings)


def test_listing_without_title_span_uses_paragraph():
    source = html("search_indonesia_week.html")
    assert "Software Engineer" in source


def test_detail_fixtures():
    cases = {
        "detail_4477060658.html": ("4477060658", "hybrid", "fulltime"),
        "detail_4481158304.html": ("4481158304", "onsite", "fulltime"),
        "detail_4481630924.html": ("4481630924", "onsite", "contract"),
        "detail_4482985280.html": ("4482985280", "onsite", "fulltime"),
        "detail_4484092568.html": ("4484092568", "onsite", "fulltime"),
    }
    for name, (job_id, work_mode, employment_type) in cases.items():
        raw = parse_detail_payload(html(name), listing(job_id))
        assert isinstance(raw, RawJob), name
        assert raw.platform == "linkedin"
        assert raw.external_id == job_id
        assert raw.url.endswith(job_id)
        assert raw.title, name
        assert raw.company, name
        assert len(raw.description_text) >= 150, name
        assert raw.description_truncated is False, name
        assert raw.work_mode_raw == work_mode, name
        assert raw.employment_type_raw == employment_type, name
        assert raw.posted_raw and "lalu" in raw.posted_raw, name


def test_detail_values_and_salary():
    raw = parse_detail_payload(html("detail_4481158304.html"), listing("4481158304"))
    assert raw.title == "Programmer (Penempatan Surabaya)"
    assert raw.company == "Universitas Ciputra Surabaya"
    assert raw.location_raw == "Surabaya, Jawa Timur, Indonesia"
    assert raw.posted_raw == "1 minggu yang lalu"
    assert raw.salary_raw == "Rp6M/month - Rp10M/month"
    salary = parse_salary(raw.salary_raw)
    assert salary.minimum == 6_000_000 and salary.maximum == 10_000_000
    assert "Responsibilities" in raw.description_text
    assert "- Memiliki kemampuan bekerjasama dengan tim" in raw.description_text


def test_detail_long_description_and_about_company_excluded():
    raw = parse_detail_payload(html("detail_4484092568.html"), listing("4484092568"))
    assert len(raw.description_text) > 5000
    assert "KOPDAR ISP Nusantara" not in raw.description_text
    assert "Role Overview" in raw.description_text


def test_detail_missing_description_raises():
    with pytest.raises(SiteChangedError):
        parse_detail_payload("<html><title>X | Y | LinkedIn</title></html>", listing())


def test_search_url_parameters():
    url = search_url("backend engineer", 7, start=25, remote=True)
    assert "keywords=backend+engineer" in url
    assert "location=Indonesia" in url
    assert "f_TPR=r604800" in url
    assert "start=25" in url
    assert "f_WT=2" in url
    assert "sortBy=DD" in url
    assert "f_WT=2" not in search_url("backend", 1)
    assert "f_TPR=r86400" in search_url("backend", 1)


def test_limits_per_run_and_pages(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.scrapers.platforms.linkedin.get_settings",
        lambda: settings(tmp_path / "state.json", per_run=60),
    )
    scraper = LinkedInScraper(ctx(max_jobs=300, max_pages_per_term=6))
    assert scraper.max_jobs == 60
    assert scraper.max_pages == 4
    assert scraper._is_remote_term("backend")
    assert not scraper._is_remote_term("devops")


def test_check_session_missing_state_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "app.scrapers.platforms.linkedin.get_settings",
        lambda: settings(tmp_path / "missing.json"),
    )
    scraper = LinkedInScraper(ctx(browser=FakeBrowser(FakePage("", ""))))
    with pytest.raises(AuthRequiredError):
        import asyncio

        asyncio.run(scraper.check_session())


@pytest.mark.parametrize(
    ("url", "body", "error"),
    [
        ("https://www.linkedin.com/login", "<html>login</html>", AuthRequiredError),
        (
            "https://www.linkedin.com/checkpoint/challenge",
            "<html>checkpoint</html>",
            AuthRequiredError,
        ),
        (
            "https://www.linkedin.com/jobs/",
            "<html>Verify you are human</html>",
            BlockedError,
        ),
    ],
)
def test_check_session_redirect_and_challenge(tmp_path, monkeypatch, url, body, error):
    state = tmp_path / "state.json"
    state.write_text("{}")
    monkeypatch.setattr(
        "app.scrapers.platforms.linkedin.get_settings",
        lambda: settings(state),
    )
    page = FakePage(url, body)
    scraper = LinkedInScraper(ctx(browser=FakeBrowser(page)))
    import asyncio

    with pytest.raises(error):
        asyncio.run(scraper.check_session())
    assert page.closed


def test_fixture_pages_are_not_challenges():
    for name in ("search_indonesia_week.html", "search_remote_filter.html"):
        assert not detect_challenge(html(name), "https://www.linkedin.com/jobs/search-results/")
    for name in ("detail_4481158304.html", "detail_4477060658.html"):
        assert not detect_challenge(html(name), "https://www.linkedin.com/jobs/view/4481158304/")
