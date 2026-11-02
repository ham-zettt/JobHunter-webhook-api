from __future__ import annotations

from collections.abc import AsyncIterator

from app.scrapers.base import BaseScraper, RawJob, RawListing
from app.scrapers.exceptions import SiteChangedError

DISCOVERY_MESSAGE = (
    "{platform}: scraper belum diimplementasikan. Jalankan discovery "
    "(SCRAPER_SPEC §3) lalu isi parser dan fixture."
)


class DiscoveryPendingScraper(BaseScraper):
    async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]:
        raise SiteChangedError(DISCOVERY_MESSAGE.format(platform=self.platform))
        yield RawListing(platform=self.platform, url="")  # pragma: no cover

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        raise SiteChangedError(DISCOVERY_MESSAGE.format(platform=self.platform))
