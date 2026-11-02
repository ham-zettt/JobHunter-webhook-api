# Task 04 — Docker, entrypoint, verifikasi `docker compose up`

- **Fase:** F0 **Prasyarat:** 01, 02, 03 **Estimasi:** S
- **Referensi:** NFR-09, NFR-11, ARCHITECTURE §9, DECISIONS D-011
- **Status:** `[~]` — file ada, build/up belum terverifikasi

## Tujuan
Membuktikan image Playwright + aplikasi dapat dibangun dan berjalan dengan
`docker compose up`, `/health` hijau, dan data persisten di `./data`.

## File yang perlu dibaca
- `Dockerfile`, `docker-compose.yml`, `docker/entrypoint.sh`
- `.env.example`, `pyproject.toml`, `uv.lock` (versi `playwright`)
- `app/main.py`, `app/api/routers/health.py`
- ARCHITECTURE §9.1–§9.2 · NFR-09/11

## File yang akan dibuat/diubah
- `Dockerfile` / `docker/entrypoint.sh` hanya bila build gagal.
- Tidak ada perubahan kode fitur.

## Langkah-langkah
1. Pastikan `.env` lokal ada dan `API_KEY` terisi.
2. Bandingkan versi image Playwright di `Dockerfile` dengan `uv.lock`
   (`playwright==1.64.1`); samakan bila berbeda.
3. Jalankan build: `docker compose build job-scraper`.
4. Jalankan `docker compose up -d`, lalu cek log entrypoint menjalankan
   `alembic upgrade head` sebelum uvicorn.
5. Cek `GET http://localhost:8000/health` → `200`, `db=ok`, `browser=ok`.
6. Hentikan container, jalankan ulang; pastikan `data/jobs.db` tetap ada.
7. Catat hasil dan waktu build di `plan/PROGRESS.md`.

## Test yang harus ditulis
Tidak ada unit test baru. Ini verifikasi manual/deploy.

## Kriteria selesai (checklist)
- [ ] `docker compose build` selesai tanpa error.
- [ ] Container berjalan sebagai user non-root (`pwuser`).
- [ ] `alembic upgrade head` sukses di entrypoint.
- [ ] `/health` `200` dengan `db=ok`, `browser=ok`.
- [ ] `data/jobs.db` bertahan setelah restart.
- [ ] Versi image = versi paket `playwright`.

## Cara verifikasi
```bash
docker compose build job-scraper
docker compose up -d
docker compose logs --tail=80 job-scraper
curl -s http://localhost:8000/health
docker compose restart job-scraper
docker compose exec job-scraper ls -l /app/data
```
Harapan: build sukses, log tanpa traceback, health `status=ok`, DB tetap ada.

## Yang TIDAK boleh dilakukan
- Mengubah kode scraper/pipeline/API.
- Memakai `latest` untuk image Playwright.
- Commit `.env` atau `data/`.
- Menembus proteksi situs untuk "membuktikan" scraper.

## Catatan / risiko
- Image ±860 MB; pull bisa timeout. Ulangi pull sebelum menyimpulkan build gagal.
- Health memeriksa browser; launch Chromium di container butuh `shm_size: 1gb`.
