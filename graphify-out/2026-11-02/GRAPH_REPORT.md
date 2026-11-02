# Graph Report - job-hunt  (2026-11-02)

## Corpus Check
- 112 files · ~357,213 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .example 1, .ini 1)

## Summary
- 938 nodes · 2338 edges · 80 communities (50 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 144 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- normalizer.py
- ._run_platform
- job_repo.py
- keyword_repo.py
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- env.py
- main.py
- deduper.py
- scrape_service.py
- errors.py
- orchestrator.py
- keywords.py
- test_scrape_jobs.py
- Glints — catatan discovery & implementasi
- browser.py
- job-scraper
- health.py
- locations_java.yaml
- PRD — Job Scraper API
- GlintsScraper
- Orchestrator (single-run execution loop)
- BaseScraper (abstract scraper contract)
- keywords.yaml
- linkedin
- Job Scraper API
- Repositories (SQLAlchemy async)
- provinces
- dealls
- glints
- jobstreet
- kalibrr
- kitalulus
- pintarnya
- Glosarium (PRD §15)
- linkedin_login.py
- Kontrak Output Data Lowongan
- jobstreet.py
- platforms
- include
- Penyaringan Lowongan (rule-based)
- Pipeline (normalize → filter → dedup)
- Kriteria Penerimaan Rilis 1.0 (PRD §13)
- Deduplikasi Lowongan
- AGENTS.md
- entrypoint.sh
- BR-02 (aturan lokasi onsite)
- job-scraper
- glints.py
- Base
- RawJob
- BrowserPool
- loader.py
- platform_config
- routers/scrape.py
- opencode.json
- registry.py
- get_run
- logging.py
- Settings

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 39 edges
2. `SCRAPER_SPEC — Mekanisme Scraping per Platform` - 34 edges
3. `utc_iso()` - 28 edges
4. `RawJob` - 28 edges
5. `RawListing` - 27 edges
6. `SiteChangedError` - 27 edges
7. `parse_salary()` - 24 edges
8. `Orchestrator` - 23 edges
9. `Deduper` - 19 edges
10. `NormalizedJob` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Anti-bot` --references--> `BlockedError`  [INFERRED]
  docs/platform_notes/glints.md → app/scrapers/exceptions.py
- `Batas kesopanan yang dipakai` --references--> `BlockedError`  [INFERRED]
  docs/platform_notes/jobstreet.md → app/scrapers/exceptions.py
- `4. Setengah jalan` --references--> `DiscoveryPendingScraper`  [INFERRED]
  plan/HANDOFF.md → app/scrapers/platforms/_placeholder.py
- `Anti-bot / akses` --references--> `BlockedError`  [INFERRED]
  docs/platform_notes/jobstreet.md → app/scrapers/exceptions.py
- `Risiko` --references--> `SiteChangedError`  [INFERRED]
  docs/platform_notes/glints.md → app/scrapers/exceptions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Alur Discovery Wajib per Platform** — scraper_spec_discovery_procedure, scripts_discover_platform, scraper_spec_platform_notes, scraper_spec_tests_fixtures, scraper_spec_parse_listing_payload, scraper_spec_parse_detail_payload [EXTRACTED 0.90]
- **Alur Integrasi n8n: scrape → polling → ambil lowongan baru** — readme_n8n, prd_rest_api, prd_scraping, prd_async_run, prd_webhook_callback [EXTRACTED 0.90]
- **Set dokumentasi teknis proyek (spesifikasi scraper, arsitektur, skema DB, keputusan)** — readme_job_scraper_api, readme_scraper_spec, readme_architecture, readme_database, readme_decisions [EXTRACTED 0.90]
- **Scraper listing/detail lifecycle (§6)** — scraperspec_iter_listings, scraperspec_fetch_detail, scraper_spec_rawlisting, scraper_spec_rawjob, scraperspec_challenge_detection [EXTRACTED 0.90]
- **Aturan Bisnis Penerimaan, Deduplikasi, dan Siklus Hidup** — prd_keyword_rules, prd_location_rules, prd_age_rule, prd_duplicate_rules, prd_duplicate_vs_similar, prd_lifecycle [EXTRACTED 0.95]
- **Registered platform scrapers implementing BaseScraper** — scraperspec_base_scraper, scraperspec_linkedin_scraper, scraperspec_jobstreet_scraper, scraperspec_glints_scraper, scraperspec_kalibrr_scraper, scraperspec_dealls_scraper, scraperspec_kitalulus_scraper, scraperspec_pintarnya_scraper, scraperspec_registry [EXTRACTED 0.95]
- **Set istilah kanonik PRD (Run, Sumber, Kanonik, Repost, Discovery, Canary check)** — prd_run, prd_sumber, prd_kanonik, prd_repost, prd_discovery, prd_canary_check [EXTRACTED 0.95]
- **Pipeline processing stages (normalize → filter → dedup)** — architecture_pipeline, architecture_normalizer, architecture_location, architecture_classifier, architecture_agefilter, architecture_deduper [EXTRACTED 1.00]
- **Cakupan Platform Scraping** — scraper_spec_jobstreet, scraper_spec_glints, scraper_spec_kalibrr, scraper_spec_dealls, scraper_spec_kitalulus, scraper_spec_linkedin, scraper_spec_pintarnya [EXTRACTED 1.00]
- **Cakupan 7 Platform Versi 1.0** — prd_platform_jobstreet, prd_platform_glints, scraper_spec_kalibrr, prd_platform_dealls, scraper_spec_kitalulus, scraper_spec_linkedin, scraper_spec_pintarnya [EXTRACTED 1.00]
- **Scraper exception hierarchy handled by orchestrator** — architecture_orchestrator, architecture_transientnetworkerror, architecture_blockederror, architecture_authrequirederror, architecture_sitechangederror, architecture_parseerror [EXTRACTED 1.00]
- **Platform scrapers implementing BaseScraper** — architecture_basescraper, architecture_jobstreet, architecture_glints, architecture_kalibrr, architecture_dealls, architecture_kitalulus, architecture_linkedin, architecture_pintarnya [EXTRACTED 1.00]
- **Kontrak Data Mentah dan Normalisasi** — scraper_spec_rawlisting, scraper_spec_rawjob, scraper_spec_salaryinfo, scraper_spec_parse_listing_payload, scraper_spec_parse_detail_payload, app_pipeline_normalizer [INFERRED 0.75]

## Communities (80 total, 30 thin omitted)

### Community 0 - "normalizer.py"
Cohesion: 0.07
Nodes (51): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), canonical_url() (+43 more)

### Community 1 - "._run_platform"
Cohesion: 0.14
Nodes (22): utc_iso(), ScrapeRun, ScrapeRunSource, add_error(), cancel_run(), create_run(), _duration(), finish_run() (+14 more)

### Community 2 - "job_repo.py"
Cohesion: 0.09
Nodes (43): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), NotFoundError, ValidationAppError, Job (+35 more)

### Community 3 - "keyword_repo.py"
Cohesion: 0.18
Nodes (17): KeywordRule, active_rules(), create_rule(), delete_rule(), list_rules(), reseed(), rule_dict(), search_terms() (+9 more)

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.06
Nodes (52): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, DATABASE — Job Scraper API, ARCHITECTURE document, DiscoveryPendingScraper, SiteChangedError, PRD.md (+44 more)

### Community 5 - "env.py"
Cohesion: 0.24
Nodes (6): ensure_schema_sync(), run_migrations_offline(), run_migrations_online(), _sync_url(), downgrade(), upgrade()

### Community 6 - "main.py"
Cohesion: 0.42
Nodes (4): UnauthorizedError, require_api_key(), create_app(), lifespan()

### Community 7 - "deduper.py"
Cohesion: 0.16
Nodes (26): _company_match(), compute_fingerprint(), _date(), Deduper, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible() (+18 more)

### Community 8 - "scrape_service.py"
Cohesion: 0.16
Nodes (11): get_settings(), PlatformDisabledError, PlatformNotFoundError, configure(), get_session(), CallbackRejectedError, validate_callback_url(), enabled_platforms() (+3 more)

### Community 9 - "errors.py"
Cohesion: 0.16
Nodes (10): AppError, ConflictError, install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload() (+2 more)

### Community 10 - "orchestrator.py"
Cohesion: 0.06
Nodes (41): is_too_old(), Classification, Classifier, KeywordSpec, _pattern(), accept_location(), LocationNormalizer, LocationResult (+33 more)

### Community 11 - "keywords.py"
Cohesion: 0.15
Nodes (7): create_keyword(), delete_keyword(), list_keywords(), patch_keyword(), reseed(), KeywordCreate, KeywordUpdate

### Community 12 - "test_scrape_jobs.py"
Cohesion: 0.12
Nodes (17): _capture(), discover(), _is_json(), main(), _slug(), fake_registry(), scrape(), seed_keywords() (+9 more)

### Community 13 - "Glints — catatan discovery & implementasi"
Cohesion: 0.20
Nodes (9): blocked(), Anti-bot, Batas kesopanan, Fixture, Glints — catatan discovery & implementasi, Keterbatasan paginasi (penting), Pemetaan field, Ringkasan metode (+1 more)

### Community 14 - "browser.py"
Cohesion: 0.29
Nodes (5): detect_challenge(), jitter(), _prune_debug_files(), save_debug_snapshot(), test_challenge_detection()

### Community 15 - "job-scraper"
Cohesion: 0.13
Nodes (14): interval, retries, test, timeout, build, env_file, healthcheck, init (+6 more)

### Community 16 - "health.py"
Cohesion: 0.21
Nodes (5): health(), check_browser(), test_health_browser_failure_returns_503(), test_health_ok(), fake()

### Community 17 - "locations_java.yaml"
Cohesion: 0.20
Nodes (9): location (normalization + is_in_java + remote Indonesia), country_foreign, country_id, outside_java_cities, name, province, outside_java_provinces, remote_words (+1 more)

### Community 18 - "PRD — Job Scraper API"
Cohesion: 0.18
Nodes (10): docs/DECISIONS.md, ARCHITECTURE.md, SCRAPER_SPEC.md, Deployment Docker (satu container, satu worker uvicorn), FastAPI, PRD — Job Scraper API, Playwright, SQLite (WAL mode) (+2 more)

### Community 19 - "GlintsScraper"
Cohesion: 0.16
Nodes (11): ScrapeContext, AuthRequiredError, BlockedError, ParseError, ScraperError, TransientNetworkError, GlintsScraper, JobStreetScraper (+3 more)

### Community 20 - "Orchestrator (single-run execution loop)"
Cohesion: 0.22
Nodes (9): AuthRequiredError, BlockedError, FastAPI app (api layer, routers + schemas), Orchestrator (single-run execution loop), ParseError, RunManager (queue + asyncio worker), Services layer (scrape / job / export / keyword), SiteChangedError (+1 more)

### Community 21 - "BaseScraper (abstract scraper contract)"
Cohesion: 0.22
Nodes (9): BaseScraper (abstract scraper contract), BrowserPool (shared Chromium + per-platform context), DeallsScraper, GlintsScraper, JobStreetScraper, KalibrrScraper, KitaLulusScraper, LinkedInScraper (+1 more)

### Community 22 - "keywords.yaml"
Cohesion: 0.25
Nodes (8): classifier (keyword include/exclude, score, role category), Seed loader (config/*.yaml → DB), exclude, role_category_terms, category, term, search_terms, keyword_rules table

### Community 23 - "linkedin"
Cohesion: 0.22
Nodes (9): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, requires_auth, search_terms_limit (+1 more)

### Community 24 - "Job Scraper API"
Cohesion: 0.25
Nodes (9): Discovery, ARCHITECTURE.md, DATABASE.md, docs/DECISIONS.md, DiscoveryPendingScraper, .env.example, Job Scraper API, SCRAPER_SPEC.md (+1 more)

### Community 25 - "Repositories (SQLAlchemy async)"
Cohesion: 0.29
Nodes (8): deduper (levels 1–3), Repositories (SQLAlchemy async), SQLite (data/jobs.db, WAL), job_run_links table, jobs table, jobs_fts (FTS5 virtual table), scrape_run_sources table, scrape_runs table

### Community 26 - "provinces"
Cohesion: 0.25
Nodes (8): aliases, name, provinces, aliases, cities, is_java, name, regions

### Community 27 - "dealls"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, dealls

### Community 28 - "glints"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, glints

### Community 29 - "jobstreet"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, jobstreet

### Community 30 - "kalibrr"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, kalibrr

### Community 31 - "kitalulus"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, kitalulus

### Community 32 - "pintarnya"
Cohesion: 0.25
Nodes (8): concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit, pintarnya

### Community 33 - "Glosarium (PRD §15)"
Cohesion: 0.25
Nodes (8): Canary check, Keputusan D2 (pemilik menerima risiko ToS), Glosarium (PRD §15), Kanonik (lowongan induk), Repost, Risiko dan Mitigasi (PRD §11), Run, Sumber (platform asal lowongan)

### Community 35 - "Kontrak Output Data Lowongan"
Cohesion: 0.33
Nodes (7): DATABASE.md, Autentikasi API Key (X-API-Key), Kontrak Output Data Lowongan, BR-07 Siklus Hidup Lowongan, REST API /api/v1, Webhook callback_url (ringkasan run), n8n (workflow konsumen API)

### Community 37 - "jobstreet.py"
Cohesion: 0.20
Nodes (19): SiteChangedError, _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode() (+11 more)

### Community 38 - "platforms"
Cohesion: 0.50
Nodes (3): Scraper registry (platform → scraper class), platforms, Kesopanan, Laju, dan Penanganan Blokir (§4)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "Penyaringan Lowongan (rule-based)"
Cohesion: 0.50
Nodes (4): BR-04 Aturan Usia Lowongan, Penyaringan Lowongan (rule-based), BR-01 Aturan Kata Kunci, BR-02/BR-03 Aturan Lokasi & Remote

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "Kriteria Penerimaan Rilis 1.0 (PRD §13)"
Cohesion: 0.67
Nodes (3): BR-06 (kasus pembeda lowongan), Kriteria Penerimaan Rilis 1.0 (PRD §13), NFR-05 (anti-duplikasi run berulang)

### Community 43 - "Deduplikasi Lowongan"
Cohesion: 0.67
Nodes (3): Deduplikasi Lowongan, BR-05 Aturan Duplikat, BR-06 Aturan Pembeda Duplikat vs Lowongan Serupa Berbeda

### Community 67 - "glints.py"
Cohesion: 0.20
Nodes (22): draft_to_parts(), job_url(), location_label(), _next_data(), parse_detail_html(), parse_search_html(), salary_text(), slugify() (+14 more)

### Community 68 - "Base"
Cohesion: 0.23
Nodes (6): Base, LocationAlias, JobRunLink, ensure_schema(), auth_headers(), clean_db()

### Community 69 - "RawJob"
Cohesion: 0.24
Nodes (5): BaseScraper, RawJob, RawListing, FakeGlintsScraper, FakeJobstreetScraper

### Community 70 - "BrowserPool"
Cohesion: 0.08
Nodes (14): BrowserPool, Anti-bot / akses, Batas kesopanan yang dipakai, Fixture, JobStreet — catatan discovery & implementasi, Parameter pencarian yang dipakai, Pemetaan field, Ringkasan metode (+6 more)

### Community 71 - "loader.py"
Cohesion: 0.25
Nodes (9): _keyword_rows(), _load(), _location_rows(), seed_all(), seed_keywords(), seed_locations(), test_seed_contains_strong_weak_and_exclude(), test_seed_is_idempotent() (+1 more)

### Community 73 - "routers/scrape.py"
Cohesion: 0.22
Nodes (5): list_platforms(), cancel_run(), scrape_all(), scrape_platform(), ScrapeRequest

### Community 76 - "registry.py"
Cohesion: 0.31
Nodes (6): DeallsScraper, KalibrrScraper, KitaLulusScraper, LinkedInScraper, PintarnyaScraper, DiscoveryPendingScraper

### Community 77 - "get_run"
Cohesion: 0.32
Nodes (6): get_run(), list_runs(), RunNotFoundError, cancel_run(), get_run(), list_runs()

## Ambiguous Edges - Review These
- `DATABASE.md` → `BR-01 Aturan Kata Kunci`  [AMBIGUOUS]
  PRD.md · relation: references
- `docs/platform_notes/<platform>.md` → `DATABASE.md`  [AMBIGUOUS]
  SCRAPER_SPEC.md · relation: references

## Knowledge Gaps
- **62 isolated node(s):** `job-scraper`, `Deployment Docker (satu container, satu worker uvicorn)`, `FastAPI`, `Playwright`, `SQLite (WAL mode)` (+57 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 267 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `normalizer.py`, `test_scrape_jobs.py`, `platforms`?**
  _High betweenness centrality (0.243) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `RawJob` (e.g. with `Normalizer` and `Pipeline`) actually correct?**
  _`RawJob` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `Deployment Docker (satu container, satu worker uvicorn)`, `FastAPI` to the rest of the system?**
  _62 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `normalizer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07111501316944688 - nodes in this community are weakly interconnected._
- **Why does `platforms` connect `platforms` to `pintarnya`, `linkedin`, `dealls`, `glints`, `jobstreet`, `kalibrr`, `kitalulus`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `DATABASE.md` and `BR-01 Aturan Kata Kunci`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._