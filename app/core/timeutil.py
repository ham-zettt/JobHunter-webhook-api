from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

WIB = ZoneInfo("Asia/Jakarta")

PRECISION_EXACT = "exact"
PRECISION_DATE = "date"
PRECISION_RELATIVE = "relative"
PRECISION_UNKNOWN = "unknown"

_MONTHS = {
    "jan": 1,
    "januari": 1,
    "january": 1,
    "feb": 2,
    "februari": 2,
    "february": 2,
    "mar": 3,
    "maret": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "mei": 5,
    "jun": 6,
    "juni": 6,
    "june": 6,
    "jul": 7,
    "juli": 7,
    "july": 7,
    "aug": 8,
    "agu": 8,
    "agustus": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "okt": 10,
    "oktober": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "des": 12,
    "desember": 12,
    "december": 12,
}
_MONTH_RE = "|".join(sorted(_MONTHS, key=len, reverse=True))

_ISO_RE = re.compile(
    r"(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})"
    r"(?:[T ](?P<hh>\d{2}):(?P<mm>\d{2})(?::(?P<ss>\d{2}))?(?:\.\d+)?(?P<tz>Z|[+-]\d{2}:?\d{2})?)?"
)
_DMY_RE = re.compile(r"(?<!\d)(?P<d>\d{1,2})[/\-\.](?P<m>\d{1,2})[/\-\.](?P<y>\d{4})(?!\d)")
_D_MON_Y_RE = re.compile(
    rf"(?<!\d)(?P<d>\d{{1,2}})\s+(?P<mon>{_MONTH_RE})\b\.?,?\s+(?P<y>\d{{4}})(?!\d)", re.I
)
_MON_D_Y_RE = re.compile(
    rf"\b(?P<mon>{_MONTH_RE})\b\.?\s+(?P<d>\d{{1,2}}),?\s+(?P<y>\d{{4}})(?!\d)", re.I
)

_NOT_POSTED_RE = re.compile(
    r"actively hiring|rekruter aktif|last active|terakhir aktif|diperbarui|updated|"
    r"lowongan serupa|similar jobs|rekomendasi",
    re.I,
)

_UNIT_DAYS = {
    "detik": 0,
    "second": 0,
    "seconds": 0,
    "sec": 0,
    "s": 0,
    "menit": 0,
    "minute": 0,
    "minutes": 0,
    "min": 0,
    "jam": 0,
    "hour": 0,
    "hours": 0,
    "hari": 1,
    "day": 1,
    "days": 1,
    "d": 1,
    "minggu": 7,
    "week": 7,
    "weeks": 7,
    "w": 7,
    "bulan": 30,
    "month": 30,
    "months": 30,
    "mo": 30,
    "tahun": 365,
    "year": 365,
    "years": 365,
    "y": 365,
}
_REL_RE = re.compile(
    r"(?P<n>\d+)\s*(?P<plus>\+)?\s*"
    r"(?P<unit>detik|menit|jam|hari|minggu|bulan|tahun|seconds?|minutes?|hours?|days?|weeks?|months?|years?|sec|min|mo|d|h|w|y)"
    r"\s*(?:ago|lalu|yang lalu)\b",
    re.I,
)
_TODAY_RE = re.compile(r"\b(hari ini|today|baru saja|just now|just posted)\b", re.I)
_YESTERDAY_RE = re.compile(r"\b(kemarin|yesterday)\b", re.I)


@dataclass(frozen=True, slots=True)
class ParsedDate:
    value: str | None
    precision: str = PRECISION_UNKNOWN


def now_utc() -> datetime:
    return datetime.now(UTC)


def to_wib(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.astimezone(WIB)


def utc_iso(dt: datetime | None = None) -> str:
    return (dt or now_utc()).astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def wib_date(dt: datetime | None = None) -> str:
    return to_wib(dt or now_utc()).date().isoformat()


def wib_today(now: datetime | None = None) -> date:
    return to_wib(now or now_utc()).date()


def parse_posted(raw: str | None, now: datetime | None = None) -> ParsedDate:
    """Parse tanggal posting menjadi (YYYY-MM-DD WIB, presisi).

    Zona acuan: Asia/Jakarta. "Updated"/"Actively hiring" bukan tanggal posting.
    """
    if not raw or not raw.strip():
        return ParsedDate(None)
    text = raw.strip()
    ref = to_wib(now or now_utc())

    if _NOT_POSTED_RE.search(text):
        return ParsedDate(None)

    m = _ISO_RE.search(text)
    if m:
        try:
            day = date(int(m["y"]), int(m["m"]), int(m["d"]))
        except ValueError:
            day = None
        if day:
            if m["hh"] is not None:
                stamp = f"{day.isoformat()}T{m['hh']}:{m['mm']}:{m['ss'] or '00'}"
                dt = datetime.fromisoformat(stamp + (m["tz"] or ""))
                if dt.tzinfo is not None:
                    day = to_wib(dt).date()
                return ParsedDate(day.isoformat(), PRECISION_EXACT)
            return ParsedDate(day.isoformat(), PRECISION_DATE)

    m = _DMY_RE.search(text)
    if m:
        try:
            return ParsedDate(
                date(int(m["y"]), int(m["m"]), int(m["d"])).isoformat(), PRECISION_DATE
            )
        except ValueError:
            pass

    for regex in (_D_MON_Y_RE, _MON_D_Y_RE):
        m = regex.search(text)
        if m:
            mon = _MONTHS[m["mon"].lower()]
            try:
                return ParsedDate(date(int(m["y"]), mon, int(m["d"])).isoformat(), PRECISION_DATE)
            except ValueError:
                pass

    m = _REL_RE.search(text)
    if m:
        unit_days = _UNIT_DAYS[m["unit"].lower()]
        n = int(m["n"]) + (1 if m["plus"] else 0)
        return ParsedDate(
            (ref.date() - timedelta(days=n * unit_days)).isoformat(), PRECISION_RELATIVE
        )

    if _YESTERDAY_RE.search(text):
        return ParsedDate((ref.date() - timedelta(days=1)).isoformat(), PRECISION_RELATIVE)
    if _TODAY_RE.search(text):
        return ParsedDate(ref.date().isoformat(), PRECISION_RELATIVE)
    return ParsedDate(None)


def age_days(effective_date: str, now: datetime | None = None) -> int:
    d = date.fromisoformat(effective_date)
    return (wib_today(now) - d).days
