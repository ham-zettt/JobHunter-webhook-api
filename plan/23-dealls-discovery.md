# Task 23 — Discovery Dealls

- **Fase:** F3 **Prasyarat:** 05–09 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §3, §5.0, §5.7, §7.5
- **Status:** `[ ]`

## Tujuan
Menentukan struktur nyata Dealls, khususnya cara memuat daftar lewat tombol
"Lihat Lebih Banyak" dan sumber **tanggal posting sebenarnya** (bukan label
aktivitas rekruter).

## File yang perlu dibaca
- `SCRAPER_SPEC.md` §3, §5.0, §5.7, §7.5
- `scripts/discover_platform.py`
- `docs/platform_notes/jobstreet.md`, `docs/platform_notes/glints.md`
- `app/scrapers/base.py`

## File yang akan dibuat/diubah
- `docs/platform_notes/dealls.md`
- `tests/fixtures/dealls/`
- Tidak ada kode scraper pada task ini.

## Langkah-langkah
1. Jalankan
   `uv run python scripts/discover_platform.py dealls --url "https://dealls.com/loker/..." --headed`
   — URL final `[verifikasi]`.
2. Catat URL pencarian, filter kata kunci/lokasi/kategori, dan cara memuat
   tambahan (tombol "Lihat Lebih Banyak"/"See More", paginasi, atau API).
3. Periksa HTML detail: JSON-LD `datePosted`, data tertanam, atau API internal.
4. **Wajib** bedakan `Rekruter aktif N hari lalu`/`Actively hiring` dari tanggal
   posting; catat sumber tanggal yang sah atau `NULL/unknown`.
5. Catat pola slug detail `<judul>-<n>~<perusahaan>`, varian `/en/`, dan URL
   kanonik tanpa locale.
6. Buka ≥3 halaman daftar (setelah klik lebih banyak) dan ≥5 detail.
7. Catat mode kerja, tipe kerja, gaji, lokasi, dan batas laju.
8. Simpan fixture bersih ke `tests/fixtures/dealls/`.
9. Tulis `docs/platform_notes/dealls.md` sesuai templat §3.

## Test yang harus ditulis
Belum ada test parser; parser dibuat pada task 24.

## Kriteria selesai (checklist)
- [ ] Catatan discovery lengkap sesuai templat §3.
- [ ] Mekanisme "Lihat Lebih Banyak" terdokumentasi (jumlah klik/batas).
- [ ] Sumber tanggal posting jelas; label aktivitas rekruter tidak dipakai.
- [ ] URL kanonik tanpa `/en`.
- [ ] ≥3 fixture daftar, ≥5 fixture detail.

## Cara verifikasi
```bash
ls tests/fixtures/dealls
grep -n "Metode terpilih\|Pagination\|Sumber tanggal\|Perbedaan\|Lebih Banyak" docs/platform_notes/dealls.md
```
Harapan: semua bagian ada; tidak ada asumsi tanggal.

## Yang TIDAK boleh dilakukan
- Menulis scraper sebelum notes lengkap.
- Memakai label "Rekruter aktif" sebagai `posted_at`.
- Mengarang selector/endpoint.
- Menembus CAPTCHA.

## Catatan / risiko
- Halaman detail Dealls dilaporkan server-rendered; HTTP-first dapat dipakai.
- Locale ganda (`/en`) harus diseragamkan.
