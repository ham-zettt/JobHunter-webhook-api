from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from app.core.config import get_settings
from app.scrapers.base import BaseScraper
from app.scrapers.platforms.dealls import DeallsScraper
from app.scrapers.platforms.glints import GlintsScraper
from app.scrapers.platforms.jobstreet import JobStreetScraper
from app.scrapers.platforms.kalibrr import KalibrrScraper
from app.scrapers.platforms.kitalulus import KitaLulusScraper
from app.scrapers.platforms.linkedin import LinkedInScraper
from app.scrapers.platforms.pintarnya import PintarnyaScraper

SCRAPERS: dict[str, type[BaseScraper]] = {
    "jobstreet": JobStreetScraper,
    "glints": GlintsScraper,
    "kalibrr": KalibrrScraper,
    "dealls": DeallsScraper,
    "kitalulus": KitaLulusScraper,
    "linkedin": LinkedInScraper,
    "pintarnya": PintarnyaScraper,
}

PLATFORM_ORDER = list(SCRAPERS)


@lru_cache
def platform_config() -> dict[str, dict[str, Any]]:
    path = Path(get_settings().config_dir) / "platforms.yaml"
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("platforms", {})


def enabled_platforms() -> list[str]:
    config = platform_config()
    return [p for p in PLATFORM_ORDER if config.get(p, {}).get("enabled", True)]


def reload_platform_config() -> None:
    platform_config.cache_clear()
