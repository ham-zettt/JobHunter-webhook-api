from __future__ import annotations

from app.scrapers.platforms._placeholder import DiscoveryPendingScraper


class KalibrrScraper(DiscoveryPendingScraper):
    platform = "kalibrr"
    requires_auth = False
