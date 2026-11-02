from __future__ import annotations

from datetime import datetime

from app.core.timeutil import age_days


def is_too_old(effective_date: str, max_age_days: int, now: datetime | None = None) -> bool:
    try:
        return age_days(effective_date, now) > max_age_days
    except ValueError:
        return False
