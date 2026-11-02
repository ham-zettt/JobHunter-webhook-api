# Task 22 — Scraper Kalibrr + fixture/test

- **Fase:** F3 **Prasyarat:** 21 **Estimasi:** L
- **Referensi:** SCRAPER_SPEC §2, §4, §5, §6, §7.4, §8; ARCHITECTURE §4.1
- **Status:** `[ ]`

## Tujuan
Mengimplementasikan `KalibrrScraper` berdasarkan hasil discovery task 21,
dengan parser murni yang diuji fixture.

## File yang perlu dibaca
- `docs/platform_notes/kalibrr.md`
- `app/scrapers/base.py`, `app/scrapers/browser.py`, `app/scrapers/exceptions.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py` (pola)
- `app/scrapers/common/text.py`, `app/scrapers/common/salary.py`
- `tests/scrapers/test_jobstreet.py`, `tests/scrapers/test_glints.py`
- `tests/fixtures/kalibrr/`
- SCRAPER_SPEC §5.6 (deskripsi lengkap), §5.7 (`external_id`/URL kanonik)

## File yang akan dibuat/diubah
- `app/scrapers/platforms/kalibrr.py`
- `tests/scrapers/test_kalibrr.py`
- `tests/fixtures/kalibrr/` (finalkan sampel dari discovery)
- `app/scrapers/registry.py` sudah memetakan `kalibrr`; jangan duplikasi.

## Langkah-langkah
1. Tulis parser murni `parse_listing_payload(payload, page=1) -> list[RawListing]`
   dan `parse_detail_payload(html|json) -> RawJob`; tanpa browser.
2. Buat `class KalibrrScraper(BaseScraper)` dengan `platform = "kalibrr"` dan
   `requires_auth = False`.
3. `iter_listings(term)`: pencarian kata kunci, urut terbaru, filter Indonesia,
   jeda acak dari `platforms.yaml`, hentikan pada halaman kosong/batas
   `max_pages_per_term`, deteksi tantangan.
4. `fetch_detail(listing)`: buka detail, terapkan §5.6 (klik perluasan, tunggu
   stabil, konversi HTML → teks, deteksi terpotong).
5. Petakan field: `external_id`, `posted_raw`, `expires_raw` dari batas lamar,
   `work_mode_raw`, `employment_type_raw`, `salary_raw`, `location_raw`.
6. Canonical URL tanpa query; gabungkan kota/provinsi/negara sesuai §5.5.
7. Tangani `BlockedError`, `TransientNetworkError`, `ParseError`, `SiteChangedError`;
   simpan snapshot debug pada kegagalan parse.
8. Tulis test parser dari fixture; jangan memakai jaringan.
9. Tambah smoke `@pytest.mark.live -k kalibrr` (≤2 halaman, ≤3 detail), manual.

## Test yang harus ditulis
- ≥3 fixture daftar: jumlah & field `RawListing`.
- ≥5 fixture detail: `RawJob` lengkap, deskripsi tidak terpotong, tanggal benar.
- Kasus tepi: tanpa gaji, tanpa perusahaan, deskripsi panjang, Unicode/emoji.
- Contract test: hasil parser lolos field wajib `RawJob`.
- `test_fixtures_are_not_challenge_pages`.

## Kriteria selesai (checklist)
- [ ] SCRAPER_SPEC §8.3 terpenuhi.
- [ ] `pytest tests/scrapers/test_kalibrr.py` hijau tanpa jaringan.
- [ ] Tidak ada selector/endpoint tanpa bukti discovery.
- [ ] `external_id` & URL kanonik sesuai §5.7.
- [ ] Kegagalan menghasilkan status `blocked`/`degraded`/`failed`, bukan crash run.

## Cara verifikasi
```bash
uv run pytest tests/scrapers/test_kalibrr.py -q
uv run pytest -q
uv run ruff check app tests
```
Harapan: semua lulus; `ruff` bersih.

## Yang TIDAK boleh dilakukan
- Menyentuh DB atau menerapkan filter bisnis di scraper.
- Mengarang selector; semua harus dari `docs/platform_notes/kalibrr.md`.
- Menembus CAPTCHA; tidak ada stealth/fingerprint spoofing.
- Menyimpan kontak rekruter.

## Catatan / risiko
- Skema API Kalibrr dapat berubah; sertakan fallback DOM minimal untuk canary.
- Jangan memakai `updatedAt` sebagai tanggal posting.
