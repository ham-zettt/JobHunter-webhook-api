# Task 26 — Scraper KitaLulus + fixture/test

- **Fase:** F4 **Prasyarat:** 25 **Estimasi:** L
- **Referensi:** SCRAPER_SPEC §2, §4, §5, §6, §7.6, §8
- **Status:** `[ ]`

## Tujuan
Mengimplementasikan `KitaLulusScraper` dengan daftar HTML awal + klik "load more"
dan detail dari halaman detail.

## File yang perlu dibaca
- `docs/platform_notes/kitalulus.md`
- `app/scrapers/base.py`, `app/scrapers/browser.py`, `app/scrapers/exceptions.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py`
- `app/scrapers/common/text.py`
- `tests/scrapers/test_{jobstreet,glints}.py`
- SCRAPER_SPEC §5.6, §5.7

## File yang akan dibuat/diubah
- `app/scrapers/platforms/kitalulus.py`
- `tests/scrapers/test_kitalulus.py`
- `tests/fixtures/kitalulus/`

## Langkah-langkah
1. Tulis parser murni `parse_listing_payload(html) -> list[RawListing]` dan
   `parse_detail_payload(html) -> RawJob`.
2. Buat `class KitaLulusScraper(BaseScraper)` dengan `platform = "kitalulus"`.
3. `iter_listings(term)`: buka daftar, klik "load more" berulang hingga
   `max_pages_per_term` atau tombol habis; jaga jeda & deteksi tantangan.
4. `fetch_detail`: buka `/lowongan/detail/<slug>`, terapkan §5.6.
5. Petakan field; pendidikan/benefit/skill ke `extra` (bukan kolom DB).
6. Tanggal: gunakan sumber terbukti; bila tidak ada → `None`, presisi `unknown`.
7. Tangani kegagalan dengan status yang benar; snapshot debug.
8. Tulis test parser; smoke live manual ≤2 halaman/≤3 detail.

## Test yang harus ditulis
- ≥3 fixture daftar.
- ≥5 fixture detail (variasi gaji/lokasi/tipe).
- Kasus tanpa tanggal → `posted_raw is None`.
- Kasus field `extra` (pendidikan/benefit/skill) terisi.
- Contract test `RawJob`.

## Kriteria selesai (checklist)
- [ ] SCRAPER_SPEC §8.3 terpenuhi.
- [ ] Deskripsi lengkap.
- [ ] Tanggal benar atau `unknown` terdokumentasi.
- [ ] Test offline hijau; `ruff` bersih.
- [ ] Gagal tanpa menjatuhkan run/platform lain.

## Cara verifikasi
```bash
uv run pytest tests/scrapers/test_kitalulus.py -q
uv run pytest -q
uv run ruff check app tests
```
Harapan: semua lulus.

## Yang TIDAK boleh dilakukan
- Menyentuh DB/filter bisnis.
- Mengarang selector.
- Menembus CAPTCHA/stealth.
- Menyimpan data pribadi.

## Catatan / risiko
- "load more" bisa memicu XHR; pilih jalur stabil dari discovery.
- Jangan memakai tanggal aktivitas sebagai tanggal posting.
