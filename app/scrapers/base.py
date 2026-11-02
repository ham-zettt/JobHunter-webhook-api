from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass(slots=True)
class RawListing:
    platform: str
    url: str
    title: str = ""
    external_id: str | None = None
    company: str | None = None
    location_raw: str | None = None
    posted_raw: str | None = None
    snippet: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RawJob:
    platform: str
    url: str
    title: str
    description_text: str
    external_id: str | None = None
    company: str | None = None
    location_raw: str | None = None
    posted_raw: str | None = None
    salary_raw: str | None = None
    work_mode_raw: str | None = None
    employment_type_raw: str | None = None
    expires_raw: str | None = None
    description_html: str | None = None
    description_truncated: bool = False
    extra: dict[str, Any] = field(default_factory=dict)
    raw_payload: dict[str, Any] | None = None


@dataclass(slots=True)
class ScrapeContext:
    run_id: str
    max_age_days: int
    max_jobs: int
    fetch_details: bool = True
    search_terms: list[str] = field(default_factory=list)
    max_pages_per_term: int = 6
    browser: Any = None
    stop_requested: bool = False

    def request_stop(self) -> None:
        self.stop_requested = True


class BaseScraper(ABC):
    platform: ClassVar[str]
    requires_auth: ClassVar[bool] = False

    def __init__(self, ctx: ScrapeContext) -> None:
        self.ctx = ctx

    @abstractmethod
    def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        """Hasilkan listing terbaru lebih dulu; berhenti saat lewat usia/maks."""

    @abstractmethod
    async def fetch_detail(self, listing: RawListing) -> RawJob:
        """Ambil deskripsi lengkap dari halaman detail."""

    async def check_session(self) -> None:
        return None
