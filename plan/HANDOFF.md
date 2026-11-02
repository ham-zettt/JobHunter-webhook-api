# HANDOFF — Job Scraper API

## 1. Selesai (F0–F3 parsial)
- F0 fondasi: `app/core/`, `app/db/` (6 tabel + FTS5), `app/main.py`, `migrations/0001`, `config/*.yaml`, Docker.
- F1 pipeline: `app/pipeline/` (normalizer, lokasi BR-02/03, classifier BR-01, age, dedup BR-05/06), `app/core/timeutil.py`, `app/scrapers/common/{text,salary}.py`.
- F2 API+runner: `app/runner/{run_manager,orchestrator}.py`, `app/api/routers/`, `app/services/`, `app/db/repositories/`. Tes API + idempotensi hijau.
- F3 JobStreet: `app/scrapers/platforms/jobstreet.py`, `app/scrapers/browser.py`, fixtures + `tests/scrapers/test_jobstreet.py`.
- F3 Glints: `app/scrapers/platforms/glints.py`, fixtures + `tests/scrapers/test_glints.py`.
- Docs: `README.md`, `docs/DECISIONS.md`, `docs/platform_notes/{jobstreet,glints}.md`.
- Status: 103 test hijau (live dikecualikan default), `ruff` bersih, live smoke JobStreet+Glints lulus, scrape nyata via API lulus.

## 2. Penyimpangan dari spesifikasi
- D-002: skema dibuat `app/db/schema.py` (idempoten); Alembic 0001 memanggilnya, bukan autogenerate.
- D-003: normalizer lokasi membaca `config/locations_java.yaml` langsung; tabel `location_aliases` hanya seed/referensi.
- D-004: `updated` hanya dihitung saat detail benar-benar diambil ulang; known-job path = `seen`.
- D-006: PATCH job menerima `active|archived|expired` (bukan hanya archived).
- D-009: env `EXPORT_MAX_ROWS` ditambahkan (tidak ada di `.env.example` asli).
- D-012: Glints hanya halaman SSR pertama per term (30); paginasi butuh JS/Turnstile; cakupan via banyak term.
- JobStreet detail memakai embedded `SEEK_REDUX_DATA`, bukan endpoint detail resmi (endpoint JSON detail 404).

## 3. Keputusan/jebakan/bug diketahui (belum diperbaiki)
- `SCHEDULE_CRON` (FR-11, OPSIONAL) belum diimplementasikan; n8n jadi penjadwal.
- Verifikasi `docker compose up`: `config` valid, build image Playwright belum tuntas (pull 860MB timeout).
- `BrowserPool` memakai `channel="chromium"` agar lolos Cloudflare JobStreet; chromium penuh wajib ada di image.
- Glints: lokasi sering hanya distrik+provinsi → `kota` bisa NULL walau provinsi valid/`lokasi_terverifikasi=1`.
- Glints detail tidak punya fallback DOM; perubahan `__NEXT_DATA__` → `SiteChangedError`/`degraded`.
- `expires_at` Glints dari `expiryDate/endDate`; JobStreet dari `job.expiresAt`.
- Callback webhook belum diuji end-to-end nyata (SSRF + retry ada, tes hanya validasi URL).
- `scripts/backup_db.sh`, `scripts/linkedin_login.py` belum dieksekusi nyata.

## 4. Setengah jalan
- F3 sisa: Kalibrr (belum discovery), lalu Dealls, KitaLulus, LinkedIn, Pintarnya (stub `DiscoveryPendingScraper`).
- F4/F5/F6 belum mulai: login LinkedIn, canary tuning, webhook e2e, README alur n8n final.
