from __future__ import annotations

from types import SimpleNamespace

from app.pipeline.deduper import Deduper, compute_fingerprint
from app.pipeline.normalizer import NormalizedJob
from app.scrapers.common.text import normalize_company


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
        duplicate_of_id=None,
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


def test_case_09_fulltime_vs_internship_is_new():
    decision = Deduper().decide(
        job(
            external_id="2",
            url_canonical="https://example.com/2",
            employment_type="internship",
        ),
        [candidate(employment_type="fulltime")],
    )
    assert decision.action == "new"


def test_case_10_hidden_company_strict_mode_duplicate():
    decision = Deduper().decide(
        job(platform="glints", company_normalized=None),
        [candidate()],
    )
    assert decision.action == "duplicate"
    assert decision.reason == "cross_platform"


def test_case_11_hidden_company_low_description_is_new():
    decision = Deduper().decide(
        job(
            platform="glints",
            company_normalized=None,
            description_text="Bangun API Python dan review kode. " * 4
            + "Tulis test otomatis untuk endpoint.",
        ),
        [candidate()],
    )
    assert decision.action == "new"


def test_case_12_company_legal_suffix_ignored():
    a = job(
        platform="glints",
        company_name="PT Maju Jaya Tbk",
        company_normalized=normalize_company("PT Maju Jaya Tbk"),
    )
    b = candidate(company_normalized=normalize_company("Maju Jaya"))
    assert a.company_normalized == b.company_normalized == "maju jaya"
    decision = Deduper().decide(a, [b])
    assert decision.action == "duplicate"
    assert decision.reason == "cross_platform"


def test_case_13_remote_vs_onsite_is_new():
    decision = Deduper().decide(
        job(platform="glints", work_mode="remote", city=None, province=None),
        [candidate(work_mode="onsite")],
    )
    assert decision.action == "new"


def test_case_14_duplicate_chain_resolves_to_root():
    decision = Deduper().decide(
        job(platform="glints", external_id="c", url_canonical="https://example.com/c"),
        [candidate(id=2, duplicate_of_id=1)],
    )
    assert decision.action == "duplicate"
    assert decision.of_id == 1
