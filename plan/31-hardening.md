# Task 31 — Hardening: retry, canary, snapshot, deteksi blokir

- **Fase:** F5 **Prasyarat:** 18, 20 **Estimasi:** L
- **Referensi:** NFR-01–NFR-03, ARCHITECTURE §5.1–§5.3, SCRAPER_SPEC §4.2–§4.3
- **Status:** `[~]` — canary dasar, `detect_challenge`, snapshot JobStreet ada;
  retry terpusat, baseline canary, snapshot Glints, dan test belum

## Tujuan

Menutup sisa ketahanan: retry jaringan terpusat, canary berbasis baseline,
snapshot debug konsisten, dan test deteksi blokir.

## File yang perlu dibaca

- `app/runner/orchestrator.py` (`_canary`, `DEGRADED_AFTER_CONSECUTIVE_ERRORS`)
- `app/scrapers/browser.py` (`detect_challenge`, `save_debug_snapshot`)
- `app/scrapers/exceptions.py`
- `app/scrapers/platforms/jobstreet.py`, `app/scrapers/platforms/glints.py`
- `app/db/repositories/run_repo.py` (riwayat sub-run)
- ARCHITECTURE §5.1–§5.3 · SCRAPER_SPEC §4.2–§4.3

## File yang akan dibuat/diubah

- Helper retry di `app/scrapers/browser.py` atau `app/scrapers/common/`
- `app/runner/orchestrator.py` (canary baseline)
- `app/scrapers/platforms/glints.py` (snapshot pada parse gagal)
- `tests/scrapers/test_block_detection.py` atau test terkait

## Langkah-langkah

1. Tambah helper retry memakai `tenacity`: 3 percobaan, backoff 2→4→8 dtk +
   jitter, hanya untuk `TransientNetworkError`/5xx/timeout.
2. Pastikan 403/CAPTCHA/challenge **tidak** di-retry → `BlockedError`.
3. Implementasikan `Retry-After` untuk 429 (maks 2 kali) sebelum `BlockedError`.
4. Tambah baseline canary: cek riwayat `scrape_run_sources` sukses untuk term
   yang sama; 0 hasil pada term historis produktif → `degraded`.
5. Pastikan >30% field wajib hilang dan median deskripsi <150 karakter →
   `degraded` (sudah ada; tambah test).
6. Panggil `save_debug_snapshot` pada kegagalan parse Glints (dan platform baru).
7. Batasi rotasi snapshot dengan `DEBUG_SNAPSHOT_MAX_FILES`.
8. Tambah test unit untuk `detect_challenge`, retry, dan canary.

## Test yang harus ditulis

- `detect_challenge` untuk teks/URL/iframe tantangan (§4.3).
- Retry 3× pada error transient; tidak retry pada 403.
- Canary: 0 hasil pada term historis produktif → `degraded`.
- Canary: median deskripsi <150 → `degraded`.
- Snapshot tidak menjatuhkan run saat gagal menulis.

## Kriteria selesai (checklist)

- [ ] Retry terpusat, bukan duplikat di tiap scraper.
- [ ] 403/CAPTCHA tidak pernah di-retry.
- [ ] Canary memakai baseline historis.
- [ ] Snapshot debug dipakai konsisten + rotasi.
- [ ] Test offline hijau; `ruff` bersih.

## Cara verifikasi

```bash
uv run pytest -q
uv run ruff check app tests
```

Harapan: semua lulus; tidak ada retry pada `BlockedError`.

## Yang TIDAK boleh dilakukan

- Menembus CAPTCHA/stealth/fingerprint spoofing.
- Retry pada 403/checkpoint.
- Menyimpan snapshot tanpa batas.
- Mengubah aturan filter bisnis.

## Catatan / risiko

- Baseline canary memerlukan query riwayat; jangan menambah tabel baru tanpa
  memperbarui DATABASE.
- Retry berlebihan memperbesar risiko blokir; patuhi batas §4.
