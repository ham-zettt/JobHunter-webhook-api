# Task 27 — Discovery LinkedIn + login/sesi

- **Fase:** F4 **Prasyarat:** 10, 18 **Estimasi:** M
- **Referensi:** SCRAPER_SPEC §3, §7.1(a)(b), §5.7; PRD D2/§11; ARCHITECTURE §9.3
- **Status:** `[~]` — `scripts/linkedin_login.py` ada; eksekusi & notes belum

## Tujuan
Menyelesaikan bagian discovery LinkedIn yang aman: login manual tersimpan,
verifikasi `storage_state`, pemetaan selector/parameter, dan catatan risiko.
Tidak melakukan scraping agresif.

## File yang perlu dibaca
- `scripts/linkedin_login.py`
- `docs/platform_notes/jobstreet.md`, `docs/platform_notes/glints.md`
- `app/services/platform_service.py` (`_auth_state`)
- `app/scrapers/browser.py`
- SCRAPER_SPEC §7.1(a)(b), §4, §5.7
- README bagian login LinkedIn

## File yang akan dibuat/diubah
- `docs/platform_notes/linkedin.md`
- `README.md` (bila prosedur/peringatan belum lengkap)
- `tests/fixtures/linkedin/` (sampel DOM yang sudah dibersihkan)
- Tidak ada perubahan kode scraper pada task ini.

## Langkah-langkah
1. Jalankan `uv run python scripts/linkedin_login.py` di mesin lokal **headed**,
   login manual (termasuk 2FA), simpan state ke
   `data/secrets/linkedin_state.json`.
2. Verifikasi permission file `600`; pastikan `data/secrets/` di `.gitignore`
   dan tidak ada isi state di log.
3. Buka halaman `https://www.linkedin.com/jobs/`; pastikan sesi valid dan tidak
   diarahkan ke `/login`, `/checkpoint`, atau `/authwall`.
4. Catat parameter pencarian nyata (`keywords`, `location=Indonesia`, `geoId`,
   `f_TPR`, `f_WT`, `sortBy`, `start`) hanya yang terbukti.
5. Catat selector stabil untuk kartu daftar dan panel detail (atribut/ARIA
   sebelum kelas CSS).
6. Catat sumber tanggal posting, pil sistem/tipe kerja, dan tombol perluasan.
7. Uji `GET /api/v1/platforms`: `auth_state` harus `valid`; jika `missing`/
   `expired`, ulangi login.
8. Catat risiko pembatasan akun + rekomendasi akun cadangan di notes/README.
9. Simpan ≥3 sampel daftar & ≥5 detail (DOM bersih) untuk task 28.

## Test yang harus ditulis
Belum ada test parser. Tambah smoke manual `check_session()` pada task 28.

## Kriteria selesai (checklist)
- [ ] Login manual berhasil; state tersimpan dengan permission `600`.
- [ ] `GET /platforms` melaporkan `auth_state="valid"`.
- [ ] Tidak ada kredensial/cookie di git atau log.
- [ ] `docs/platform_notes/linkedin.md` lengkap + bagian risiko.
- [ ] Selector/parameter final terbukti, bukan asumsi.
- [ ] Fixture tersedia untuk task 28.

## Cara verifikasi
```bash
uv run python scripts/linkedin_login.py
ls -l data/secrets/linkedin_state.json     # -rw------- 
git status --short                          # tidak ada state
curl -s -H "X-API-Key: $API_KEY" http://localhost:8000/api/v1/platforms | grep linkedin
```
Harapan: state `600`, tidak masuk git, `auth_state` valid.

## Yang TIDAK boleh dilakukan
- Menyimpan kata sandi atau melakukan login otomatis.
- Menjalankan login di container headless.
- Menembus checkpoint/CAPTCHA.
- Menyimpan/mengekstrak data rekruter.
- Commit `data/secrets/`.

## Catatan / risiko
- Risiko tertinggi dari semua platform; gunakan akun khusus/cadangan.
- Sesi dapat kedaluwarsa; scraper harus menghasilkan `auth_required`.
- Jangan menjalankan banyak instance bersamaan.
