from __future__ import annotations

from app.scrapers.platforms._placeholder import DiscoveryPendingScraper


class PintarnyaScraper(DiscoveryPendingScraper):
    platform = "pintarnya"
    requires_auth = False
