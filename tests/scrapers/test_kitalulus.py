from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.scrapers.browser import detect_challenge
from app.scrapers.common.salary import parse_salary
from app.scrapers.exceptions import ParseError, SiteChangedError
from app.scrapers.platforms.kitalulus import (
    parse_detail_payload,
    parse_listing_payload,
)

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures" / "kitalulus"


def html(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_listing_developer_first_card():
    listings = parse_listing_payload(html("search_developer.html"))
    assert len(listings) == 30
    first = listings[0]
    assert first.external_id == "misi-seru-remote-hadiah-puluhan-ribu-freelance-dar-xxja"
    assert first.url == (
        "https://www.kitalulus.com/lowongan/detail/"
        "misi-seru-remote-hadiah-puluhan-ribu-freelance-dar-xxja"
    )
    assert first.title.startswith("Lowongan Admin Freelance WFH")
    assert first.company == "Misi Seru - KitaLulus"
    assert first.location_raw == "Jakarta Selatan, DKI Jakarta"
    assert first.extra["pendidikan"] == "Minimal SMA/SMK/Sederajat"
    assert first.extra["salary_raw"] == "Dapat Dinegosiasikan"
    assert first.extra["promoted"] is True
    assert first.extra["updated_at_str"] == "Terakhir diperbarui hari ini"


def test_listing_has_no_posting_date():
    listings = parse_listing_payload(html("search_developer.html"))
    backend = next(item for item in listings if item.external_id == "backend-developer-dpfd")
    assert backend.posted_raw is None
    assert backend.location_raw == "Kabupaten Lampung Tengah, Lampung"


def test_listing_software_engineer_small_result():
    listings = parse_listing_payload(html("search_software_engineer.html"))
    assert len(listings) == 2
    assert all(item.posted_raw is None for item in listings)


def test_listing_location_filter():
    listings = parse_listing_payload(html("search_developer_jakarta.html"))
    assert len(listings) == 12
    assert all(item.location_raw for item in listings)


def test_listing_after_load_more_deduplicates():
    listings = parse_listing_payload(html("search_developer_page2.html"))
    assert len(listings) == 40
    slugs = [item.external_id for item in listings]
    assert len(set(slugs)) == 40
    assert slugs[0] == "misi-seru-remote-hadiah-puluhan-ribu-freelance-dar-xxja"


def test_listing_invalid_page():
    with pytest.raises(SiteChangedError):
        parse_listing_payload("<html><body>kosong</body></html>")


def test_detail_fullstack_salary_and_extra():
    raw = parse_detail_payload(
        html("detail_fullstack-developer-angular-java-spring-bootout-gdvm.html")
    )
    assert raw.external_id == "fullstack-developer-angular-java-spring-bootout-gdvm"
    assert raw.title.startswith("Fullstack Developer")
    assert raw.company == "PT Padepokan Tujuh Sembilan"
    assert raw.location_raw == "Jakarta Selatan, DKI Jakarta"
    assert raw.posted_raw == "2026-11-01T01:31:36.000Z"
    assert raw.expires_raw == "2026-11-27T17:00:00.000Z"
    assert raw.employment_type_raw == "contract"
    assert raw.work_mode_raw == "onsite"
    salary = parse_salary(raw.salary_raw)
    assert (salary.minimum, salary.maximum) == (6_000_000, 9_700_000)
    assert salary.currency == "IDR"
    assert raw.extra["pendidikan"] == "Minimal S1"
    assert raw.extra["pengalaman_bulan"] == 24
    assert "Angular" in raw.extra["skill"]
    assert "BPJS" in raw.extra["benefit"]
    assert raw.extra["kategori"]
    assert len(raw.description_text) > 1000
    assert raw.description_truncated is False


def test_detail_backend_without_salary():
    raw = parse_detail_payload(html("detail_backend-developer-dpfd.html"))
    assert raw.title == "Back-end Developer"
    assert raw.posted_raw == "2026-11-02T14:00:58.000Z"
    assert raw.salary_raw is None
    assert raw.employment_type_raw == "fulltime"
    assert raw.work_mode_raw == "onsite"
    assert raw.extra["pendidikan"] == "Minimal D3/D4"
    assert raw.extra["pengalaman_bulan"] == 12
    assert raw.extra["skill"]
    assert raw.extra["benefit"]


def test_detail_qa_salary():
    raw = parse_detail_payload(html("detail_quality-assurance-qa-muvz.html"))
    assert raw.title == "Quality Assurance (QA)"
    assert raw.company == "PT Shelter Indonesia"
    salary = parse_salary(raw.salary_raw)
    assert (salary.minimum, salary.maximum) == (4_500_000, 5_187_681)


def test_detail_internship():
    raw = parse_detail_payload(html("detail_mobile-developer-intern-vqgu.html"))
    assert raw.employment_type_raw == "internship"
    assert raw.posted_raw == "2026-10-13T10:18:25.000Z"
    assert len(raw.description_text) > 200


def test_detail_remote_freelance():
    raw = parse_detail_payload(
        html("detail_misi-seru-remote-hadiah-puluhan-ribu-freelance-dar-xxja.html")
    )
    assert raw.work_mode_raw == "remote"
    assert raw.employment_type_raw == "freelance"
    assert raw.posted_raw == "2026-11-02T13:17:38.000Z"
    assert raw.description_text


def test_detail_education_and_benefit_extra():
    raw = parse_detail_payload(html("detail_admin-lsin.html"))
    assert raw.extra["pendidikan"] == "Minimal S1"
    assert raw.extra["skill"] == ["Administrasi"]
    assert raw.extra["benefit"] is None
    assert raw.salary_raw is None


def test_detail_without_date_is_none():
    source = re.sub(r'"datePosted":"[^"]+",', "", html("detail_backend-developer-dpfd.html"))
    raw = parse_detail_payload(source)
    assert raw.posted_raw is None


def test_detail_all_fixtures_are_complete():
    for path in sorted(FIXTURES.glob("detail_*.html")):
        raw = parse_detail_payload(path.read_text(encoding="utf-8"))
        assert raw.platform == "kitalulus", path.name
        assert raw.title, path.name
        assert raw.url.endswith(raw.external_id or ""), path.name
        assert raw.company, path.name
        assert raw.location_raw, path.name
        assert len(raw.description_text) >= 100, path.name
        assert isinstance(raw.extra, dict), path.name


def test_detail_invalid_page():
    with pytest.raises(SiteChangedError):
        parse_detail_payload("<html><body>kosong</body></html>")


def test_detail_empty_description():
    source = (
        '<html><head><script type="application/ld+json">'
        '{"@type":"JobPosting","title":"Kosong"}</script></head><body></body></html>'
    )
    with pytest.raises(ParseError):
        parse_detail_payload(source)


def test_fixtures_are_not_challenge_pages():
    search_url = "https://www.kitalulus.com/lowongan?keyword=developer"
    for name in ("search_developer.html", "search_developer_page2.html"):
        assert not detect_challenge(html(name), search_url)
    assert not detect_challenge(
        html("detail_backend-developer-dpfd.html"),
        "https://www.kitalulus.com/lowongan/detail/backend-developer-dpfd",
    )
