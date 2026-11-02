# Task 32 — Webhook callback end-to-end

- **Fase:** F6 **Prasyarat:** 10, 11 **Estimasi:** M
- **Referensi:** PRD FR-10, NFR-06; ARCHITECTURE §4.3, §7.1; DECISIONS D-008
- **Status:** `[~]` — SSRF + retry 3× ada; hanya validasi URL yang diuji

## Tujuan
Membuktikan callback benar-benar terkirim saat run selesai, dengan retry
2/5/10 detik, `callback_status` diperbarui, dan kegagalan callback tidak
mengubah status run.

## File yang perlu dibaca
- `app/runner/run_manager.py` (`validate_callback_url`, `_send_callback`,
  `CALLBACK_RETRY_DELAYS`)
- `app/services/scrape_service.py`
- `app/db/models/scrape_run.py` (`callback_status`)
- `app/db/repositories/run_repo.py` (`run_dict`)
- `tests/api/test_scrape_jobs.py`, `tests/conftest.py`
- ARCHITECTURE §4.3 · DECISIONS D-008

## File yang akan dibuat/diubah
- `tests/api/test_scrape_jobs.py` atau `tests/api/test_callback.py`
- `tests/conftest.py` hanya bila butuh server callback lokal
- `app/runner/run_manager.py` hanya bila test menemukan bug

## Langkah-langkah
1. Buat server HTTP lokal (stdlib `http.server` di thread) yang mencatat body
   dan mengembalikan status tertentu.
2. Set `CALLBACK_ALLOWED_HOSTS=127.0.0.1` (atau host server uji) agar SSRF
   allowlist mengizinkan target lokal; reset cache settings setelah test.
3. Jalankan run dengan `callback_url` menunjuk server; tunggu worker selesai.
4. Assert body ringkasan berisi `run_id`, `status`, `totals`, `platforms`.
5. Assert `callback_status="sent"` pada `scrape_runs`.
6. Simulasikan server mengembalikan 500 lalu 200; assert retry dan hasil akhir.
7. Simulasikan semua gagal; assert `callback_status="failed"` dan status run
   **tidak** berubah.
8. Pastikan `httpx` timeout memakai `CALLBACK_TIMEOUT_SEC`.

## Test yang harus ditulis
- `test_callback_sent_after_run`
- `test_callback_retries_on_5xx`
- `test_callback_failure_does_not_change_run_status`

## Kriteria selesai (checklist)
- [ ] Callback terkirim setelah run selesai.
- [ ] Retry 3× dengan jeda 2/5/10 (boleh di-mock agar cepat).
- [ ] `callback_status` `pending` → `sent`/`failed`.
- [ ] Kegagalan callback tidak mengubah status run.
- [ ] SSRF tetap menolak host privat tanpa allowlist.

## Cara verifikasi
```bash
uv run pytest tests/api -q -k callback
uv run pytest -q
```
Harapan: tiga test baru lulus; test lama tidak berubah.

## Yang TIDAK boleh dilakukan
- Mengirim callback ke host eksternal nyata.
- Melemahkan validasi SSRF.
- Mengubah status run karena callback gagal.
- Mencatat isi header sensitif.

## Catatan / risiko
- Retry nyata memakan 17 detik; gunakan `monkeypatch`/delay kecil di test
  tanpa mengubah konstanta produksi.
- `callback_allowed_hosts` dibaca dari settings cache; reset `get_settings.cache_clear()`.
