# Graph Report - job-hunt  (2026-11-02)

## Corpus Check
- 155 files · ~634,747 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .example 1, .ini 1)

## Summary
- 1477 nodes · 3450 edges · 109 communities (79 shown, 30 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2fe61cf3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- normalizer.py
- keyword_repo.py
- job_repo.py
- Task 16 — Uji filter `max_age_days`
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- CODEMAP
- scrape_service.py
- deduper.py
- env.py
- PRD — Job Scraper API
- ._run_platform
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
- kitalulus.py
- include
- pipeline.py
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
- json
- SiteChangedError
- Task 28 — Scraper LinkedIn + fixture/test
- routers/scrape.py
- opencode.json
- kalibrr.py
- Base
- orchestrator.py
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
- Task 26 — Scraper KitaLulus + fixture/test
- Task 30 — Scraper/stub Pintarnya + test
- jobstreet.py
- BrowserPool
- linkedin_login.py
- PLAN — Job Scraper API
- KitaLulus — catatan discovery (2026-11-02)
- job_service.py
- location
- Task 22 — Scraper Kalibrr + fixture/test
- Glints — catatan discovery & implementasi
- platforms
- Dealls — catatan discovery (2026-11-02)
- JobStreet — catatan discovery & implementasi
- Settings
- NOTES — asumsi, konflik, penyimpangan
- Assistant (Build · fullstack-development · 7.3s)

## God Nodes (most connected - your core abstractions)
1. `CODEMAP` - 69 edges
2. `SiteChangedError` - 65 edges
3. `RawListing` - 54 edges
4. `RawJob` - 50 edges
5. `Implementasi scraper Kalibrr sesuai plan task 22` - 42 edges
6. `get_settings()` - 39 edges
7. `BlockedError` - 37 edges
8. `SCRAPER_SPEC — Mekanisme Scraping per Platform` - 34 edges
9. `parse_salary()` - 33 edges
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

## Communities (109 total, 30 thin omitted)

### Community 0 - "normalizer.py"
Cohesion: 0.05
Nodes (63): Classification, Classifier, KeywordSpec, _pattern(), canonical_url(), detect_employment_type(), detect_work_mode(), Normalizer (+55 more)

### Community 1 - "keyword_repo.py"
Cohesion: 0.11
Nodes (27): ConflictError, KeywordRule, active_rules(), create_rule(), delete_rule(), list_rules(), reseed(), rule_dict() (+19 more)

### Community 2 - "job_repo.py"
Cohesion: 0.17
Nodes (25): Job, add_link(), _apply_richer(), build_query(), count_jobs_by_platform(), export_jobs(), find_candidates(), find_known() (+17 more)

### Community 3 - "Task 16 — Uji filter `max_age_days`"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 16 — Uji filter `max_age_days`, Test yang harus ditulis, Tujuan (+1 more)

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.05
Nodes (54): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, parse_posted(raw, now), DATABASE — Job Scraper API, ARCHITECTURE document, DiscoveryPendingScraper, SiteChangedError (+46 more)

### Community 5 - "CODEMAP"
Cohesion: 0.03
Nodes (69): `app/api/__init__.py`, `app/api/router.py`, `app/api/routers/health.py`, `app/api/routers/__init__.py`, `app/api/routers/jobs.py`, `app/api/routers/keywords.py`, `app/api/routers/platforms.py`, `app/api/routers/scrape.py` (+61 more)

### Community 6 - "scrape_service.py"
Cohesion: 0.14
Nodes (18): AppError, NotFoundError, PlatformDisabledError, PlatformNotFoundError, RunNotCancellableError, RunNotFoundError, ServiceUnavailableError, UnauthorizedError (+10 more)

### Community 7 - "deduper.py"
Cohesion: 0.10
Nodes (42): _company_match(), compute_fingerprint(), _date(), Deduper, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible() (+34 more)

### Community 8 - "env.py"
Cohesion: 0.47
Nodes (3): run_migrations_offline(), run_migrations_online(), _sync_url()

### Community 9 - "PRD — Job Scraper API"
Cohesion: 0.20
Nodes (9): docs/DECISIONS.md, ARCHITECTURE.md, SCRAPER_SPEC.md, Deployment Docker (satu container, satu worker uvicorn), FastAPI, PRD — Job Scraper API, Playwright, SQLite (WAL mode) (+1 more)

### Community 10 - "._run_platform"
Cohesion: 0.23
Nodes (3): Pipeline, Orchestrator, RunManager

### Community 11 - "Implementasi scraper Kalibrr sesuai plan task 22"
Cohesion: 0.05
Nodes (36): 6. Alur Umum Setiap Scraper, Assistant (Build · fullstack-development · 10.1s), Assistant (Build · fullstack-development · 10.6s), Assistant (Build · fullstack-development · 10.9s), Assistant (Build · fullstack-development · 12.4s), Assistant (Build · fullstack-development · 14.4s), Assistant (Build · fullstack-development · 15.5s), Assistant (Build · fullstack-development · 19.1s) (+28 more)

### Community 12 - "keywords.py"
Cohesion: 0.16
Nodes (7): create_keyword(), delete_keyword(), list_keywords(), patch_keyword(), reseed(), KeywordCreate, KeywordUpdate

### Community 13 - "Kalibrr — catatan discovery (2026-11-02)"
Cohesion: 0.17
Nodes (11): Batas laju aman yang diamati, Fixture, Kalibrr — catatan discovery (2026-11-02), Lokasi deskripsi dan kelengkapan, Metode terpilih, Pagination, Pemetaan field → `RawJob`, Perbedaan dari SCRAPER_SPEC.md (+3 more)

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
Nodes (17): jitter(), AuthRequiredError, BlockedError, ParseError, ScraperError, SiteChangedError, TransientNetworkError, GlintsScraper (+9 more)

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

### Community 34 - "save_debug_snapshot"
Cohesion: 0.40
Nodes (4): _prune_debug_files(), save_debug_snapshot(), Assistant (Build · fullstack-development · 11.2s), Assistant (Build · fullstack-development · 28.1s)

### Community 35 - "Task 27 — Discovery LinkedIn + login/sesi"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 27 — Discovery LinkedIn + login/sesi, Tujuan (+1 more)

### Community 37 - "KalibrrScraper"
Cohesion: 0.21
Nodes (8): _is_challenge(), KalibrrScraper, _save_snapshot(), test_iter_listings_guard_offset_against_count(), test_kalibrr_live_smoke(), test_search_challenge_raises_blocked(), fake_get(), test_search_malformed_json_raises_site_changed()

### Community 38 - "kitalulus.py"
Cohesion: 0.12
Nodes (36): _bounds_salary(), _canonical_slug(), _card_count(), _dom_description(), _dom_listings(), _employment_type(), _expand_description(), _flight_listings() (+28 more)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "pipeline.py"
Cohesion: 0.09
Nodes (31): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), is_too_old() (+23 more)

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "install_handlers"
Cohesion: 0.27
Nodes (6): install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload()

### Community 67 - "glints.py"
Cohesion: 0.21
Nodes (22): draft_to_parts(), job_url(), location_label(), _next_data(), parse_detail_html(), parse_search_html(), salary_text(), slugify() (+14 more)

### Community 68 - "codemap.py"
Cohesion: 0.30
Nodes (5): _file_lines(), main(), _module_doc(), _signature(), _summary()

### Community 69 - "RawListing"
Cohesion: 0.17
Nodes (11): BaseScraper, RawJob, RawListing, LinkedInScraper, PintarnyaScraper, DiscoveryPendingScraper, File yang perlu dibaca, Test yang harus ditulis (+3 more)

### Community 70 - "json"
Cohesion: 0.23
Nodes (20): utc_iso(), ScrapeRun, ScrapeRunSource, add_error(), cancel_run(), create_run(), _duration(), finish_run() (+12 more)

### Community 71 - "SiteChangedError"
Cohesion: 0.10
Nodes (46): ScrapeContext, _canonical(), canonical_url(), _clean_url(), DeallsScraper, _decode(), _detail_job(), _employment_type() (+38 more)

### Community 72 - "Task 28 — Scraper LinkedIn + fixture/test"
Cohesion: 0.20
Nodes (8): Test yang harus ditulis, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Task 28 — Scraper LinkedIn + fixture/test, Yang TIDAK boleh dilakukan

### Community 73 - "routers/scrape.py"
Cohesion: 0.15
Nodes (7): list_platforms(), cancel_run(), get_run(), list_runs(), scrape_all(), scrape_platform(), ScrapeRequest

### Community 76 - "kalibrr.py"
Cohesion: 0.20
Nodes (25): _canonical(), _job_url(), _location(), _next_data(), parse_detail_payload(), parse_listing_payload(), _salary_text(), _work_mode() (+17 more)

### Community 77 - "Base"
Cohesion: 0.20
Nodes (8): Base, LocationAlias, JobRunLink, ensure_schema_sync(), downgrade(), upgrade(), auth_headers(), clean_db()

### Community 78 - "orchestrator.py"
Cohesion: 0.12
Nodes (10): health(), get_settings(), get_logger(), setup_logging(), ensure_schema(), configure(), get_session(), create_app() (+2 more)

### Community 79 - "Penyaringan Lowongan (rule-based)"
Cohesion: 0.50
Nodes (4): BR-04 Aturan Usia Lowongan, Penyaringan Lowongan (rule-based), BR-01 Aturan Kata Kunci, BR-02/BR-03 Aturan Lokasi & Remote

### Community 80 - "test_scrape_jobs.py"
Cohesion: 0.13
Nodes (16): _capture(), discover(), _is_json(), main(), _slug(), fake_registry(), scrape(), seed_keywords() (+8 more)

### Community 81 - "Task 04 — Docker, entrypoint, verifikasi `docker compose up`"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 04 — Docker, entrypoint, verifikasi `docker compose up`, Test yang harus ditulis (+2 more)

### Community 82 - "Task 21 — Discovery Kalibrr"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 21 — Discovery Kalibrr, Test yang harus ditulis, Tujuan (+1 more)

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

### Community 92 - "Task 26 — Scraper KitaLulus + fixture/test"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 26 — Scraper KitaLulus + fixture/test, Test yang harus ditulis (+2 more)

### Community 93 - "Task 30 — Scraper/stub Pintarnya + test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Task 30 — Scraper/stub Pintarnya + test, Test yang harus ditulis, Tujuan (+1 more)

### Community 94 - "jobstreet.py"
Cohesion: 0.20
Nodes (18): _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode(), html() (+10 more)

### Community 97 - "PLAN — Job Scraper API"
Cohesion: 0.40
Nodes (4): Dependensi, Indeks task, PLAN — Job Scraper API, Urutan eksekusi

### Community 98 - "KitaLulus — catatan discovery (2026-11-02)"
Cohesion: 0.15
Nodes (12): Endpoint / selector final, Fixture, Kepatuhan & batas laju, KitaLulus — catatan discovery (2026-11-02), Metode terpilih, Pagination / "load more", Pemetaan field → RawListing/RawJob, Perbedaan dari SCRAPER_SPEC.md (+4 more)

### Community 99 - "job_service.py"
Cohesion: 0.15
Nodes (18): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), api_dict(), _csv(), iter_jsonl() (+10 more)

### Community 100 - "location"
Cohesion: 0.22
Nodes (9): blocked(), Risiko, URL pencarian, Kriteria selesai (checklist), Tujuan, 8.1 Registry, 8.3 Definisi Selesai (per platform), 8. Registry, Pengujian, dan Definisi Selesai (+1 more)

### Community 101 - "Task 22 — Scraper Kalibrr + fixture/test"
Cohesion: 0.22
Nodes (8): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Koreksi berdasarkan discovery (mengalahkan langkah di bawah bila bertentangan), Task 22 — Scraper Kalibrr + fixture/test, Tujuan, Yang TIDAK boleh dilakukan

### Community 102 - "Glints — catatan discovery & implementasi"
Cohesion: 0.25
Nodes (7): Anti-bot, Batas kesopanan, Fixture, Glints — catatan discovery & implementasi, Keterbatasan paginasi (penting), Pemetaan field, Ringkasan metode

### Community 103 - "platforms"
Cohesion: 0.50
Nodes (3): Scraper registry (platform → scraper class), platforms, Kesopanan, Laju, dan Penanganan Blokir (§4)

### Community 104 - "Dealls — catatan discovery (2026-11-02)"
Cohesion: 0.14
Nodes (13): Anti-bot / blokir, Batas laju yang diamati, Dealls — catatan discovery (2026-11-02), Endpoint final, Fixture, Metode terpilih, Pagination ("Lihat Lebih Banyak"), Pemetaan field → RawListing/RawJob (+5 more)

### Community 107 - "JobStreet — catatan discovery & implementasi"
Cohesion: 0.25
Nodes (7): Batas kesopanan yang dipakai, Fixture, JobStreet — catatan discovery & implementasi, Parameter pencarian yang dipakai, Pemetaan field, Ringkasan metode, Risiko / catatan

### Community 109 - "NOTES — asumsi, konflik, penyimpangan"
Cohesion: 0.29
Nodes (6): Asumsi, Jebakan yang sudah terbukti, Konflik antar dokumen, NOTES — asumsi, konflik, penyimpangan, P-21 — KitaLulus (task 25), Penyimpangan kode vs spesifikasi

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
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 584 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `pipeline.py`, `normalizer.py`, `test_scrape_jobs.py`, `platforms`?**
  _High betweenness centrality (0.200) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `SiteChangedError` (e.g. with `Orchestrator` and `DeallsScraper`) actually correct?**
  _`SiteChangedError` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `Autentikasi API Key (X-API-Key)`, `BR-05 Aturan Duplikat` to the rest of the system?**
  _61 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `normalizer.py` be split into smaller, more focused modules?**
  _Cohesion score 0.052659716653301256 - nodes in this community are weakly interconnected._
- **Why does `RawJob` connect `RawListing` to `normalizer.py`, `glints.py`, `KalibrrScraper`, `kitalulus.py`, `SiteChangedError`, `pipeline.py`, `._run_platform`, `Implementasi scraper Kalibrr sesuai plan task 22`, `kalibrr.py`, `Kalibrr — catatan discovery (2026-11-02)`, `orchestrator.py`, `KalibrrScraper`, `Task 25 — Discovery KitaLulus`, `Task 24 — Scraper Dealls + fixture/test`, `Task 26 — Scraper KitaLulus + fixture/test`, `Task 30 — Scraper/stub Pintarnya + test`, `jobstreet.py`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `DATABASE.md` and `BR-01 Aturan Kata Kunci`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._