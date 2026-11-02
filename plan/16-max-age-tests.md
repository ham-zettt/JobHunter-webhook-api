# Task 16 — Uji filter `max_age_days`

- **Fase:** F2 **Prasyarat:** 09, 10, 12 **Estimasi:** S
- **Referensi:** PRD BR-04, FR-06, FR-22; ARCHITECTURE §4.4, §7.2
- **Status:** `[~]` — validasi range ada; filter query & henti-dini belum diuji

## Tujuan
Membuktikan `max_age_days` bekerja di dua tempat: berhenti paginasi saat scraping
(FR-06) dan filter `GET /jobs` (FR-22).

## File yang perlu dibaca
- `app/runner/orchestrator.py` (blok `is_too_old`, `old_streak >= 5`)
- `app/pipeline/age_filter.py`
- `app/db/repositories/job_repo.py` (`JobFilters.max_age_days`, `build_query`)
- `tests/api/test_scrape_jobs.py`, `tests/fixtures/fake_scrapers.py`
- PRD BR-04 · ARCHITECTURE §7.2

## File yang akan dibuat/diubah
- `tests/api/test_scrape_jobs.py`
- `tests/fixtures/fake_scrapers.py` (hanya bila butuh listing tua/baru)

## Langkah-langkah
1. Tambah test query: seed dua lowongan dengan `effective_date` berbeda
   (satu di dalam batas, satu lebih tua), panggil
   `GET /api/v1/jobs?max_age_days=3`, pastikan hanya yang baru kembali.
2. Pastikan `total` dan `has_more` konsisten setelah filter.
3. Tambah test scrape: fake scraper mengeluarkan ≥5 `RawListing` berurutan dengan
   `posted_raw` lebih tua dari `max_age_days`, lalu satu listing baru.
4. Jalankan scrape; pastikan listing tua menambah `filtered_age` dan listing baru
   setelah streak tidak diproses (henti-dini).
5. Bila `fake_scrapers.py` perlu data, tambah helper tanpa mengubah perilaku default
   test lain.

## Test yang harus ditulis
- `test_jobs_max_age_filter`
- `test_scrape_stops_after_five_old_listings`

## Kriteria selesai (checklist)
- [ ] `GET /jobs?max_age_days=N` menyaring berdasarkan `effective_date` (fallback WIB).
- [ ] Nilai `max_age_days` di luar `1..MAX_AGE_DAYS_LIMIT` tetap `422`.
- [ ] Scraper berhenti setelah 5 listing tua berurutan.
- [ ] `filtered_age` bertambah sesuai jumlah listing tua.

## Cara verifikasi
```bash
uv run pytest tests/api/test_scrape_jobs.py -q -k "max_age or old_listings"
uv run pytest -q
```
Harapan: dua test baru lulus; tidak ada test lama berubah.

## Yang TIDAK boleh dilakukan
- Mengubah default global `DEFAULT_MAX_AGE_DAYS=14` atau batas `90`.
- Menambah filter usia ke query default tanpa parameter.
- Menguji dengan jaringan nyata.

## Catatan / risiko
- `tanggal_masuk` memakai WIB; jangan membandingkan dengan UTC mentah.
- Henti-dini hanya untuk daftar terurut terbaru; toleransi 5 listing.
