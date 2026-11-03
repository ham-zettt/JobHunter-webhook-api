# Graph Report - job-hunt  (2026-11-03)

## Corpus Check
- 167 files · ~774,398 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 7 file(s) not represented in the graph (top: (none) 3, .example 1, .ini 1)

## Summary
- 1628 nodes · 3964 edges · 117 communities (90 shown, 27 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 329 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `84e7df52`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Classifier
- loader.py
- job_repo.py
- Task 16 — Uji filter `max_age_days`
- SCRAPER_SPEC — Mekanisme Scraping per Platform
- CODEMAP
- scrape_service.py
- deduper.py
- re
- test_location.py
- Base
- Implementasi scraper Kalibrr sesuai plan task 22
- keywords.py
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
- kitalulus.py
- include
- timeutil.py
- Pipeline (normalize → filter → dedup)
- errors.py
- platform_config
- AGENTS.md
- entrypoint.sh
- BR-02 (aturan lokasi onsite)
- job-scraper
- glints.py
- codemap.py
- RawJob
- json
- SiteChangedError
- linkedin.py
- routers/scrape.py
- opencode.json
- test_kalibrr.py
- asyncio
- get_settings
- test_pipeline.py
- SiteChangedError
- Task 04 — Docker, entrypoint, verifikasi `docker compose up`
- Task 21 — Discovery Kalibrr
- Task 23 — Discovery Dealls
- test_scrape_jobs.py
- Task 29 — Discovery Pintarnya
- KalibrrScraper
- Task 33 — Backup, retensi, `scripts/prune.py`
- Task 34 — Tuning dedup + reclassify (OPSIONAL)
- Task 35 — README final + contoh workflow n8n
- Task 36 — Uji end-to-end + review kriteria rilis PRD §13
- Task 24 — Scraper Dealls + fixture/test
- job_service.py
- jobs.py
- Pipeline Scraping Multi-Platform
- BlockedError
- linkedin_login.py
- PLAN — Job Scraper API
- KitaLulus — catatan discovery (2026-11-02)
- browser.py
- blocked
- Task 22 — Scraper Kalibrr + fixture/test
- Glints — catatan discovery & implementasi
- platforms
- Dealls — catatan discovery (2026-11-02)
- Task 26 — Scraper KitaLulus + fixture/test
- RawListing
- DATABASE — Job Scraper API
- env.py
- Task 28 — Scraper LinkedIn + fixture/test
- PROGRESS
- registry.py
- detect_challenge
- LinkedIn
- LinkedIn — catatan discovery & implementasi
- _auth_state
- Penyaringan Lowongan (rule-based)

## God Nodes (most connected - your core abstractions)
1. `SiteChangedError` - 81 edges
2. `RawListing` - 71 edges
3. `CODEMAP` - 69 edges
4. `RawJob` - 62 edges
5. `BlockedError` - 51 edges
6. `Implementasi scraper Kalibrr sesuai plan task 22` - 42 edges
7. `get_settings()` - 41 edges
8. `detect_challenge()` - 39 edges
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

## Communities (117 total, 27 thin omitted)

### Community 0 - "Classifier"
Cohesion: 0.18
Nodes (13): Classification, Classifier, KeywordSpec, make_classifier(), test_description_one_strong_rejected(), test_description_penalty_reduces_score(), test_description_two_strong_accepted(), test_exclude_title_rejected_even_with_strong_description() (+5 more)

### Community 1 - "loader.py"
Cohesion: 0.28
Nodes (9): _keyword_rows(), _load(), _location_rows(), seed_all(), seed_keywords(), seed_locations(), test_seed_contains_strong_weak_and_exclude(), test_seed_is_idempotent() (+1 more)

### Community 2 - "job_repo.py"
Cohesion: 0.18
Nodes (22): Job, _apply_richer(), build_query(), count_jobs_by_platform(), export_jobs(), find_candidates(), find_known(), get_job() (+14 more)

### Community 3 - "Task 16 — Uji filter `max_age_days`"
Cohesion: 0.22
Nodes (8): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 16 — Uji filter `max_age_days`, Tujuan, Yang TIDAK boleh dilakukan

### Community 4 - "SCRAPER_SPEC — Mekanisme Scraping per Platform"
Cohesion: 0.16
Nodes (18): parse_posted(raw, now), PRD.md, SCRAPER_SPEC — Mekanisme Scraping per Platform, ARCHITECTURE.md, DATABASE.md, Parser Tanggal (§5.1), Dealls, Deskripsi Lengkap / FR-05 (§5.6) (+10 more)

### Community 5 - "CODEMAP"
Cohesion: 0.03
Nodes (69): `app/api/__init__.py`, `app/api/router.py`, `app/api/routers/health.py`, `app/api/routers/__init__.py`, `app/api/routers/jobs.py`, `app/api/routers/keywords.py`, `app/api/routers/platforms.py`, `app/api/routers/scrape.py` (+61 more)

### Community 6 - "scrape_service.py"
Cohesion: 0.19
Nodes (13): PlatformDisabledError, PlatformNotFoundError, RunNotCancellableError, RunNotFoundError, CallbackRejectedError, validate_callback_url(), enabled_platforms(), cancel_run() (+5 more)

### Community 7 - "deduper.py"
Cohesion: 0.10
Nodes (43): _company_match(), compute_fingerprint(), _date(), Deduper, description_similarity(), _is_cross_platform(), _is_repost(), location_compatible() (+35 more)

### Community 8 - "re"
Cohesion: 0.23
Nodes (18): _dom_text(), _employment_type(), _extract_assignment(), extract_redux_state(), parse_detail_html(), parse_search_payload(), _work_mode(), html() (+10 more)

### Community 9 - "test_location.py"
Cohesion: 0.21
Nodes (11): LocationNormalizer, _norm(), loc(), test_accept_location_rules(), test_city_alias(), test_city_and_province(), test_city_inherits_province(), test_foreign_country() (+3 more)

### Community 10 - "Base"
Cohesion: 0.19
Nodes (8): Base, LocationAlias, JobRunLink, ensure_schema_sync(), downgrade(), upgrade(), auth_headers(), clean_db()

### Community 11 - "Implementasi scraper Kalibrr sesuai plan task 22"
Cohesion: 0.05
Nodes (39): 5.5 Lokasi, 5.6 Deskripsi Lengkap (FR-05), 5.7 `external_id` dan `url_canonical` per Platform, 6. Alur Umum Setiap Scraper, Assistant (Build · fullstack-development · 10.1s), Assistant (Build · fullstack-development · 10.6s), Assistant (Build · fullstack-development · 10.9s), Assistant (Build · fullstack-development · 14.4s) (+31 more)

### Community 12 - "keywords.py"
Cohesion: 0.12
Nodes (9): create_keyword(), list_keywords(), patch_keyword(), reseed(), list_platforms(), KeywordCreate, KeywordUpdate, list_platforms() (+1 more)

### Community 13 - "Kalibrr — catatan discovery (2026-11-02)"
Cohesion: 0.06
Nodes (31): Batas laju aman yang diamati, Fixture, Kalibrr — catatan discovery (2026-11-02), Lokasi deskripsi dan kelengkapan, Metode terpilih, Pagination, Pemetaan field → `RawJob`, Perbedaan dari SCRAPER_SPEC.md (+23 more)

### Community 14 - "test_pintarnya.py"
Cohesion: 0.08
Nodes (44): ScrapeContext, canonical_url(), _description_html(), _employment_type(), _is_challenge(), _items(), _job_ld(), _location() (+36 more)

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
Cohesion: 0.14
Nodes (18): docs/DECISIONS.md, ARCHITECTURE.md, DATABASE.md, SCRAPER_SPEC.md, Autentikasi API Key (X-API-Key), Deduplikasi Lowongan, Deployment Docker (satu container, satu worker uvicorn), BR-05 Aturan Duplikat (+10 more)

### Community 19 - "BaseScraper"
Cohesion: 0.17
Nodes (11): ARCHITECTURE document, DiscoveryPendingScraper, SiteChangedError, BaseScraper, DeallsScraper, Discovery phase, GlintsScraper, KalibrrScraper (+3 more)

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

### Community 34 - "Pintarnya — catatan discovery (2026-11-02)"
Cohesion: 0.14
Nodes (14): Deskripsi lengkap, Endpoint / selector final, Fixture, Kepatuhan & batas laju, Keputusan, Metode terpilih, Pagination / infinite scroll, Pemetaan field → RawListing/RawJob (+6 more)

### Community 35 - "Task 27 — Discovery LinkedIn + login/sesi"
Cohesion: 0.20
Nodes (9): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Langkah-langkah, Task 27 — Discovery LinkedIn + login/sesi, Test yang harus ditulis, Tujuan (+1 more)

### Community 37 - "keyword_repo.py"
Cohesion: 0.23
Nodes (14): ConflictError, KeywordRule, active_rules(), create_rule(), delete_rule(), list_rules(), reseed(), rule_dict() (+6 more)

### Community 38 - "kitalulus.py"
Cohesion: 0.06
Nodes (70): _pattern(), canonical_url(), detect_employment_type(), detect_work_mode(), _detect_currency(), parse_salary(), SalaryInfo, _to_number() (+62 more)

### Community 39 - "include"
Cohesion: 0.50
Nodes (4): include, role_category, strength, term

### Community 40 - "timeutil.py"
Cohesion: 0.20
Nodes (16): age_days(), now_utc(), parse_posted(), ParsedDate, to_wib(), wib_date(), wib_today(), check() (+8 more)

### Community 41 - "Pipeline (normalize → filter → dedup)"
Cohesion: 0.67
Nodes (3): age_filter, normalizer (RawJob → NormalizedJob), Pipeline (normalize → filter → dedup)

### Community 42 - "errors.py"
Cohesion: 0.18
Nodes (8): AppError, install_handlers(), _app_error(), _http(), _unhandled(), _validation(), _payload(), ServiceUnavailableError

### Community 67 - "glints.py"
Cohesion: 0.22
Nodes (22): draft_to_parts(), job_url(), location_label(), _next_data(), parse_detail_html(), parse_search_html(), salary_text(), slugify() (+14 more)

### Community 68 - "codemap.py"
Cohesion: 0.30
Nodes (5): _file_lines(), main(), _module_doc(), _signature(), _summary()

### Community 69 - "RawJob"
Cohesion: 0.19
Nodes (8): is_too_old(), DedupDecision, accept_location(), LocationResult, Normalizer, Pipeline, PipelineResult, test_age_filter_invalid_date()

### Community 70 - "json"
Cohesion: 0.06
Nodes (43): utc_iso(), ScrapeRun, ScrapeRunSource, add_link(), add_error(), cancel_run(), create_run(), details_fetched_since() (+35 more)

### Community 71 - "SiteChangedError"
Cohesion: 0.10
Nodes (45): _canonical(), canonical_url(), _clean_url(), DeallsScraper, _decode(), _detail_job(), _employment_type(), _find() (+37 more)

### Community 72 - "linkedin.py"
Cohesion: 0.08
Nodes (38): _auth_url(), _check_response(), _company_from_dom(), _description_html(), _expand_and_wait(), _inside_about_company(), _label(), LinkedInScraper (+30 more)

### Community 73 - "routers/scrape.py"
Cohesion: 0.24
Nodes (6): cancel_run(), get_run(), list_runs(), scrape_all(), scrape_platform(), ScrapeRequest

### Community 76 - "test_kalibrr.py"
Cohesion: 0.19
Nodes (25): _canonical(), _job_url(), _location(), _next_data(), parse_detail_payload(), parse_listing_payload(), _salary_text(), _work_mode() (+17 more)

### Community 77 - "asyncio"
Cohesion: 0.33
Nodes (5): _capture(), discover(), _is_json(), main(), _slug()

### Community 78 - "get_settings"
Cohesion: 0.17
Nodes (10): health(), get_settings(), UnauthorizedError, get_logger(), setup_logging(), require_api_key(), ensure_schema(), create_app() (+2 more)

### Community 79 - "test_pipeline.py"
Cohesion: 0.27
Nodes (14): URL pencarian, Parameter pencarian (terbukti), classifier(), location(), make_pipeline(), raw(), test_happy_path(), test_html_description_extracted() (+6 more)

### Community 80 - "SiteChangedError"
Cohesion: 0.19
Nodes (11): BaseScraper, RawJob, RawListing, SiteChangedError, KitaLulusScraper, DiscoveryPendingScraper, File yang perlu dibaca, Test yang harus ditulis (+3 more)

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
Cohesion: 0.18
Nodes (16): Test yang harus ditulis, fake_registry(), scrape(), seed_keywords(), test_archive_job(), test_description_included_and_detailed(), test_export_formats(), test_jobs_max_age_filter() (+8 more)

### Community 85 - "Task 29 — Discovery Pintarnya"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 29 — Discovery Pintarnya, Test yang harus ditulis (+2 more)

### Community 86 - "KalibrrScraper"
Cohesion: 0.20
Nodes (9): _is_challenge(), KalibrrScraper, _save_snapshot(), client(), test_iter_listings_guard_offset_against_count(), test_kalibrr_live_smoke(), test_search_challenge_raises_blocked(), fake_get() (+1 more)

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

### Community 92 - "job_service.py"
Cohesion: 0.28
Nodes (12): NotFoundError, ValidationAppError, api_dict(), _load_keywords(), _csv_cell(), _csv_stream(), get_job(), _json_stream() (+4 more)

### Community 93 - "jobs.py"
Cohesion: 0.22
Nodes (8): export_jobs(), _filters(), get_job(), list_jobs(), patch_job(), _csv(), iter_jsonl(), to_filters()

### Community 94 - "Pipeline Scraping Multi-Platform"
Cohesion: 0.25
Nodes (8): Eksekusi Scraping Asinkron (run_id), Dealls, Glints (glints.com/id), JobStreet (id.jobstreet.com), Pipeline Scraping Multi-Platform, Kalibrr, KitaLulus, Pintarnya

### Community 95 - "BlockedError"
Cohesion: 0.18
Nodes (12): AuthRequiredError, BlockedError, ParseError, ScraperError, TransientNetworkError, JobStreetScraper, Langkah-langkah, Langkah-langkah (+4 more)

### Community 96 - "linkedin_login.py"
Cohesion: 0.33
Nodes (3): Fase Pengembangan F0–F6 (PRD §12), Folder plan/ (task files untuk AI Agent), main()

### Community 97 - "PLAN — Job Scraper API"
Cohesion: 0.40
Nodes (4): Dependensi, Indeks task, PLAN — Job Scraper API, Urutan eksekusi

### Community 98 - "KitaLulus — catatan discovery (2026-11-02)"
Cohesion: 0.15
Nodes (12): Endpoint / selector final, Fixture, Kepatuhan & batas laju, KitaLulus — catatan discovery (2026-11-02), Metode terpilih, Pagination / "load more", Pemetaan field → RawListing/RawJob, Perbedaan dari SCRAPER_SPEC.md (+4 more)

### Community 99 - "browser.py"
Cohesion: 0.31
Nodes (3): jitter(), GlintsScraper, test_glints_live_smoke()

### Community 100 - "blocked"
Cohesion: 0.29
Nodes (7): blocked(), Risiko, Kriteria selesai (checklist), Tujuan, 8.1 Registry, 8.3 Definisi Selesai (per platform), 8. Registry, Pengujian, dan Definisi Selesai

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

### Community 105 - "Task 26 — Scraper KitaLulus + fixture/test"
Cohesion: 0.18
Nodes (10): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah, Task 26 — Scraper KitaLulus + fixture/test, Test yang harus ditulis (+2 more)

### Community 106 - "RawListing"
Cohesion: 0.47
Nodes (6): parse_listing_payload (pure parser), RawListing, Challenge detection, fetch_detail, iter_listings, XxxScraper (platform scraper template)

### Community 107 - "DATABASE — Job Scraper API"
Cohesion: 0.83
Nodes (4): ARCHITECTURE — Job Scraper API, PRD.md, SCRAPER_SPEC.md, DATABASE — Job Scraper API

### Community 108 - "env.py"
Cohesion: 0.47
Nodes (3): run_migrations_offline(), run_migrations_online(), _sync_url()

### Community 109 - "Task 28 — Scraper LinkedIn + fixture/test"
Cohesion: 0.29
Nodes (6): Cara verifikasi, Catatan / risiko, File yang akan dibuat/diubah, Kriteria selesai (checklist), Task 28 — Scraper LinkedIn + fixture/test, Yang TIDAK boleh dilakukan

### Community 110 - "PROGRESS"
Cohesion: 0.33
Nodes (5): Catatan penting (hanya yang tidak terlihat dari kode), Daftar task, Masalah terbuka / utang teknis, PROGRESS, Status

### Community 111 - "registry.py"
Cohesion: 0.12
Nodes (5): delete_keyword(), Settings, configure(), get_session(), delete_keyword()

### Community 112 - "detect_challenge"
Cohesion: 0.08
Nodes (25): detect_challenge(), _prune_debug_files(), save_debug_snapshot(), Catatan / risiko, File yang akan dibuat/diubah, File yang perlu dibaca, Kriteria selesai (checklist), Langkah-langkah (+17 more)

### Community 113 - "LinkedIn"
Cohesion: 0.40
Nodes (5): AuthRequiredError, BlockedError, LinkedIn, JobStreetScraper, LinkedInScraper

### Community 114 - "LinkedIn — catatan discovery & implementasi"
Cohesion: 0.20
Nodes (9): Fixture, Kartu daftar, LinkedIn — catatan discovery & implementasi, Panel detail, Perintah discovery (reproduksi), Ringkasan metode, Risiko, Selector (terbukti dari fixture) (+1 more)

### Community 115 - "_auth_state"
Cohesion: 0.50
Nodes (4): _auth_state(), Autentikasi, File yang perlu dibaca, File yang perlu dibaca

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
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 612 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `SCRAPER_SPEC — Mekanisme Scraping per Platform` connect `SCRAPER_SPEC — Mekanisme Scraping per Platform` to `kitalulus.py`, `platforms`, `timeutil.py`, `RawListing`, `DATABASE — Job Scraper API`, `asyncio`, `LinkedIn`, `Pipeline Scraping Multi-Platform`?**
  _High betweenness centrality (0.140) - this node is a cross-community bridge._
- **Are the 28 inferred relationships involving `SiteChangedError` (e.g. with `Orchestrator` and `DeallsScraper`) actually correct?**
  _`SiteChangedError` has 28 INFERRED edges - model-reasoned connections that need verification._
- **What connects `job-scraper`, `BR-04 Aturan Usia Lowongan`, `BR-02/BR-03 Aturan Lokasi & Remote` to the rest of the system?**
  _59 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CODEMAP` be split into smaller, more focused modules?**
  _Cohesion score 0.02857142857142857 - nodes in this community are weakly interconnected._
- **Why does `RawJob` connect `SiteChangedError` to `glints.py`, `browser.py`, `RawJob`, `json`, `kitalulus.py`, `SiteChangedError`, `re`, `linkedin.py`, `Task 26 — Scraper KitaLulus + fixture/test`, `test_kalibrr.py`, `Kalibrr — catatan discovery (2026-11-02)`, `test_pintarnya.py`, `Implementasi scraper Kalibrr sesuai plan task 22`, `test_pipeline.py`, `KalibrrScraper`, `Task 24 — Scraper Dealls + fixture/test`, `BlockedError`?**
  _High betweenness centrality (0.109) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `BR-01 Aturan Kata Kunci` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._
- **What is the exact relationship between `docs/platform_notes/<platform>.md` and `DATABASE.md`?**
  _Edge tagged AMBIGUOUS (relation: references) - confidence is low._