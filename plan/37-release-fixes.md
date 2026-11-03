# Task 37 — Perbaikan temuan rilis (dari task 36)

- **Fase:** F6 **Prasyarat:** 36 **Estimasi:** M
- **Referensi:** `docs/RELEASE_CHECKLIST.md` §3; NFR-02, NFR-05; SCRAPER_SPEC §4.2, §5.3
- **Status:** `[x]`

## Tujuan
Menutup tiga temuan pada task 36 (uji e2e rilis).

## Perbaikan
1. **`app/scrapers/common/retry.py`** — clamp `Retry-After` ke `RATE_LIMIT_MAX_WAIT_SEC=60`.
   Header `429` besar (mis. `86400`) sebelumnya membuat `asyncio.sleep` menahan run
   hingga berjam-jam ("hang" Kalibrr run-2). Kini maksimum 60 dtk sebelum fallback.
2. **`app/runner/orchestrator.py`** — canary lebih akurat:
   - `_baseline_degraded` hanya dievaluasi pada term yang **benar-benar dicoba**
     (`attempted`); term yang tak tersentuh karena cap `max_jobs` tidak lagi memicu
     `degraded` pada run idempoten.
   - Cek deskripsi/field minimum hanya bila `detail_count >= CANARY_MIN_DETAILS` (3),
     menghindari false-positive saat run hanya mengambil sedikit detail.
3. **`app/scrapers/platforms/kitalulus.py`** — timeout `page.goto` dikonversi ke
   `TransientNetworkError` sehingga sub-run terisolasi (`degraded`), bukan
   `INTERNAL_ERROR`/`failed` total.

## Test
- `tests/scrapers/test_block_detection.py::test_retry_after_is_clamped`
- `tests/unit/test_canary.py::test_canary_tiny_sample_not_degraded`
- Suite offline hijau + `ruff` bersih.

## Yang TIDAK boleh dilakukan
- Menembus CAPTCHA/checkpoint. Menghapus test yang gagal.
