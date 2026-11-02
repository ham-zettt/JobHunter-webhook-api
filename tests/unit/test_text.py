from __future__ import annotations

from app.scrapers.common.text import (
    clean_text,
    html_to_text,
    looks_truncated,
    normalize_company,
    normalize_for_match,
)


def test_clean_text():
    assert clean_text("  Backend\u00a0Engineer\n\n\n\nJakarta  ") == "Backend Engineer\n\nJakarta"
    assert clean_text(None) == ""
    assert clean_text("A &amp; B") == "A & B"


def test_normalize_for_match():
    assert normalize_for_match("Back-end / Back_End!") == "back end back end"
    assert normalize_for_match("C++ & .NET") == "c++ .net"


def test_normalize_company():
    assert normalize_company("PT Contoh Teknologi Tbk.") == "contoh teknologi"
    assert normalize_company("") is None
    assert normalize_company(None) is None


def test_html_to_text():
    html = """
    <div>
      <h2>Tanggung Jawab</h2>
      <ul><li>Bangun API</li><li>Review kode</li></ul>
      <p>Gaji kompetitif</p><script>alert(1)</script>
      <table><tr><td>A</td><td>B</td></tr></table>
    </div>
    """
    text = html_to_text(html)
    assert "Tanggung Jawab" in text
    assert "- Bangun API" in text
    assert "Review kode" in text
    assert "alert" not in text
    assert "A | B" in text


def test_html_to_text_null():
    assert html_to_text(None) == ""


def test_truncation_detection():
    assert looks_truncated("")
    assert looks_truncated("Deskripsi singkat...")
    assert looks_truncated("Lihat selengkapnya")
    assert not looks_truncated("x" * 500)
