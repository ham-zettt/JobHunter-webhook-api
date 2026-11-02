# Task 25 — Discovery KitaLulus

- **Fase:** F4 **Prasyarat:** 05–09 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §3, §5.0, §5.7, §7.6
- **Status:** `[ ]`

## Tujuan
Memetakan struktur nyata KitaLulus: daftar `/lowongan`, mekanisme "load more",
halaman detail `/lowongan/detail/<slug>`, sumber tanggal, dan volume lowongan IT.

## File yang perlu dibaca
- `SCRAPER_SPEC.md` §3, §5.0, §5.7, §7.6
- `scripts/discover_platform.py`
- `docs/platform_notes/jobstreet.md`, `docs/platform_notes/glints.md`
- `app/scrapers/base.py`

## File yang akan dibuat/diubah
- `docs/platform_notes/kitalulus.md`
- `tests/fixtures/kitalulus/`
- Tidak ada kode scraper pada task ini.

## Langkah-langkah
1. Jalankan
   `uv run python scripts/discover_platform.py kitalulus --url "https://www.kitalulus.com/lowongan" --headed`.
2. Catat URL pencarian/filter kata kunci & lokasi, serta tombol "load more".
3. Tentukan cara memuat tambahan: klik Playwright, parameter page, atau API.
4. Buka detail; temukan wadah deskripsi, tombol perluasan, dan sumber tanggal.
5. Catat field: judul, perusahaan, lokasi, gaji, pendidikan, benefit, skill.
6. Catat pola `external_id`/slug dan URL kanonik tanpa query.
7. Ukur volume lowongan IT pada beberapa `search_term` prioritas.
8. Buka ≥3 halaman daftar dan ≥5 detail; simpan fixture bersih.
9. Tulis `docs/platform_notes/kitalulus.md` sesuai templat §3.

## Test yang harus ditulis
Belum ada test parser; parser dibuat pada task 26.

## Kriteria selesai (checklist)
- [ ] Catatan discovery lengkap.
- [ ] Mekanisme "load more" dan batasnya jelas.
- [ ] Sumber tanggal posting jelas atau `unknown` terdokumentasi.
- [ ] Pemetaan field → `RawJob` tercatat.
- [ ] ≥3 fixture daftar, ≥5 fixture detail.

## Cara verifikasi
```bash
ls tests/fixtures/kitalulus
grep -n "Metode terpilih\|Pagination\|Sumber tanggal\|Perbedaan\|load more" docs/platform_notes/kitalulus.md
```
Harapan: semua bagian ada.

## Yang TIDAK boleh dilakukan
- Menulis scraper sebelum notes lengkap.
- Mengarang selector/endpoint.
- Menembus CAPTCHA.
- Menyimpan kontak pribadi.

## Catatan / risiko
- Volume IT mungkin rendah; itu normal, catat temuannya.
- Tanggal posting mungkin tidak tersedia; jangan menebak.
