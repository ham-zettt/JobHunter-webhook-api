# DECISIONS — interpretasi & penyimpangan dari spesifikasi

Dicatat sesuai PRD §0.3. Prioritas: PRD > DATABASE > ARCHITECTURE > SCRAPER_SPEC.

## D-001 — Backend parser HTML: selectolax lexbor
ARCHITECTURE §3 membolehkan selectolax atau bs4+lxml. Dipilih `selectolax.lexbor`
(backend `parser` deprecated sejak selectolax 1.0). Konsekuensi: tidak ada dependensi lxml.

## D-002 — Skema dibuat oleh `app/db/schema.py`, Alembic memanggilnya
`ensure_schema_sync()` membuat tabel dari metadata + DDL FTS5/trigger secara idempoten.
Alembic migration `0001` memanggil fungsi yang sama, dan lifespan aplikasi juga
memanggilnya. Keuntungan: satu sumber kebenaran, aman untuk DB baru; kerugian: perubahan
skema berikutnya tetap wajib ditulis sebagai migration eksplisit.

## D-003 — Alias lokasi dibaca dari YAML, tabel `location_aliases` sebagai seed
`pipeline/location.py` memuat `config/locations_java.yaml` langsung agar pipeline murni
dan dapat diuji tanpa DB. Tabel `location_aliases` tetap di-seed untuk kebutuhan referensi.
Jika kelak alias diedit lewat DB/API, normalizer harus diubah untuk membaca tabel.

## D-004 — Statistik `updated` hanya saat detail benar-benar diambil ulang
Jalur "lowongan dikenal" (ARCHITECTURE §4.4) hanya `touch last_seen_at` + link `seen`.
Karena itu scrape kedua tanpa perubahan menghasilkan `new=0, updated=0`, bukan `updated=N`.

## D-005 — Seed kata kunci otomatis saat startup hanya bila tabel kosong
`lifespan` memanggil `seed_all()`; `seed_keywords` idempoten dan tidak menimpa
`source='user'`. Bila pengguna menghapus seed tertentu, seed tidak dipaksa kembali
selama tabel masih berisi aturan lain. `POST /keywords/reseed` untuk reset eksplisit.

## D-006 — Endpoint ubah status menerima `active|archived|expired`
FR-47 hanya menyebut `archived`; `active` dipakai untuk membatalkan arsip. `expired`
disertakan agar konsisten dengan enum DB dan tidak menambah endpoint baru.

## D-007 — Status scraper per platform
JobStreet dan Glints sudah diimplementasikan setelah discovery nyata (2026-11-02).
JobStreet: daftar lewat JSON API internal, detail lewat halaman dengan Playwright +
parsing embedded Redux state. Glints: SSR `__NEXT_DATA__` untuk daftar dan detail,
tanpa browser. Lima platform lain masih `DiscoveryPendingScraper` yang mengangkat
`SiteChangedError` (sub-run `degraded`) sampai discovery masing-masing dilakukan.
Ini disengaja: SCRAPER_SPEC melarang mengarang selector.

## D-011 — Browser memakai Chromium penuh (channel="chromium")
Cloudflare JobStreet menantang headless-shell bawaan Playwright, tetapi meloloskan
Chromium penuh mode new-headless. `BrowserPool` karena itu memakai
`channel="chromium"` (fallback ke default bila channel tidak tersedia). Ini bukan
stealth/spoof: browser asli, tanpa plugin anti-detect, dan tantangan tidak pernah
ditembus secara otomatis.

## D-008 — SSRF callback
`callback_url` wajib http/https. Tanpa `CALLBACK_ALLOWED_HOSTS`, host privat/loopback/
link-local/reserved ditolak (termasuk hasil resolusi DNS). Bila allowlist diisi, hanya
host tersebut yang diizinkan — host n8n di jaringan Docker harus didaftarkan.

## D-009 — `EXPORT_MAX_ROWS`
Disebut di ARCHITECTURE §7.2 tetapi tidak ada di blok `.env.example`; ditambahkan sebagai
env dengan default 50000.

## D-010 — Scheduler internal belum diaktifkan
`SCHEDULE_CRON` (FR-11, OPSIONAL) belum diimplementasikan. Penjadwal utama adalah n8n.

## D-012 — Paginasi Glints dibatasi SSR halaman pertama
`?page=2` tidak membawa `initialJobs`; paginasi klien memerlukan JS yang ditantang
Cloudflare Turnstile, dan GraphQL `searchJobsV3` tanpa sesi mengabaikan `SearchTerm`.
Scraper Glints karena itu mengambil 30 lowongan pertama per search term dan menambah
cakupan lewat banyak term (mitigasi yang memang disebut SCRAPER_SPEC §1). Tidak ada
upaya menembus tantangan. Detail: `docs/platform_notes/glints.md`.

## D-013 — Discovery Kalibrr: XHR untuk daftar, `__NEXT_DATA__` untuk detail
Daftar memakai `GET https://www.kalibrr.com/kjs/job_board/search` (offset-based,
tanpa token); detail memakai HTML `/id-ID/c/<company>/jobs/<id>/<slug>` dan
`props.pageProps.job` dari `__NEXT_DATA__` (JSON-LD hanya `WebSite`). URL kanonik
situs tidak memakai locale. `sort=Freshness` hanya berlaku di SSR halaman pertama;
endpoint XHR mengabaikan sort, dan tidak ada filter tanggal. Paginasi wajib dibatasi
`count` karena offset berlebih mengembalikan feed umum. Detail:
`docs/platform_notes/kalibrr.md`.

## D-014 — Kalibrr tanpa henti-dini usia
Karena endpoint daftar Kalibrr tidak menjamin urutan terbaru, penghentian dini
berdasarkan usia (FR-06) tidak diterapkan di scraper maupun orchestrator untuk
platform ini. Usia tetap menjadi pre-filter lokal dari `posted_raw`; cakupan
dibatasi `max_pages_per_term` dan guard `offset < count`. Detail diambil via HTTP
(httpx), bukan browser, karena `__NEXT_DATA__` sudah memuat seluruh deskripsi.

## D-015 — Discovery Dealls: API langsung `api.sejutacita.id`, tanpa browser
Daftar memakai `GET https://api.sejutacita.id/v1/explore-job/job` dengan
`search`, `page/limit`, `sortParam=publishedAt&sortBy=desc` (urut terbaru
terverifikasi), filter `workplaceTypes`/`employmentTypes`/`cityIds`. Detail
memakai `GET /v1/job-portal/job/slug/<slug>` (`data.result`), fallback SSR
`https://dealls.com/loker/<slug>~<company-slug>` dengan JSON-LD `datePosted`
(presisi tanggal saja). Tanggal posting = `publishedAt`; `lastActivelyHiringAt`
(label "Rekruter aktif") tidak boleh dipakai. Playwright headless ditantang
Cloudflare sedangkan HTTP polos tidak → scraper Dealls HTTP-first (httpx), tanpa
browser. Kanonik: locale `idn`, URL tanpa `/en`, wajib sufiks `~<company>`.
Detail: `docs/platform_notes/dealls.md`.

## P-26 — Tanggal daftar KitaLulus

`updatedAtStr` pada daftar adalah "Terakhir diperbarui", bukan tanggal posting.
`RawListing.posted_raw` diisi `None` dan nilai asli disimpan di
`extra.updated_at_str`; tanggal posting hanya diambil dari JSON-LD `datePosted`
pada detail (`exact`). Ini mencegah pipeline memakai tanggal aktivitas sebagai
`posted_at`.

## D-016 — Pintarnya dapat diakses publik; implementasi normal
Discovery 2026-11-02 menemukan daftar lowongan publik tanpa login di
`https://pintarnya.com/q-<kata>-lowongan`, dengan API daftar
`https://api.pintarnya.com/api/v2/pk/job` dan detail `/lowongan/<slug>` berisi
JSON-LD `JobPosting`. Karena itu §7.7 memilih implementasi normal, **bukan** stub
`skipped`/`NOT_PUBLICLY_ACCESSIBLE`. API butuh konteks browser (HTTP polos 403
Cloudflare), paginasi berupa infinite scroll (`page`/`p` URL diabaikan), dan
kategori IT (`job_category=17`) berisi 117 lowongan. Detail:
`docs/platform_notes/pintarnya.md`.

## D-016 — LinkedIn: path `search-results` + selector berbasis `componentkey`

Discovery 2026-11-03: UI baru LinkedIn (SDUI) memakai kelas CSS acak dan dua panel.
Scraper memakai `/jobs/search-results/` (bukan `/jobs/search/` yang membuang
`location=Indonesia`), `location=Indonesia`/`geoId=102478259`, `f_TPR`, `f_WT`.
Kartu dikenali lewat `componentkey^="job-card-component-ref-"` (ID = sufiks) dan
dedupe ID; detail lewat `data-testid="expandable-text-box"`/`expandable-text-button`.
Tidak ada `<time>`/`datetime`: tanggal hanya relatif. `sortBy`/`start` belum terbukti
dan harus diverifikasi di task 28.

## Task 31 — Retry terpusat, baseline canary, snapshot HTTP (2026-11-03)

- Retry jaringan terpusat di `app/scrapers/common/retry.py` (`fetch_with_retry`);
  duplikasi loop retry dihapus dari glints/jobstreet/kalibrr/dealls. 403/999/
  CAPTCHA/challenge langsung `BlockedError` tanpa retry; 429 maks 2 retry lalu
  `BlockedError`.
- Canary baseline: `run_repo.productive_terms(platform, terms)` mencari term yang
  pernah menghasilkan (`status='completed'`, `found_count>0`, `search_terms`
  cocok). 0 hasil pada term produktif → sub-run `degraded`. Tidak menambah tabel.
- Snapshot HTTP: `save_debug_snapshot(page=None, ..., html=...)` agar Glints
  (tanpa Playwright) tetap menyimpan HTML saat parse gagal.
