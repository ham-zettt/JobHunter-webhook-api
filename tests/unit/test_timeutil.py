from __future__ import annotations

from datetime import UTC, datetime

from app.core.timeutil import (
    PRECISION_DATE,
    PRECISION_EXACT,
    PRECISION_RELATIVE,
    PRECISION_UNKNOWN,
    age_days,
    parse_posted,
    to_wib,
    utc_iso,
    wib_date,
)

NOW = datetime(2026, 11, 1, 2, 10, tzinfo=UTC)


def check(raw: str | None, value: str | None, precision: str) -> None:
    parsed = parse_posted(raw, NOW)
    assert parsed.value == value, raw
    assert parsed.precision == precision, raw


def test_empty_and_unknown():
    assert parse_posted(None, NOW).precision == PRECISION_UNKNOWN
    assert parse_posted("   ", NOW).value is None
    assert parse_posted("Lowongan ini tidak punya tanggal", NOW).value is None


def test_iso_date_and_datetime():
    check("2026-10-29", "2026-10-29", PRECISION_DATE)
    check("2026-10-29T17:30:00Z", "2026-10-30", PRECISION_EXACT)
    check("2026-10-29T10:00:00+07:00", "2026-10-29", PRECISION_EXACT)
    check("2026-10-29T23:30:00", "2026-10-29", PRECISION_EXACT)


def test_named_months():
    check("29 Oct 2026", "2026-10-29", PRECISION_DATE)
    check("29 Oktober 2026", "2026-10-29", PRECISION_DATE)
    check("Oct 29, 2026", "2026-10-29", PRECISION_DATE)
    check("Senin, 3 November 2026", "2026-11-03", PRECISION_DATE)


def test_numeric_date():
    check("29/10/2026", "2026-10-29", PRECISION_DATE)
    check("29-10-2026", "2026-10-29", PRECISION_DATE)
    check("31/02/2026", None, PRECISION_UNKNOWN)


def test_relative_indonesian():
    check("3 hari lalu", "2026-10-29", PRECISION_RELATIVE)
    check("30+ hari lalu", "2026-10-01", PRECISION_RELATIVE)
    check("1 bulan lalu", "2026-10-02", PRECISION_RELATIVE)
    check("2 minggu yang lalu", "2026-10-18", PRECISION_RELATIVE)
    check("5 jam lalu", "2026-11-01", PRECISION_RELATIVE)
    check("kemarin", "2026-10-31", PRECISION_RELATIVE)
    check("Hari ini", "2026-11-01", PRECISION_RELATIVE)


def test_relative_english():
    check("3 days ago", "2026-10-29", PRECISION_RELATIVE)
    check("2 weeks ago", "2026-10-18", PRECISION_RELATIVE)
    check("1 month ago", "2026-10-02", PRECISION_RELATIVE)
    check("Reposted 3 days ago", "2026-10-29", PRECISION_RELATIVE)
    check("yesterday", "2026-10-31", PRECISION_RELATIVE)
    check("Just now", "2026-11-01", PRECISION_RELATIVE)


def test_not_a_posting_date():
    check("Actively hiring 7d ago", None, PRECISION_UNKNOWN)
    check("Updated 3 days ago", None, PRECISION_UNKNOWN)
    check("Rekruter aktif 8j lalu", None, PRECISION_UNKNOWN)
    check("Diperbarui kemarin", None, PRECISION_UNKNOWN)


def test_helpers():
    assert to_wib(NOW).hour == 9
    assert wib_date(NOW) == "2026-11-01"
    assert utc_iso(NOW) == "2026-11-01T02:10:00Z"
    assert age_days("2026-10-29", NOW) == 3
