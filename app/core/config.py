from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "production"
    api_key: str = ""
    log_level: str = "INFO"
    tz: str = "Asia/Jakarta"

    database_url: str = "sqlite+aiosqlite:///./data/jobs.db"
    sqlite_busy_timeout_ms: int = 5000

    default_max_age_days: int = 14
    max_age_days_limit: int = 90
    relevance_threshold: int = 50
    keep_unverified_location: bool = True
    store_rejected: bool = False
    detail_refresh_days: int = 3
    store_html: bool = True
    store_raw_payload: bool = False

    playwright_headless: bool = True
    nav_timeout_ms: int = 45000
    action_timeout_ms: int = 15000
    max_jobs_per_platform: int = 300
    platform_max_duration_sec: int = 1500
    debug_snapshot_max_files: int = 200

    linkedin_state_path: str = "./data/secrets/linkedin_state.json"
    linkedin_max_jobs_per_run: int = 60
    linkedin_max_jobs_per_day: int = 150

    callback_allowed_hosts: str = ""
    callback_timeout_sec: int = 10
    export_max_rows: int = 50000
    schedule_cron: str = ""

    config_dir: str = "config"

    @property
    def callback_allowed_host_set(self) -> set[str]:
        return {h.strip().lower() for h in self.callback_allowed_hosts.split(",") if h.strip()}

    @model_validator(mode="after")
    def _require_api_key_in_production(self) -> Settings:
        if self.app_env == "production" and not self.api_key:
            raise ValueError("API_KEY wajib diisi saat APP_ENV=production")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
