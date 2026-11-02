# Task 35 — README final + contoh workflow n8n

- **Fase:** F6 **Prasyarat:** 17–30 **Estimasi:** S
- **Referensi:** NFR-10, PRD §10, §11; ARCHITECTURE §9.3
- **Status:** `[~]` — README ada; workflow n8n impor, risiko LinkedIn final,
  dan status platform terbaru belum

## Tujuan
README menjadi satu-satunya panduan operasional: menjalankan, login LinkedIn,
alur n8n impor, endpoint, batas, dan status platform.

## File yang perlu dibaca
- `README.md`
- `.env.example`, `docker-compose.yml`
- `docs/platform_notes/*.md`
- PRD §10 · ARCHITECTURE §7 · NFR-10

## File yang akan dibuat/diubah
- `README.md`
- `docs/n8n_workflow.json`
- `docs/platform_notes/*.md` hanya bila ada koreksi

## Langkah-langkah
1. Perbarui status implementasi platform (P1–P3) sesuai PROGRESS.
2. Pastikan perintah lokal, Docker, test, lint, backup, dan `scripts/codemap.py`
   tercantum dan benar.
3. Tulis ulang alur n8n PRD §10 dengan nama node + HTTP method/path + body.
4. Buat `docs/n8n_workflow.json` yang dapat diimpor: Schedule Trigger →
   POST `/scrape/all` → Wait → GET status → IF → GET jobs baru → Split In Batches.
5. Tambahkan peringatan risiko LinkedIn: akun cadangan, batas run/hari,
   `auth_required`, jangan commit state.
6. Tambahkan tabel endpoint + kode error + contoh `X-API-Key`.
7. Pastikan tidak ada rahasia/contoh API key nyata.

## Test yang harus ditulis
Tidak ada test kode. Validasi manual: JSON workflow dapat diimpor, perintah
README dijalankan ulang.

## Kriteria selesai (checklist)
- [ ] README menyebut semua perintah penting (run, test, lint, backup, codemap).
- [ ] Alur n8n §10 lengkap dan cocok dengan endpoint nyata.
- [ ] `docs/n8n_workflow.json` valid dan dapat diimpor.
- [ ] Prosedur login LinkedIn + risiko ada.
- [ ] Status platform akurat.
- [ ] Tidak ada rahasia di dokumentasi.

## Cara verifikasi
```bash
python -m json.tool docs/n8n_workflow.json >/dev/null
uv run pytest -q
uv run ruff check app tests
```
Harapan: JSON valid, test/lint hijau, langkah README tidak error.

## Yang TIDAK boleh dilakukan
- Menulis API key/sesi nyata di README.
- Menjanjikan platform yang belum diimplementasikan.
- Mengubah kontrak API diam-diam.
- Menyalin seluruh dokumen spesifikasi ke README.

## Catatan / risiko
- Workflow n8n bergantung pada URL host; gunakan placeholder/env.
- Callback butuh `CALLBACK_ALLOWED_HOSTS` bila n8n di Docker.
