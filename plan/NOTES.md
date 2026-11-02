# NOTES — asumsi, konflik, penyimpangan

## Asumsi
- A-01 Prioritas dokumen: **PRD > DATABASE > ARCHITECTURE > SCRAPER_SPEC**.
- A-02 Nilai default PRD §14 dipakai (usia 14 hari, magang diterima, hybrid = aturan onsite,
  tanggal WIB, timestamp lain UTC).
- A-03 Selector/endpoint ber-tanda `[verifikasi]` di SCRAPER_SPEC tidak boleh di-hard-code
  tanpa discovery + `docs/platform_notes/<platform>.md`.
- A-04 n8n adalah penjadwal utama. `SCHEDULE_CRON` (FR-11, OPSIONAL) boleh ditunda.
- A-05 Test `-m live` manual; CI/default hanya offline. Fixture wajib bebas data pribadi.
- A-06 Satu container, satu worker uvicorn, satu run aktif. Antrean in-process boleh hilang
  saat restart karena run `queued` dipulihkan dari DB.

## Konflik antar dokumen
- K-01 ARCH §3 menyebut `app/api/deps.py`, `app/services/export_service.py`,
  `keyword_service.py`, `app/db/repositories/location_repo.py`,
  `app/db/models/location_alias.py`, `app/scrapers/common/jsonld.py`. Implementasi
  menggabungkan/menghilangkan file tersebut. **Rekomendasi:** perbarui ARCHITECTURE §3
  agar cocok; tidak perlu memecah kode.
- K-02 PRD FR-47 hanya menyebut `archived`; DATABASE §3.1 mengizinkan
  `active|expired|archived`. Kode menerima ketiganya. **Rekomendasi:** ikuti DATABASE
  untuk enum, perluas teks FR-47 saat revisi dokumen.
- K-03 ARCH §5.3 canary: 0 listing hanya `degraded` bila term historis pernah menghasilkan.
  Kode menandai `degraded` untuk semua `found_count == 0`. Kode lebih ketat.
  **Rekomendasi:** ikuti dokumen (butuh baseline historis) atau terima perilaku ketat dan
  catat di DECISIONS.
- K-04 DATABASE §3.2 `sumber_lain` (detail) = `[{sumber, url}]`. Kode mengembalikan
  `int` jumlah duplikat. **Rekomendasi:** ikuti dokumen; ubah `sibling_count` menjadi
  query daftar `(platform, url)` di `GET /jobs/{id}`.
- K-05 ARCH §7.2 `GET /jobs/export` menyebut `EXPORT_MAX_ROWS=50000`, tetapi tidak ada di
  blok `.env.example` asli. Sudah ditambahkan. **Rekomendasi:** pertahankan; selaraskan
  `.env.example` dengan ARCH.
- K-06 `callback_status` ada di DATABASE §4 dan kode; ARCH §4.3 tidak menyebut kolom.
  **Rekomendasi:** ikuti DATABASE.

## Penyimpangan kode vs spesifikasi

| ID | Spesifikasi | Kode saat ini | Rekomendasi |
|----|-------------|---------------|-------------|
| P-01 | ARCH §3: `app/api/deps.py` | Auth di `app/core/security.py`, dipasang di `app/main.py` | Perbarui dokumen |
| P-02 | ARCH §3: `export_service.py`, `keyword_service.py` | Ekspor di `app/services/job_service.py`; keyword di `app/services/platform_service.py` | Perbarui dokumen |
| P-03 | ARCH §3: `location_repo.py` + `models/location_alias.py` | `LocationAlias` di `app/db/models/keyword_rule.py`; lokasi dibaca dari YAML | Perbarui dokumen (D-003) |
| P-04 | ARCH §3: `scrapers/common/jsonld.py` | Belum ada; parsing per platform | Tambah hanya bila platform butuh JSON-LD |
| P-05 | DATABASE §5: `job_run_links(run_id, job_id, action)` | Ada kolom tambahan `created_at` | Perbarui DATABASE |
| P-06 | DATABASE §3.2: `sumber_lain` list objek | `int` jumlah saudara | Ikuti dokumen (lihat K-04) |
| P-07 | PRD §6: daftar field API | Ada field tambahan `deskripsi_terpotong` | Perbarui PRD/DATABASE mapping atau hapus dari API |
| P-08 | DATABASE §3.3: update selalu sentuh `last_seen_at`, `last_run_id`, `missed_runs` | Sesuai; `updated` hanya saat detail diambil ulang | Pertahankan (D-004), dokumentasikan di kontrak |
| P-09 | DATABASE §8.4: 14 kasus uji wajib | 10 test; kasus #9–#14 belum ada | Ikuti dokumen; tambah test |
| P-10 | ARCH §5.3 canary butuh baseline historis | Baseline belum disimpan; 0 hasil selalu `degraded` | Ikuti dokumen (lihat K-03) |
| P-11 | SCRAPER_SPEC §7.5 Dealls: tanggal aktivitas ≠ tanggal posting | Belum diimplementasikan | Wajib saat discovery Dealls |
| P-12 | SCRAPER_SPEC §7.3 Glints: paginasi penuh | Hanya halaman SSR pertama per term | Pertahankan + catat (D-012); jangan menembus Turnstile |
| P-13 | NFR-01/SCRAPER_SPEC §4.2: retry tenacity | `tenacity` terpasang; retry scraper belum terpusat | Ikuti dokumen pada task 31 |
| P-14 | DATABASE §10.2: `scripts/prune.py` | Belum ada | Ikuti dokumen pada task 33 |
| P-15 | ARCH §9.1: versi image = paket Playwright | Image `v1.64.1`, `uv.lock` 1.64.1 | Sesuai; verifikasi build pada task 04 |
| P-16 | FR-11: `SCHEDULE_CRON` | Config ada, tidak dijalankan | OPSIONAL; tunda, n8n penjadwal (D-010) |
| P-17 | NFR-03: snapshot debug saat parse gagal | `save_debug_snapshot` dipakai JobStreet; Glints belum | Ikuti dokumen pada task 31 |
| P-18 | SCRAPER_SPEC §7.4: urut terbaru & filter tanggal Kalibrr | API XHR mengabaikan `sort`; `sort=Freshness` hanya SSR halaman 1; tidak ada filter tanggal | Terapkan usia lokal; jangan kirim sort ke API (D-013) |

## Jebakan yang sudah terbukti
- `BrowserPool` memakai `channel="chromium"`; image wajib memuat Chromium penuh (D-011).
- Detail JobStreet hanya dari `window.SEEK_REDUX_DATA`; jangan andalkan endpoint detail JSON.
- Glints: lokasi sering hanya distrik + provinsi; `kota` boleh NULL meski provinsi valid.
- `expires_at` Glints dari `expiryDate/endDate`; JobStreet dari `job.expiresAt`.
- Jangan menganggap teks "Rekruter aktif N hari lalu" sebagai tanggal posting.
- Kalibrr: `offset` melewati `count` mengabaikan `text` dan mengembalikan feed umum; batasi loop dengan `count` halaman pertama.
- Kalibrr: deskripsi detail = `description` + `qualifications`; keduanya wajib digabung.
