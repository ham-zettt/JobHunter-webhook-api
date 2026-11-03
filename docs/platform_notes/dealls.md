# Dealls — catatan discovery (2026-11-02)

Dokumen acuan: SCRAPER_SPEC §3, §7.5 · Status: **implemented (task 24)** · Parser: `app/scrapers/platforms/dealls.py`.

## Metode terpilih

**API langsung (HTTP-first), tanpa login, tanpa browser.** Alasan: seluruh data
lowongan tersedia lewat API publik situs (`api.sejutacita.id`) yang merespons
`200 application/json` tanpa cookie/header khusus, dan halaman detail punya
JSON-LD `datePosted`. Sebaliknya Playwright headless langsung ditantang
Cloudflare (403) pada halaman daftar, sedangkan `curl`/HTTP polos tidak —
sama seperti pola Glints (lihat anti-bot di bawah).

Base API ditemukan dari bundle JS (`/_app-*.js`): `https://api.sejutacita.id`
(konsisten dengan CDN logo `cdn.sejutacita.id`).

## Endpoint final

| Tujuan | Endpoint | Keterangan |
|--------|----------|------------|
| Daftar | `GET https://api.sejutacita.id/v1/explore-job/job?page=1&limit=18&search=<term>&sortParam=publishedAt&sortBy=desc` | tanpa cookie, 200 |
| Detail | `GET https://api.sejutacita.id/v1/job-portal/job/slug/<slug>` | 200; payload di `data.result` |
| Detail (fallback SSR) | `GET https://dealls.com/loker/<slug>~<company-slug>` | server-rendered; JSON-LD `JobPosting` + `__NEXT_DATA__` |

Perhatian: URL detail **tanpa** sufiks `~<company-slug>` (mis. `/loker/<slug>`
saja) → 302 ke `sh.dealls.com` → **403**. Selalu pakai slug penuh
`<slug>~<company-slug>`.

## URL pencarian & parameter

- URL UI: `https://dealls.com/loker?search=<term>` (SSR membawa query ke
  `queryKey` react-query; hasil konsisten dengan API — `akuntan` 0 hasil di
  keduanya).
- Parameter API daftar (dari `queryKey` SSR):
  `search`, `page`, `limit` (SSR memakai 18), `sortParam`, `sortBy`,
  `workplaceTypes`, `employmentTypes`, `cityIds`, `sectors`, `categoryIds`,
  `companyIds`, `benefits`, `lastEducations`, `status=active`, `published=true`.
- **Urut terbaru:** `sortParam=publishedAt&sortBy=desc` — terverifikasi
  (urutan `publishedAt` menurun). Nilai `sortParam` lain dari bundle JS:
  `mostRelevant` (default), `mostActivelyHiring`, `highestSalary`.
  Nilai tak dikenal → 400.
- **Filter tanggal:** tidak ada parameter rentang tanggal; pre-filter usia
  dilakukan pipeline (`posted_raw` ISO tersedia per item).

## Pagination ("Lihat Lebih Banyak")

Daftar SSR hanya membawa halaman 1 (`pageParams=[1]`, `limit=18`). Tombol
**"Lihat Lebih Banyak"** memicu `fetchNextPage` (react-query useInfiniteQuery,
dikonfirmasi di bundle JS) → panggilan API yang sama dengan `page=N+1`.
Respons berisi `totalDocs`, `totalPages`, `page` → berhenti bila
`page > totalPages` atau `docs` kosong. Maks halaman dibatasi
`max_pages_per_term` di config (6).

## Sumber tanggal posting

- **Sah:** `publishedAt` (ISO UTC, presisi `exact`) — ada di listing maupun
  detail (`data.result.publishedAt`).
- **DILARANG dipakai:** `lastActivelyHiringAt` → label UI
  `Rekruter aktif N j lalu` / `Actively hiring`. Pada sampel, `publishedAt`
  2026-10-29 vs `lastActivelyHiringAt` 2026-11-02 (4 hari beda) — jelas bukan
  tanggal posting.
- JSON-LD `datePosted` pada SSR detail hanya presisi tanggal (`2026-10-29`);
  prioritas: API `publishedAt` > JSON-LD. Jika keduanya absen →
  `posted_at=NULL`, presisi `unknown`.

## Pemetaan field → RawListing/RawJob

| Sumber | Field | Catatan |
|--------|-------|---------|
| `docs[].id` (hex ObjectId) | `external_id` | alternatif slug; `data.result.id` di detail |
| `docs[].slug` | `external_id` alternatif, URL `/loker/<slug>~<company.slug>` | |
| `docs[].role` | `title` | |
| `docs[].company.name` | `perusahaan` | detail memakai `data.result.company.name` |
| `docs[].city.name` | `lokasi` | bisa `null` (remote); `country.name` = Indonesia |
| `docs[].publishedAt` | `posted_raw` | ISO UTC presisi `exact` |
| `docs[].salaryRange.start/end` + `salaryType` | `gaji` | IDR angka; detail `salaryRange` bisa beda tampilan |
| `docs[].workplaceType` | `sistem_kerja` | `onSite`/`hybrid`/`remote` |
| `docs[].employmentTypes[]` | `tipe_kerja` | `fullTime`/`partTime`/`internship`/`contract`/`freelance` |
| `data.result.responsibilities` + `requirements` + `description` | `deskripsi` | HTML; gabung ketiganya, tidak terpotong (tanpa tombol "selengkapnya" pada sampel) |
| `data.result.company` (headline/tentang) | diabaikan | tidak masuk deskripsi |
| `data.result.closed`, `status` | skip | hanya `active`/`closed=false` yang diambil |

## Slug & kanonikalisasi

- Pola slug: `<judul>-<n>~<perusahaan>` — angka `n` adalah suffix unik
  (`slugSecondarySegment`, bisa 0/tidak muncul di teks slug). Contoh:
  `software-engineer-java-t24~pt-lawencon-internasional`.
- Varian `/en/loker/...` ada; canonical `/en` **tetap memuat `/en`**, sedangkan
  locale `idn` canonical bersih: `https://dealls.com/loker/<slug>~<company>`.
  Scraper memakai locale `idn` (URL tanpa `/en`) — seragam sesuai SCRAPER_SPEC
  §5.7. Query API tidak terpengaruh locale.

## Batas laju yang diamati

- 8 request beruntun (`limit=5..18`, jeda acak 1,5–2,5 dtk) → semua 200; tidak
  ada 429/403 pada sesi discovery (total ±25 request, tersebar ~15 menit).
- Config `platforms.yaml`: konkurensi 2, jeda 1,5–4 dtk, maks 6 halaman/term,
  maks 300 detail/run, maks 25 menit.
- `robots.txt`: `User-agent: *  Allow: /` + sitemap.

## Anti-bot / blokir

- **HTTP polos (curl/urllib):** 200 untuk API dan halaman SSR.
- **Playwright headless:** 403 Cloudflare challenge pada `/loker` (marker
  "Attention Required! | Cloudflare", "captcha") — **tidak ditembus**; scraper
  tidak memakai browser.
- Browser headed tidak diuji (env tanpa display/xvfb) — dicatat sebagai
  keterbatasan, bukan kebutuhan.
- Kebijakan: 403/429 → `BlockedError`/tunggu sesuai SCRAPER_SPEC §4; tanpa
  bypass CAPTCHA.

## Fixture

`tests/fixtures/dealls/` (email/kontak pribadi direduksi `[REDACTED]`,
`author`/`hiringTeam` dinolkan):
- Daftar (API JSON): `search_software_engineer_p1.json` (14 dokumen),
  `search_staff_p1.json` (18), `search_remote_p1.json` (18, filter
  `workplaceTypes=remote`), `search_software_engineer_p2.json` (kosong — bukti
  berhenti pada `totalPages`).
- Detail (API JSON, 6): `detail_software-engineer-juniormiddle.json`
  (onsite, bergaji), `detail_software-engineer-java-t24.json` (onsite, tanpa
  gaji), `detail_software-development-engineer-in-test-10.json` (kontrak),
  `detail_software-engineer-fullstack-order-management.json` (hybrid),
  `detail_software-engineer-golang-1.json` (hybrid, kontrak),
  `detail_part-time-pengajar-coding-kota.json` (remote, partTime).
- Detail SSR HTML (1): `detail_ssr_dexa_group.html` — JSON-LD `JobPosting`
  dengan `datePosted`, canonical tanpa `/en`.

## Perbedaan dari SCRAPER_SPEC.md

- §7.5 menduga daftar butuh tombol "Lihat Lebih Banyak" — benar di UI, tetapi
  klik tombol setara panggilan API `page=N+1`, jadi scraper tidak butuh browser.
- §7.5 menduga API internal "di bawah domain induk perusahaan" — terbukti:
  `api.sejutacita.id` (bukan subdomain dealls.com).
- Detail tidak butuh halaman HTML sama sekali: API by-slug lebih lengkap
  (presisi `publishedAt` ISO dengan waktu) daripada JSON-LD (tanggal saja);
  SSR HTML hanya fallback.
- Field `expires_at`: tidak ditemukan padanan eksplisit pada sampel
  (`jobActivationExpiredDurationDays` internal; tidak dipetakan).

## Risiko / catatan

- `api.sejutacita.id` adalah domain induk (Sejutacita); perubahan versi `/v1`
  dapat memutus scraper → deteksi via `SiteChangedError` (payload tanpa
  `data.docs`/`data.result`).
- `salaryRange` listing vs detail bisa berbeda; listing diprioritaskan (pola
  sama dengan JobStreet).
- `city` sering `null` untuk remote; lokasi fallback ke `location.country`.
- Field `description` bisa `null` sementara `responsibilities`/`requirements`
  terisi — deskripsi digabung dari yang tersedia.
- Sort `publishedAt` desc diuji; bila diubah server, fallback: urutkan
  klien-side berdasar `publishedAt` sebelum pre-filter usia.
