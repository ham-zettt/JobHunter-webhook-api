from __future__ import annotations

from types import SimpleNamespace

from app.pipeline.deduper import Deduper, compute_fingerprint
from app.pipeline.normalizer import NormalizedJob


def job(**overrides) -> NormalizedJob:
    base = dict(
        platform="jobstreet",
        url="https://example.com/1",
        url_canonical="https://example.com/1",
        title="Backend Engineer",
        title_normalized="backend engineer",
        description_text="Bangun API Python dan review kode. " * 5,
        description_hash="hash-a",
        effective_date="2026-10-30",
        posted_at="2026-10-30",
        external_id="1",
        company_name="PT Contoh",
        company_normalized="contoh",
        city="Jakarta Selatan",
        province="DKI Jakarta",
        work_mode="onsite",
        employment_type="fulltime",
    )
    base.update(overrides)
    item = NormalizedJob(**base)
    item.fingerprint = compute_fingerprint(item)
    return item


def candidate(**overrides) -> SimpleNamespace:
    base = dict(
        id=1,
        platform="jobstreet",
        external_id="1",
        url_canonical="https://example.com/1",
        title="Backend Engineer",
        company_normalized="contoh",
        city="Jakarta Selatan",
        province="DKI Jakarta",
        work_mode="onsite",
        employment_type="fulltime",
        description_text="Bangun API Python dan review kode. " * 5,
        description_hash="hash-a",
        posted_at="2026-10-30",
    )
    base.update(overrides)
    return SimpleNamespace(**base)


def test_identity_update():
    decision = Deduper().decide(job(), [candidate()])
    assert decision.action == "update"
    assert decision.of_id == 1


def test_url_canonical_update():
    decision = Deduper().decide(job(external_id=None), [candidate(external_id=None)])
    assert decision.action == "update"


def test_repost_same_platform_new_id():
    decision = Deduper().decide(
        job(external_id="2", url_canonical="https://example.com/2"),
        [candidate(id=7, external_id="1")],
    )
    assert decision.action == "duplicate"
    assert decision.reason == "repost"
    assert decision.of_id == 7


def test_repost_different_city_is_new():
    decision = Deduper().decide(
        job(
            external_id="2",
            url_canonical="https://example.com/2",
            city="Surabaya",
            province="Jawa Timur",
        ),
        [candidate()],
    )
    assert decision.action == "new"


def test_repost_different_seniority_is_new():
    decision = Deduper().decide(
        job(
            external_id="2",
            url_canonical="https://example.com/2",
            title="Senior Backend Engineer",
            title_normalized="senior backend engineer",
            description_hash="hash-b",
            description_text="Isi berbeda sama sekali tentang arsitektur sistem.",
        ),
        [candidate()],
    )
    assert decision.action == "new"


def test_repost_different_tech_is_new():
    decision = Deduper().decide(
        job(
            external_id="2",
            url_canonical="https://example.com/2",
            title="Backend (Go)",
            description_hash="hash-b",
            description_text="Bangun service Go.",
        ),
        [candidate(title="Backend (Java)", description_hash="hash-a")],
    )
    assert decision.action == "new"


def test_cross_platform_duplicate():
    decision = Deduper().decide(
        job(platform="glints", external_id="g1", url_canonical="https://glints.com/1"),
        [candidate(id=9)],
    )
    assert decision.action == "duplicate"
    assert decision.reason == "cross_platform"
    assert decision.of_id == 9


def test_cross_platform_different_city_new():
    decision = Deduper().decide(
        job(platform="glints", city="Bandung", province="Jawa Barat"),
        [candidate()],
    )
    assert decision.action == "new"


def test_cross_platform_low_description_similarity_new():
    decision = Deduper().decide(
        job(platform="glints", description_text="Lowongan sales marketing di mall."),
        [candidate()],
    )
    assert decision.action == "new"


def test_cross_platform_old_posting_new():
    decision = Deduper().decide(
        job(platform="glints", posted_at="2026-09-01"),
        [candidate()],
    )
    assert decision.action == "new"
