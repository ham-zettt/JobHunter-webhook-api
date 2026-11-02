# PROGRESS

## Status

Fase aktif: F3 · Task terakhir selesai: 21 · Berikutnya: 22 (tinggal smoke live)
Commit terakhir: 6f3d7a4

## Daftar task

- [x] 01 Fondasi proyek & konfigurasi — bukti: `app/core/config.py`, `app/main.py`, `pyproject.toml`
- [x] 02 Skema SQLite, PRAGMA, FTS5, Alembic — bukti: `app/db/schema.py`, `app/db/session.py`, `migrations/versions/0001_initial.py`
- [x] 03 Auth, format error, `/health` — bukti: `app/core/security.py`, `app/core/errors.py`, `tests/api/test_health.py`
- [x] 04 Docker & entrypoint: build image/`docker compose up` sudah terverifikasi
- [x] 05 Normalizer + parser tanggal/gaji + sistem/tipe kerja — bukti: `app/pipeline/normalizer.py`, `app/core/timeutil.py`, `app/scrapers/common/{text,salary}.py`, `tests/unit/test_{timeutil,salary,text}.py`
- [x] 06 Normalisasi lokasi + BR-02/BR-03 — bukti: `app/pipeline/location.py`, `tests/unit/test_location.py`, `tests/unit/test_pipeline.py`
- [x] 07 Classifier BR-01 + skor — bukti: `app/pipeline/classifier.py`, `tests/unit/test_classifier.py`
- [x] 08 Deduper L1–L3 + matriks 14 kasus — bukti: `app/pipeline/deduper.py`, `tests/unit/test_deduper.py` (16 test, §8.4 #1–#14); resolusi akar `duplicate_of_id` ditambahkan
- [x] 09 Pipeline orchestration + statistik filter — bukti: `app/pipeline/pipeline.py`, `tests/unit/test_pipeline.py`, `tests/api/test_scrape_jobs.py`
- [x] 10 RunManager + Orchestrator — bukti: `app/runner/{run_manager,orchestrator}.py`, `tests/api/test_scrape_jobs.py`
- [x] 11 Endpoint scrape/status/platforms/keywords — bukti: `app/api/routers/`, `app/services/`, `tests/api/test_{scrape_jobs,platforms_keywords}.py`
- [x] 12 Jobs list/detail/export + filter + FTS5 — bukti: `app/services/job_service.py`, `app/db/repositories/job_repo.py`, `tests/api/test_scrape_jobs.py`
- [x] 13 Seed keyword & location_aliases — bukti: `app/seed/loader.py`, `tests/unit/test_seed.py`, `tests/api/test_platforms_keywords.py`
- [x] 14 Uji idempotensi NFR-05 — bukti: `tests/api/test_scrape_jobs.py::test_scrape_is_idempotent`
- [x] 15 Uji remote Indonesia BR-03 — bukti: `tests/unit/test_pipeline.py::test_remote_indonesia_accepted`, `::test_remote_abroad_rejected`, `tests/unit/test_location.py`
- [~] 16 Uji filter `max_age_days` — kurang: test API `GET /jobs?max_age_days=` dan uji henti-dini 5 listing tua
- [x] 17 Discovery JobStreet — bukti: `docs/platform_notes/jobstreet.md`
- [x] 18 Scraper JobStreet + fixture/test — bukti: `app/scrapers/platforms/jobstreet.py`, `tests/scrapers/test_jobstreet.py`
- [x] 19 Discovery Glints — bukti: `docs/platform_notes/glints.md`
- [x] 20 Scraper Glints + fixture/test — bukti: `app/scrapers/platforms/glints.py`, `tests/scrapers/test_glints.py`
- [x] 21 Discovery Kalibrr — bukti: `docs/platform_notes/kalibrr.md`, `tests/fixtures/kalibrr/` (3 daftar + 5 detail)
- [~] 22 Scraper Kalibrr + fixture/test — bukti: `app/scrapers/platforms/kalibrr.py`, `tests/scrapers/test_kalibrr.py` (16 test); kurang: smoke `live` belum dijalankan (dilarang pada sesi ini)
- [ ] 23 Discovery Dealls
- [ ] 24 Scraper Dealls + fixture/test
- [ ] 25 Discovery KitaLulus
- [ ] 26 Scraper KitaLulus + fixture/test
- [~] 27 Discovery LinkedIn + login/sesi — kurang: catatan discovery, eksekusi `scripts/linkedin_login.py`, verifikasi state
- [ ] 28 Scraper LinkedIn + fixture/test
- [ ] 29 Discovery Pintarnya
- [ ] 30 Scraper/stub Pintarnya + test
- [~] 31 Hardening retry/canary/snapshot/blokir — kurang: retry tenacity, baseline canary historis, test deteksi blokir
- [~] 32 Webhook callback end-to-end — kurang: uji kirim nyata + retry/`callback_status`, hanya validasi URL yang diuji
- [~] 33 Backup, retensi, prune — kurang: `scripts/backup_db.sh` belum dieksekusi, `scripts/prune.py` belum ada
- [ ] 34 Tuning dedup + reclassify (OPSIONAL)
- [~] 35 README + contoh workflow n8n — kurang: workflow JSON impor, catatan risiko LinkedIn, README final
- [ ] 36 Uji end-to-end + review kriteria rilis PRD §13

## Catatan penting (hanya yang tidak terlihat dari kode)

- 125 test offline hijau (`uv run pytest -q`), `ruff` bersih. Test `live` dikecualikan default.
- JobStreet memakai embedded `SEEK_REDUX_DATA` untuk detail; endpoint JSON detail resmi 404.
- Glints hanya halaman SSR pertama per term (30); paginasi butuh JS/Turnstile. Cakupan lewat banyak term.
- Kalibrr: daftar lewat `/kjs/job_board/search` (offset); detail `__NEXT_DATA__`. `sort=Freshness` hanya SSR halaman 1; offset > `count` jatuh ke feed umum.
- `updated` hanya bertambah saat detail benar-benar diambil ulang; jalur dikenal = `seen`.
- Callback SSRF + retry 3× sudah ada; e2e nyata belum.

## Masalah terbuka / utang teknis

- `sumber_lain` mengembalikan jumlah (int), bukan `[{sumber,url}]` seperti DATABASE §3.2.
- `job_run_links.created_at` ada di kode, tidak ada di DATABASE §5.
- `deskripsi_terpotong` adalah field API tambahan di luar PRD §6.
- `SCHEDULE_CRON` diterima config tetapi tidak dijalankan (n8n penjadwal); APScheduler terpasang.
- `scripts/backup_db.sh` dan `scripts/linkedin_login.py` belum dijalankan nyata.
- Build image Playwright (860 MB) belum tuntas diverifikasi.
