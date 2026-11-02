# Task 33 — Backup, retensi, `scripts/prune.py`

- **Fase:** F6 **Prasyarat:** 02 **Estimasi:** S
- **Referensi:** DATABASE §10.2–§10.3, NFR-11
- **Status:** `[~]` — `scripts/backup_db.sh` ada tetapi belum dieksekusi;
  `scripts/prune.py` belum ada

## Tujuan
Membuktikan backup aman saat WAL aktif dan menyediakan skrip retensi sesuai
DATABASE §10.2.

## File yang perlu dibaca
- `scripts/backup_db.sh`
- `app/db/schema.py`, `app/db/models/job.py`, `app/db/models/scrape_run.py`
- DATABASE §5 (retensi `job_run_links`), §10.2, §10.3
- `README.md` bagian backup

## File yang akan dibuat/diubah
- `scripts/prune.py`
- `tests/unit/test_prune.py` atau self-check di skrip
- `scripts/backup_db.sh` hanya bila bug

## Langkah-langkah
1. Buat DB sementara + jalankan `alembic upgrade head`.
2. Jalankan `scripts/backup_db.sh` dengan `DATABASE_PATH` menunjuk DB sementara;
   verifikasi file backup dapat dibuka dan berisi tabel `jobs`.
3. Jalankan dua kali; pastikan hanya 7 salinan terakhir disimpan.
4. Tulis `scripts/prune.py` (stdlib `sqlite3` + `argparse`):
   - hapus `job_run_links` untuk run `created_at` > 90 hari;
   - hapus `jobs` `status='expired'` dengan `effective_date` > 180 hari;
   - opsi `--include-archived` juga menghapus `archived`;
   - `VACUUM` setelah penghapusan besar.
5. Gunakan transaksi dan `PRAGMA foreign_keys=ON`; `--dry-run` untuk hitung baris.
6. Tambah test kecil dengan DB sementara: data tua terhapus, data baru tetap,
   link run >90 hari terhapus.
7. Perbarui README bila perintah berubah.

## Test yang harus ditulis
- `test_backup_script_creates_openable_db` (bila memungkinkan di pytest).
- `test_prune_removes_old_links_and_expired_jobs`
- `test_prune_keeps_recent_jobs`
- `test_prune_dry_run_deletes_nothing`

## Kriteria selesai (checklist)
- [ ] Backup dibuat dengan `.backup` dan dapat dibuka.
- [ ] Maksimal 7 salinan tersimpan.
- [ ] Prune menghapus sesuai ambang 90/180 hari.
- [ ] `--include-archived` bekerja.
- [ ] `VACUUM` dijalankan setelah penghapusan.
- [ ] Test offline hijau.

## Cara verifikasi
```bash
DATABASE_PATH=/tmp/jobs_test.db ./scripts/backup_db.sh
uv run python scripts/prune.py --db /tmp/jobs_test.db --dry-run
uv run pytest tests/unit/test_prune.py -q
```
Harapan: backup terbuka, dry-run tidak mengubah data, test lulus.

## Yang TIDAK boleh dilakukan
- Menghapus data tanpa opsi eksplisit.
- Menjalankan `VACUUM` di dalam transaksi aktif.
- Menyentuh `data/jobs.db` produksi saat test.
- Mengubah skema.

## Catatan / risiko
- SQLite `VACUUM` butuh koneksi di luar transaksi.
- Backup WAL harus memakai `.backup`, bukan `cp`.
