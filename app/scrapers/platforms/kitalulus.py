from __future__ import annotations

from app.scrapers.platforms._placeholder import DiscoveryPendingScraper


class KitaLulusScraper(DiscoveryPendingScraper):
    platform = "kitalulus"
    requires_auth = False
