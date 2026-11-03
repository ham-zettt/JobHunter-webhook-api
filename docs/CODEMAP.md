# CODEMAP

Dihasilkan otomatis oleh `python scripts/codemap.py`. Jangan edit manual.
Hanya simbol publik; lihat file sumber untuk detail.

## `app/__init__.py`
(no docstring) __init__.py


## `app/api/__init__.py`
(no docstring) __init__.py


## `app/api/router.py`
(no docstring) router.py


## `app/api/routers/__init__.py`
(no docstring) __init__.py


## `app/api/routers/health.py`
(no docstring) health.py

- `async def health() -> dict`

## `app/api/routers/jobs.py`
(no docstring) jobs.py

- `async def list_jobs(filters: Filters)`
- `async def export_jobs(filters: Filters, format: str=Query(default='json'))`
- `async def get_job(job_id: int) -> dict`
- `async def patch_job(job_id: int, status: str=Body(embed=True)) -> dict`

## `app/api/routers/keywords.py`
(no docstring) keywords.py

- `async def list_keywords(type: str | None=Query(default=None), is_active: bool | None=Query(default=None)) -> list[dict]`
- `async def create_keyword(body: KeywordCreate) -> dict`
- `async def patch_keyword(rule_id: int, body: KeywordUpdate) -> dict`
- `async def delete_keyword(rule_id: int) -> None`
- `async def reseed() -> dict`

## `app/api/routers/platforms.py`
(no docstring) platforms.py

- `async def list_platforms() -> list[dict]`

## `app/api/routers/scrape.py`
(no docstring) scrape.py

- `async def scrape_all(body: ScrapeRequest | None=Body(default=None)) -> JSONResponse`
- `async def scrape_platform(platform: str, body: ScrapeRequest | None=Body(default=None)) -> JSONResponse`
- `async def list_runs(status: str | None=Query(default=None), limit: int=Query(default=20, ge=1, le=200), page: int=Query(default=1, ge=1)) -> dict`
- `async def get_run(run_id: str) -> dict`
- `async def cancel_run(run_id: str) -> dict`

## `app/api/schemas/__init__.py`
(no docstring) __init__.py


## `app/api/schemas/keyword.py`
(no docstring) keyword.py

- `class KeywordCreate` (BaseModel)
  - `def to_row(self) -> dict`
- `class KeywordUpdate` (BaseModel)
  - `def to_row(self) -> dict`

## `app/api/schemas/scrape.py`
(no docstring) scrape.py

- `class ScrapeRequest` (BaseModel)

## `app/core/__init__.py`
(no docstring) __init__.py


## `app/core/config.py`
(no docstring) config.py

- `class Settings` (BaseSettings)
  - `def callback_allowed_host_set(self) -> set[str]`
- `def get_settings() -> Settings`

## `app/core/errors.py`
(no docstring) errors.py

- `class AppError` (Exception)
- `class UnauthorizedError` (AppError)
- `class NotFoundError` (AppError)
- `class PlatformNotFoundError` (NotFoundError)
- `class RunNotFoundError` (NotFoundError)
- `class ConflictError` (AppError)
- `class PlatformDisabledError` (ConflictError)
- `class RunNotCancellableError` (ConflictError)
- `class ValidationAppError` (AppError)
- `class ServiceUnavailableError` (AppError)
- `def install_handlers(app: FastAPI) -> None`

## `app/core/logging.py`
(no docstring) logging.py

- `def setup_logging() -> None`
- `def get_logger(name: str='app') -> structlog.stdlib.BoundLogger`

## `app/core/security.py`
(no docstring) security.py

- `async def require_api_key(x_api_key: str | None=Header(default=None)) -> None`

## `app/core/timeutil.py`
(no docstring) timeutil.py

- `class ParsedDate`
- `def now_utc() -> datetime`
- `def to_wib(dt: datetime) -> datetime`
- `def utc_iso(dt: datetime | None=None) -> str`
- `def wib_date(dt: datetime | None=None) -> str`
- `def wib_today(now: datetime | None=None) -> date`
- `def parse_posted(raw: str | None, now: datetime | None=None) -> ParsedDate` — Parse tanggal posting menjadi (YYYY-MM-DD WIB, presisi).
- `def age_days(effective_date: str, now: datetime | None=None) -> int`

## `app/db/__init__.py`
(no docstring) __init__.py


## `app/db/base.py`
(no docstring) base.py

- `class Base` (DeclarativeBase)

## `app/db/models/__init__.py`
(no docstring) __init__.py


## `app/db/models/job.py`
(no docstring) job.py

- `class Job` (Base)

## `app/db/models/keyword_rule.py`
(no docstring) keyword_rule.py

- `class KeywordRule` (Base)
- `class LocationAlias` (Base)

## `app/db/models/scrape_run.py`
(no docstring) scrape_run.py

- `class ScrapeRun` (Base)
- `class ScrapeRunSource` (Base)
- `class JobRunLink` (Base)

## `app/db/repositories/__init__.py`
(no docstring) __init__.py


## `app/db/repositories/job_repo.py`
(no docstring) job_repo.py

- `class JobFilters`
- `def api_dict(job: Job, *, include_description: bool=True, siblings: int=0) -> dict[str, Any]`
- `def build_query(filters: JobFilters, *, use_fts: bool=True)`
- `async def list_jobs(session: AsyncSession, filters: JobFilters) -> tuple[list[Job], int]`
- `async def export_jobs(session: AsyncSession, filters: JobFilters, max_rows: int) -> list[Job]`
- `async def get_job(session: AsyncSession, job_id: int) -> Job | None`
- `async def sibling_count(session: AsyncSession, job_id: int) -> int`
- `async def find_known(session: AsyncSession, platform: str, external_id: str | None, url_canonical: str) -> Job | None`
- `async def find_candidates(session: AsyncSession, job: NormalizedJob) -> list[Job]`
- `async def insert_new(session: AsyncSession, result: PipelineResult, run_id: str, now: str | None=None) -> Job`
- `async def insert_duplicate(session: AsyncSession, result: PipelineResult, run_id: str, now: str | None=None) -> Job`
- `async def update_existing(session: AsyncSession, row: Job, result: PipelineResult, run_id: str, now: str | None=None) -> Job`
- `async def touch_existing(session: AsyncSession, row: Job, run_id: str, now: str | None=None) -> Job`
- `async def add_link(session: AsyncSession, run_id: str, job_id: int, action: str, now: str | None=None) -> None`
- `async def set_status(session: AsyncSession, job_id: int, status: str) -> Job | None`
- `async def count_jobs_by_platform(session: AsyncSession) -> dict[str, int]`
- `def to_filters(**kwargs: Any) -> JobFilters`
- `def iter_jsonl(rows: Iterable[dict[str, Any]])`

## `app/db/repositories/keyword_repo.py`
(no docstring) keyword_repo.py

- `def rule_dict(rule: KeywordRule) -> dict[str, Any]`
- `async def list_rules(session: AsyncSession, *, type_: str | None=None, is_active: bool | None=None) -> list[KeywordRule]`
- `async def active_rules(session: AsyncSession) -> list[KeywordRule]`
- `async def search_terms(session: AsyncSession, limit: int) -> list[str]`
- `async def create_rule(session: AsyncSession, data: dict[str, Any]) -> KeywordRule`
- `async def update_rule(session: AsyncSession, rule_id: int, data: dict[str, Any]) -> KeywordRule`
- `async def delete_rule(session: AsyncSession, rule_id: int) -> None`
- `async def reseed(session: AsyncSession) -> dict[str, int]`

## `app/db/repositories/run_repo.py`
(no docstring) run_repo.py

- `async def create_run(session: AsyncSession, *, run_id: str, platforms: list[str], params: dict[str, Any], trigger: str='api', callback_url: str | None=None) -> ScrapeRun`
- `async def get_run(session: AsyncSession, run_id: str) -> ScrapeRun | None`
- `async def list_runs(session: AsyncSession, *, status: str | None=None, limit: int=20, page: int=1) -> tuple[list[ScrapeRun], int]`
- `async def sources_for(session: AsyncSession, run_id: str) -> list[ScrapeRunSource]`
- `async def get_source(session: AsyncSession, run_id: str, platform: str) -> ScrapeRunSource`
- `async def start_run(session: AsyncSession, run: ScrapeRun) -> None`
- `async def finish_run(session: AsyncSession, run: ScrapeRun, status: str, error: str | None=None) -> None`
- `async def start_source(session: AsyncSession, source: ScrapeRunSource) -> None`
- `async def finish_source(session: AsyncSession, source: ScrapeRunSource, status: str) -> None`
- `def add_error(source: ScrapeRunSource, code: str, message: str, url: str | None=None) -> None`
- `async def recover(session: AsyncSession) -> list[str]`
- `async def cancel_run(session: AsyncSession, run: ScrapeRun) -> None`
- `async def details_fetched_since(session: AsyncSession, platform: str, since_iso: str) -> int`
- `async def productive_terms(session: AsyncSession, platform: str, terms: list[str]) -> set[str]` — Term yang pernah menghasilkan listing pada sub-run sukses (canary §5.3).
- `async def last_source_by_platform(session: AsyncSession) -> dict[str, ScrapeRunSource]`
- `def source_dict(source: ScrapeRunSource) -> dict[str, Any]`
- `def run_dict(run: ScrapeRun, sources: list[ScrapeRunSource]) -> dict[str, Any]`

## `app/db/schema.py`
(no docstring) schema.py

- `def ensure_schema_sync(conn: Connection) -> None`
- `async def ensure_schema(engine: AsyncEngine) -> None`

## `app/db/session.py`
(no docstring) session.py

- `def configure(database_url: str | None=None, busy_timeout_ms: int | None=None) -> None`
- `async def get_session() -> AsyncIterator[AsyncSession]`

## `app/main.py`
(no docstring) main.py

- `async def lifespan(_: FastAPI)`
- `def create_app() -> FastAPI`

## `app/pipeline/__init__.py`
(no docstring) __init__.py


## `app/pipeline/age_filter.py`
(no docstring) age_filter.py

- `def is_too_old(effective_date: str, max_age_days: int, now: datetime | None=None) -> bool`

## `app/pipeline/classifier.py`
(no docstring) classifier.py

- `class KeywordSpec`
  - `def from_row(cls, row: Any) -> KeywordSpec`
- `class Classification`
- `class Classifier`
  - `def from_rows(cls, rows: Iterable[Any], *, threshold: int=50) -> Classifier`
  - `def is_title_excluded(self, title: str) -> bool`
  - `def classify(self, title: str, description: str) -> Classification`

## `app/pipeline/deduper.py`
(no docstring) deduper.py

- `class DedupDecision`
- `def seniority_tokens(title: str) -> set[str]`
- `def tech_tokens(title: str) -> set[str]`
- `def compute_fingerprint(job: NormalizedJob) -> str`
- `def title_similarity(a: str, b: str) -> float`
- `def description_similarity(a: str, b: str) -> float`
- `def location_compatible(a: NormalizedJob, b: Any) -> bool`
- `class Deduper`
  - `def decide(self, job: NormalizedJob, candidates: Iterable[Any]) -> DedupDecision`

## `app/pipeline/location.py`
(no docstring) location.py

- `class LocationResult`
- `class LocationNormalizer`
  - `def normalize(self, raw: str | None) -> LocationResult`
- `def accept_location(work_mode: str, loc: LocationResult, keep_unverified: bool) -> bool`

## `app/pipeline/normalizer.py`
(no docstring) normalizer.py

- `def canonical_url(url: str) -> str`
- `def detect_work_mode(*values: str | None) -> str`
- `def detect_employment_type(*values: str | None) -> str`
- `class NormalizedJob`
- `class Normalizer`
  - `def normalize(self, raw: RawJob, *, first_seen: datetime | None=None) -> NormalizedJob`

## `app/pipeline/pipeline.py`
(no docstring) pipeline.py

- `class PipelineResult`
- `class Pipeline`
  - `def prepare(self, raw: RawJob, *, first_seen: datetime | None=None) -> tuple[NormalizedJob, LocationResult]`
  - `def process(self, raw: RawJob, *, candidates: Iterable[Any]=(), first_seen: datetime | None=None) -> PipelineResult`

## `app/runner/__init__.py`
(no docstring) __init__.py


## `app/runner/orchestrator.py`
(no docstring) orchestrator.py

- `class Orchestrator`
  - `async def run(self, run_id: str, cancel_event: asyncio.Event | None=None, browser_pool: Any=None) -> None`
- `def discovery_stub_message(platform: str) -> str`

## `app/runner/run_manager.py`
(no docstring) run_manager.py

- `class CallbackRejectedError` (Exception)
- `def validate_callback_url(url: str) -> str`
- `class RunManager`
  - `async def start(self) -> None`
  - `async def stop(self) -> None`
  - `async def enqueue(self, *, run_id: str, platforms: list[str], params: dict[str, Any], trigger: str='api', callback_url: str | None=None) -> None`
  - `async def cancel(self, run_id: str) -> Any`

## `app/scrapers/__init__.py`
(no docstring) __init__.py


## `app/scrapers/base.py`
(no docstring) base.py

- `class RawListing`
- `class RawJob`
- `class ScrapeContext`
  - `def request_stop(self) -> None`
- `class BaseScraper` (ABC)
  - `def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]` — Hasilkan listing terbaru lebih dulu; berhenti saat lewat usia/maks.
  - `async def fetch_detail(self, listing: RawListing) -> RawJob` — Ambil deskripsi lengkap dari halaman detail.
  - `async def check_session(self) -> None`

## `app/scrapers/browser.py`
(no docstring) browser.py

- `def detect_challenge(html: str, url: str) -> bool`
- `class BrowserPool` — Satu Chromium per aplikasi, satu context per platform per run.
  - `async def start(self) -> None`
  - `async def context(self, platform: str, *, storage_state: str | None=None) -> BrowserContext`
  - `async def new_page(self, platform: str, *, storage_state: str | None=None) -> Page`
  - `async def reset_context(self, platform: str) -> None`
  - `async def stop(self) -> None`
- `def jitter(delay_ms: tuple[int, int] | list[int]) -> float`
- `async def save_debug_snapshot(page: Page | None, run_id: str, platform: str, reason: str='error', *, html: str | None=None) -> Path | None` — Screenshot + HTML ke data/debug/<run_id>/, dengan rotasi jumlah file.

## `app/scrapers/common/__init__.py`
(no docstring) __init__.py


## `app/scrapers/common/retry.py`
(no docstring) retry.py

- `async def fetch_with_retry(client: httpx.AsyncClient, url: str, *, method: str='GET', headers: dict[str, str] | None=None, check_challenge: bool=False, **kwargs: Any) -> httpx.Response` — GET dengan retry terpusat (SCRAPER_SPEC §4.2).

## `app/scrapers/common/salary.py`
(no docstring) salary.py

- `class SalaryInfo`
- `def parse_salary(raw: str | None) -> SalaryInfo`

## `app/scrapers/common/text.py`
(no docstring) text.py

- `def clean_text(text: str | None) -> str`
- `def normalize_for_match(text: str | None) -> str`
- `def normalize_company(name: str | None) -> str | None`
- `def description_hash(text: str) -> str`
- `def html_to_text(html: str | None) -> str`
- `def looks_truncated(text: str, html_len: int | None=None) -> bool`

## `app/scrapers/exceptions.py`
(no docstring) exceptions.py

- `class ScraperError` (Exception) — Kesalahan scraper yang dapat ditangani orchestrator.
- `class TransientNetworkError` (ScraperError)
- `class BlockedError` (ScraperError)
- `class AuthRequiredError` (ScraperError)
- `class SiteChangedError` (ScraperError)
- `class ParseError` (ScraperError)

## `app/scrapers/platforms/__init__.py`
(no docstring) __init__.py


## `app/scrapers/platforms/_placeholder.py`
(no docstring) _placeholder.py

- `class DiscoveryPendingScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/dealls.py`
(no docstring) dealls.py

- `def salary_text(salary_type: str | None, salary_range: Any) -> str | None`
- `def canonical_url(slug: str | None, company_slug: str | None=None) -> str`
- `def parse_listing_payload(payload: dict[str, Any] | str, *, page: int=1, platform: str='dealls') -> list[RawListing]`
- `def parse_detail_payload(payload: dict[str, Any] | str, listing: RawListing | None=None, *, platform: str='dealls') -> RawJob`
- `class DeallsScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/glints.py`
(no docstring) glints.py

- `def slugify(title: str) -> str`
- `def job_url(title: str, job_id: str) -> str`
- `def location_label(location: dict[str, Any] | None) -> str | None`
- `def salary_text(salaries: list[dict[str, Any]] | None, should_show: bool | None=True) -> str | None`
- `def draft_to_parts(raw: str | None) -> tuple[str, str]`
- `def parse_search_html(html: str, *, platform: str='glints') -> list[RawListing]`
- `def parse_detail_html(html: str, listing: RawListing, platform: str='glints') -> RawJob`
- `class GlintsScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/jobstreet.py`
(no docstring) jobstreet.py

- `def extract_redux_state(html: str) -> dict[str, Any] | None`
- `def parse_search_payload(payload: dict[str, Any], *, page: int=1, platform: str='jobstreet') -> list[RawListing]`
- `def parse_detail_html(html: str, listing: RawListing, platform: str='jobstreet') -> RawJob`
- `class JobStreetScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/kalibrr.py`
(no docstring) kalibrr.py

- `def parse_listing_payload(payload: dict[str, Any], *, page: int=1, platform: str='kalibrr') -> list[RawListing]`
- `def parse_detail_payload(payload: str | dict[str, Any], listing: RawListing, *, platform: str='kalibrr') -> RawJob`
- `class KalibrrScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/kitalulus.py`
(no docstring) kitalulus.py

- `def parse_listing_payload(html: str, *, platform: str='kitalulus') -> list[RawListing]`
- `def parse_detail_payload(html: str, *, platform: str='kitalulus') -> RawJob`
- `class KitaLulusScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/linkedin.py`
(no docstring) linkedin.py

- `def search_url(term: str, max_age_days: int, *, start: int=0, remote: bool=False) -> str`
- `def parse_listing_payload(html: str, *, page: int=1, platform: str='linkedin') -> list[RawListing]`
- `def parse_detail_payload(html: str, listing: RawListing, platform: str='linkedin') -> RawJob`
- `class LinkedInScraper` (BaseScraper)
  - `async def check_session(self) -> None`
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/platforms/pintarnya.py`
(no docstring) pintarnya.py

- `def search_slug(term: str) -> str`
- `def canonical_url(slug: str | None) -> str`
- `def salary_text(low: Any, high: Any, *, currency: str='IDR', unit: str='MONTH') -> str | None`
- `def parse_list_payload(payload: Any, *, page: int=1, platform: str='pintarnya') -> list[RawListing]`
- `def total_pages(payload: Any) -> int`
- `def parse_detail_payload(payload: dict[str, Any] | str, listing: RawListing | None=None, *, platform: str='pintarnya') -> RawJob`
- `class PintarnyaScraper` (BaseScraper)
  - `async def iter_listings(self, search_term: str) -> AsyncIterator[RawListing]`
  - `async def fetch_detail(self, listing: RawListing) -> RawJob`

## `app/scrapers/registry.py`
(no docstring) registry.py

- `def platform_config() -> dict[str, dict[str, Any]]`
- `def enabled_platforms() -> list[str]`
- `def reload_platform_config() -> None`

## `app/seed/__init__.py`
(no docstring) __init__.py


## `app/seed/loader.py`
(no docstring) loader.py

- `async def seed_keywords(session: AsyncSession) -> int`
- `async def seed_locations(session: AsyncSession) -> int`
- `async def seed_all(session: AsyncSession) -> dict[str, int]`

## `app/services/__init__.py`
(no docstring) __init__.py


## `app/services/health_service.py`
(no docstring) health_service.py

- `async def check_browser() -> tuple[bool, str]`

## `app/services/job_service.py`
(no docstring) job_service.py

- `async def list_jobs(filters: JobFilters) -> dict[str, Any]`
- `async def get_job(job_id: int) -> dict[str, Any]`
- `async def update_status(job_id: int, status: str) -> dict[str, Any]`
- `async def run_export(filters: JobFilters, fmt: str)`

## `app/services/platform_service.py`
(no docstring) platform_service.py

- `async def list_keywords(type_: str | None, is_active: bool | None) -> list[dict[str, Any]]`
- `async def create_keyword(data: dict[str, Any]) -> dict[str, Any]`
- `async def patch_keyword(rule_id: int, data: dict[str, Any]) -> dict[str, Any]`
- `async def delete_keyword(rule_id: int) -> None`
- `async def reseed_keywords() -> dict[str, int]`
- `async def list_platforms() -> list[dict[str, Any]]`
- `async def keyword_rules_for_pipeline(session: AsyncSession) -> list[Any]`

## `app/services/scrape_service.py`
(no docstring) scrape_service.py

- `def new_run_id() -> str`
- `async def start_scrape(platform: str | None, body: dict[str, Any]) -> dict[str, Any]`
- `async def get_run(run_id: str) -> dict[str, Any]`
- `async def list_runs(*, status: str | None, limit: int, page: int) -> dict[str, Any]`
- `async def cancel_run(run_id: str) -> dict[str, Any]`

## `scripts/codemap.py`
Generate docs/CODEMAP.md from app/ and scripts/ with the stdlib ast module.

- `def main() -> None`

## `scripts/discover_platform.py`
Alat bantu discovery SCRAPER_SPEC §3.

- `async def discover(platform: str, url: str, headed: bool, wait_ms: int, storage_state: str | None, interactive: bool) -> None`
- `def main() -> None`

## `scripts/linkedin_login.py`
Login LinkedIn manual (headed) lalu simpan storage_state.

- `async def main() -> None`
