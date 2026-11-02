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
