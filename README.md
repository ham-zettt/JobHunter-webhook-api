# Job Scraper API

Layanan backend Python + FastAPI untuk mengumpulkan lowongan Software Engineering & AI
dari 7 platform, menormalkan, menyaring, mendeduplikasi, lalu menyajikannya lewat REST API
untuk dikonsumsi n8n. Tanpa frontend.

Status implementasi: **F0–F2 selesai** (fondasi, pipeline, run manager, API),
**F3 JobStreet & Glints selesai** (discovery + parser + fixture). Lima platform lain
masih `DiscoveryPendingScraper` sampai discovery masing-masing dilakukan sesuai
`SCRAPER_SPEC.md §3`. Catatan: `docs/platform_notes/jobstreet.md`,
`docs/platform_notes/glints.md`.

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
| GET | `/api/v1/scrape/runs/{run_id}` | Status + statistik per platform |
| POST | `/api/v1/scrape/runs/{run_id}/cancel` | Batalkan run |
| GET | `/api/v1/jobs` | Daftar lowongan (filter, pencarian, sort, paginasi) |
| GET | `/api/v1/jobs/{id}` | Detail |
| PATCH | `/api/v1/jobs/{id}` | Ubah status (`active`/`archived`/`expired`) |
| GET | `/api/v1/jobs/export?format=csv\|jsonl\|json` | Ekspor |
| GET | `/api/v1/platforms` | Status platform + run terakhir |
| GET/POST/PATCH/DELETE | `/api/v1/keywords` | CRUD aturan kata kunci |
| GET | `/health` | DB + browser |

Contoh:

```bash
curl -X POST http://localhost:8000/api/v1/scrape/all \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"max_age_days": 7, "callback_url": "http://n8n:5678/webhook/job-done"}'
```

Parameter body scrape (semua opsional): `keywords`, `max_age_days` (1..90),
`max_jobs_per_platform`, `fetch_details` (default `true`), `callback_url`.

Filter `/jobs`: `q`, `platform`, `sistem_kerja`, `tipe_kerja`, `provinsi`, `kota`,
`kategori_peran`, `max_age_days`, `has_gaji`, `min_gaji`, `first_seen_after`, `run_id`,
`only_new`, `include_duplicates`, `include_description`, `status`, `sort`, `page`, `limit`
(maks 200).

## Alur n8n

```text
Schedule Trigger
  → POST /api/v1/scrape/all {"max_age_days": 7}      (simpan run_id)
  → Wait 60s
  → GET /api/v1/scrape/runs/{run_id}
  → IF status ∈ {completed, partial} ? lanjut : kembali ke Wait
  → GET /api/v1/jobs?run_id={run_id}&only_new=true&include_description=true
  → Split In Batches → Telegram / Email / Notion / Sheets
```

Alternatif tanpa polling: kirim `callback_url` (POST ringkasan run, retry 3× dengan jeda
2/5/10 detik). Untuk n8n di jaringan Docker, tambahkan host-nya ke
`CALLBACK_ALLOWED_HOSTS` (mis. `n8n`), lalu panggil `http://job-scraper:8000`.

## Login LinkedIn (saat scraper F4 aktif)

```bash
uv run python scripts/linkedin_login.py
# login manual (termasuk 2FA), lalu tekan Enter
# state tersimpan di data/secrets/linkedin_state.json (permission 600)
```

Gunakan akun khusus/cadangan, bukan akun utama. Jangan commit file state, dan jangan
menjalankan banyak instance bersamaan. Skrip memverifikasi sesi mencapai `/jobs/`
sebelum menimpa state lama. Jika sesi kedaluwarsa, `GET /api/v1/platforms` menampilkan
`auth_state` `missing`/`expired` dan sub-run LinkedIn berstatus `auth_required`.

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
uv run pytest -m live              # manual, menyentuh situs nyata (JobStreet & Glints)
```

Parser scraper diuji dengan fixture HTML/JSON di `tests/fixtures/<platform>/` (NFR-08).

## Backup

```bash
./scripts/backup_db.sh             # simpan 7 salinan terakhir di data/backups
```

## Catatan operasional

- Satu run aktif pada satu waktu; permintaan berikutnya masuk antrean `queued`.
- Run `running` yang terputus saat restart ditandai `failed`; run `queued` dipulihkan.
- `data/debug/` menyimpan snapshot kegagalan parse (dibatasi jumlah file, tidak diekspos API).
- Detail arsitektur: `ARCHITECTURE.md`; skema DB: `DATABASE.md`; aturan scraper:
  `SCRAPER_SPEC.md`; keputusan implementasi: `docs/DECISIONS.md`.
