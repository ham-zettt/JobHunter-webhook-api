# Task 29 — Discovery Pintarnya

- **Fase:** F5 **Prasyarat:** 05–09 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §3, §7.7, §8.1
- **Status:** `[ ]`

## Tujuan
Menjawab apakah Pintarnya punya daftar lowongan publik yang layak di-scrape.
Hasil discovery menentukan implementasi normal vs stub `skipped`.

## File yang perlu dibaca
- `SCRAPER_SPEC.md` §3, §7.7, §8.1
- `scripts/discover_platform.py`
- `app/scrapers/platforms/_placeholder.py`
- `app/scrapers/registry.py`, `config/platforms.yaml`

## File yang akan dibuat/diubah
- `docs/platform_notes/pintarnya.md`
- `tests/fixtures/pintarnya/` (bila ada data publik)
- Tidak ada kode scraper pada task ini.

## Langkah-langkah
1. Jalankan
   `uv run python scripts/discover_platform.py pintarnya --url "https://pintarnya.com" --headed`.
2. Jawab: apakah ada daftar lowongan **publik** tanpa login/aplikasi?
3. Jika ada, catat pencarian, paginasi, tanggal posting, gaji, sistem kerja,
   tipe kerja, dan apakah ada lowongan IT.
4. Jika hanya via aplikasi/login berbayar/CAPTCHA permanen, catat bukti dan
   rekomendasikan stub `skipped` dengan
   `errors=[{code:"NOT_PUBLICLY_ACCESSIBLE"}]`.
5. Catat `robots.txt` dan halaman yang tidak akan diakses.
6. Bila publik, simpan ≥3 halaman daftar & ≥5 detail (bersih) sebagai fixture.
7. Tulis `docs/platform_notes/pintarnya.md` sesuai templat §3 + keputusan.

## Test yang harus ditulis
Belum ada. Bila hasilnya stub, test stub ditulis pada task 30.

## Kriteria selesai (checklist)
- [ ] Catatan discovery lengkap.
- [ ] Keputusan eksplisit: publik → implementasi, tidak publik → stub `skipped`.
- [ ] Bukti (URL/status/HTML) untuk keputusan, bukan asumsi.
- [ ] Fixture tersedia bila publik.
- [ ] Volume/keberadaan lowongan IT dicatat.

## Cara verifikasi
```bash
grep -n "Metode terpilih\|Keputusan\|NOT_PUBLICLY_ACCESSIBLE\|Perbedaan" docs/platform_notes/pintarnya.md
```
Harapan: keputusan jelas dan dapat diuji.

## Yang TIDAK boleh dilakukan
- Mengarang endpoint/selector.
- Menembus CAPTCHA/login/aplikasi.
- Memaksa implementasi bila tidak dapat diakses publik.

## Catatan / risiko
- SCRAPER_SPEC menyebut struktur belum diketahui; temuan apa pun harus jujur.
- Stub `skipped` bukan kegagalan run.
