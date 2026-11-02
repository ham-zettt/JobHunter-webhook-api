# Task 08 — Deduper L1–L3 + matriks 14 kasus

- **Fase:** F1 **Prasyarat:** 02 **Estimasi:** M
- **Referensi:** DATABASE §8.1–§8.4, PRD BR-05, BR-06, FR-30–FR-33
- **Status:** `[~]` — implementasi & 10 test ada; kasus §8.4 #9–#14 belum

## Tujuan
Melengkapi matriks kasus uji wajib DATABASE §8.4 sehingga semua aturan
duplikat/repost/berbeda terkunci oleh test.

## File yang perlu dibaca
- `app/pipeline/deduper.py` (fungsi `Deduper`, `compute_fingerprint`, helper similarity)
- `app/pipeline/normalizer.py` (`NormalizedJob`, `normalize_company`, `title_normalized`)
- `tests/unit/test_deduper.py`
- DATABASE §8.1–§8.4 · PRD BR-05/BR-06

## File yang akan dibuat/diubah
- `tests/unit/test_deduper.py` (tambah kasus)
- `app/pipeline/deduper.py` hanya bila test mengungkap bug.

## Langkah-langkah
1. Tambah test **#9**: `employment_type` `fulltime` vs `internship`, judul &
   perusahaan sama → `action="new"`.
2. Tambah test **#10**: salah satu `company_normalized` kosong, judul sama persis,
   `desc_sim ≥ 0.90`, lokasi identik → duplikat mode ketat.
3. Tambah test **#11**: mode ketat yang sama tetapi `desc_sim ≈ 0.82` → `new`.
4. Tambah test **#12**: `company_name="PT Maju Jaya Tbk"` vs `"Maju Jaya"`,
   `company_normalized` keduanya `maju jaya` → perusahaan dianggap sama.
5. Tambah test **#13**: `work_mode` `remote` vs `onsite`, judul & perusahaan sama
   → `new` (lokasi tidak kompatibel).
6. Tambah test **#14**: kandidat B sudah `duplicate_of_id=A`; C cocok dengan B →
   `C.duplicate_of_id == A.id` (tanpa rantai).
7. Bila kode gagal, perbaiki minimal di `deduper.py` tanpa mengubah ambang §8.3.

## Test yang harus ditulis
`tests/unit/test_deduper.py`: enam test baru, nama memakai nomor kasus §8.4.
Gunakan pola `job()`/`candidate()` yang sudah ada.

## Kriteria selesai (checklist)
- [ ] Kasus #1–#14 DATABASE §8.4 masing-masing punya test.
- [ ] `candidate(duplicate_of_id=...)` diuji untuk resolusi kanonik.
- [ ] Semua test dedup lulus.
- [ ] Tidak ada perubahan ambang (`title_sim`, `desc_sim`, `posted_at`).

## Cara verifikasi
```bash
uv run pytest tests/unit/test_deduper.py -q
uv run pytest -q
```
Harapan: semua test lulus; jumlah test dedup = 16.

## Yang TIDAK boleh dilakukan
- Mengubah ambang atau aturan BR-06 agar test lulus.
- Menghapus test lama.
- Menyentuh scraper/API.

## Catatan / risiko
- `rapidfuzz` dipakai untuk similarity; jaga fixture deskripsi cukup panjang
  agar skor stabil dan tidak flaky.
