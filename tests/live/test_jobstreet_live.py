from __future__ import annotations

import pytest

from app.scrapers.base import ScrapeContext
from app.scrapers.browser import BrowserPool
from app.scrapers.platforms.jobstreet import JobStreetScraper

pytestmark = pytest.mark.live


async def test_jobstreet_live_smoke():
    pool = BrowserPool()
    ctx = ScrapeContext(
        run_id="live_jobstreet",
        max_age_days=7,
        max_jobs=3,
        fetch_details=True,
        max_pages_per_term=1,
        browser=pool,
    )
    try:
        scraper = JobStreetScraper(ctx)
        listings = [item async for item in scraper.iter_listings("software engineer")][:3]
        assert listings, "tidak ada listing dari JobStreet"
        first = listings[0]
        assert first.external_id and first.title
        raw = await scraper.fetch_detail(first)
        assert raw.title and len(raw.description_text) > 200
    finally:
        await pool.stop()
