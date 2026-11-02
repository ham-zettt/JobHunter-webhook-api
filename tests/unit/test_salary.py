from __future__ import annotations

from app.scrapers.common.salary import parse_salary


def test_range_idr():
    s = parse_salary("Rp 12.000.000 – Rp 18.000.000 per bulan")
    assert (s.minimum, s.maximum, s.currency, s.period) == (12_000_000, 18_000_000, "IDR", "month")


def test_short_range_with_unit_at_end():
    s = parse_salary("8-12 juta")
    assert (s.minimum, s.maximum) == (8_000_000, 12_000_000)


def test_single_amount():
    s = parse_salary("Rp 5.000.000")
    assert (s.minimum, s.maximum, s.period) == (5_000_000, 5_000_000, "month")


def test_confidential_clears_everything():
    for raw in ("Negosiasi", "Dirahasiakan", "Competitive salary"):
        s = parse_salary(raw)
        assert s.raw is None
        assert s.minimum is None and s.maximum is None


def test_usd():
    s = parse_salary("$1,000 - $2,000 per month")
    assert (s.minimum, s.maximum, s.currency) == (1_000, 2_000, "USD")


def test_per_day():
    s = parse_salary("Rp 100.000 per hari")
    assert (s.minimum, s.period) == (100_000, "day")


def test_decimal_million():
    s = parse_salary("Rp 8,5 juta per bulan")
    assert s.minimum == 8_500_000


def test_year_is_not_amount():
    s = parse_salary("Gaji 5 juta, 2 tahun pengalaman")
    assert s.maximum == 5_000_000


def test_no_amount():
    s = parse_salary("Gaji tidak dicantumkan")
    assert s.minimum is None
    assert s.currency is None
