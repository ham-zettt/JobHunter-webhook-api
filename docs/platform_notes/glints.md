# Glints — catatan discovery & implementasi

Tanggal: 2026-11-02 · Status: **implemented (F3)** · Dokumen acuan: SCRAPER_SPEC §3, §7

## Ringkasan metode

Tanpa login, tanpa browser:

1. **Daftar** — halaman eksplor di-SSR oleh Next.js:
   `GET https://glints.com/id/opportunities/jobs/explore?keyword=<term>&country=ID`
   Data lowongan ada di `#__NEXT_DATA__` → `props.pageProps.initialJobs.jobsInPage`
   (30 lowongan per halaman pertama). `httpx` menerima HTML penuh (200).
2. **Detail** — `GET /id/opportunities/jobs/<slug>/<uuid>`, slug bebas (server 301 ke
   slug kanonik). Data di `#__NEXT_DATA__` → `props.pageProps.initialData.data`.

GraphQL (`/api/graphql`, `/api/v2/graphql`) ada, tetapi `searchJobsV3` pada v2
mengabaikan `SearchTerm` untuk request tanpa sesi (mengembalikan feed default non-IT),
dan `/api/graphql` tidak mengekspos `searchJobsV3`. Introspection dimatikan.

## Keterbatasan paginasi (penting)

- `?page=2` di-SSR **tanpa** `initialJobs`; daftar lowongan page 2 hanya dimuat oleh
  JavaScript klien.
- Browser Chromium penuh pun ditantang Cloudflare Turnstile pada halaman eksplor;
  challenge tidak ditembus.
- Mitigasi sesuai SCRAPER_SPEC §1: **banyak `search_term`** (default 10, masing-masing
  30 lowongan) sehingga cakupan per run tetap besar. `max_pages_per_term` disimpan di
  config tetapi efektif 1 untuk Glints; dicatat di sini agar tidak menyesatkan.

## Pemetaan field

| Sumber | Field API | Catatan |
|--------|-----------|---------|
| `job.id` (UUID) | `external_id`, URL detail | |
| `job.title` | `posisi` | slug URL dibuat dari judul |
| `job.company.name` / `displayName` | `perusahaan` | detail memakai `displayName` |
| `job.location` (hierarki) | `lokasi` | `formattedName` + Kab/Kota + Provinsi + Indonesia |
| `job.createdAt` | `tanggal_masuk` | **bukan** `updatedAt`; ISO UTC presisi `exact` |
| `job.expiryDate` / `endDate` | `expires_at` | detail |
| `job.salaries[]` | `gaji` | hanya bila `shouldShowSalary`; `MIN/MAX`, `CurrencyCode`, `salaryMode` |
| `job.workArrangementOption` | `sistem_kerja` | `ONSITE/HYBRID/REMOTE` |
| `job.type` | `tipe_kerja` | `FULL_TIME/PART_TIME/CONTRACT/PROJECT_BASED/INTERNSHIP` |
| `descriptionJsonString` (Draft.js) | `deskripsi` | blocks → teks + HTML; tidak terpotong |
| `JobSkills`, `hierarchicalJobCategory`, `benefits` | `extra` | v1.0 tidak masuk kolom khusus |

Mode gaji `PROJECT` (mis. `IDR 1.000.000 - 2.000.000 per project`) menghasilkan
`salary_period = NULL` (enum DB tidak punya `project`); parser gaji tidak lagi
memaksa default `month` untuk teks "per project".

## Anti-bot

- HTML SSR diakses normal via HTTP (200) pada saat discovery.
- Halaman eksplor di Chromium memicu Turnstile; scraper tidak memakai browser.
- Respons 403/999, header `cf-mitigated`, atau marker tantangan → `BlockedError`
  (tanpa retry, tanpa bypass). 429 → tunggu lalu ulang maks 2.
- Retry jaringan 3× (2/4/8 dtk).

## Batas kesopanan

`config/platforms.yaml`: konkurensi 2, jeda acak 1,5–4 dtk (dipakai penuh antar-detail,
dibagi 4 antar-kartu dalam satu halaman), maks 6 halaman/term (efektif 1), maks 300
detail/run, maks 25 menit.

## Fixture

`tests/fixtures/glints/`:
- `search_software_engineer.html` — SSR 30 lowongan.
- `search_page2.html` — bukti page 2 tidak membawa `initialJobs`.
- `detail_c1a83f29.html` (onsite, bergaji), `detail_b78541fb.html` (remote),
  `detail_8fd4f744.html` (internship/hybrid), `detail_66c8002a.html` (kontrak, tanpa gaji),
  `detail_812c9d0b.html` (gaji project), `detail_4de455c8.html`.

Parser diuji tanpa jaringan: `tests/scrapers/test_glints.py`.
Smoke live manual: `uv run pytest -m live`.

## Risiko

- Struktur `__NEXT_DATA__` dapat berubah; ketiadaan `initialJobs`/`initialData` →
  `SiteChangedError` → sub-run `degraded`.
- `location` sering hanya distrik + provinsi (mis. "Setiabudi, DKI Jakarta"); kota bisa
  `NULL` meski provinsi valid dan lolos BR-02.
- Turnstile dapat diperketat kapan saja; bila halaman SSR mulai ditantang, platform akan
  berstatus `blocked`.
