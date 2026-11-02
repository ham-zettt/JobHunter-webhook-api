# JobStreet — catatan discovery & implementasi

Tanggal: 2026-11-02 · Status: **implemented (F3)** · Dokumen acuan: SCRAPER_SPEC §3, §7

## Ringkasan metode

Dua jalur, keduanya tanpa login:

1. **Daftar lowongan** — JSON API internal yang sama dengan yang dipakai situs:
   `GET https://id.jobstreet.com/api/jobsearch/v5/search`
   Diakses lewat `httpx` (bukan browser). Terbukti `200 application/json` tanpa cookie.
2. **Detail lowongan** — halaman `/id/job/<id>` dibuka dengan Playwright (Chromium penuh).
   Data terstruktur dibaca dari `script[data-automation="server-state"]` →
   `window.SEEK_REDUX_DATA` → `jobdetails.result.job`, dengan fallback DOM
   `[data-automation="jobAdDetails"]` dan field `job-detail-*`.

Endpoint detail JSON yang umum diduga (`/api/jobad/v1/job/<id>`,
`/api/jobsearch/v5/job/<id>`) mengembalikan 404. GraphQL introspection dimatikan.
Embedded Redux state adalah sumber detail paling lengkap dan stabil yang ditemukan.

## Parameter pencarian yang dipakai

| Param | Nilai | Catatan |
|-------|-------|---------|
| `siteKey` | `ID` | wajib |
| `sourcesystem` | `houston` | wajib |
| `keywords` | search term | di-encode otomatis oleh httpx |
| `page` | 1..N | 20 hasil/halaman |
| `daterange` | `max_age_days` | filter usia sisi platform |
| `sortmode` | `ListedDate` | terbaru dulu; terbukti menurun |

Pagination berhenti bila `data` kosong, hasil < 20, batas `max_pages_per_term`
(default 8), `max_jobs`, atau dihentikan orchestrator (usia/kursor).

## Pemetaan field

| Sumber | Field API | Catatan |
|--------|-----------|---------|
| `data[].id` | `external_id`, URL `/id/job/<id>` | |
| `data[].title` | `posisi` | |
| `data[].companyName` / `advertiser.description` | `perusahaan` | detail memakai `job.advertiser.name` |
| `data[].locations[0].label` | `lokasi` | label kota Inggris; alias lokasi menanganinya |
| `data[].listingDate` | `tanggal_masuk` | ISO UTC, presisi `exact` |
| `data[].salaryLabel` | `gaji` | fallback bila detail `job.salary` null |
| `data[].workArrangements.data[0].label.text` | `sistem_kerja` | On-site/Hibrid/Remote |
| `data[].workTypes[]` | `tipe_kerja` | Full time/Contract/Temp/Part time |
| `job.content2` | `deskripsi` | HTML lengkap, tidak terpotong |
| `job.listedAt.dateTimeUtc` | `tanggal_masuk` | presisi lebih tinggi dari label relatif |
| `job.expiresAt.dateTimeUtc` | `expires_at` | |
| `result.workArrangements.label` | `sistem_kerja` | detail; kosong untuk onsite → fallback listing |
| `job.workTypes.label` | `tipe_kerja` | mis. "Kontrak/Temporer" → `contract` |

Deskripsi tidak memerlukan klik "See more" pada sampel (5 detail). `content2`
berisi HTML penuh; konversi teks memakai `app/scrapers/common/text.html_to_text`.

## Anti-bot / akses

- `curl` ke halaman HTML → **403 Cloudflare challenge**; API JSON tetap `200`.
- Playwright **headless-shell default** → challenge "Tunggu sebentar...".
- Playwright **Chromium penuh** (`channel="chromium"`, new headless) → halaman detail
  normal. Ini alasan `BrowserPool` memakai channel tersebut.
- Tidak ada stealth plugin, tidak ada upaya menembus CAPTCHA. Tantangan terdeteksi →
  `BlockedError`, snapshot disimpan, platform dihentikan.

## Batas kesopanan yang dipakai

Dari `config/platforms.yaml`: konkurensi 2, jeda acak 1,5–4 dtk antar navigasi/API,
maks 8 halaman/term, maks 300 detail/run, maks 25 menit. Retry: jaringan 3× (2/4/8 dtk),
429 tunggu lalu ulang (maks 2), 403/999 langsung `BlockedError`.

## Fixture

`tests/fixtures/jobstreet/`:
- `search_page1.json`, `search_backend.json`, `search_ai.json` — respons API asli.
- `detail_95140055.html` (onsite, gaji), `detail_95366834.html` (hybrid),
  `detail_95226394.html` (kontrak/hybrid), `detail_95542339.html`
  (intern, tanpa gaji), `detail_95525906.html`, `detail_95515141.html`.

Parser diuji tanpa jaringan: `tests/scrapers/test_jobstreet.py`.
Smoke live manual: `uv run pytest -m live`.

## Risiko / catatan

- Struktur `SEEK_REDUX_DATA` dapat berubah; parser fallback DOM menjaga canary.
- `job.location.label` lebih kasar dari label listing; listing diprioritaskan.
- `workArrangements` kosong pada detail onsite; label listing dipakai.
- `salary` sering null meski listing punya `salaryLabel`; fallback listing.
- Tanggal relatif ("Diposting 24 hari yang lalu") hanya fallback; ISO dari API/Redux
  diprioritaskan.
