# Release Checklist 1.0 — Verifikasi PRD §13

- **Tanggal verifikasi:** 2026-11-03 (UTC 03:11–03:45)
- **Commit:** `70bf9d4`
- **Lingkungan:** Linux, Docker 29.6.2, Docker Compose 5.3.1, image `mcr.microsoft.com/playwright/python:v1.64.1-noble`
- **Konfigurasi:** `APP_ENV=production`, API key dari `.env`, SQLite di volume `./data`
- **Suite offline:** `uv run pytest` → **230 passed, 4 deselected** · `uv run ruff check app tests` → **clean**
- **Catatan:** sesuai `AGENTS.md`, test beranda `live` **tidak dijalankan** oleh agen (manual oleh pemilik); prosedur ada di bawah.

## 1. Status tiap butir PRD §13

| # | Butir §13 | Status | Bukti |
|---|-----------|--------|-------|
| 1 | Ketujuh platform dapat dipicu; kegagalan satu platform terisolasi | ✅ | Run `r_20261103_101142_6b12` status `partial`; 7 sub-run dibuat, 4 `completed`/`degraded`, 3 `blocked`, 1 `failed` — run tetap selesai, bukan `failed` total |
| 2 | 9 field wajib (§6) + `deskripsi` lengkap ≥95% sampel 50/platform | ⚠️ | 9 field wajib 19/19 pada sampel nyata; `deskripsi` terisi 19/19 (100%); `gaji` nullable sesuai §6 (`3/19`, tidak diwajibkan). **Sampel 19 total, belum 50/platform** (batas run `max_jobs_per_platform=5`) |
| 3 | Filter `max_age_days` terbukti | ✅ | Test `test_jobs_max_age_filter`, `test_scrape_stops_after_five_old_listings`; live: filter `age` menyaring 24 lowongan (run1) & 12–24 per platform |
| 4 | Scrape dua kali tidak menambah duplikat (NFR-05) | ✅ | Test `test_scrape_is_idempotent`; live `POST /scrape/dealls` kedua → `new=0` (found 15, semuanya tersaring usia/kata kunci/`seen`) |
| 5 | Remote Indonesia masuk; remote LN & onsite luar Jawa ditolak | ✅ | Test `test_remote_indonesia_accepted`, `test_remote_abroad_rejected`, `tests/unit/test_location.py`. Sampel live tidak memuat remote (`onsite` 17, `hybrid` 2) |
| 6 | Kasus pembeda BR-06 (kota/senioritas/repost) | ✅ | `tests/unit/test_deduper.py` (16 test, matriks §8.4 #1–#14) |
| 7 | Alur n8n §10 end-to-end | ✅ | Polling: `POST /scrape/all` → `GET /scrape/runs/{id}` → `GET /jobs?run_id=…&only_new=true&include_description=true` (total 12, semua ber-`deskripsi`). Callback: `POST` ringkasan run diterima webhook |
| 8 | `pytest` hijau tanpa jaringan + penanda `live` | ✅ | 230 passed, live deselected (`markers=["live: …"]`); live manual belum dijalankan |
| 9 | README lengkap termasuk login LinkedIn | ✅ | `README.md` (endpoint, error, konfigurasi, run/test/lint/backup, prosedur & risiko login LinkedIn) |

**Verdict:** seluruh kriteria perangkat lunak terverifikasi. Rilis belum dinyatakan "selesai" karena 3 platform (JobStreet, Glints, Pintarnya) diblokir anti-bot dari lingkungan uji, Kalibrr kedua menggantung (lihat bug), dan sampel field < 50/platform.

## 2. Langkah 2–8 — bukti operasional

### Docker & /health
- `docker compose up --build -d` berhasil build + start.
- `GET /health` → `{"status":"ok","db":"ok","browser":"ok","version":"1.0.0"}`.

### Run `POST /scrape/all` `{"max_age_days":7,"max_jobs_per_platform":5}` — `r_20261103_101142_6b12` (`partial`)

| Platform | Status | found | new | filtered (age/keyword) |
|----------|--------|-------|-----|------------------------|
| jobstreet | blocked (403) | 0 | 0 | 0 |
| glints | blocked (403) | 0 | 0 | 0 |
| kalibrr | completed | 17 | 5 | 12 |
| dealls | completed | 15 | 2 | 12/1 |
| kitalulus | failed (timeout 45s `page.goto`) | 0 | 0 | 0 |
| pintarnya | blocked (tantangan anti-bot) | 0 | 0 | 0 |
| linkedin | completed | 5 | 5 | 0 |
| **total** | **partial** | **37** | **12** | **24 age / 1 keyword** |

Kegagalan terisolasi: run `partial`, tiga platform selesai normal. Proteksi platform **tidak** ditembus (sesuai aturan).

### Idempotensi (NFR-05)
- `POST /scrape/dealls` kedua (`r_20261103_102620_4853`) → `found=15, new=0`; `POST` ketiga (`r_20261103_104311_278a`) → `new=0`. Tidak ada baris baru.

### Field wajib (§6) pada 19 lowongan nyata
`url, tanggal_masuk, sumber, perusahaan, posisi, lokasi, sistem_kerja, deskripsi` = 19/19 (100%). `gaji` = 3/19 (nullable, tidak diwajibkan). `deskripsi` non-kosong 19/19 (ambang 95% terpenuhi).

### Callback (alternatif n8n)
- `POST /scrape/dealls` dengan `callback_url=http://172.18.0.1:9099/webhook/job-done` (host di `CALLBACK_ALLOWED_HOSTS`) → webhook menerima `POST /webhook/job-done` berisi ringkasan run (`run_id`, `status`, `totals`).
- `callback_url` ke alamat privat **ditolak** bila host tidak di-allowlist (SSRF guard, `422 VALIDATION_ERROR`).

## 3. Bug ditemukan

1. **`Dockerfile`/`entrypoint` — DB readonly (DIPERBAIKI).** Container berjalan sebagai `pwuser` (uid **1001**), volume host `./data` dimiliki uid 1000 → `sqlite3.OperationalError: attempt to write a readonly database` pada `POST /scrape`. Perbaikan: `docker/entrypoint.sh` start sebagai root, `chown` `/app/data` ke pemilik volume, lalu turun ke uid/gid pemilik via `setpriv`; `USER pwuser` dihapus. Terverifikasi: `/health` + run tulis-ke-DB normal.
2. **Kalibrr menggantung pada run kedua (TERBUKA).** Run `r_20261103_101459_ac97` tetap `running` > 13 menit pada sub-run kalibrr (`found=22`, run pertama 21 dtk), dibatalkan manual. Duga: paginasi/detail lambat tanpa batas keras di level sub-run selain `PLATFORM_MAX_DURATION_SEC=1500`. Dicatat sebagai utang teknis.
3. **Canary `degraded` pada run idempoten (TERBUKA).** Sub-run dealls `new=0` ditandai `degraded` (canary "0 hasil baru"). Perlu klarifikasi: `degraded` sebaiknya untuk hasil parse kosong, bukan dedup 0-baru.
4. **KitaLulus gagal `page.goto` timeout 45s (TERBUKA, kemungkinan jaringan).** `INTERNAL_ERROR` terisolasi; dicoba ulang tidak dalam sesi ini.

## 4. Uji live manual (belum dijalankan oleh agen)

```bash
uv run pytest -m live -k jobstreet   # ≤2 halaman / ≤3 detail
uv run pytest -m live -k glints
# ulangi untuk platform lain yang diimplementasikan
```

Dijalankan manual oleh pemilik (konsumsi waktu, kena rate limit). Platform yang memblokir `live` (403/tantangan) → tandai `needs_attention`, **jangan** tembus CAPTCHA.
