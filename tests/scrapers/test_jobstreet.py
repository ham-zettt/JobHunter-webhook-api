from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from app.scrapers.base import RawListing
from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import SiteChangedError
from app.scrapers.platforms.jobstreet import (
    extract_redux_state,
    parse_detail_html,
    parse_search_payload,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "jobstreet"


def listing(job_id: str = "95140055", **extra) -> RawListing:
    return RawListing(
        platform="jobstreet",
        url=f"https://id.jobstreet.com/id/job/{job_id}",
        external_id=job_id,
        title="",
        extra=extra,
    )


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_search_payload_parsing():
    payload = json.loads((FIXTURES / "search_page1.json").read_text(encoding="utf-8"))
    listings = parse_search_payload(payload, page=2)
    assert len(listings) == 20
    first = listings[0]
    assert first.external_id == "95140055"
    assert first.title == "Software Engineer"
    assert first.company == "Petrosync"
    assert first.location_raw == "West Jakarta, Jakarta"
    assert first.posted_raw == "2026-10-08T05:44:02Z"
    assert first.url == "https://id.jobstreet.com/id/job/95140055"
    assert first.extra["page"] == 2
    assert first.extra["salary_raw"].startswith("Rp")
    assert first.extra["work_mode_raw"] == "On-site"
    assert first.extra["employment_type_raw"] == "Full time"


def test_search_payload_sorted_newest_first():
    payload = json.loads((FIXTURES / "search_backend.json").read_text(encoding="utf-8"))
    dates = [p.posted_raw for p in parse_search_payload(payload)]
    assert dates == sorted(dates, reverse=True)


def test_search_payload_invalid_shape():
    with pytest.raises(SiteChangedError):
        parse_search_payload({"unexpected": True})


def test_detail_onsite_with_salary():
    raw = parse_detail_html(html("detail_95140055.html"), listing(work_mode_raw="On-site"))
    assert raw.external_id == "95140055"
    assert raw.title == "Software Engineer"
    assert raw.company == "PetroSYNC"
    assert raw.location_raw == "Jakarta Barat, Jakarta Raya"
    assert raw.posted_raw.startswith("2026-10-08T05:44:02")
    assert raw.work_mode_raw == "onsite"
    assert raw.employment_type_raw == "fulltime"
    assert len(raw.description_text) > 1000
    assert raw.description_truncated is False
    assert raw.expires_raw.startswith("2026-11-")
    salary = parse_salary(raw.salary_raw)
    assert (salary.minimum, salary.maximum) == (5_800_000, 7_000_000)


def test_detail_hybrid_without_salary():
    raw = parse_detail_html(html("detail_95366834.html"), listing("95366834"))
    assert raw.title.startswith("Senior Backend Engineer")
    assert raw.work_mode_raw == "hybrid"
    assert raw.salary_raw is None
    assert raw.posted_raw == "2026-10-20T01:20:50.779Z"
    assert "backend" in raw.description_text.lower()


def test_detail_contract():
    raw = parse_detail_html(html("detail_95226394.html"), listing("95226394"))
    assert raw.employment_type_raw == "contract"
    assert raw.work_mode_raw == "hybrid"


def test_detail_internship_listing():
    raw = parse_detail_html(html("detail_95542339.html"), listing("95542339"))
    assert "Intern" in raw.title
    assert len(raw.description_text) > 500


def test_detail_all_fixtures_have_required_fields():
    for path in sorted(FIXTURES.glob("detail_*.html")):
        job_id = path.stem.split("_", 1)[1]
        raw = parse_detail_html(path.read_text(encoding="utf-8"), listing(job_id))
        assert raw.title, path.name
        assert raw.url.endswith(job_id)
        assert len(raw.description_text) >= 150, path.name


def test_detail_dom_fallback_when_state_missing():
    source = html("detail_95140055.html")
    stripped = re.sub(
        r"<script data-automation=\"server-state\">.*?</script>", "", source, flags=re.S
    )
    assert extract_redux_state(stripped) is None
    raw = parse_detail_html(stripped, listing())
    assert raw.title == "Software Engineer"
    assert raw.company == "PetroSYNC"
    assert len(raw.description_text) > 1000


def test_challenge_detection():
    assert detect_challenge(
        "<html><title>Tunggu sebentar...</title></html>", "https://id.jobstreet.com/id/job/1"
    )
    assert detect_challenge("<html>Just a moment...</html>", "https://x.test/")
    assert not detect_challenge(
        "<html><title>Software Engineer</title></html>", "https://id.jobstreet.com/id/job/1"
    )
