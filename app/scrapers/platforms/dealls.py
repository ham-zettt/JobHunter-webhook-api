from __future__ import annotations

from app.scrapers.platforms._placeholder import DiscoveryPendingScraper


class DeallsScraper(DiscoveryPendingScraper):
    platform = "dealls"
    requires_auth = False
