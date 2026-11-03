from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import timedelta
from typing import Any

from app.core.timeutil import wib_today
from app.scrapers.base import BaseScraper, RawJob, RawListing

DATA: list[dict[str, Any]] = []
PAGES: list[int] = []


class FakeJobstreetScraper(BaseScraper):
    platform = "jobstreet"

    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        for index, item in enumerate(DATA):
            yield RawListing(
                platform=self.platform,
                url=item["url"],
                external_id=item["external_id"],
                title=item["title"],
                company=item.get("company"),
                location_raw=item.get("location_raw"),
                posted_raw=item.get("posted_raw"),
                snippet=item.get("description", "")[:120],
                extra={"page": 1 + index // 20},
            )

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        item = next(i for i in DATA if i["url"] == listing.url)
        return RawJob(
            platform=self.platform,
            url=item["url"],
            external_id=item["external_id"],
            title=item["title"],
            company=item.get("company"),
            location_raw=item.get("location_raw"),
            posted_raw=item.get("posted_raw"),
            salary_raw=item.get("salary_raw"),
            work_mode_raw=item.get("work_mode_raw"),
            employment_type_raw=item.get("employment_type_raw"),
            description_text=item["description"],
        )


class FakeGlintsScraper(FakeJobstreetScraper):
    platform = "glints"


def seed_old_then_new(max_age_days: int = 30, old: int = 5) -> None:
    today = wib_today()
    old_date = (today - timedelta(days=max_age_days + 10)).isoformat()
    for index in range(old):
        DATA.append(
            {
                "url": f"https://id.jobstreet.com/job/old{index}",
                "external_id": f"old{index}",
                "title": "Backend Engineer",
                "company": "PT Tua",
                "location_raw": "Jakarta Selatan, DKI Jakarta",
                "posted_raw": old_date,
                "description": "Lowongan lama. " * 20,
            }
        )
    DATA.append(
        {
            "url": "https://id.jobstreet.com/job/new",
            "external_id": "new",
            "title": "Backend Engineer",
            "company": "PT Baru",
            "location_raw": "Jakarta Selatan, DKI Jakarta",
            "posted_raw": today.isoformat(),
            "description": "Lowongan baru. " * 20,
        }
    )


def reset() -> None:
    DATA.clear()
    PAGES.clear()


def seed_sample() -> None:
    DATA.extend(
        [
            {
                "url": "https://id.jobstreet.com/job/1",
                "external_id": "1",
                "title": "Backend Engineer",
                "company": "PT Contoh Teknologi",
                "location_raw": "Jakarta Selatan, DKI Jakarta",
                "salary_raw": "Rp 12.000.000 - Rp 18.000.000 per bulan",
                "work_mode_raw": "On-site",
                "employment_type_raw": "Full-time",
                "description": "Bangun API Python dan review kode. " * 20,
            },
            {
                "url": "https://id.jobstreet.com/job/2",
                "external_id": "2",
                "title": "AI Engineer",
                "company": "PT Contoh Teknologi",
                "location_raw": "Remote - Indonesia",
                "work_mode_raw": "Remote",
                "description": "Kembangkan machine learning dan LLM. " * 20,
            },
            {
                "url": "https://id.jobstreet.com/job/3",
                "external_id": "3",
                "title": "IT Support",
                "company": "PT Lain",
                "location_raw": "Bandung, Jawa Barat",
                "description": "Dukungan teknis kantor. " * 20,
            },
        ]
    )
