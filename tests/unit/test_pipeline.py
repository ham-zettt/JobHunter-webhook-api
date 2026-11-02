from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.core.config import get_settings
from app.pipeline.classifier import Classifier, KeywordSpec
from app.pipeline.location import LocationNormalizer
from app.pipeline.normalizer import canonical_url, detect_employment_type, detect_work_mode
from app.pipeline.pipeline import Pipeline
from app.scrapers.base import RawJob

NOW = datetime(2026, 11, 1, 2, 10, tzinfo=UTC)


@pytest.fixture(scope="module")
def classifier() -> Classifier:
    return Classifier(
        [
            KeywordSpec("backend", "include", "strong", role_category="backend"),
            KeywordSpec("frontend", "include", "strong", role_category="frontend"),
            KeywordSpec("machine learning", "include", "strong", role_category="ai_engineer"),
            KeywordSpec("it support", "exclude", scope="title"),
        ],
        threshold=50,
    )


@pytest.fixture(scope="module")
def location() -> LocationNormalizer:
    return LocationNormalizer(Path(get_settings().config_dir) / "locations_java.yaml")


def make_pipeline(classifier, location, **kwargs) -> Pipeline:
    return Pipeline(classifier, location, max_age_days=14, **kwargs)


def raw(**overrides) -> RawJob:
    base = dict(
        platform="jobstreet",
        url="https://id.jobstreet.com/job/123?ref=abc",
        external_id="123",
        title="Backend Engineer",
        company="PT Contoh Teknologi",
        location_raw="Jakarta Selatan, DKI Jakarta",
        posted_raw="2026-10-29",
        work_mode_raw="On-site",
        salary_raw="Rp 12.000.000 - Rp 18.000.000 per bulan",
        description_text="Bangun API Python. " * 10,
    )
    base.update(overrides)
    return RawJob(**base)


def test_happy_path(classifier, location):
    result = make_pipeline(classifier, location).process(raw(), first_seen=NOW)
    assert result.accepted
    assert result.filter_reason is None
    assert result.dedup is not None and result.dedup.action == "new"
    job = result.job
    assert job.url_canonical == "https://id.jobstreet.com/job/123"
    assert job.company_normalized == "contoh teknologi"
    assert job.city == "Jakarta Selatan"
    assert job.province == "DKI Jakarta"
    assert job.is_in_java == 1
    assert job.location_verified == 1
    assert job.work_mode == "onsite"
    assert job.salary_min == 12_000_000
    assert job.salary_max == 18_000_000
    assert job.posted_at_precision == "date"
    assert job.effective_date == "2026-10-29"
    assert job.matched_keywords == ["backend"]
    assert job.role_category == "backend"
    assert job.fingerprint


def test_remote_abroad_rejected(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(location_raw="Singapore", work_mode_raw="Remote"), first_seen=NOW
    )
    assert not result.accepted
    assert result.filter_reason == "location"


def test_remote_indonesia_accepted(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(location_raw="Remote - Indonesia", work_mode_raw="Remote"), first_seen=NOW
    )
    assert result.accepted
    assert result.job.work_mode == "remote"


def test_onsite_outside_java_rejected(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(location_raw="Medan, Sumatera Utara"), first_seen=NOW
    )
    assert not result.accepted
    assert result.filter_reason == "location"


def test_old_posting_rejected(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(posted_raw="2026-09-01"), first_seen=NOW
    )
    assert not result.accepted
    assert result.filter_reason == "age"


def test_irrelevant_title_rejected(classifier, location):
    result = make_pipeline(classifier, location).process(raw(title="IT Support"), first_seen=NOW)
    assert not result.accepted
    assert result.filter_reason == "keyword"


def test_unknown_date_uses_first_seen(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(posted_raw="Aktif merekrut"), first_seen=NOW
    )
    assert result.job.posted_at is None
    assert result.job.posted_at_precision == "unknown"
    assert result.job.effective_date == "2026-11-01"


def test_html_description_extracted(classifier, location):
    result = make_pipeline(classifier, location).process(
        raw(
            description_text="",
            description_html="<p>Bangun <b>API</b> backend</p><ul><li>Review</li></ul>",
        ),
        first_seen=NOW,
    )
    assert "Bangun API backend" in result.job.description_text
    assert "- Review" in result.job.description_text


def test_helpers():
    assert canonical_url("https://X.com/a/b/?q=1#frag") == "https://x.com/a/b"
    assert detect_work_mode("Remote") == "remote"
    assert detect_work_mode("Hybrid") == "hybrid"
    assert detect_work_mode("WFO") == "onsite"
    assert detect_work_mode(None) == "unknown"
    assert detect_employment_type("Magang") == "internship"
    assert detect_employment_type("Kontrak 6 bulan") == "contract"
    assert detect_employment_type("Full-time") == "fulltime"
    assert detect_employment_type("Part time") == "parttime"
    assert detect_employment_type("Freelance") == "freelance"


def test_age_filter_invalid_date(classifier, location):
    from app.pipeline.age_filter import is_too_old

    assert is_too_old("bukan-tanggal", 7, NOW) is False
