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
| P-11 | SCRAPER_SPEC §7.5 Dealls: tanggal aktivitas ≠ tanggal posting | Tuntas (task 24): `posted_raw` hanya `publishedAt`; `lastActivelyHiringAt` diabaikan | Pertahankan |
| P-12 | SCRAPER_SPEC §7.3 Glints: paginasi penuh | Hanya halaman SSR pertama per term | Pertahankan + catat (D-012); jangan menembus Turnstile |
| P-13 | NFR-01/SCRAPER_SPEC §4.2: retry tenacity | `tenacity` terpasang; retry scraper belum terpusat | Ikuti dokumen pada task 31 |
| P-14 | DATABASE §10.2: `scripts/prune.py` | Belum ada | Ikuti dokumen pada task 33 |
| P-15 | ARCH §9.1: versi image = paket Playwright | Image `v1.64.1`, `uv.lock` 1.64.1 | Sesuai; verifikasi build pada task 04 |
| P-16 | FR-11: `SCHEDULE_CRON` | Config ada, tidak dijalankan | OPSIONAL; tunda, n8n penjadwal (D-010) |
| P-17 | NFR-03: snapshot debug saat parse gagal | `save_debug_snapshot` dipakai JobStreet; Glints belum | Ikuti dokumen pada task 31 |
| P-18 | SCRAPER_SPEC §7.4: urut terbaru & filter tanggal Kalibrr | API XHR mengabaikan `sort`; `sort=Freshness` hanya SSR halaman 1; tidak ada filter tanggal | Terapkan usia lokal; jangan kirim sort ke API (D-013) |
| P-19 | FR-06: henti-dini berdasarkan usia | Kalibrr XHR tidak menjamin urutan terbaru; usia hanya pre-filter | Jangan ubah orchestrator; batasi halaman + guard `count` (D-014) |
| P-20 | Task 24 langkah 4: fallback Playwright untuk detail Dealls | Fallback memakai SSR HTTP (`httpx`) + `__NEXT_DATA__`/JSON-LD, tanpa browser (headless ditantang Cloudflare, D-015) | Pertahankan; jangan pakai browser |

## Jebakan yang sudah terbukti
- `BrowserPool` memakai `channel="chromium"`; image wajib memuat Chromium penuh (D-011).
- Detail JobStreet hanya dari `window.SEEK_REDUX_DATA`; jangan andalkan endpoint detail JSON.
- Glints: lokasi sering hanya distrik + provinsi; `kota` boleh NULL meski provinsi valid.
- `expires_at` Glints dari `expiryDate/endDate`; JobStreet dari `job.expiresAt`.
- Jangan menganggap teks "Rekruter aktif N hari lalu" sebagai tanggal posting.
- Kalibrr: `offset` melewati `count` mengabaikan `text` dan mengembalikan feed umum; batasi loop dengan `count` halaman pertama.
- Kalibrr: deskripsi detail = `description` + `qualifications`; keduanya wajib digabung.
- P-11 tuntas (task 23): Dealls punya tanggal posting sah `publishedAt` (listing + detail API); `lastActivelyHiringAt` = label "Rekruter aktif N j lalu", DILARANG dipakai sebagai `posted_at` (beda 4 hari pada sampel).
- Dealls: browser headless ditantang Cloudflare (403); HTTP polos 200 — scraper harus HTTP-first tanpa browser (D-015).
- Dealls: URL detail wajib memuat sufiks `~<company-slug>`; tanpa itu → 302 ke `sh.dealls.com` → 403.

## P-21 — KitaLulus (task 25)
- Pagination client-side: tombol "Lebih Banyak", +30 item/klik; `?page=N` DIABAIKAN server. Playwright hanya untuk klik, ekstraksi dari SSR HTML (`vacancyList.list`).
- Tanggal posting hanya ada di detail JSON-LD `datePosted`; listing hanya `updatedAtStr` ("Terakhir diperbarui") — jangan dipakai sebagai `posted_at` final.
- GraphQL `gql.kitalulus.com/graphql` memakai persisted query hash yang bisa berubah; bukan jalur utama.
- `salaryLowerBound/UpperBound = 0/0` berarti negosiasi, bukan gaji 0.

## P-26 — Scraper KitaLulus (task 26)

- Parsing daftar memakai DOM (`a[href^="/lowongan/detail/"]`, `h3`, `p[title]`)
  sebagai jalur utama, bukan flight `vacancyList`: setelah "Lebih Banyak" DOM
  berisi 40 item unik sedangkan flight tetap 30 (stale). Flight hanya fallback.
- Dedupe per `slug` di dalam parser; fixture `search_developer_page2.html`
  (42 kartu) menghasilkan 40 `RawListing`.
- `posted_raw` daftar sengaja `None`; `updatedAtStr` hanya perkiraan aktivitas
  dan disimpan di `extra.updated_at_str`. Tanggal posting final dari JSON-LD
  `datePosted` di detail (presisi `exact`).
- Detail menggabungkan JSON-LD `JobPosting` (deskripsi/tanggal/gaji) dengan
  objek flight `vacancy` (`skillTags`, `benefits`, `locationSiteStr`, `typeStr`,
  `jobRole`). `typeStr` diprioritaskan untuk tipe kerja agar "Freelance" tidak
  menjadi "contract" dari `employmentType=CONTRACTOR`.
- Pendidikan/benefit/skill/pengalaman masuk `extra`; gaji 0/0 → `None`.

## P-27 — Discovery LinkedIn belum dieksekusi

`scripts/linkedin_login.py` kini membuka `/jobs/` setelah login manual dan menolak
menyimpan state bila URL akhir masih `/login`, `/checkpoint`, `/authwall`, `/uas/`,
atau `/signup`; state ditulis atomik (`tmp` → `0600` → `replace`).
`docs/platform_notes/linkedin.md` dibuat, tetapi seluruh selector/parameter tetap
`[verifikasi]` dan `tests/fixtures/linkedin/` kosong: eksekusi login headed + akun
khusus harus dilakukan pemilik di mesin lokal. Task 27 tetap `[~]` sampai itu selesai.

## P-28 — Discovery Pintarnya

Pintarnya publik tanpa login: daftar lewat XHR `api.pintarnya.com/api/v2/pk/job`
dan detail lewat JSON-LD `JobPosting` di `/lowongan/<slug>`. API menolak HTTP polos
(403 Cloudflare) tetapi berhasil di konteks browser; tanpa stealth/CAPTCHA.
Paginasi = infinite scroll container internal; `page`/`p` di URL diabaikan.
`published_at` daftar dan `datePosted` detail presisi exact. Kategori IT
(`job_category=17`) = 117 lowongan; keyword pendek seperti `it` terlalu longgar.
Fixture: 3 daftar + 5 detail di `tests/fixtures/pintarnya/`.

## Task 30 — Pintarnya (2026-11-02)

- Discovery menyatakan lowongan publik → scraper normal, bukan stub `skipped`.
- `app/scrapers/platforms/pintarnya.py`: daftar via `api.pintarnya.com/api/v2/pk/job`
  memakai `BrowserContext.request` (cookies sesi; HTTP polos 403), fallback SSR
  `initialJobList` saat API 410, dedupe slug, detail dari JSON-LD `JobPosting`
  + `__NEXT_DATA__.jobData.page_header`.
- Tantangan: `detect_challenge` dijalankan pada HTML tanpa `<script>`/`<style>`
  agar string `recaptcha` di CSP/script tidak salah dianggap challenge.
- Test: `tests/scrapers/test_pintarnya.py` (21 test, fixture 3 daftar + 5 detail).
- Catatan: retry 429/5xx hanya menghasilkan `TransientNetworkError` (orchestrator
  menandai degraded); belum ada retry tenacity.

## P-27 (lanjutan) — Discovery LinkedIn selesai

Sesi login headed berhasil; state `600`, `auth_state=valid`. Discovery membuktikan:
UI baru SDUI dua panel, kelas CSS acak, selector stabil hanya
`componentkey^="job-card-component-ref-"`, `data-testid="expandable-text-box"`/
`expandable-text-button`, href, dan teks. Path `/jobs/search/` mengabaikan
`location=Indonesia` (jatuh ke lokasi profil); `/jobs/search-results/` menghormatinya.
`f_TPR=r604800` (chip `1 minggu terakhir`) dan `f_WT=2` (chip `Jarak jauh`) terbukti.
`sortBy` dan `start` belum terbukti. Fixture (`3 daftar + 5 detail`) dibersihkan dari
script, token, nama akun, kartu orang/rekruter, email, dan telepon.

## P-28 — Scraper LinkedIn (2026-11-03)

- `check_session()` menolak state hilang/redirect login/checkpoint via `AuthRequiredError`;
  CAPTCHA/999/429 → `BlockedError` tanpa retry. Detail memakai `/jobs/view/<id>/`.
- Deskripsi diambil dari section heading `Tentang pekerjaan ini`/`About the job`
  (bukan seluruh `expandable-text-box`, karena sebagian kotak milik "Tentang perusahaan"
  dan carousel feed). §5.6 diterapkan lewat klik `expandable-text-button` + tunggu stabil.
- Batas: `max_jobs=min(ctx.max_jobs, LINKEDIN_MAX_JOBS_PER_RUN)`, paginasi `start` kelipatan 25,
  `f_WT=2` hanya untuk 3 term pertama. Cap harian dihitung di orchestrator dari
  `scrape_run_sources.detail_fetched` hari WIB (scraper tidak menyentuh DB); cap habis → `skipped`.
- Registry mengubah `PLATFORM_ORDER`: LinkedIn paling akhir.
- Perbaikan lintas modul: `detect_challenge` memakai word boundary agar teks
  "Pekerjaan terverifikasi" tidak dianggap tantangan; `parse_salary` mendukung `Rp6M/month`.
- Kurang: smoke `live` (dilarang pada sesi ini); parameter `sortBy`/`start` tetap
  belum diverifikasi discovery, hanya diuji lewat unit test URL.

## Task 16 — Uji filter max_age_days (2026-11-03)

- `GET /jobs?max_age_days` (FR-22) hanya memvalidasi batas bawah `ge=1` (`app/api/routers/jobs.py:23`).
  Batas atas `1..MAX_AGE_DAYS_LIMIT` (90) hanya diterapkan pada body `POST /scrape`
  (`app/services/scrape_service.py:36-40`). Test mengunci `max_age_days=0 -> 422`; batas atas
  GET tidak diuji karena belum ada. Bila PRD mensyaratkan 422 di GET juga, tambahkan
  `le=settings.max_age_days_limit` pada Query (1 baris, ubah `app/`).
- Data uji `test_jobs_max_age_filter`: `seed_sample()` + scrape, lalu `effective_date` satu job
  digeser ke 10 hari lalu via `SessionLocal`; `GET /jobs` tanpa param membuktikan default tak memfilter.
- Henti-dini (FR-06): run berstatus `partial` (bukan `completed`) karena `found_count>0` tetapi
  `detail_count==0` -> source `degraded` (`orchestrator.py:248`). Test memakai totals, bukan status.
