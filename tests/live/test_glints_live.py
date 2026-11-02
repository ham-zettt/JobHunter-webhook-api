from __future__ import annotations

import pytest

from app.scrapers.base import ScrapeContext
from app.scrapers.platforms.glints import GlintsScraper

pytestmark = pytest.mark.live


async def test_glints_live_smoke():
    ctx = ScrapeContext(
        run_id="live_glints",
        max_age_days=14,
        max_jobs=3,
        fetch_details=True,
        max_pages_per_term=1,
    )
    scraper = GlintsScraper(ctx)
    listings = [item async for item in scraper.iter_listings("software engineer")][:3]
    assert listings, "tidak ada listing dari Glints"
    first = listings[0]
    assert first.external_id and first.title
    raw = await scraper.fetch_detail(first)
    assert raw.title and len(raw.description_text) > 200
    assert raw.work_mode_raw in ("remote", "hybrid", "onsite")
