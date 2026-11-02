# Task 36 — Uji end-to-end + review kriteria rilis PRD §13

- **Fase:** F6 **Prasyarat:** semua task **Estimasi:** L
- **Referensi:** PRD §13, §10; NFR-01–NFR-11; SCRAPER_SPEC §8.3
- **Status:** `[ ]`

## Tujuan
Membuktikan rilis 1.0 memenuhi semua kriteria PRD §13 dengan bukti yang dapat
diulang, tanpa menembus proteksi platform.

## File yang perlu dibaca
- `PRD.md` §13, §10
- `plan/PROGRESS.md`, `plan/NOTES.md`
- `README.md`, `docs/n8n_workflow.json`
- `docs/platform_notes/*.md`
- `tests/` (semua level)

## File yang akan dibuat/diubah
- `docs/RELEASE_CHECKLIST.md` (hasil verifikasi + tanggal + commit)
- `plan/PROGRESS.md`
- Perbaikan hanya bila menemukan bug; bug besar dicatat sebagai task baru.

## Langkah-langkah
1. Jalankan `uv run pytest -q` dan `uv run ruff check app tests`.
2. Jalankan `docker compose up --build`; cek `/health`.
3. Untuk setiap platform yang berfungsi: `POST /scrape/{platform}` dengan
   `max_age_days=7`, lalu cek status run + statistik.
4. Jalankan `POST /scrape/all`; pastikan kegagalan satu platform terisolasi
   (`partial`/`degraded`), bukan `failed` total.
5. Jalankan scrape dua kali berturut-turut; catat `new`/duplikat (NFR-05).
6. Ambil sampel 50 lowongan/platform; verifikasi 9 field wajib PRD §6 dan
   `deskripsi` lengkap ≥95%.
7. Verifikasi filter `max_age_days`, remote Indonesia diterima, remote asing &
   onsite luar Jawa ditolak, dan kasus BR-06.
8. Jalankan alur n8n §10 end-to-end (termasuk callback bila dipakai).
9. Jalankan `pytest -m live -k <platform>` manual untuk platform yang
   diimplementasikan (≤2 halaman/≤3 detail).
10. Tulis `docs/RELEASE_CHECKLIST.md` dengan status tiap butir §13 + bukti.

## Test yang harus ditulis
Tidak ada test baru kecuali celah yang ditemukan saat verifikasi. Setiap bug
besar → catat di PROGRESS dan buat task terpisah; jangan perbaiki diam-diam.

## Kriteria selesai (checklist)
- [ ] Semua butir PRD §13 tercentang dengan bukti.
- [ ] 7 platform dapat dipicu; kegagalan terisolasi.
- [ ] Field wajib + deskripsi lengkap memenuhi ambang sampel.
- [ ] Idempotensi & filter usia/remote/BR-06 terbukti.
- [ ] Alur n8n berjalan tanpa kode tambahan.
- [ ] Test offline hijau; live manual terdokumentasi.
- [ ] README + login LinkedIn lengkap.

## Cara verifikasi
```bash
uv run pytest -q
uv run ruff check app tests
curl -s -X POST http://localhost:8000/api/v1/scrape/all \
  -H "X-API-Key: $API_KEY" -H "Content-Type: application/json" \
  -d '{"max_age_days": 7}'
curl -s -H "X-API-Key: $API_KEY" http://localhost:8000/api/v1/jobs?only_new=true
```
Harapan: run selesai `completed`/`partial`, lowongan baru dapat diambil.

## Yang TIDAK boleh dilakukan
- Menembus CAPTCHA/checkpoint untuk "meluluskan" uji.
- Menandai rilis selesai tanpa bukti.
- Menghapus test yang gagal.
- Memakai data pribadi dalam sampel/fixture.

## Catatan / risiko
- Uji live memakan waktu dan bisa kena rate limit; jalankan bertahap.
- Simpan bukti (run_id, status, jumlah) di RELEASE_CHECKLIST, bukan salinan data.
