from __future__ import annotations

import re
from dataclasses import dataclass

_CONFIDENTIAL_RE = re.compile(
    r"negotiat|negosiasi|dirahasiakan|confidential|kompetitif|competitive|"
    r"sesuai kualifikasi|undisclosed",
    re.I,
)
_AMT_RE = re.compile(
    r"(?<![\d.,])(\d{1,3}(?:[.,]\d{3})+|\d+(?:[.,]\d+)?)\s*"
    r"(ribu|rb|k|juta|jt|mn|miliar|b)?(?![\w])",
    re.I,
)
_MULT = {
    "k": 1_000,
    "rb": 1_000,
    "ribu": 1_000,
    "juta": 1_000_000,
    "jt": 1_000_000,
    "mn": 1_000_000,
    "miliar": 1_000_000_000,
    "b": 1_000_000_000,
}
_PERIODS = [
    ("hour", re.compile(r"per jam|/\s*jam|per hour|/\s*hour|hourly|jam\b", re.I)),
    ("day", re.compile(r"per hari|/\s*hari|per day|/\s*day|daily|hari\b", re.I)),
    ("week", re.compile(r"per minggu|/\s*minggu|per week|/\s*week|weekly", re.I)),
    (
        "year",
        re.compile(
            r"per tahun|/\s*tahun|per year|/\s*year|per annum|annually|"
            r"yearly|p\.?a\.?\b",
            re.I,
        ),
    ),
    ("month", re.compile(r"per bulan|/\s*bulan|per month|/\s*month|monthly|/\s*mo\b", re.I)),
]
_THOUSANDS_RE = re.compile(r"\d{1,3}(?:[.,]\d{3})+")
_PROJECT_RE = re.compile(r"per project|/\s*project|project[-\s]based", re.I)


@dataclass(slots=True)
class SalaryInfo:
    raw: str | None = None
    minimum: int | None = None
    maximum: int | None = None
    currency: str | None = None
    period: str | None = None


def _to_number(token: str) -> float | None:
    if _THOUSANDS_RE.fullmatch(token):
        return float(re.sub(r"[.,]", "", token))
    if "." in token and "," in token:
        token = token.replace(".", "").replace(",", ".")
    elif "," in token:
        token = token.replace(",", ".")
    try:
        return float(token)
    except ValueError:
        return None


def _detect_currency(text: str) -> str:
    if re.search(r"\busd|us\$|\$", text):
        return "USD"
    if re.search(r"\bsgd|s\$", text):
        return "SGD"
    if re.search(r"\bmyr|rm\b", text):
        return "MYR"
    if re.search(r"\beur|€", text):
        return "EUR"
    return "IDR"


def parse_salary(raw: str | None) -> SalaryInfo:
    if not raw or not raw.strip():
        return SalaryInfo()
    text = raw.replace("\u00a0", " ").strip()
    if _CONFIDENTIAL_RE.search(text):
        return SalaryInfo()

    currency = _detect_currency(text.lower())
    project = bool(_PROJECT_RE.search(text))
    period = next((name for name, rx in _PERIODS if rx.search(text)), None)

    matches: list[tuple[float, int, int, int]] = []
    for m in _AMT_RE.finditer(text):
        number = _to_number(m.group(1))
        if number is None:
            continue
        unit = (m.group(2) or "").lower()
        matches.append((number, _MULT.get(unit, 1), m.start(), m.end()))

    max_mult = max((mult for _, mult, _, _ in matches), default=1)
    gap_re = re.compile(r"^\s*(?:-|–|—|to|s/d|sampai)\s*$", re.I)
    found: list[float] = []
    for idx, (number, mult, _start, end) in enumerate(matches):
        if mult == 1:
            if max_mult > 1 and number < 1000:
                gap = text[end : matches[idx + 1][2]] if idx + 1 < len(matches) else ""
                if not gap_re.match(gap):
                    continue
                value = number * max_mult
            elif number < 1000 and currency == "IDR":
                continue
            elif currency == "IDR" and 1900 <= number <= 2100:
                continue
            else:
                value = number
        else:
            value = number * mult
        found.append(value)

    if not found:
        return SalaryInfo(
            currency=currency if re.search(r"rp|idr|\$|sgd|usd|myr|eur", text, re.I) else None
        )

    values = [int(v) for v in found[:2]]
    minimum, maximum = min(values), max(values)
    if len(values) == 1:
        minimum = maximum = values[0]
    if period is None and not project:
        period = "month"
    return SalaryInfo(raw=text, minimum=minimum, maximum=maximum, currency=currency, period=period)
