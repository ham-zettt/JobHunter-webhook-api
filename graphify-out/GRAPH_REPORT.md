# Graph Report - job-hunt  (2026-11-03)

## Corpus Check
- 172 files · ~776,446 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .example 1, .ini 1)

## Summary
- 1724 nodes · 4245 edges · 113 communities (83 shown, 30 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 365 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `8771a70b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Classifier
- deduper.py
- job_repo.py
- normalizer.py
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- CODEMAP
- scrape_service.py
- deduper.py
- re
- test_location.py
- kitalulus.py
- Implementasi scraper Kalibrr sesuai plan task 22
- FakeContext
- Kalibrr — catatan discovery (2026-11-02)
- test_pintarnya.py
- job-scraper
- health.py
- locations_java.yaml
- Kontrak Output Data Lowongan
- BaseScraper
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
- Pintarnya — catatan discovery (2026-11-02)
- Task 27 — Discovery LinkedIn + login/sesi
- keyword_repo.py
- parse_salary
- include
- BrowserPool
- Pipeline (normalize → filter → dedup)
- install_handlers
- platform_config
- AGENTS.md
- entrypoint.sh
- BR-02 (aturan lokasi onsite)
- test_pipeline.py
- job-scraper
- PRD — Job Scraper API
- codemap.py
- orchestrator.py
- json
- SiteChangedError
- linkedin.py
- routers/scrape.py
- opencode.json
- test_kalibrr.py
- main.py
- Settings
- SiteChangedError
- Task 04 — Docker, entrypoint, verifikasi `docker compose up`
- Task 21 — Discovery Kalibrr
- Task 23 — Discovery Dealls
- test_scrape_jobs.py
- Task 29 — Discovery Pintarnya
- Task 25 — Discovery KitaLulus
- test_prune.py
- Task 34 — Tuning dedup + reclassify (OPSIONAL)
- Task 35 — README final + contoh workflow n8n
- Task 36 — Uji end-to-end + review kriteria rilis PRD §13
- Task 24 — Scraper Dealls + fixture/test
- test_scrape_jobs.py
- _auth_state
- Pipeline Scraping Multi-Platform
- env.py
- linkedin_login.py
- PLAN — Job Scraper API
- KitaLulus — catatan discovery (2026-11-02)
- ScraperError
- blocked
- Task 22 — Scraper Kalibrr + fixture/test
- Glints — catatan discovery & implementasi
- Dealls — catatan discovery (2026-11-02)
- Task 26 — Scraper KitaLulus + fixture/test
- RawListing
- DATABASE — Job Scraper API
- Task 30 — Scraper/stub Pintarnya + test
- Task 28 — Scraper LinkedIn + fixture/test
- get_settings
- BlockedError
- LinkedIn — catatan discovery & implementasi
- Penyaringan Lowongan (rule-based)

## God Nodes (most connected - your core abstractions)
1. `SiteChangedError` - 80 edges
2. `RawListing` - 71 edges
3. `CODEMAP` - 71 edges
4. `RawJob` - 62 edges
5. `BlockedError` - 54 edges
6. `get_settings()` - 43 edges
7. `detect_challenge()` - 43 edges
8. `Implementasi scraper Kalibrr sesuai plan task 22` - 42 edges
9. `parse_salary()` - 39 edges
10. `ParseError` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Langkah-langkah` --references--> `RawListing`  [INFERRED]
  plan/16-max-age-tests.md → app/scrapers/base.py
- `P-26 — Scraper KitaLulus (task 26)` --references--> `RawListing`  [INFERRED]
  plan/NOTES.md → app/scrapers/base.py
- `Pemetaan field → `RawJob`` --references--> `RawJob`  [INFERRED]
  docs/platform_notes/kalibrr.md → app/scrapers/base.py
- `Test yang harus ditulis` --references--> `RawJob`  [INFERRED]
  plan/24-dealls-scraper.md → app/scrapers/base.py
- `Kriteria selesai (checklist)` --references--> `RawJob`  [INFERRED]
  plan/25-kitalulus-discovery.md → app/scrapers/base.py

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

## Communities (113 total, 30 thin omitted)

### Community 0 - "Classifier"
Cohesion: 0.18
Nodes (15): Classification, Classifier, KeywordSpec, _pattern(), make_classifier(), test_description_one_strong_rejected(), test_description_penalty_reduces_score(), test_description_two_strong_accepted() (+7 more)

### Community 1 - "deduper.py"
Cohesion: 0.22
Nodes (15): _company_match(), compute_fingerprint(), _date(), DedupDecision, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible() (+7 more)

### Community 2 - "job_repo.py"
Cohesion: 0.09
Nodes (44): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), list_platforms(), NotFoundError, ValidationAppError (+36 more)

### Community 3 - "normalizer.py"
Cohesion: 0.23
Nodes (16): canonical_url(), detect_employment_type(), detect_work_mode(), clean_text(), description_hash(), html_to_text(), looks_truncated(), normalize_company() (+8 more)

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.15
Nodes (20): PRD.md, SCRAPER_SPEC — Mekanisme Scraping per Platform, ARCHITECTURE.md, DATABASE.md, Dealls, Deskripsi Lengkap / FR-05 (§5.6), Prosedur Discovery (§3), Deteksi tipe_kerja (§5.4) (+12 more)

### Community 5 - "CODEMAP"
Cohesion: 0.03
Nodes (71): `app/api/__init__.py`, `app/api/router.py`, `app/api/routers/health.py`, `app/api/routers/__init__.py`, `app/api/routers/jobs.py`, `app/api/routers/keywords.py`, `app/api/routers/platforms.py`, `app/api/routers/scrape.py` (+63 more)

### Community 6 - "scrape_service.py"
Cohesion: 0.21
Nodes (14): AppError, ConflictError, PlatformDisabledError, PlatformNotFoundError, RunNotCancellableError, RunNotFoundError, ServiceUnavailableError, enabled_platforms() (+6 more)

### Community 7 - "deduper.py"
Cohesion: 0.16
Nodes (28): Deduper, Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 08 — Deduper L1–L3 + matriks 14 kasus, Test yang harus ditulis (+20 more)

### Community 8 - "re"
Cohesion: 0.19
Nodes (19): _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode(), html() (+11 more)

### Community 9 - "test_location.py"
Cohesion: 0.14
Nodes (16): accept_location(), LocationNormalizer, LocationResult, _norm(), Normalizer, Pipeline, PipelineResult, loc() (+8 more)

### Community 10 - "kitalulus.py"
Cohesion: 0.16
Nodes (9): BaseScraper, _save_snapshot(), _canonical_slug(), _card_count(), _dom_listings(), _expand_description(), _slug_from_href(), FakeGlintsScraper (+1 more)

### Community 11 - "Implementasi scraper Kalibrr sesuai plan task 22"
Cohesion: 0.05
Nodes (42): 5.5 Lokasi, 5.6 Deskripsi Lengkap (FR-05), 5.7 `external_id` dan `url_canonical` per Platform, 6. Alur Umum Setiap Scraper, Assistant (Build · fullstack-development · 10.1s), Assistant (Build · fullstack-development · 10.6s), Assistant (Build · fullstack-development · 10.9s), Assistant (Build · fullstack-development · 11.0s) (+34 more)

### Community 12 - "FakeContext"
Cohesion: 0.13
Nodes (4): FakeContext, FakePage, FakeRequest, FakeResponse

### Community 13 - "Kalibrr — catatan discovery (2026-11-02)"
Cohesion: 0.17
Nodes (11): Batas laju aman yang diamati, Fixture, Kalibrr — catatan discovery (2026-11-02), Lokasi deskripsi dan kelengkapan, Metode terpilih, Pagination, Pemetaan field → `RawJob`, Perbedaan dari SCRAPER_SPEC.md (+3 more)

### Community 14 - "test_pintarnya.py"
Cohesion: 0.11
Nodes (41): ScrapeContext, canonical_url(), _description_html(), _employment_type(), _is_challenge(), _items(), _job_ld(), _location() (+33 more)

### Community 15 - "job-scraper"
Cohesion: 0.13
Nodes (14): interval, retries, test, timeout, build, env_file, healthcheck, init (+6 more)

### Community 16 - "health.py"
Cohesion: 0.21
Nodes (5): health(), check_browser(), test_health_browser_failure_returns_503(), test_health_ok(), fake()

### Community 17 - "locations_java.yaml"
Cohesion: 0.20
Nodes (9): location (normalization + is_in_java + remote Indonesia), country_foreign, country_id, outside_java_cities, name, province, outside_java_provinces, remote_words (+1 more)

### Community 18 - "Kontrak Output Data Lowongan"
Cohesion: 0.22
Nodes (10): DATABASE.md, Autentikasi API Key (X-API-Key), Deduplikasi Lowongan, BR-05 Aturan Duplikat, BR-06 Aturan Pembeda Duplikat vs Lowongan Serupa Berbeda, Kontrak Output Data Lowongan, BR-07 Siklus Hidup Lowongan, REST API /api/v1 (+2 more)

### Community 19 - "BaseScraper"
Cohesion: 0.15
Nodes (13): ARCHITECTURE document, DiscoveryPendingScraper, AuthRequiredError, BlockedError, LinkedIn, BaseScraper, DeallsScraper, GlintsScraper (+5 more)

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
Cohesion: 0.17
Nodes (11): Scraper registry (platform → scraper class), concurrency, delay_ms, enabled, max_details_per_run, max_duration_sec, max_pages_per_term, search_terms_limit (+3 more)

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

### Community 34 - "Pintarnya — catatan discovery (2026-11-02)"
Cohesion: 0.11
Nodes (17): SiteChangedError, Deskripsi lengkap, Endpoint / selector final, Fixture, Kepatuhan & batas laju, Keputusan, Metode terpilih, Pagination / infinite scroll (+9 more)

### Community 35 - "Task 27 — Discovery LinkedIn + login/sesi"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 27 — Discovery LinkedIn + login/sesi, Test yang harus ditulis, Tujuan (+1 more)

### Community 37 - "keyword_repo.py"
Cohesion: 0.06
Nodes (40): create_keyword(), delete_keyword(), list_keywords(), patch_keyword(), reseed(), KeywordCreate, KeywordUpdate, Base (+32 more)

### Community 38 - "parse_salary"
Cohesion: 0.06
Nodes (66): _detect_currency(), parse_salary(), SalaryInfo, _to_number(), draft_to_parts(), job_url(), location_label(), _next_data() (+58 more)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "BrowserPool"
Cohesion: 0.07
Nodes (19): BrowserPool, Anti-bot / akses, Batas kesopanan yang dipakai, Fixture, JobStreet — catatan discovery & implementasi, Parameter pencarian yang dipakai, Pemetaan field, Ringkasan metode (+11 more)

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "install_handlers"
Cohesion: 0.27
Nodes (6): install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload()

### Community 54 - "test_pipeline.py"
Cohesion: 0.47
Nodes (10): make_pipeline(), raw(), test_happy_path(), test_html_description_extracted(), test_irrelevant_title_rejected(), test_old_posting_rejected(), test_onsite_outside_java_rejected(), test_remote_abroad_rejected() (+2 more)

### Community 67 - "PRD — Job Scraper API"
Cohesion: 0.20
Nodes (9): docs/DECISIONS.md, ARCHITECTURE.md, SCRAPER_SPEC.md, Deployment Docker (satu container, satu worker uvicorn), FastAPI, PRD — Job Scraper API, Playwright, SQLite (WAL mode) (+1 more)

### Community 68 - "codemap.py"
Cohesion: 0.30
Nodes (5): _file_lines(), main(), _module_doc(), _signature(), _summary()

### Community 70 - "json"
Cohesion: 0.10
Nodes (32): utc_iso(), ScrapeRun, ScrapeRunSource, add_error(), cancel_run(), create_run(), details_fetched_since(), _duration() (+24 more)

### Community 71 - "SiteChangedError"
Cohesion: 0.10
Nodes (45): _canonical(), canonical_url(), _clean_url(), DeallsScraper, _decode(), _detail_job(), _employment_type(), _find() (+37 more)

### Community 72 - "linkedin.py"
Cohesion: 0.08
Nodes (39): AuthRequiredError, _auth_url(), _check_response(), _company_from_dom(), _description_html(), _expand_and_wait(), _inside_about_company(), _label() (+31 more)

### Community 73 - "routers/scrape.py"
Cohesion: 0.19
Nodes (6): cancel_run(), get_run(), list_runs(), scrape_all(), scrape_platform(), ScrapeRequest

### Community 76 - "test_kalibrr.py"
Cohesion: 0.11
Nodes (33): _canonical(), _is_challenge(), _job_url(), KalibrrScraper, _location(), _next_data(), parse_detail_payload(), parse_listing_payload() (+25 more)

### Community 78 - "main.py"
Cohesion: 0.42
Nodes (4): UnauthorizedError, require_api_key(), create_app(), lifespan()

### Community 80 - "SiteChangedError"
Cohesion: 0.14
Nodes (17): RawJob, RawListing, jitter(), save_debug_snapshot(), ParseError, SiteChangedError, GlintsScraper, JobStreetScraper (+9 more)

### Community 81 - "Task 04 — Docker, entrypoint, verifikasi `docker compose up`"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 04 — Docker, entrypoint, verifikasi `docker compose up`, Test yang harus ditulis (+2 more)

### Community 82 - "Task 21 — Discovery Kalibrr"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 21 — Discovery Kalibrr, Test yang harus ditulis, Tujuan (+1 more)

### Community 83 - "Task 23 — Discovery Dealls"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 23 — Discovery Dealls, Test yang harus ditulis (+2 more)

### Community 84 - "test_scrape_jobs.py"
Cohesion: 0.19
Nodes (18): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), parse_posted(raw, now) (+10 more)

### Community 85 - "Task 29 — Discovery Pintarnya"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 29 — Discovery Pintarnya, Test yang harus ditulis (+2 more)

### Community 86 - "Task 25 — Discovery KitaLulus"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 25 — Discovery KitaLulus, Test yang harus ditulis (+2 more)

### Community 87 - "test_prune.py"
Cohesion: 0.10
Nodes (31): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 33 — Backup, retensi, `scripts/prune.py`, Test yang harus ditulis (+23 more)

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

### Community 92 - "test_scrape_jobs.py"
Cohesion: 0.05
Nodes (49): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 16 — Uji filter `max_age_days`, Test yang harus ditulis (+41 more)

### Community 93 - "_auth_state"
Cohesion: 0.50
Nodes (4): _auth_state(), Autentikasi, File yang perlu dibaca, File yang perlu dibaca

### Community 94 - "Pipeline Scraping Multi-Platform"
Cohesion: 0.29
Nodes (7): Eksekusi Scraping Asinkron (run_id), Dealls, Glints (glints.com/id), JobStreet (id.jobstreet.com), Pipeline Scraping Multi-Platform, Kalibrr, KitaLulus

### Community 95 - "env.py"
Cohesion: 0.47
Nodes (3): run_migrations_offline(), run_migrations_online(), _sync_url()

### Community 96 - "linkedin_login.py"
Cohesion: 0.33
Nodes (3): Fase Pengembangan F0–F6 (PRD §12), Folder plan/ (task files untuk AI Agent), main()

### Community 97 - "PLAN — Job Scraper API"
Cohesion: 0.40
Nodes (4): Dependensi, Indeks task, PLAN — Job Scraper API, Urutan eksekusi

### Community 98 - "KitaLulus — catatan discovery (2026-11-02)"
Cohesion: 0.15
Nodes (12): Endpoint / selector final, Fixture, Kepatuhan & batas laju, KitaLulus — catatan discovery (2026-11-02), Metode terpilih, Pagination / "load more", Pemetaan field → RawListing/RawJob, Perbedaan dari SCRAPER_SPEC.md (+4 more)

### Community 100 - "blocked"
Cohesion: 0.29
Nodes (7): blocked(), Risiko, Kriteria selesai (checklist), Tujuan, 8.1 Registry, 8.3 Definisi Selesai (per platform), 8. Registry, Pengujian, dan Definisi Selesai

### Community 101 - "Task 22 — Scraper Kalibrr + fixture/test"
Cohesion: 0.22
Nodes (8): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Koreksi berdasarkan discovery (mengalahkan langkah di bawah bila bertentangan), Task 22 — Scraper Kalibrr + fixture/test, Tujuan, Yang TIDAK boleh dilakukan

### Community 102 - "Glints — catatan discovery & implementasi"
Cohesion: 0.25
Nodes (7): Anti-bot, Batas kesopanan, Fixture, Glints — catatan discovery & implementasi, Keterbatasan paginasi (penting), Pemetaan field, Ringkasan metode

### Community 104 - "Dealls — catatan discovery (2026-11-02)"
Cohesion: 0.14
Nodes (13): Anti-bot / blokir, Batas laju yang diamati, Dealls — catatan discovery (2026-11-02), Endpoint final, Fixture, Metode terpilih, Pagination ("Lihat Lebih Banyak"), Pemetaan field → RawListing/RawJob (+5 more)

### Community 105 - "Task 26 — Scraper KitaLulus + fixture/test"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 26 — Scraper KitaLulus + fixture/test, Test yang harus ditulis (+2 more)

### Community 106 - "RawListing"
Cohesion: 0.47
Nodes (6): parse_listing_payload (pure parser), RawListing, Challenge detection, fetch_detail, iter_listings, XxxScraper (platform scraper template)

### Community 107 - "DATABASE — Job Scraper API"
Cohesion: 0.83
Nodes (4): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, DATABASE — Job Scraper API

### Community 108 - "Task 30 — Scraper/stub Pintarnya + test"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Task 30 — Scraper/stub Pintarnya + test, Test yang harus ditulis, Tujuan (+1 more)

### Community 109 - "Task 28 — Scraper LinkedIn + fixture/test"
Cohesion: 0.25
Nodes (7): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 28 — Scraper LinkedIn + fixture/test, Yang TIDAK boleh dilakukan

### Community 111 - "get_settings"
Cohesion: 0.13
Nodes (9): get_settings(), get_logger(), setup_logging(), configure(), get_session(), CallbackRejectedError, validate_callback_url(), _prune_debug_files() (+1 more)

### Community 112 - "BlockedError"
Cohesion: 0.07
Nodes (36): detect_challenge(), _attempt(), fetch_with_retry(), _RateLimited, _retry_after_seconds(), BlockedError, TransientNetworkError, Risiko (+28 more)

### Community 114 - "LinkedIn — catatan discovery & implementasi"
Cohesion: 0.17
Nodes (11): URL pencarian, Fixture, Kartu daftar, LinkedIn — catatan discovery & implementasi, Panel detail, Parameter pencarian (terbukti), Perintah discovery (reproduksi), Ringkasan metode (+3 more)

### Community 117 - "Penyaringan Lowongan (rule-based)"
Cohesion: 0.50
Nodes (4): BR-04 Aturan Usia Lowongan, Penyaringan Lowongan (rule-based), BR-01 Aturan Kata Kunci, BR-02/BR-03 Aturan Lokasi & Remote

## Ambiguous Edges - Review These
- `BR-01 Aturan Kata Kunci` → `DATABASE.md`  [AMBIGUOUS]
  PRD.md · relation: references
- `docs/platform_notes/<platform>.md` → `DATABASE.md`  [AMBIGUOUS]
  SCRAPER_SPEC.md · relation: references

## Knowledge Gaps
- **59 isolated node(s):** `job-scraper`, `BR-04 Aturan Usia Lowongan`, `BR-02/BR-03 Aturan Lokasi & Remote`, `Autentikasi API Key (X-API-Key)`, `Deployment Docker (satu container, satu worker uvicorn)` (+54 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 636 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `normalizer.py`, `parse_salary`, `RawListing`, `DATABASE — Job Scraper API`, `BaseScraper`, `test_scrape_jobs.py`, `test_prune.py`, `jobstreet`, `Pipeline Scraping Multi-Platform`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `SiteChangedError` (e.g. with `Orchestrator` and `DeallsScraper`) actually correct?**
  _`SiteChangedError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `BR-04 Aturan Usia Lowongan`, `BR-02/BR-03 Aturan Lokasi & Remote` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `job_repo.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08591466978375219 - nodes in this community are weakly interconnected._
- **Why does `RawJob` connect `SiteChangedError` to `normalizer.py`, `re`, `test_location.py`, `kitalulus.py`, `Implementasi scraper Kalibrr sesuai plan task 22`, `Kalibrr — catatan discovery (2026-11-02)`, `test_pintarnya.py`, `parse_salary`, `test_pipeline.py`, `orchestrator.py`, `json`, `SiteChangedError`, `linkedin.py`, `test_kalibrr.py`, `._run_platform`, `Task 25 — Discovery KitaLulus`, `Task 24 — Scraper Dealls + fixture/test`, `Task 26 — Scraper KitaLulus + fixture/test`, `Task 30 — Scraper/stub Pintarnya + test`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `BR-01 Aturan Kata Kunci` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._