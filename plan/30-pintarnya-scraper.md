# Task 30 — Scraper/stub Pintarnya + test

- **Fase:** F5 **Prasyarat:** 29 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §6, §7.7, §8.1–§8.3
- **Status:** `[ ]`

## Tujuan
Mengimplementasikan Pintarnya sesuai hasil discovery: scraper normal bila publik,
atau stub `skipped` dengan kode alasan bila tidak dapat diakses.

## File yang perlu dibaca
- `docs/platform_notes/pintarnya.md`
- `app/scrapers/base.py`, `app/scrapers/browser.py`, `app/scrapers/exceptions.py`
- `app/scrapers/platforms/_placeholder.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py`
- `app/runner/orchestrator.py` (penanganan `skipped`)
- `tests/scrapers/test_{jobstreet,glints}.py`

## File yang akan dibuat/diubah
- `app/scrapers/platforms/pintarnya.py`
- `tests/scrapers/test_pintarnya.py`
- `tests/fixtures/pintarnya/` (bila publik)

## Langkah-langkah
1. Bila **tidak publik**: ganti subclass placeholder dengan scraper yang
   `iter_listings` langsung menandai sub-run `skipped` dan
   `errors=[{code:"NOT_PUBLICLY_ACCESSIBLE", message:...}]`; jangan melempar
   exception yang menjatuhkan run. Sesuaikan orchestrator hanya bila perlu.
2. Bila **publik**: tulis parser murni + navigasi mengikuti §6, dengan
   selector/endpoint dari notes.
3. Petakan `external_id`, URL kanonik, tanggal, mode/tipe kerja, gaji, lokasi.
4. Terapkan §5.6 untuk deskripsi lengkap.
5. Tangani `BlockedError`/`SiteChangedError`; snapshot debug.
6. Tulis test sesuai jalur yang dipilih.
7. Pastikan `config/platforms.yaml` tetap `enabled: true`.

## Test yang harus ditulis
- Jalur stub: test bahwa hasil sub-run `skipped` + `NOT_PUBLICLY_ACCESSIBLE`,
  run keseluruhan tidak `failed`.
- Jalur publik: ≥3 fixture daftar, ≥5 detail, kasus tepi, contract `RawJob`.
- Test deteksi tantangan bila ada halaman tantangan.

## Kriteria selesai (checklist)
- [ ] Keputusan discovery diterapkan konsisten.
- [ ] Stub tidak menjatuhkan run/platform lain.
- [ ] Bila publik: SCRAPER_SPEC §8.3 terpenuhi.
- [ ] Test offline hijau; `ruff` bersih.
- [ ] Notes diperbarui dengan hasil final.

## Cara verifikasi
```bash
uv run pytest tests/scrapers/test_pintarnya.py -q
uv run pytest -q
uv run ruff check app tests
```
Harapan: semua lulus.

## Yang TIDAK boleh dilakukan
- Menembus CAPTCHA/login/aplikasi.
- Mengarang selector/endpoint.
- Menyentuh DB/filter bisnis.
- Menandai run keseluruhan `failed` hanya karena Pintarnya tidak publik.

## Catatan / risiko
- Bila lowongan IT nyaris tidak ada, implementasi sederhana tetap sah; catat.
- Stub `skipped` harus terlihat di `GET /scrape/runs/{run_id}`.
