# PLAN — Job Scraper API

Turunan fase PRD §12 dan SCRAPER_SPEC. Sumber kebenaran requirement tetap
`PRD.md > DATABASE.md > ARCHITECTURE.md > SCRAPER_SPEC.md`.
Status per task: `[x]` selesai + bukti, `[~]` sebagian, `[ ]` belum.

File task `plan/NN-*.md` **hanya dibuat untuk task `[~]` dan `[ ]`**.
Task `[x]` cukup dicatat di `plan/PROGRESS.md`. Detail penyimpangan: `plan/NOTES.md`.
Handoff historis: `plan/HANDOFF.md` (jangan dianggap status terkini).

## Indeks task

| No | Judul | Fase | Status |
|----|-------|------|--------|
| 01 | Fondasi proyek & konfigurasi | F0 | [x] |
| 02 | Skema SQLite, PRAGMA, FTS5, Alembic | F0 | [x] |
| 03 | Auth API key, format error, `/health` | F0 | [x] |
| 04 | Docker, entrypoint, verifikasi `docker compose up` | F0 | [x] |
| 05 | Normalizer teks + parser tanggal/gaji + deteksi sistem/tipe kerja | F1 | [x] |
| 06 | Normalisasi lokasi + BR-02/BR-03 | F1 | [x] |
| 07 | Classifier kata kunci + skor + role category | F1 | [x] |
| 08 | Deduper L1–L3 + matriks 14 kasus | F1 | [~] |
| 09 | Pipeline orchestration + statistik alasan filter | F1 | [x] |
| 10 | RunManager + Orchestrator | F2 | [x] |
| 11 | Endpoint scrape/status/platforms/keywords | F2 | [x] |
| 12 | Endpoint jobs list/detail/export + filter + FTS5 | F2 | [x] |
| 13 | Seed keyword & `location_aliases` | F2 | [x] |
| 14 | Uji idempotensi NFR-05 | F2 | [x] |
| 15 | Uji filter remote Indonesia BR-03 | F2 | [x] |
| 16 | Uji filter `max_age_days` BR-04/FR-22 | F2 | [~] |
| 17 | Discovery JobStreet | F3 | [x] |
| 18 | Scraper JobStreet + fixture/test | F3 | [x] |
| 19 | Discovery Glints | F3 | [x] |
| 20 | Scraper Glints + fixture/test | F3 | [x] |
| 21 | Discovery Kalibrr | F3 | [ ] |
| 22 | Scraper Kalibrr + fixture/test | F3 | [ ] |
| 23 | Discovery Dealls | F3 | [ ] |
| 24 | Scraper Dealls + fixture/test | F3 | [ ] |
| 25 | Discovery KitaLulus | F4 | [ ] |
| 26 | Scraper KitaLulus + fixture/test | F4 | [ ] |
| 27 | Discovery LinkedIn + login/sesi | F4 | [~] |
| 28 | Scraper LinkedIn + fixture/test | F4 | [ ] |
| 29 | Discovery Pintarnya | F5 | [ ] |
| 30 | Scraper/stub Pintarnya + test | F5 | [ ] |
| 31 | Hardening: retry, canary, snapshot, deteksi blokir | F5 | [~] |
| 32 | Webhook callback end-to-end | F6 | [~] |
| 33 | Backup, retensi, `scripts/prune.py` | F6 | [~] |
| 34 | Tuning dedup + reclassify (OPSIONAL) | F6 | [ ] |
| 35 | README + contoh workflow n8n | F6 | [~] |
| 36 | Uji end-to-end + review kriteria rilis PRD §13 | F6 | [ ] |

## Dependensi

| Task | Prasyarat | Catatan |
|------|-----------|---------|
| 02 | 01 | konfigurasi DB |
| 03 | 01, 02 | auth + health butuh DB |
| 04 | 01–03 | build image |
| 05–08 | 02 | pipeline butuh model |
| 09 | 05–08 | menyatukan tahap |
| 10 | 09 | runner memakai pipeline |
| 11–13 | 10 | endpoint memakai runner/repo |
| 14–16 | 09–12 | uji lintas pipeline/API |
| 17,19 | 05–09 | discovery setelah kontrak data stabil |
| 18 | 17 | implementasi setelah catatan discovery |
| 20 | 19 | implementasi setelah catatan discovery |
| 21,23,25,29 | 05–09 | discovery per platform, paralel |
| 22 | 21 | implementasi Kalibrr |
| 24 | 23 | implementasi Dealls |
| 26 | 25 | implementasi KitaLulus |
| 27 | 10, 18 | script login + pola browser |
| 28 | 27 | implementasi LinkedIn |
| 30 | 29 | implementasi/stub Pintarnya |
| 31 | 18, 20 | hardening setelah ada 2 scraper nyata |
| 32 | 10, 11 | callback butuh run + status |
| 33 | 02 | backup/retensi DB |
| 34 | 08 | tuning setelah matriks dedup lengkap |
| 35 | 17–30 | dokumentasi platform |
| 36 | semua | gerbang rilis |

## Urutan eksekusi

1. Selesaikan utang F0–F2: **04, 08, 16**.
2. F3 platform: **21 → 22**, **23 → 24** (bisa paralel antar-platform).
3. F4: **25 → 26**, **27 → 28** (LinkedIn terakhir di `scrape/all`).
4. F5: **29 → 30**, lalu **31**.
5. F6: **32, 33, 34, 35**, terakhir **36**.

Paralel yang aman: discovery 21/23/25/29; implementasi 22/24/26 setelah
discovery masing-masing; 33 dan 35 dapat berjalan kapan saja setelah 02.
Jangan paralelkan dua task yang menulis file sama (`registry.py`, `platforms.yaml`,
`PROGRESS.md`).
