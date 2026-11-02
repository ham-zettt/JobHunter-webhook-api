# Task 24 — Scraper Dealls + fixture/test

- **Fase:** F3 **Prasyarat:** 23 **Estimasi:** L
- **Referensi:** SCRAPER_SPEC §2, §4, §5, §6, §7.5, §8; ARCHITECTURE §4.1
- **Status:** `[ ]`

## Tujuan
Mengimplementasikan `DeallsScraper`: detail HTTP-first, daftar dengan tombol
"Lihat Lebih Banyak", dan tanggal posting yang benar.

## File yang perlu dibaca
- `docs/platform_notes/dealls.md`
- `app/scrapers/base.py`, `app/scrapers/browser.py`, `app/scrapers/exceptions.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py`
- `app/scrapers/common/text.py`
- `tests/scrapers/test_{jobstreet,glints}.py`
- SCRAPER_SPEC §5.1 (tanggal), §5.6 (deskripsi), §5.7 (ID/URL)

## File yang akan dibuat/diubah
- `app/scrapers/platforms/dealls.py`
- `tests/scrapers/test_dealls.py`
- `tests/fixtures/dealls/`

## Langkah-langkah
1. Tulis `parse_listing_payload(html) -> list[RawListing]` dan
   `parse_detail_payload(html|json) -> RawJob` murni.
2. Buat `class DeallsScraper(BaseScraper)` dengan `platform = "dealls"`.
3. `iter_listings(term)`: buka halaman pencarian, klik
   "Lihat Lebih Banyak"/"See More" hingga batas `max_pages_per_term` atau tombol
   habis, dengan jeda acak §4.1 dan deteksi tantangan.
4. `fetch_detail`: HTTP-first bila halaman server-rendered; fallback Playwright.
5. Terapkan §5.6 untuk deskripsi lengkap; simpan `description_html` bila
   `STORE_HTML=true`.
6. Tanggal: pakai `datePosted`/data tertanam/API yang terbukti. Bila tidak ada,
   `posted_raw=None`; jangan pakai label aktivitas rekruter.
7. Seragamkan URL kanonik tanpa `/en` dan tanpa query pelacak.
8. Tangani error & snapshot debug sesuai §4.3/ARCH §5.1.
9. Tulis test parser + smoke live manual.

## Test yang harus ditulis
- ≥3 fixture daftar (termasuk setelah "lebih banyak").
- ≥5 fixture detail dengan variasi gaji/mode kerja/tipe kerja.
- Kasus tanpa tanggal posting → `posted_raw is None`.
- Kasus label "Rekruter aktif" tidak menghasilkan tanggal posting.
- Contract test field wajib `RawJob`.

## Kriteria selesai (checklist)
- [ ] SCRAPER_SPEC §8.3 terpenuhi.
- [ ] Deskripsi lengkap; tidak ada potongan daftar.
- [ ] Tanggal posting benar atau `None` dengan alasan terdokumentasi.
- [ ] URL kanonik konsisten (tanpa locale/query).
- [ ] Test offline hijau; `ruff` bersih.

## Cara verifikasi
```bash
uv run pytest tests/scrapers/test_dealls.py -q
uv run pytest -q
uv run ruff check app tests
```
Harapan: semua lulus.

## Yang TIDAK boleh dilakukan
- Menyentuh DB/filter bisnis.
- Memakai `updatedAt` atau aktivitas rekruter sebagai tanggal posting.
- Mengarang selector; ikuti notes discovery.
- Menembus CAPTCHA/stealth.

## Catatan / risiko
- Tombol "lebih banyak" bisa memuat data via XHR; pilih jalur paling stabil.
- Banyak lowongan non-IT; pre-filter judul menghemat detail.
