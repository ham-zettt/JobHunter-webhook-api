# Graph Report - job-hunt  (2026-11-02)

## Corpus Check
- 136 files · ~368,625 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 6 file(s) not represented in the graph (top: (none) 2, .example 1, .ini 1)

## Summary
- 1245 nodes · 2690 edges · 100 communities (69 shown, 31 thin omitted)
- Extraction: 92% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 200 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f3d7a41`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- normalizer.py
- ._run_platform
- job_repo.py
- keyword_repo.py
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- CODEMAP
- scrape_service.py
- deduper.py
- get_settings
- errors.py
- orchestrator.py
- keywords.py
- test_scrape_jobs.py
- Glints — catatan discovery & implementasi
- detect_challenge
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
- Task 27 — Discovery LinkedIn + login/sesi
- jobstreet.py
- platforms
- include
- timeutil.py
- Pipeline (normalize → filter → dedup)
- test_location.py
- test_classifier.py
- AGENTS.md
- entrypoint.sh
- BR-02 (aturan lokasi onsite)
- job-scraper
- glints.py
- test_pipeline.py
- RawListing
- browser.py
- codemap.py
- Classifier
- routers/scrape.py
- opencode.json
- registry.py
- parse_salary
- main.py
- Settings
- discover_platform.py
- Task 04 — Docker, entrypoint, verifikasi `docker compose up`
- Task 21 — Discovery Kalibrr
- Task 23 — Discovery Dealls
- Task 25 — Discovery KitaLulus
- Task 29 — Discovery Pintarnya
- Task 32 — Webhook callback end-to-end
- Task 33 — Backup, retensi, `scripts/prune.py`
- Task 34 — Tuning dedup + reclassify (OPSIONAL)
- Task 35 — README final + contoh workflow n8n
- Task 36 — Uji end-to-end + review kriteria rilis PRD §13
- Task 24 — Scraper Dealls + fixture/test
- Task 26 — Scraper KitaLulus + fixture/test
- Task 30 — Scraper/stub Pintarnya + test
- run_manager.py
- JobStreet — catatan discovery & implementasi
- HANDOFF — Job Scraper API
- PLAN — Job Scraper API
- Normalizer
- kalibrr.py

## God Nodes (most connected - your core abstractions)
1. `CODEMAP` - 69 edges
2. `get_settings()` - 39 edges
3. `RawJob` - 35 edges
4. `SCRAPER_SPEC — Mekanisme Scraping per Platform` - 34 edges
5. `RawListing` - 30 edges
6. `SiteChangedError` - 29 edges
7. `utc_iso()` - 28 edges
8. `parse_salary()` - 24 edges
9. `Orchestrator` - 23 edges
10. `Deduper` - 20 edges

## Surprising Connections (you probably didn't know these)
- `Langkah-langkah` --references--> `RawListing`  [INFERRED]
  plan/16-max-age-tests.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/24-dealls-scraper.md → app/scrapers/base.py
- `Kriteria selesai (checklist)` --references--> `RawJob`  [INFERRED]
  plan/25-kitalulus-discovery.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/26-kitalulus-scraper.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/30-pintarnya-scraper.md → app/scrapers/base.py

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

## Communities (100 total, 31 thin omitted)

### Community 0 - "normalizer.py"
Cohesion: 0.18
Nodes (18): canonical_url(), detect_employment_type(), detect_work_mode(), _detect_currency(), SalaryInfo, _to_number(), clean_text(), description_hash() (+10 more)

### Community 1 - "._run_platform"
Cohesion: 0.13
Nodes (24): utc_iso(), ScrapeRun, ScrapeRunSource, add_link(), add_error(), cancel_run(), create_run(), _duration() (+16 more)

### Community 2 - "job_repo.py"
Cohesion: 0.07
Nodes (51): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), ValidationAppError, Job, api_dict() (+43 more)

### Community 3 - "keyword_repo.py"
Cohesion: 0.20
Nodes (15): ConflictError, NotFoundError, KeywordRule, active_rules(), create_rule(), delete_rule(), list_rules(), reseed() (+7 more)

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.05
Nodes (56): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, DATABASE — Job Scraper API, ARCHITECTURE document, DiscoveryPendingScraper, SiteChangedError, PRD.md (+48 more)

### Community 5 - "CODEMAP"
Cohesion: 0.03
Nodes (69): `app/api/__init__.py`, `app/api/router.py`, `app/api/routers/health.py`, `app/api/routers/__init__.py`, `app/api/routers/jobs.py`, `app/api/routers/keywords.py`, `app/api/routers/platforms.py`, `app/api/routers/scrape.py` (+61 more)

### Community 6 - "scrape_service.py"
Cohesion: 0.17
Nodes (12): AppError, PlatformDisabledError, PlatformNotFoundError, RunNotCancellableError, RunNotFoundError, ServiceUnavailableError, UnauthorizedError, require_api_key() (+4 more)

### Community 7 - "deduper.py"
Cohesion: 0.10
Nodes (36): _company_match(), compute_fingerprint(), _date(), Deduper, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible() (+28 more)

### Community 8 - "get_settings"
Cohesion: 0.14
Nodes (9): health(), get_settings(), configure(), get_session(), enabled_platforms(), platform_config(), check_browser(), _auth_state() (+1 more)

### Community 9 - "errors.py"
Cohesion: 0.27
Nodes (6): install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload()

### Community 10 - "orchestrator.py"
Cohesion: 0.19
Nodes (7): is_too_old(), accept_location(), LocationResult, Pipeline, BaseScraper, RawJob, test_age_filter_invalid_date()

### Community 11 - "keywords.py"
Cohesion: 0.13
Nodes (9): create_keyword(), delete_keyword(), list_keywords(), patch_keyword(), reseed(), KeywordCreate, KeywordUpdate, delete_keyword() (+1 more)

### Community 12 - "test_scrape_jobs.py"
Cohesion: 0.06
Nodes (37): Base, LocationAlias, JobRunLink, ensure_schema_sync(), _keyword_rows(), _load(), _location_rows(), seed_all() (+29 more)

### Community 13 - "Glints — catatan discovery & implementasi"
Cohesion: 0.11
Nodes (17): blocked(), Anti-bot, Batas kesopanan, Fixture, Glints — catatan discovery & implementasi, Keterbatasan paginasi (penting), Pemetaan field, Ringkasan metode (+9 more)

### Community 14 - "detect_challenge"
Cohesion: 0.19
Nodes (12): detect_challenge(), Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 31 — Hardening: retry, canary, snapshot, deteksi blokir (+4 more)

### Community 15 - "job-scraper"
Cohesion: 0.13
Nodes (14): interval, retries, test, timeout, build, env_file, healthcheck, init (+6 more)

### Community 16 - "health.py"
Cohesion: 0.33
Nodes (3): test_health_browser_failure_returns_503(), test_health_ok(), fake()

### Community 17 - "locations_java.yaml"
Cohesion: 0.20
Nodes (9): location (normalization + is_in_java + remote Indonesia), country_foreign, country_id, outside_java_cities, name, province, outside_java_provinces, remote_words (+1 more)

### Community 18 - "PRD — Job Scraper API"
Cohesion: 0.11
Nodes (22): docs/DECISIONS.md, ARCHITECTURE.md, DATABASE.md, SCRAPER_SPEC.md, BR-04 Aturan Usia Lowongan, Autentikasi API Key (X-API-Key), Deduplikasi Lowongan, Deployment Docker (satu container, satu worker uvicorn) (+14 more)

### Community 19 - "GlintsScraper"
Cohesion: 0.18
Nodes (12): jitter(), BlockedError, ParseError, ScraperError, SiteChangedError, TransientNetworkError, GlintsScraper, JobStreetScraper (+4 more)

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
Cohesion: 0.15
Nodes (13): BR-06 (kasus pembeda lowongan), Discovery, Kriteria Penerimaan Rilis 1.0 (PRD §13), NFR-05 (anti-duplikasi run berulang), ARCHITECTURE.md, DATABASE.md, docs/DECISIONS.md, DiscoveryPendingScraper (+5 more)

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

### Community 35 - "Task 27 — Discovery LinkedIn + login/sesi"
Cohesion: 0.10
Nodes (20): AuthRequiredError, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 27 — Discovery LinkedIn + login/sesi (+12 more)

### Community 37 - "jobstreet.py"
Cohesion: 0.21
Nodes (18): _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode(), html() (+10 more)

### Community 38 - "platforms"
Cohesion: 0.50
Nodes (3): Scraper registry (platform → scraper class), platforms, Kesopanan, Laju, dan Penanganan Blokir (§4)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "timeutil.py"
Cohesion: 0.22
Nodes (16): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), check() (+8 more)

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "test_location.py"
Cohesion: 0.21
Nodes (11): LocationNormalizer, _norm(), loc(), test_accept_location_rules(), test_city_alias(), test_city_and_province(), test_city_inherits_province(), test_foreign_country() (+3 more)

### Community 43 - "test_classifier.py"
Cohesion: 0.24
Nodes (11): KeywordSpec, make_classifier(), test_description_one_strong_rejected(), test_description_penalty_reduces_score(), test_description_two_strong_accepted(), test_exclude_title_rejected_even_with_strong_description(), test_matched_keywords_capped_at_20(), test_no_match_rejected() (+3 more)

### Community 67 - "glints.py"
Cohesion: 0.20
Nodes (22): draft_to_parts(), job_url(), location_label(), _next_data(), parse_detail_html(), parse_search_html(), salary_text(), slugify() (+14 more)

### Community 68 - "test_pipeline.py"
Cohesion: 0.33
Nodes (12): classifier(), location(), make_pipeline(), raw(), test_happy_path(), test_html_description_extracted(), test_irrelevant_title_rejected(), test_old_posting_rejected() (+4 more)

### Community 69 - "RawListing"
Cohesion: 0.38
Nodes (3): RawListing, FakeGlintsScraper, FakeJobstreetScraper

### Community 70 - "browser.py"
Cohesion: 0.10
Nodes (9): BrowserPool, _prune_debug_files(), save_debug_snapshot(), Asumsi, Jebakan yang sudah terbukti, Konflik antar dokumen, NOTES — asumsi, konflik, penyimpangan, Penyimpangan kode vs spesifikasi (+1 more)

### Community 71 - "codemap.py"
Cohesion: 0.30
Nodes (5): _file_lines(), main(), _module_doc(), _signature(), _summary()

### Community 72 - "Classifier"
Cohesion: 0.29
Nodes (5): Classification, Classifier, _pattern(), normalize_for_match(), test_normalize_for_match()

### Community 73 - "routers/scrape.py"
Cohesion: 0.16
Nodes (8): list_platforms(), cancel_run(), get_run(), list_runs(), scrape_all(), scrape_platform(), ScrapeRequest, list_runs()

### Community 76 - "registry.py"
Cohesion: 0.19
Nodes (8): DeallsScraper, KitaLulusScraper, LinkedInScraper, PintarnyaScraper, DiscoveryPendingScraper, Tujuan, Tujuan, Tujuan

### Community 77 - "parse_salary"
Cohesion: 0.35
Nodes (10): parse_salary(), test_confidential_clears_everything(), test_decimal_million(), test_no_amount(), test_per_day(), test_range_idr(), test_short_range_with_unit_at_end(), test_single_amount() (+2 more)

### Community 78 - "main.py"
Cohesion: 0.27
Nodes (5): get_logger(), setup_logging(), ensure_schema(), create_app(), lifespan()

### Community 80 - "discover_platform.py"
Cohesion: 0.33
Nodes (5): _capture(), discover(), _is_json(), main(), _slug()

### Community 81 - "Task 04 — Docker, entrypoint, verifikasi `docker compose up`"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 04 — Docker, entrypoint, verifikasi `docker compose up`, Test yang harus ditulis (+2 more)

### Community 82 - "Task 21 — Discovery Kalibrr"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 21 — Discovery Kalibrr, Test yang harus ditulis (+2 more)

### Community 83 - "Task 23 — Discovery Dealls"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 23 — Discovery Dealls, Test yang harus ditulis (+2 more)

### Community 84 - "Task 25 — Discovery KitaLulus"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 25 — Discovery KitaLulus, Test yang harus ditulis (+2 more)

### Community 85 - "Task 29 — Discovery Pintarnya"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 29 — Discovery Pintarnya, Test yang harus ditulis (+2 more)

### Community 86 - "Task 32 — Webhook callback end-to-end"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 32 — Webhook callback end-to-end, Test yang harus ditulis (+2 more)

### Community 87 - "Task 33 — Backup, retensi, `scripts/prune.py`"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 33 — Backup, retensi, `scripts/prune.py`, Test yang harus ditulis (+2 more)

### Community 88 - "Task 34 — Tuning dedup + reclassify (OPSIONAL)"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 34 — Tuning dedup + reclassify (OPSIONAL), Test yang harus ditulis (+2 more)

### Community 89 - "Task 35 — README final + contoh workflow n8n"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 35 — README final + contoh workflow n8n, Test yang harus ditulis (+2 more)

### Community 90 - "Task 36 — Uji end-to-end + review kriteria rilis PRD §13"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 36 — Uji end-to-end + review kriteria rilis PRD §13, Test yang harus ditulis (+2 more)

### Community 91 - "Task 24 — Scraper Dealls + fixture/test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 24 — Scraper Dealls + fixture/test, Test yang harus ditulis (+1 more)

### Community 92 - "Task 26 — Scraper KitaLulus + fixture/test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 26 — Scraper KitaLulus + fixture/test, Test yang harus ditulis (+1 more)

### Community 93 - "Task 30 — Scraper/stub Pintarnya + test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Task 30 — Scraper/stub Pintarnya + test, Test yang harus ditulis, Tujuan (+1 more)

### Community 95 - "JobStreet — catatan discovery & implementasi"
Cohesion: 0.22
Nodes (8): Anti-bot / akses, Batas kesopanan yang dipakai, Fixture, JobStreet — catatan discovery & implementasi, Parameter pencarian yang dipakai, Pemetaan field, Ringkasan metode, Risiko / catatan

### Community 96 - "HANDOFF — Job Scraper API"
Cohesion: 0.33
Nodes (5): 1. Selesai (F0–F3 parsial), 2. Penyimpangan dari spesifikasi, 3. Keputusan/jebakan/bug diketahui (belum diperbaiki), 4. Setengah jalan, HANDOFF — Job Scraper API

### Community 97 - "PLAN — Job Scraper API"
Cohesion: 0.40
Nodes (4): Dependensi, Indeks task, PLAN — Job Scraper API, Urutan eksekusi

## Ambiguous Edges - Review These
- `DATABASE.md` → `BR-01 Aturan Kata Kunci`  [AMBIGUOUS]
  PRD.md · relation: references
- `docs/platform_notes/<platform>.md` → `DATABASE.md`  [AMBIGUOUS]
  SCRAPER_SPEC.md · relation: references

## Knowledge Gaps
- **61 isolated node(s):** `job-scraper`, `Deployment Docker (satu container, satu worker uvicorn)`, `FastAPI`, `Playwright`, `SQLite (WAL mode)` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 509 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `timeutil.py`, `normalizer.py`, `discover_platform.py`, `platforms`?**
  _High betweenness centrality (0.178) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `RawJob` (e.g. with `Normalizer` and `Pipeline`) actually correct?**
  _`RawJob` has 14 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `Deployment Docker (satu container, satu worker uvicorn)`, `FastAPI` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `._run_platform` be split into smaller, more focused modules?**
  _Cohesion score 0.1276595744680851 - nodes in this community are weakly interconnected._
- **Why does `platforms` connect `platforms` to `pintarnya`, `linkedin`, `dealls`, `glints`, `jobstreet`, `kalibrr`, `kitalulus`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `DATABASE.md` and `BR-01 Aturan Kata Kunci`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._