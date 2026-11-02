from __future__ import annotations

from app.scrapers.platforms._placeholder import DiscoveryPendingScraper


class LinkedInScraper(DiscoveryPendingScraper):
    platform = "linkedin"
    requires_auth = True
