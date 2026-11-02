from __future__ import annotations


class ScraperError(Exception):
    """Kesalahan scraper yang dapat ditangani orchestrator."""

    code = "SCRAPER_ERROR"

    def __init__(self, message: str = "", *, url: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.url = url


class TransientNetworkError(ScraperError):
    code = "TRANSIENT_NETWORK"


class BlockedError(ScraperError):
    code = "BLOCKED"


class AuthRequiredError(ScraperError):
    code = "AUTH_REQUIRED"


class SiteChangedError(ScraperError):
    code = "SITE_CHANGED"


class ParseError(ScraperError):
    code = "PARSE_ERROR"
