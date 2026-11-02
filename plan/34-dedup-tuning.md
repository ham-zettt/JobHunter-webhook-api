# Task 34 — Tuning dedup + reclassify (OPSIONAL)

- **Fase:** F6 **Prasyarat:** 08 **Estimasi:** M
- **Referensi:** PRD §1.2 G4, BR-05/BR-06; ARCHITECTURE §7.4; DATABASE §8
- **Status:** `[ ]` — OPSIONAL, ditunda sampai data nyata cukup

## Tujuan
Menyesuaikan ambang dedup berdasarkan sampel nyata dan menyediakan
`POST /jobs/reclassify` (OPSIONAL) untuk menghitung ulang skor/kategori.

## File yang perlu dibaca
- `app/pipeline/deduper.py`, `app/pipeline/classifier.py`
- `app/db/repositories/job_repo.py`
- `app/api/routers/jobs.py`, `app/services/job_service.py`
- `tests/unit/test_deduper.py`, `tests/unit/test_classifier.py`
- PRD BR-05/BR-06 · DATABASE §8.3 · ARCHITECTURE §7.4

## File yang akan dibuat/diubah
- `app/pipeline/deduper.py` (hanya bila tuning disetujui)
- `app/api/routers/jobs.py` + `app/services/job_service.py` (reclassify)
- `tests/unit/test_deduper.py`, `tests/api/test_scrape_jobs.py`
- `plan/PROGRESS.md` (keputusan: implementasi atau defer)

## Langkah-langkah
1. Ambil sampel ≥100 lowongan kanonik dari DB nyata; ukur duplikat lolos
   (target G4 <3%) dan duplikat palsu.
2. Bila perlu tuning, ubah **hanya** ambang di satu konstanta; jangan mengubah
   urutan aturan BR-05/BR-06.
3. Dokumentasikan alasan tuning di `docs/DECISIONS.md`.
4. Implementasikan `POST /api/v1/jobs/reclassify` (OPSIONAL): hitung ulang
   `role_category`, `matched_keywords`, `relevance_score` dari aturan aktif.
5. Batasi batch; laporkan jumlah diperbarui/ditolak.
6. Tambah test classifier ulang untuk perubahan aturan.
7. Bila tidak dikerjakan, tandai `[x]` dengan catatan "ditunda atas keputusan
   pemilik" di PROGRESS — jangan biarkan menggantung tanpa keputusan.

## Test yang harus ditulis
- Tuning: matriks 14 kasus tetap lulus.
- Reclassify: skor berubah setelah aturan diubah; endpoint butuh API key.
- Reclassify idempoten pada aturan yang sama.

## Kriteria selesai (checklist)
- [ ] Ada keputusan eksplisit: implementasi atau defer.
- [ ] Bila tuning: bukti sampel + alasan di DECISIONS.
- [ ] Bila reclassify: endpoint + test + batas batch.
- [ ] Matriks dedup §8.4 tetap hijau.

## Cara verifikasi
```bash
uv run pytest tests/unit/test_deduper.py tests/unit/test_classifier.py -q
uv run pytest -q
```
Harapan: semua lulus; tidak ada regresi BR-06.

## Yang TIDAK boleh dilakukan
- Melonggarkan ambang tanpa data pendukung.
- Menghapus baris duplikat.
- Menukar kanonik otomatis (dilarang DATABASE §8.3).
- Menambah dependency baru.

## Catatan / risiko
- Tanpa data nyata yang cukup, tuning berisiko; lebih baik defer.
- Reclassify massal bisa lama; batasi dan jalankan di background bila perlu.
