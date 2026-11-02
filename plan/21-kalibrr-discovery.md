# Task 21 — Discovery Kalibrr

- **Fase:** F3 **Prasyarat:** 05–09 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §3, §5.0, §5.7, §7.4, §8.1; PRD §0.5
- **Status:** `[ ]`

## Tujuan
Membuktikan struktur nyata Kalibrr sebelum menulis scraper: URL pencarian,
sumber data daftar/detail, paginasi, tanggal posting, batas lamar, dan field
yang tersedia.

## File yang perlu dibaca
- `SCRAPER_SPEC.md` §3 (prosedur discovery), §5.0, §5.7, §7.4, §8.1
- `scripts/discover_platform.py`
- `docs/platform_notes/jobstreet.md`, `docs/platform_notes/glints.md` (contoh format)
- `app/scrapers/base.py` (`RawListing`, `RawJob`)

## File yang akan dibuat/diubah
- `docs/platform_notes/kalibrr.md`
- `tests/fixtures/kalibrr/` (HTML/JSON sampel)
- Tidak ada kode scraper pada task ini.

## Langkah-langkah
1. Jalankan
   `uv run python scripts/discover_platform.py kalibrr --url "https://www.kalibrr.com/id-ID/job-board/..." --headed`
   — URL pasti bertanda `[verifikasi]`.
2. Catat URL pencarian final, parameter kata kunci, filter negara Indonesia,
   urutan terbaru, dan mekanisme paginasi (page/offset/cursor).
3. Cari sumber data: JSON-LD, `__NEXT_DATA__`, state global, atau respons XHR/API
   internal. Catat endpoint, method, header penting, bentuk payload.
4. Buka ≥3 halaman daftar dan ≥5 halaman detail; catat selector/field stabil.
5. Catat sumber tanggal posting dan `application_deadline` → `expires_raw`.
6. Catat pola `external_id` dan URL kanonik sesuai §5.7.
7. Uji permintaan beruntun; catat 429/403/CAPTCHA dan `robots.txt`.
8. Simpan fixture bersih (tanpa data pribadi) ke `tests/fixtures/kalibrr/`.
9. Tulis `docs/platform_notes/kalibrr.md` memakai templat §3, termasuk
   "Perbedaan dari SCRAPER_SPEC.md".

## Test yang harus ditulis
Belum ada test parser; parser dibuat pada task 22.

## Kriteria selesai (checklist)
- [ ] `docs/platform_notes/kalibrr.md` lengkap sesuai templat §3.
- [ ] Metode terpilih (JSON-LD/XHR/API/DOM) dibuktikan, bukan diasumsikan.
- [ ] Paginasi & batas hasil per kueri terdokumentasi.
- [ ] Sumber tanggal posting + format terdokumentasi.
- [ ] ≥3 fixture daftar, ≥5 fixture detail tersimpan.
- [ ] Semua selector/endpoint `[verifikasi]` yang terbukti dicatat final.

## Cara verifikasi
```bash
ls tests/fixtures/kalibrr
grep -n "Metode terpilih\|Pagination\|Sumber tanggal\|Perbedaan" docs/platform_notes/kalibrr.md
```
Harapan: file notes lengkap, fixture cukup, tidak ada `TODO(discovery)` yang
diam-diam dianggap final.

## Yang TIDAK boleh dilakukan
- Mengarang selector/endpoint dari SCRAPER_SPEC.
- Menulis `app/scrapers/platforms/kalibrr.py`.
- Menembus CAPTCHA atau memakai plugin stealth.
- Menyimpan data pribadi/kontak rekruter.

## Catatan / risiko
- Kalibrr memuat banyak lowongan non-IT; pre-filter judul penting.
- Bila data hanya tersedia via API bertoken sekali pakai, pilih DOM/JSON-LD.
