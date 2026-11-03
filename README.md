# Job Scraper API

Layanan backend Python + FastAPI untuk mengumpulkan lowongan Software Engineering & AI
dari 7 platform, menormalkan, menyaring, mendeduplikasi, lalu menyajikannya lewat REST API
untuk dikonsumsi n8n. Tanpa frontend.

Status implementasi: **F0–F6 selesai** — fondasi, pipeline, run manager, API, ketujuh
scraper platform (P1 JobStreet/Glints/Kalibrr/Dealls, P2 KitaLulus/LinkedIn, P3
Pintarnya) dengan parser + fixture, hardening (retry/canary/snapshot), webhook callback,
serta backup/prune. Smoke `live` dijalankan manual (`uv run pytest -m live`, dikecualikan
dari default). Catatan discovery & implementasi tiap platform: `docs/platform_notes/`.

## Menjalankan (lokal)

```bash
uv sync --python 3.12
cp .env.example .env          # isi API_KEY
uv run alembic upgrade head
uv run uvicorn app.main:app --port 8000 --workers 1
```

Buka `http://localhost:8000/docs` untuk OpenAPI. `/health` tidak butuh autentikasi.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

Data persisten di `./data` (SQLite `jobs.db`, `debug/`, `secrets/`). Satu container,
satu worker uvicorn (wajib: SQLite + antrean in-process).

## Autentikasi

Semua endpoint selain `/health`, `/docs`, `/openapi.json` memerlukan header:

```bash
curl -H "X-API-Key: $API_KEY" http://localhost:8000/api/v1/jobs
```

`APP_ENV=production` + `API_KEY` kosong → aplikasi menolak start.

## Endpoint utama

| Method | Path | Keterangan |
|--------|------|------------|
| POST | `/api/v1/scrape/all` | Mulai scrape semua platform (`202` + `run_id`) |
| POST | `/api/v1/scrape/{platform}` | Mulai scrape satu platform |
| GET | `/api/v1/scrape/runs` | Daftar run (filter `status`, paginasi) |
| GET | `/api/v1/scrape/runs/{run_id}` | Status + statistik per platform |
| POST | `/api/v1/scrape/runs/{run_id}/cancel` | Batalkan run |
| GET | `/api/v1/jobs` | Daftar lowongan (filter, pencarian, sort, paginasi) |
| GET | `/api/v1/jobs/{id}` | Detail |
| PATCH | `/api/v1/jobs/{id}` | Ubah status (`active`/`archived`/`expired`) |
| GET | `/api/v1/jobs/export?format=csv\|jsonl\|json` | Ekspor |
| GET | `/api/v1/platforms` | Status platform + run terakhir |
| GET/POST/PATCH/DELETE | `/api/v1/keywords` | CRUD aturan kata kunci |
| POST | `/api/v1/keywords/reseed` | Muat ulang aturan dari `config/*.yaml` |
| GET | `/health` | DB + browser |

Contoh:

```bash
curl -X POST http://localhost:8000/api/v1/scrape/all \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"max_age_days": 7, "callback_url": "http://n8n:5678/webhook/job-done"}'
```

Parameter body scrape (semua opsional): `keywords`, `max_age_days` (1..90),
`max_jobs_per_platform`, `fetch_details` (default `true`), `callback_url`.

Kode error seragam (`{"error": {"code", "message", "details?"}}`, ARCHITECTURE §7.6):

| HTTP | `code` |
|------|--------|
| 401 | `UNAUTHORIZED` |
| 404 | `NOT_FOUND`, `PLATFORM_NOT_FOUND`, `RUN_NOT_FOUND` |
| 409 | `PLATFORM_DISABLED`, `RUN_NOT_CANCELLABLE` |
| 422 | `VALIDATION_ERROR` |
| 500 | `INTERNAL_ERROR` |
| 503 | `SERVICE_UNAVAILABLE` |

Filter `/jobs`: `q`, `platform`, `sistem_kerja`, `tipe_kerja`, `provinsi`, `kota`,
`kategori_peran`, `max_age_days`, `has_gaji`, `min_gaji`, `first_seen_after`, `run_id`,
`only_new`, `include_duplicates`, `include_description`, `status`, `sort`, `page`, `limit`
(maks 200).

## Alur n8n

Workflow siap impor: `docs/n8n_workflow.json` (n8n → **Import from File**). Set dua
variabel lingkungan di n8n: `JOB_SCRAPER_URL` (mis. `http://job-scraper:8000`) dan
`JOB_SCRAPER_API_KEY`. Pemetaan node:

```text
Schedule Trigger
  → HTTP POST  {{JOB_SCRAPER_URL}}/api/v1/scrape/all   body {"max_age_days": 7} → simpan run_id
  → Wait 60s
  → HTTP GET   /api/v1/scrape/runs/{run_id}            header X-API-Key
  → IF status ∈ {completed, partial}  true → lanjut · false → kembali ke Wait
  → HTTP GET   /api/v1/jobs?run_id={run_id}&only_new=true&include_description=true&limit=200
  → Split Out `items` → Split In Batches → Telegram / Email / Notion / Sheets
```

Alternatif tanpa polling: kirim `callback_url` (POST ringkasan run, retry 3× dengan jeda
2/5/10 detik). Untuk n8n di jaringan Docker, tambahkan host-nya ke
`CALLBACK_ALLOWED_HOSTS` (mis. `n8n`), lalu panggil `http://job-scraper:8000`.

## Login & risiko LinkedIn

```bash
uv run python scripts/linkedin_login.py
# browser headed terbuka; login manual (termasuk 2FA), lalu tekan Enter
# state tersimpan di data/secrets/linkedin_state.json (permission 600)
```

Jalankan skrip di mesin lokal (bukan container headless, ARCHITECTURE §9.3), lalu salin
hasilnya ke volume `./data/secrets` container. Skrip memverifikasi sesi mencapai
`/jobs/` sebelum menimpa state lama.

**Risiko — patuhi semua (PRD §11, D2):**
- Gunakan akun LinkedIn **khusus/cadangan**, bukan akun utama.
- Hormati batas volume: `LINKEDIN_MAX_JOBS_PER_RUN=60`, `LINKEDIN_MAX_JOBS_PER_DAY=150`;
  jangan menjalankan banyak instance/run bersamaan.
- **Jangan commit** file state (`data/` sudah di `.gitignore`) atau kredensial lain.
- Sesi kedaluwarsa/checkpoint → **jangan menembusnya**. `GET /api/v1/platforms`
  menampilkan `auth_state` `missing`/`expired` dan sub-run LinkedIn berstatus
  `auth_required`; login ulang manual kemudian.

## Konfigurasi

Lihat `.env.example`. Nilai penting: `RELEVANCE_THRESHOLD` (default 50),
`DEFAULT_MAX_AGE_DAYS` (14), `DETAIL_REFRESH_DAYS` (3), batas LinkedIn
(`LINKEDIN_MAX_JOBS_PER_RUN=60`, `_PER_DAY=150`), `CALLBACK_ALLOWED_HOSTS`,
`EXPORT_MAX_ROWS` (50000). Aturan kata kunci & alias lokasi di `config/*.yaml`;
rate limit per platform di `config/platforms.yaml`.

## Testing

```bash
uv run pytest                      # offline, tanpa jaringan
uv run pytest --cov=app            # coverage
uv run ruff check app tests
uv run python scripts/codemap.py   # regenerasi docs/CODEMAP.md
uv run pytest -m live              # manual, menyentuh situs nyata (semua platform)
```

Parser scraper diuji dengan fixture HTML/JSON di `tests/fixtures/<platform>/` (NFR-08).

## Backup

```bash
./scripts/backup_db.sh             # simpan 7 salinan terakhir di data/backups
uv run python scripts/prune.py --db data/jobs.db --dry-run   # pratinjau retensi
uv run python scripts/prune.py --db data/jobs.db             # hapus link >90 hari & job expired >180 hari
```

## Catatan operasional

- Satu run aktif pada satu waktu; permintaan berikutnya masuk antrean `queued`.
- Run `running` yang terputus saat restart ditandai `failed`; run `queued` dipulihkan.
- `data/debug/` menyimpan snapshot kegagalan parse (dibatasi jumlah file, tidak diekspos API).
- Detail arsitektur: `ARCHITECTURE.md`; skema DB: `DATABASE.md`; aturan scraper:
  `SCRAPER_SPEC.md`; keputusan implementasi: `docs/DECISIONS.md`.
