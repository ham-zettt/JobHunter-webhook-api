from __future__ import annotations

from pydantic import BaseModel


class ScrapeRequest(BaseModel):
    keywords: list[str] | None = None
    max_age_days: int | None = None
    max_jobs_per_platform: int | None = None
    fetch_details: bool = True
    callback_url: str | None = None
