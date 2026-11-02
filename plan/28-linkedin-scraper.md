# Task 28 — Scraper LinkedIn + fixture/test

- **Fase:** F4 **Prasyarat:** 27 **Estimasi:** L
- **Referensi:** SCRAPER_SPEC §4, §5, §6, §7.1, §8; ARCHITECTURE §4.4
- **Status:** `[ ]`

## Tujuan
Mengimplementasikan `LinkedInScraper` memakai sesi tersimpan, dengan batas
ketat, deteksi tantangan, dan status `auth_required`/`blocked` yang benar.

## File yang perlu dibaca
- `docs/platform_notes/linkedin.md`
- `app/scrapers/base.py`, `app/scrapers/browser.py`, `app/scrapers/exceptions.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py`
- `app/runner/orchestrator.py` (penanganan `AuthRequiredError`)
- `app/services/platform_service.py` (`_auth_state`)
- `tests/scrapers/test_{jobstreet,glints}.py`
- SCRAPER_SPEC §7.1(c)(d)(e), §5.1, §5.6, §5.7

## File yang akan dibuat/diubah
- `app/scrapers/platforms/linkedin.py`
- `tests/scrapers/test_linkedin.py`
- `tests/fixtures/linkedin/`

## Langkah-langkah
1. Tulis parser murni untuk kartu daftar dan panel detail
   (`parse_listing_payload`, `parse_detail_payload`).
2. Buat `class LinkedInScraper(BaseScraper)` dengan
   `platform = "linkedin"` dan `requires_auth = True`.
3. `check_session()`: buka `https://www.linkedin.com/jobs/`; bila redirect ke
   login/checkpoint/authwall atau state tidak ada → `AuthRequiredError`.
4. `iter_listings(term)`: `location=Indonesia`, urut terbaru, `f_TPR` dari
   `max_age_days`, `start` kelipatan 25; tambahan `f_WT=2` untuk 3 term prioritas.
5. `fetch_detail`: buka `/jobs/view/<id>/`, klik perluasan, terapkan §5.6,
   dukung UI Indonesia/Inggris.
6. Hormati batas: konkurensi 1, jeda 4–9 dtk, `LINKEDIN_MAX_JOBS_PER_RUN`,
   `LINKEDIN_MAX_JOBS_PER_DAY`, `search_terms_limit=6`.
7. Deteksi 999/429/checkpoint/CAPTCHA → `BlockedError`/`AuthRequiredError`;
   berhenti, snapshot, tanpa retry.
8. Jalankan LinkedIn **terakhir** pada `scrape/all` (registry order/`PLATFORM_ORDER`).
9. Read-only: jangan klik Apply/Save/Follow/Connect/Message/Report.
10. Tulis test parser dari fixture; smoke live manual sangat terbatas.

## Test yang harus ditulis
- ≥3 fixture daftar: ID, judul, perusahaan, lokasi, waktu.
- ≥5 fixture detail: deskripsi lengkap, pil remote/onsite/hybrid, tipe kerja.
- `check_session` dengan state hilang → `AuthRequiredError` (mock).
- Deteksi halaman checkpoint → `BlockedError`/`auth_required`.
- Contract test `RawJob`.

## Kriteria selesai (checklist)
- [ ] SCRAPER_SPEC §8.3 terpenuhi.
- [ ] `check_session()` dan status `auth_required` teruji.
- [ ] Batas per run/hari dihormati.
- [ ] Tidak ada kredensial di log/repo.
- [ ] Test offline hijau; live manual opsional.
- [ ] LinkedIn diproses terakhir.

## Cara verifikasi
```bash
uv run pytest tests/scrapers/test_linkedin.py -q
uv run pytest -q
uv run ruff check app tests
```
Harapan: semua lulus; tidak ada state sesi tersimpan di repo.

## Yang TIDAK boleh dilakukan
- Login otomatis/menyimpan kata sandi.
- Menembus CAPTCHA/checkpoint atau memakai stealth.
- Mengekstrak data rekruter.
- Menyentuh DB/filter bisnis.
- Menjalankan live test di CI/default.

## Catatan / risiko
- Paling rawan pembatasan akun; patuhi batas dan urutan.
- Gunakan jalur "lowongan dikenal" agresif untuk mengurangi detail.
