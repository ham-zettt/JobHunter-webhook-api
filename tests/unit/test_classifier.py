from __future__ import annotations

from app.pipeline.classifier import Classifier, KeywordSpec


def make_classifier(threshold: int = 50) -> Classifier:
    rules = [
        KeywordSpec("backend", "include", "strong", role_category="backend"),
        KeywordSpec("frontend", "include", "strong", role_category="frontend"),
        KeywordSpec("machine learning", "include", "strong", role_category="ai_engineer"),
        KeywordSpec("n8n", "include", "strong", role_category="ai_automation"),
        KeywordSpec("web", "include", "weak"),
        KeywordSpec("developer", "include", "weak"),
        KeywordSpec("it", "include", "weak"),
        KeywordSpec("it support", "exclude", scope="title"),
        KeywordSpec("sales", "exclude", scope="title"),
        KeywordSpec("marketing", "exclude", scope="title"),
        KeywordSpec("administrasi", "exclude", scope="both"),
    ]
    return Classifier(rules, threshold=threshold)


def test_strong_title_accepted():
    result = make_classifier().classify("Backend Engineer (Python)", "Bangun API.")
    assert result.accepted
    assert result.score >= 100
    assert result.role_category == "backend"
    assert "backend" in result.matched


def test_two_strong_titles_score_bonus():
    result = make_classifier().classify("Backend / Frontend Developer", "Fullstack work.")
    assert result.score >= 110
    assert result.role_category == "fullstack"


def test_weak_title_only_accepted():
    result = make_classifier().classify("Web Content Staff", "Menulis artikel.")
    assert result.accepted
    assert result.score == 40


def test_exclude_title_rejected_even_with_strong_description():
    result = make_classifier().classify(
        "IT Support", "Dibutuhkan backend engineer untuk machine learning project."
    )
    assert not result.accepted
    assert result.reason == "keyword"


def test_description_two_strong_accepted():
    result = make_classifier().classify(
        "Senior Engineer", "Kami butuh machine learning dan n8n automation."
    )
    assert result.accepted
    assert result.score >= 50
    assert result.role_category == "ai_automation"


def test_description_one_strong_rejected():
    result = make_classifier().classify("Senior Engineer", "Kami butuh machine learning.")
    assert not result.accepted


def test_description_penalty_reduces_score():
    result = make_classifier().classify(
        "Engineer", "machine learning administrasi administrasi administrasi"
    )
    assert result.score == 25 - 15
    assert not result.accepted


def test_no_match_rejected():
    result = make_classifier().classify("Office Boy", "Bersihkan kantor.")
    assert not result.accepted


def test_matched_keywords_capped_at_20():
    rules = [KeywordSpec(f"term{i}", "include", "strong") for i in range(30)]
    text = " ".join(f"term{i}" for i in range(30))
    result = Classifier(rules, threshold=50).classify("x", text)
    assert len(result.matched) <= 20
