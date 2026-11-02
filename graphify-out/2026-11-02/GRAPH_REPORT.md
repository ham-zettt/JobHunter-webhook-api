# Graph Report - job-hunt  (2026-11-02)

## Corpus Check
- 153 files · ~509,757 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .example 1, .ini 1)

## Summary
- 1421 nodes · 3252 edges · 111 communities (81 shown, 30 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 271 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `43b75e7c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- normalizer.py
- job_repo.py
- job_repo.py
- Task 16 — Uji filter `max_age_days`
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- CODEMAP
- get_settings
- deduper.py
- env.py
- PRD — Job Scraper API
- orchestrator.py
- Implementasi scraper Kalibrr sesuai plan task 22
- keywords.py
- Kalibrr — catatan discovery (2026-11-02)
- detect_challenge
- job-scraper
- health.py
- locations_java.yaml
- Kontrak Output Data Lowongan
- KalibrrScraper
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
- save_debug_snapshot
- Task 27 — Discovery LinkedIn + login/sesi
- KalibrrScraper
- BaseScraper
- include
- timeutil.py
- Pipeline (normalize → filter → dedup)
- install_handlers
- platform_config
- AGENTS.md
- entrypoint.sh
- BR-02 (aturan lokasi onsite)
- job-scraper
- glints.py
- codemap.py
- RawListing
- Pipeline Scraping Multi-Platform
- SiteChangedError
- Task 28 — Scraper LinkedIn + fixture/test
- routers/scrape.py
- opencode.json
- kalibrr.py
- Classifier
- get_settings
- Penyaringan Lowongan (rule-based)
- test_scrape_jobs.py
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
- registry.py
- Task 30 — Scraper/stub Pintarnya + test
- jobstreet.py
- BrowserPool
- linkedin_login.py
- PLAN — Job Scraper API
- DATABASE — Job Scraper API
- jobs.py
- deduper.py
- ScrapeContext
- test_location.py
- job_service.py
- Dealls — catatan discovery (2026-11-02)
- test_pipeline.py
- session.py
- JobStreet — catatan discovery & implementasi
- Settings
- NOTES — asumsi, konflik, penyimpangan
- Assistant (Build · fullstack-development · 7.3s)

## God Nodes (most connected - your core abstractions)
1. `CODEMAP` - 69 edges
2. `SiteChangedError` - 56 edges
3. `RawListing` - 47 edges
4. `RawJob` - 46 edges
5. `Implementasi scraper Kalibrr sesuai plan task 22` - 42 edges
6. `get_settings()` - 39 edges
7. `SCRAPER_SPEC — Mekanisme Scraping per Platform` - 34 edges
8. `BlockedError` - 33 edges
9. `parse_salary()` - 30 edges
10. `parse_detail_payload()` - 29 edges

## Surprising Connections (you probably didn't know these)
- `Langkah-langkah` --references--> `RawListing`  [INFERRED]
  plan/16-max-age-tests.md → app/scrapers/base.py
- `Pemetaan field → `RawJob`` --references--> `RawJob`  [INFERRED]
  docs/platform_notes/kalibrr.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/24-dealls-scraper.md → app/scrapers/base.py
- `Kriteria selesai (checklist)` --references--> `RawJob`  [INFERRED]
  plan/25-kitalulus-discovery.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/26-kitalulus-scraper.md → app/scrapers/base.py

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

## Communities (111 total, 30 thin omitted)

### Community 0 - "normalizer.py"
Cohesion: 0.16
Nodes (21): _pattern(), canonical_url(), detect_employment_type(), detect_work_mode(), _detect_currency(), SalaryInfo, _to_number(), clean_text() (+13 more)

### Community 1 - "job_repo.py"
Cohesion: 0.05
Nodes (56): utc_iso(), Base, KeywordRule, LocationAlias, JobRunLink, ScrapeRun, ScrapeRunSource, add_link() (+48 more)

### Community 2 - "job_repo.py"
Cohesion: 0.18
Nodes (22): Job, _apply_richer(), build_query(), count_jobs_by_platform(), export_jobs(), find_candidates(), find_known(), get_job() (+14 more)

### Community 3 - "Task 16 — Uji filter `max_age_days`"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 16 — Uji filter `max_age_days`, Test yang harus ditulis (+2 more)

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.13
Nodes (25): PRD.md, SCRAPER_SPEC — Mekanisme Scraping per Platform, ARCHITECTURE.md, DATABASE.md, Dealls, Deskripsi Lengkap / FR-05 (§5.6), Prosedur Discovery (§3), Deteksi tipe_kerja (§5.4) (+17 more)

### Community 5 - "CODEMAP"
Cohesion: 0.03
Nodes (69): `app/api/__init__.py`, `app/api/router.py`, `app/api/routers/health.py`, `app/api/routers/__init__.py`, `app/api/routers/jobs.py`, `app/api/routers/keywords.py`, `app/api/routers/platforms.py`, `app/api/routers/scrape.py` (+61 more)

### Community 6 - "get_settings"
Cohesion: 0.21
Nodes (11): PlatformNotFoundError, RunNotFoundError, CallbackRejectedError, validate_callback_url(), enabled_platforms(), cancel_run(), get_run(), list_runs() (+3 more)

### Community 7 - "deduper.py"
Cohesion: 0.15
Nodes (28): Deduper, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 08 — Deduper L1–L3 + matriks 14 kasus, Test yang harus ditulis (+20 more)

### Community 8 - "env.py"
Cohesion: 0.47
Nodes (3): run_migrations_offline(), run_migrations_online(), _sync_url()

### Community 9 - "PRD — Job Scraper API"
Cohesion: 0.20
Nodes (9): docs/DECISIONS.md, ARCHITECTURE.md, SCRAPER_SPEC.md, Deployment Docker (satu container, satu worker uvicorn), FastAPI, PRD — Job Scraper API, Playwright, SQLite (WAL mode) (+1 more)

### Community 10 - "orchestrator.py"
Cohesion: 0.16
Nodes (10): is_too_old(), compute_fingerprint(), accept_location(), LocationResult, Normalizer, Pipeline, PipelineResult, RawJob (+2 more)

### Community 11 - "Implementasi scraper Kalibrr sesuai plan task 22"
Cohesion: 0.06
Nodes (35): 6. Alur Umum Setiap Scraper, Assistant (Build · fullstack-development · 10.1s), Assistant (Build · fullstack-development · 10.6s), Assistant (Build · fullstack-development · 10.9s), Assistant (Build · fullstack-development · 14.4s), Assistant (Build · fullstack-development · 15.5s), Assistant (Build · fullstack-development · 19.1s), Assistant (Build · fullstack-development · 3.8s) (+27 more)

### Community 12 - "keywords.py"
Cohesion: 0.15
Nodes (7): create_keyword(), delete_keyword(), list_keywords(), patch_keyword(), reseed(), KeywordCreate, KeywordUpdate

### Community 13 - "Kalibrr — catatan discovery (2026-11-02)"
Cohesion: 0.05
Nodes (37): blocked(), Anti-bot, Batas kesopanan, Fixture, Glints — catatan discovery & implementasi, Keterbatasan paginasi (penting), Pemetaan field, Ringkasan metode (+29 more)

### Community 14 - "detect_challenge"
Cohesion: 0.18
Nodes (13): detect_challenge(), Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 31 — Hardening: retry, canary, snapshot, deteksi blokir (+5 more)

### Community 15 - "job-scraper"
Cohesion: 0.13
Nodes (14): interval, retries, test, timeout, build, env_file, healthcheck, init (+6 more)

### Community 16 - "health.py"
Cohesion: 0.33
Nodes (3): test_health_browser_failure_returns_503(), test_health_ok(), fake()

### Community 17 - "locations_java.yaml"
Cohesion: 0.20
Nodes (9): location (normalization + is_in_java + remote Indonesia), country_foreign, country_id, outside_java_cities, name, province, outside_java_provinces, remote_words (+1 more)

### Community 18 - "Kontrak Output Data Lowongan"
Cohesion: 0.22
Nodes (10): DATABASE.md, Autentikasi API Key (X-API-Key), Deduplikasi Lowongan, BR-05 Aturan Duplikat, BR-06 Aturan Pembeda Duplikat vs Lowongan Serupa Berbeda, Kontrak Output Data Lowongan, BR-07 Siklus Hidup Lowongan, REST API /api/v1 (+2 more)

### Community 19 - "KalibrrScraper"
Cohesion: 0.15
Nodes (14): jitter(), AuthRequiredError, BlockedError, ParseError, ScraperError, TransientNetworkError, GlintsScraper, JobStreetScraper (+6 more)

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
Cohesion: 0.18
Nodes (12): BR-06 (kasus pembeda lowongan), Discovery, Kriteria Penerimaan Rilis 1.0 (PRD §13), NFR-05 (anti-duplikasi run berulang), ARCHITECTURE.md, DATABASE.md, docs/DECISIONS.md, DiscoveryPendingScraper (+4 more)

### Community 25 - "Repositories (SQLAlchemy async)"
Cohesion: 0.29
Nodes (8): deduper (levels 1–3), Repositories (SQLAlchemy async), SQLite (data/jobs.db, WAL), job_run_links table, jobs table, jobs_fts (FTS5 virtual table), scrape_run_sources table, scrape_runs table

### Community 26 - "provinces"
Cohesion: 0.25
Nodes (8): aliases, name, provinces, aliases, cities, is_java, name, regions

### Community 27 - "dealls"
Cohesion: 0.17
Nodes (11): Scraper registry (platform → scraper class), concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit (+3 more)

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

### Community 34 - "save_debug_snapshot"
Cohesion: 0.40
Nodes (4): _prune_debug_files(), save_debug_snapshot(), Assistant (Build · fullstack-development · 11.2s), Assistant (Build · fullstack-development · 28.1s)

### Community 35 - "Task 27 — Discovery LinkedIn + login/sesi"
Cohesion: 0.17
Nodes (11): _auth_state(), Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 27 — Discovery LinkedIn + login/sesi (+3 more)

### Community 37 - "KalibrrScraper"
Cohesion: 0.18
Nodes (8): _is_challenge(), KalibrrScraper, _save_snapshot(), test_iter_listings_guard_offset_against_count(), test_kalibrr_live_smoke(), test_search_challenge_raises_blocked(), fake_get(), test_search_malformed_json_raises_site_changed()

### Community 38 - "BaseScraper"
Cohesion: 0.14
Nodes (17): ARCHITECTURE document, DiscoveryPendingScraper, SiteChangedError, AuthRequiredError, BlockedError, BaseScraper, DeallsScraper, Discovery phase (+9 more)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "timeutil.py"
Cohesion: 0.19
Nodes (18): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), parse_posted(raw, now) (+10 more)

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "install_handlers"
Cohesion: 0.15
Nodes (11): AppError, ConflictError, install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload() (+3 more)

### Community 67 - "glints.py"
Cohesion: 0.13
Nodes (32): parse_salary(), draft_to_parts(), job_url(), location_label(), _next_data(), parse_detail_html(), parse_search_html(), salary_text() (+24 more)

### Community 68 - "codemap.py"
Cohesion: 0.30
Nodes (5): _file_lines(), main(), _module_doc(), _signature(), _summary()

### Community 69 - "RawListing"
Cohesion: 0.21
Nodes (4): BaseScraper, RawListing, FakeGlintsScraper, FakeJobstreetScraper

### Community 70 - "Pipeline Scraping Multi-Platform"
Cohesion: 0.20
Nodes (9): Eksekusi Scraping Asinkron (run_id), Dealls, Glints (glints.com/id), JobStreet (id.jobstreet.com), Pipeline Scraping Multi-Platform, Kalibrr, KitaLulus, LinkedIn (+1 more)

### Community 71 - "SiteChangedError"
Cohesion: 0.14
Nodes (39): SiteChangedError, _canonical(), canonical_url(), _clean_url(), _decode(), _detail_job(), _employment_type(), _find() (+31 more)

### Community 72 - "Task 28 — Scraper LinkedIn + fixture/test"
Cohesion: 0.22
Nodes (7): Test yang harus ditulis, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Task 28 — Scraper LinkedIn + fixture/test, Yang TIDAK boleh dilakukan

### Community 73 - "routers/scrape.py"
Cohesion: 0.27
Nodes (6): cancel_run(), get_run(), list_runs(), scrape_all(), scrape_platform(), ScrapeRequest

### Community 76 - "kalibrr.py"
Cohesion: 0.19
Nodes (24): _canonical(), _job_url(), _location(), parse_detail_payload(), parse_listing_payload(), _salary_text(), _work_mode(), Assistant (Build · fullstack-development · 7.9s) (+16 more)

### Community 77 - "Classifier"
Cohesion: 0.16
Nodes (14): Classification, Classifier, KeywordSpec, make_classifier(), test_description_one_strong_rejected(), test_description_penalty_reduces_score(), test_description_two_strong_accepted(), test_exclude_title_rejected_even_with_strong_description() (+6 more)

### Community 78 - "get_settings"
Cohesion: 0.22
Nodes (7): get_settings(), UnauthorizedError, get_logger(), setup_logging(), require_api_key(), create_app(), lifespan()

### Community 79 - "Penyaringan Lowongan (rule-based)"
Cohesion: 0.50
Nodes (4): BR-04 Aturan Usia Lowongan, Penyaringan Lowongan (rule-based), BR-01 Aturan Kata Kunci, BR-02/BR-03 Aturan Lokasi & Remote

### Community 80 - "test_scrape_jobs.py"
Cohesion: 0.10
Nodes (22): Catatan penting (hanya yang tidak terlihat dari kode), Daftar task, Masalah terbuka / utang teknis, PROGRESS, Status, _capture(), discover(), _is_json() (+14 more)

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
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 24 — Scraper Dealls + fixture/test, Test yang harus ditulis (+2 more)

### Community 92 - "registry.py"
Cohesion: 0.14
Nodes (14): KitaLulusScraper, LinkedInScraper, PintarnyaScraper, DiscoveryPendingScraper, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca (+6 more)

### Community 93 - "Task 30 — Scraper/stub Pintarnya + test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Task 30 — Scraper/stub Pintarnya + test, Test yang harus ditulis, Tujuan (+1 more)

### Community 94 - "jobstreet.py"
Cohesion: 0.23
Nodes (18): _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode(), html() (+10 more)

### Community 97 - "PLAN — Job Scraper API"
Cohesion: 0.40
Nodes (4): Dependensi, Indeks task, PLAN — Job Scraper API, Urutan eksekusi

### Community 98 - "DATABASE — Job Scraper API"
Cohesion: 0.83
Nodes (4): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, DATABASE — Job Scraper API

### Community 99 - "jobs.py"
Cohesion: 0.15
Nodes (9): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), list_platforms(), _csv(), iter_jsonl() (+1 more)

### Community 100 - "deduper.py"
Cohesion: 0.26
Nodes (13): _company_match(), _date(), DedupDecision, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible(), _posted_diff() (+5 more)

### Community 101 - "ScrapeContext"
Cohesion: 0.20
Nodes (10): ScrapeContext, DeallsScraper, _save_snapshot(), test_dealls_live_smoke(), test_fetch_detail_falls_back_to_ssr(), test_iter_listings_stops_on_empty_page(), fake_search(), test_search_challenge_raises_blocked() (+2 more)

### Community 102 - "test_location.py"
Cohesion: 0.21
Nodes (11): LocationNormalizer, _norm(), loc(), test_accept_location_rules(), test_city_alias(), test_city_and_province(), test_city_inherits_province(), test_foreign_country() (+3 more)

### Community 103 - "job_service.py"
Cohesion: 0.34
Nodes (11): NotFoundError, ValidationAppError, api_dict(), _csv_cell(), _csv_stream(), get_job(), _json_stream(), _jsonl_stream() (+3 more)

### Community 104 - "Dealls — catatan discovery (2026-11-02)"
Cohesion: 0.14
Nodes (13): Anti-bot / blokir, Batas laju yang diamati, Dealls — catatan discovery (2026-11-02), Endpoint final, Fixture, Metode terpilih, Pagination ("Lihat Lebih Banyak"), Pemetaan field → RawListing/RawJob (+5 more)

### Community 105 - "test_pipeline.py"
Cohesion: 0.47
Nodes (10): make_pipeline(), raw(), test_happy_path(), test_html_description_extracted(), test_irrelevant_title_rejected(), test_old_posting_rejected(), test_onsite_outside_java_rejected(), test_remote_abroad_rejected() (+2 more)

### Community 106 - "session.py"
Cohesion: 0.24
Nodes (4): health(), configure(), get_session(), check_browser()

### Community 107 - "JobStreet — catatan discovery & implementasi"
Cohesion: 0.25
Nodes (7): Batas kesopanan yang dipakai, Fixture, JobStreet — catatan discovery & implementasi, Parameter pencarian yang dipakai, Pemetaan field, Ringkasan metode, Risiko / catatan

### Community 109 - "NOTES — asumsi, konflik, penyimpangan"
Cohesion: 0.40
Nodes (4): Asumsi, Jebakan yang sudah terbukti, NOTES — asumsi, konflik, penyimpangan, Penyimpangan kode vs spesifikasi

### Community 110 - "Assistant (Build · fullstack-development · 7.3s)"
Cohesion: 0.50
Nodes (4): 5.5 Lokasi, 5.6 Deskripsi Lengkap (FR-05), 5.7 `external_id` dan `url_canonical` per Platform, Assistant (Build · fullstack-development · 7.3s)

## Ambiguous Edges - Review These
- `DATABASE.md` → `BR-01 Aturan Kata Kunci`  [AMBIGUOUS]
  PRD.md · relation: references
- `docs/platform_notes/<platform>.md` → `DATABASE.md`  [AMBIGUOUS]
  SCRAPER_SPEC.md · relation: references

## Knowledge Gaps
- **61 isolated node(s):** `job-scraper`, `Autentikasi API Key (X-API-Key)`, `BR-05 Aturan Duplikat`, `BR-06 Aturan Pembeda Duplikat vs Lowongan Serupa Berbeda`, `BR-07 Siklus Hidup Lowongan` (+56 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 571 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `normalizer.py`, `DATABASE — Job Scraper API`, `BaseScraper`, `Pipeline Scraping Multi-Platform`, `timeutil.py`, `test_scrape_jobs.py`, `dealls`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SiteChangedError` (e.g. with `Orchestrator` and `DeallsScraper`) actually correct?**
  _`SiteChangedError` has 20 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `Autentikasi API Key (X-API-Key)`, `BR-05 Aturan Duplikat` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `job_repo.py` be split into smaller, more focused modules?**
  _Cohesion score 0.053606065949567974 - nodes in this community are weakly interconnected._
- **Why does `RawJob` connect `orchestrator.py` to `normalizer.py`, `job_repo.py`, `glints.py`, `ScrapeContext`, `RawListing`, `SiteChangedError`, `KalibrrScraper`, `test_pipeline.py`, `Implementasi scraper Kalibrr sesuai plan task 22`, `kalibrr.py`, `Kalibrr — catatan discovery (2026-11-02)`, `Task 21 — Discovery Kalibrr`, `KalibrrScraper`, `Task 25 — Discovery KitaLulus`, `Task 24 — Scraper Dealls + fixture/test`, `registry.py`, `Task 30 — Scraper/stub Pintarnya + test`, `jobstreet.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `DATABASE.md` and `BR-01 Aturan Kata Kunci`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._