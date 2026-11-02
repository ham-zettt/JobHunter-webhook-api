from __future__ import annotations

from pathlib import Path

import pytest

from app.scrapers.base import RawListing
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import SiteChangedError
from app.scrapers.platforms.glints import (
    draft_to_parts,
    job_url,
    parse_detail_html,
    parse_search_html,
    salary_text,
    slugify,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "glints"


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def listing(
    job_id: str = "c1a83f29-5719-492d-bd1d-5a5794fd519d", title: str = "Software Engineer", **extra
) -> RawListing:
    return RawListing(
        platform="glints",
        url=job_url(title, job_id),
        external_id=job_id,
        title=title,
        extra=extra,
    )


def test_search_parsing():
    listings = parse_search_html(html("search_software_engineer.html"))
    assert len(listings) == 30
    first = listings[0]
    assert first.external_id == "c1a83f29-5719-492d-bd1d-5a5794fd519d"
    assert first.title == "Software Engineer"
    assert first.company.startswith("PT. Digerati")
    assert first.location_raw == "Kelapa Dua, Kab. Tangerang, Banten, Indonesia"
    assert first.posted_raw.startswith("2026-10-20T09:36:34")
    assert first.url.endswith("/software-engineer/c1a83f29-5719-492d-bd1d-5a5794fd519d")
    assert first.extra["work_mode_raw"] == "onsite"
    assert first.extra["employment_type_raw"] == "fulltime"
    salary = parse_salary(first.extra["salary_raw"])
    assert (salary.minimum, salary.maximum) == (4_901_117, 5_000_000)


def test_search_missing_next_data():
    with pytest.raises(SiteChangedError):
        parse_search_html("<html><body>kosong</body></html>")


def test_search_page_without_initial_jobs():
    with pytest.raises(SiteChangedError):
        parse_search_html(html("search_page2.html"))


def test_detail_remote_with_salary():
    raw = parse_detail_html(
        html("detail_b78541fb.html"),
        listing("b78541fb-0dd0-46b4-9c1d-5880afca5414", "Software Developer"),
    )
    assert raw.external_id == "b78541fb-0dd0-46b4-9c1d-5880afca5414"
    assert raw.work_mode_raw == "remote"
    assert raw.employment_type_raw == "fulltime"
    assert raw.posted_raw == "2026-07-26T14:46:27.975Z"
    salary = parse_salary(raw.salary_raw)
    assert salary.currency == "IDR"
    assert salary.minimum == 4_000_000 and salary.maximum == 5_000_000
    assert len(raw.description_text) > 1000
    assert raw.description_truncated is False


def test_detail_internship_hybrid():
    raw = parse_detail_html(
        html("detail_8fd4f744.html"),
        listing("8fd4f744-94de-4213-9e3b-b10a68c3db0c", "Software Engineer Intern"),
    )
    assert raw.work_mode_raw == "hybrid"
    assert raw.employment_type_raw == "internship"
    salary = parse_salary(raw.salary_raw)
    assert salary.maximum == 600_000


def test_detail_contract_without_salary():
    raw = parse_detail_html(
        html("detail_66c8002a.html"),
        listing("66c8002a-4953-4e90-b8a3-625d58e7feb8", "Software Developer"),
    )
    assert raw.employment_type_raw == "contract"
    assert raw.salary_raw is None
    assert len(raw.description_text) > 300


def test_detail_project_salary_not_monthly():
    raw = parse_detail_html(
        html("detail_812c9d0b.html"),
        listing("812c9d0b-4912-49df-8a75-d80a791b9a44", "Software Developer"),
    )
    assert "per project" in raw.salary_raw
    salary = parse_salary(raw.salary_raw)
    assert salary.minimum == 1_000_000
    assert salary.period is None


def test_detail_all_fixtures():
    for path in sorted(FIXTURES.glob("detail_*.html")):
        job_id = path.stem.split("_", 1)[1]
        raw = parse_detail_html(path.read_text(encoding="utf-8"), listing(job_id))
        assert raw.title, path.name
        assert raw.description_text, path.name
        assert raw.work_mode_raw in ("remote", "hybrid", "onsite"), path.name


def test_salary_text_rules():
    salaries = [{"CurrencyCode": "IDR", "minAmount": 1, "maxAmount": 2, "salaryMode": "MONTH"}]
    assert salary_text(salaries, True) == "IDR 1 - 2 per month"
    assert salary_text(salaries, False) is None
    assert salary_text([], True) is None
    assert (
        salary_text([{"CurrencyCode": "IDR", "maxAmount": 5, "salaryMode": "DAY"}])
        == "IDR 5 per day"
    )


def test_draft_to_parts():
    raw = (
        '{"blocks":[{"type":"header-one","text":"Judul"},'
        '{"type":"unordered-list-item","text":"Poin"},'
        '{"type":"unstyled","text":"Paragraf"}]}'
    )
    text, html_out = draft_to_parts(raw)
    assert text == "Judul\n- Poin\nParagraf"
    assert "<h1>Judul</h1>" in html_out and "<li>Poin</li>" in html_out
    assert draft_to_parts(None) == ("", "")


def test_slug_and_url():
    assert slugify("Software Engineer (Fullstack)") == "software-engineer-fullstack"
    assert slugify("") == "job"
    assert job_url("Backend Developer", "abc").endswith("/backend-developer/abc")


def test_fixtures_are_not_challenge_pages():
    assert not detect_challenge(
        html("search_software_engineer.html"), "https://glints.com/id/opportunities/jobs/explore"
    )
    assert not detect_challenge(
        html("detail_b78541fb.html"), "https://glints.com/id/opportunities/jobs/x/y"
    )
