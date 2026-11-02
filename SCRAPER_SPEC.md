# SCRAPER_SPEC — Mekanisme Scraping per Platform

> **Versi:** 1.0 · **Tanggal:** 1 November 2026
> **Dokumen terkait:** [`PRD.md`](./PRD.md) · [`ARCHITECTURE.md`](./ARCHITECTURE.md) · [`DATABASE.md`](./DATABASE.md)

---

## 0. Status Pengetahuan dan Cara Memakai Dokumen Ini

**Peringatan penting untuk AI Agent.** Struktur situs pihak ketiga berubah tanpa pemberitahuan. Isi bagian per platform (§7) berasal dari riset awal pada **1 November 2026** (dokumentasi publik scraper pihak ketiga dan pengetahuan umum tentang situs), **bukan** dari pengujian langsung terhadap situs. Karena itu:

| Jenis informasi | Status |
|-----------------|--------|
| Domain, pola umum URL, alur halaman | **Petunjuk**; verifikasi saat discovery |
| Nama parameter query, selector CSS, nama field JSON, endpoint internal | **Hipotesis** (ditandai `[verifikasi]`); jangan di-hard-code sebelum dibuktikan |
| Aturan normalisasi (§5), batas kesopanan (§4), kontrak data (§5.0), alur kode (§6) | **Mengikat** |

Urutan kerja untuk setiap platform: **Discovery (§3) → catat hasil → tulis parser murni + fixture → tulis navigasi → test → canary.** Jangan menulis scraper dari asumsi di dokumen ini saja.

Aturan emas:
1. Jangan pernah mengarang selector atau endpoint. Jika tidak terbukti, tandai `TODO(discovery)` dan laporkan.
2. Jika platform mustahil di-scrape secara wajar (login paksa tanpa akses, CAPTCHA permanen), implementasikan scraper yang mengembalikan status `skipped`/`blocked` dengan alasan jelas, dokumentasikan, dan lanjutkan. Jangan menembus CAPTCHA atau proteksi.
3. Scraper bersifat **read-only**: tidak melamar, tidak mengirim pesan, tidak mengikuti/connect, tidak menyimpan lowongan di akun, tidak mengubah apa pun di platform.

---

## 1. Ringkasan Platform

| Platform | Domain (diperkirakan) | Login | Metode utama (hipotesis) | Tingkat kesulitan | Kendala utama |
|----------|----------------------|-------|--------------------------|-------------------|---------------|
| JobStreet | `id.jobstreet.com` | Tidak | JSON/GraphQL internal (jaringan SEEK) via intersepsi, fallback DOM | Sedang–Tinggi | Anti-bot (403 pada IP yang ditandai) |
| Glints | `glints.com/id` | Tidak | Data tertanam (`__NEXT_DATA__`) / GraphQL internal; fallback DOM | Sedang | Batas hasil per halaman, rate limit |
| Kalibrr | `kalibrr.com` | Tidak | API internal via intersepsi; fallback DOM | Sedang | Skema berubah, hasil per kota/kata kunci |
| Dealls | `dealls.com` | Tidak | HTML/JSON halaman detail (HTTP-first) + Playwright untuk "Lebih Banyak" pada daftar | Sedang | Tanggal "aktif" ≠ tanggal posting |
| KitaLulus | `kitalulus.com` | Tidak | HTML awal + tombol "load more" via Playwright | Sedang | Tanggal posting, volume IT rendah |
| LinkedIn | `linkedin.com` | **Ya** | Playwright dengan sesi tersimpan; DOM | **Tinggi** | Anti-bot, checkpoint, risiko akun |
| Pintarnya | `pintarnya.com` | ? | **Belum diketahui** | ? | Struktur tidak diketahui; mungkin app-first |

Urutan implementasi: JobStreet → Glints → Kalibrr → Dealls → KitaLulus → LinkedIn → Pintarnya. Urutan eksekusi pada `scrape/all`: LinkedIn **terakhir** (agar kegagalan/jeda panjangnya tidak menghambat yang lain).

---

## 2. Hierarki Strategi Ekstraksi

Untuk setiap platform, coba dari atas ke bawah dan pilih yang **paling stabil dan paling sedikit request**:

1. **Data terstruktur dalam halaman** — `<script type="application/ld+json">` (`schema.org/JobPosting`: `title`, `datePosted`, `validThrough`, `hiringOrganization`, `jobLocation`, `employmentType`, `baseSalary`, `description`, `jobLocationType: TELECOMMUTE`), `__NEXT_DATA__`, `window.__INITIAL_STATE__`/`__APOLLO_STATE__`. Sangat stabil dan memuat `datePosted` yang akurat.
2. **Intersepsi respons XHR/fetch** dengan Playwright (`page.on("response")`) pada panggilan JSON yang dipakai situs itu sendiri. Parser menerima JSON, bukan DOM.
3. **Panggilan langsung ke endpoint internal** yang sama memakai `context.request` (berbagi cookie/sesi browser), hanya bila terbukti dapat dipanggil tanpa token sekali pakai. Tetap tunduk pada jeda dan batas §4.
4. **Parsing DOM** (selector). Gunakan atribut stabil (`data-*`, `aria-*`, role, JSON-LD) sebelum kelas CSS yang tampak di-hash/dihasilkan otomatis (mis. `css-1x2y3z`). Simpan semua selector di satu modul konfigurasi per platform (`SELECTORS = {...}`), bukan tersebar.

Aturan:
- Jangan menyimpan seluruh respons API ke DB kecuali `STORE_RAW_PAYLOAD=true`.
- Setiap scraper mengekspos fungsi parser murni (`parse_listing_payload`, `parse_detail_payload`) yang menerima str/dict/HTML dan **tidak** memakai browser.
- Bila memakai jalur 2/3, simpan juga fallback DOM minimal untuk deteksi cepat saat skema JSON berubah (canary).

---

## 3. Prosedur Discovery (WAJIB sebelum menulis scraper tiap platform)

Gunakan `scripts/discover_platform.py <platform>` (headed, opsional merekam HAR dan menyimpan HTML/JSON ke `data/discovery/<platform>/`).

| # | Langkah | Hasil yang dicatat |
|---|---------|--------------------|
| 1 | Buka halaman pencarian dengan kata kunci contoh; catat URL akhir dan parameter query | Pola URL pencarian |
| 2 | Pantau panggilan jaringan; cari respons JSON yang memuat daftar lowongan | Endpoint, method, header penting, bentuk payload, pagination (offset/cursor/page) |
| 3 | Periksa HTML untuk JSON-LD, `__NEXT_DATA__`, state global | Lokasi data terstruktur |
| 4 | Tentukan cara paginasi (page param, offset, infinite scroll, tombol "lebih banyak") dan batas maksimum hasil per kueri | Mekanisme + batas |
| 5 | Temukan parameter **urut terbaru** dan **filter tanggal** (bila ada) | Parameter atau "tidak ada" |
| 6 | Buka beberapa halaman detail; temukan wadah deskripsi, tombol "selengkapnya", dan sumber tanggal posting | Selector/field + contoh format tanggal |
| 7 | Periksa field: perusahaan, lokasi, sistem kerja, tipe kerja, gaji | Pemetaan field (§7 tiap platform) |
| 8 | Periksa respons terhadap permintaan beruntun (adakah 429/403/CAPTCHA) dan catat ambang kasar | Batas aman |
| 9 | Catat isi `robots.txt` dan halaman mana yang **tidak** akan diakses (info untuk pemilik) | Catatan kepatuhan |
| 10 | Simpan ≥ 3 halaman daftar dan ≥ 5 halaman detail sebagai fixture (bersihkan data pribadi) | `tests/fixtures/<platform>/` |

**Output wajib:** `docs/platform_notes/<platform>.md` dengan templat:

```markdown
# <platform> — catatan discovery (tanggal)
- Metode terpilih: (JSON-LD | XHR | API langsung | DOM) + alasan
- URL pencarian: ...   Parameter urut terbaru: ...   Filter tanggal: ...
- Endpoint/selector final: ...
- Pagination: ... (maks N hasil/kueri)
- Sumber tanggal posting + format: ...
- Lokasi deskripsi + cara memastikan tidak terpotong: ...
- Pemetaan field → RawJob: tabel
- Batas laju aman yang diamati: ...
- Risiko/blokir yang ditemui: ...
- Perbedaan dari SCRAPER_SPEC.md: ...
```

---

## 4. Kesopanan, Laju, dan Penanganan Blokir

### 4.1 Batas Laju (default; dapat diubah di `config/platforms.yaml`)

| Platform | Konkurensi halaman | Jeda acak antar-aksi | Maks halaman/kata kunci | Maks detail per run | Maks durasi |
|----------|--------------------|----------------------|-------------------------|---------------------|-------------|
| jobstreet | 2 | 1,5–4 dtk | 8 | 300 | 25 mnt |
| glints | 2 | 1,5–4 dtk | 6 | 300 | 25 mnt |
| kalibrr | 2 | 1,5–4 dtk | 6 | 300 | 25 mnt |
| dealls | 2 | 1,5–4 dtk | 6 | 300 | 25 mnt |
| kitalulus | 1 | 2–5 dtk | 6 | 200 | 25 mnt |
| pintarnya | 1 | 2–5 dtk | 5 | 150 | 20 mnt |
| linkedin | **1** | **4–9 dtk** | 4 | **60/run, 150/hari** | 25 mnt |

- Jeda berlaku antara **setiap navigasi dan setiap panggilan** (juga untuk `context.request`).
- Jumlah `search_term` per platform dibatasi oleh `search_terms_limit` (default 10; **LinkedIn 6**), mengambil dari urutan prioritas `search_term` di DATABASE §6.2.
- Perhitungan harian LinkedIn: jumlah `scrape_run_sources.detail_fetched` untuk `platform='linkedin'` dengan `started_at` pada hari WIB yang sama. Jika ≥ `LINKEDIN_MAX_JOBS_PER_DAY` → sub-run `skipped` (alasan `daily_cap`).

### 4.2 Retry

- Kesalahan jaringan/timeout: `tenacity` 3 percobaan, backoff eksponensial 2→4→8 dtk + jitter.
- 429: tunggu `Retry-After` (bila ada) atau 60 dtk; maksimum 2 kali sebelum `BlockedError`.
- 5xx: retry seperti jaringan.
- 403/CAPTCHA/challenge: **tidak di-retry**; langsung `BlockedError`.

### 4.3 Deteksi Tantangan / Blokir

Tandai sebagai `BlockedError` (atau `AuthRequiredError` untuk login) bila salah satu:
- Status HTTP 403, 429 berulang, atau 999 (LinkedIn).
- URL akhir mengandung `/checkpoint`, `/authwall`, `/login`, `/uas/`, `captcha`, `challenge`, `cf-chl`.
- Teks halaman cocok `verify you are human`, `just a moment`, `access denied`, `unusual activity`, `aktivitas tidak biasa`, `verifikasi`, atau ada iframe `recaptcha`/`hcaptcha`/`turnstile`.
- Daftar kosong padahal sebelumnya ada hasil **dan** halaman memuat elemen tantangan.

Tindakan: simpan screenshot + HTML ke `data/debug/`, hentikan platform, catat `errors`, lanjut ke platform berikutnya. **Tidak ada upaya melewati tantangan** dan **tidak memakai plugin stealth atau pemalsuan fingerprint**.

### 4.4 Konfigurasi Browser

- Chromium bawaan Playwright, viewport 1366×768, `locale="id-ID"`, `timezone_id="Asia/Jakarta"`, user-agent bawaan Chromium yang cocok dengan versinya (jangan memalsukan versi berbeda).
- Blokir resource `image`, `media`, `font` bila tidak memengaruhi konten (terutama daftar). Jangan blokir stylesheet/script yang dibutuhkan render.
- Timeout navigasi 45 dtk, aksi 15 dtk. Tunggu elemen/respons spesifik, bukan `sleep` buta (gunakan `wait_for_selector`/`expect_response`).
- Tutup `page` setelah dipakai; satu `context` per platform per run; tutup di `finally`.

### 4.5 Cakupan Akses

Scraper hanya mengakses halaman **pencarian lowongan** dan **detail lowongan**. Tidak mengakses profil orang, pesan, notifikasi, halaman pelamar, atau data kontak rekruter. Nama rekruter/kontak **tidak** disimpan.

---

## 5. Kontrak Data dan Normalisasi Bersama

### 5.0 Struktur `RawListing` dan `RawJob`

```python
@dataclass
class RawListing:
    platform: str
    url: str                          # URL detail (absolut)
    external_id: str | None
    title: str
    company: str | None = None
    location_raw: str | None = None
    posted_raw: str | datetime | None = None   # teks relatif/ISO/None — dipakai untuk pre-filter & penghentian dini
    snippet: str | None = None
    extra: dict = field(default_factory=dict)

@dataclass
class RawJob:
    platform: str
    url: str
    external_id: str | None
    title: str
    company: str | None
    location_raw: str | None
    posted_raw: str | datetime | None
    work_mode_raw: str | None         # nilai terstruktur platform atau teks
    employment_type_raw: str | None
    salary_raw: str | None
    description_html: str | None
    description_text: str            # LENGKAP
    expires_raw: str | None = None
    scraped_at: datetime = field(default_factory=now_utc)
    extra: dict = field(default_factory=dict)       # field tambahan platform (kategori, pendidikan, dll.)
    raw_payload: dict | None = None
```

Scraper mengisi **nilai mentah**; konversi ke tipe final dilakukan `pipeline/normalizer.py` memakai parser di bawah.

### 5.1 Parser Tanggal (`core/timeutil.py::parse_posted(raw, now) -> (date_wib | None, precision)`)

Zona acuan: `Asia/Jakarta`. `now` = waktu scraping.

| Masukan | Hasil | Presisi |
|---------|-------|---------|
| ISO 8601 dengan jam (`2026-10-29T08:12:00Z`) | tanggal WIB | `exact` |
| ISO tanggal saja / `29 Okt 2026` / `Oct 29, 2026` / `29/10/2026` (dd/mm/yyyy) | tanggal tsb | `date` |
| `baru saja`, `just now`, `hari ini`, `today`, `N menit/jam lalu`, `N minutes/hours ago`, `8j lalu`, `5h`, `Posted today` | tanggal `now` (dikurangi durasi bila melewati tengah malam) | `relative` |
| `kemarin`, `yesterday` | `now − 1 hari` | `relative` |
| `N hari lalu`, `N days ago`, `7d ago`, `3d` | `now − N hari` | `relative` |
| `N minggu lalu`, `N weeks ago`, `2w` | `now − 7N hari` | `relative` |
| `N bulan lalu`, `N months ago` | `now − 30N hari` | `relative` |
| `30+ hari lalu`, `30+ days ago`, `lebih dari 30 hari` | `now − 31 hari` | `relative` |
| Awalan `Reposted`/`Diposting ulang`/`Dibagikan ulang` | diperlakukan sama seperti relatif biasa | `relative` |
| Tidak dikenali / tanggal di masa depan (> now + 1 hari) | `None` | `unknown` (+ log peringatan) |

Aturan tambahan:
- Dukung nama bulan Indonesia & Inggris (termasuk singkatan `Agu/Agt`, `Mei`, `Okt`, `Des`, `Sept`).
- **Jangan** menganggap teks seperti `Rekruter aktif 8j lalu`, `Actively hiring`, `Diperbarui N hari lalu`, `Updated N days ago` sebagai tanggal posting. Itu aktivitas/pembaruan. Gunakan hanya bila **tidak ada** sumber lain, set presisi `relative`, dan catat di `docs/platform_notes/`.
- Unit test wajib memuat ≥ 30 contoh (ID + EN) termasuk tepi: tengah malam, awal bulan, tahun kabisat, spasi/huruf besar tak lazim.

### 5.2 Parser Gaji (`scrapers/common/salary.py::parse_salary(raw) -> SalaryInfo`)

`SalaryInfo(min, max, currency, period, raw)`.

| Contoh masukan | min | max | currency | period |
|----------------|-----|-----|----------|--------|
| `Rp 8.000.000 - Rp 12.000.000` | 8000000 | 12000000 | IDR | month* |
| `IDR 8,000,000 – 12,000,000 per month` | 8000000 | 12000000 | IDR | month |
| `Rp8 - 12 juta` / `8 - 12 Jt` / `Rp 8jt-12jt` | 8000000 | 12000000 | IDR | month* |
| `Rp 8,5 juta` | 8500000 | 8500000 | IDR | month* |
| `Up to Rp 15 juta` / `Hingga Rp 15 juta` | NULL | 15000000 | IDR | month* |
| `Mulai dari Rp 7.000.000` / `From IDR 7M` | 7000000 | NULL | IDR | month* |
| `USD 3,000 - 5,000 / month` | 3000 | 5000 | USD | month |
| `Rp 100 juta per tahun` | 100000000 | 100000000 | IDR | year |
| `Rp 150.000 / jam` | 150000 | 150000 | IDR | hour |
| `Negosiasi`, `Dirahasiakan`, `Kompetitif`, `Confidential`, kosong | NULL | NULL | NULL | NULL (dan `salary_raw = NULL`) |

\* Periode default `month` bila mata uang IDR, nilai ≥ 1.000.000, dan tidak ada petunjuk periode.

Aturan: pemisah ribuan `.`/`,` dibedakan lewat pola (`\d{1,3}([.,]\d{3})+` = ribuan; `\d+[.,]\d{1,2}` diikuti `juta/jt/million/M` = desimal); `k/rb/ribu` = ×1.000; `juta/jt/million/mn` = ×1.000.000; `M` setelah mata uang = juta; `miliar/billion/b` = ×1.000.000.000. Jika `min > max` → tukar. Jika tidak dapat diparse tetapi ada angka → simpan `salary_raw`, kolom numerik NULL. `salary_raw` selalu teks asli (dirapikan spasi), tidak diubah bentuknya.

### 5.3 Deteksi `sistem_kerja`

Prioritas:
1. **Nilai terstruktur** platform: `REMOTE`/`Remote`/`Jarak jauh`/`WFH`/`TELECOMMUTE` → `remote`; `HYBRID`/`Hybrid` → `hybrid`; `ONSITE`/`On-site`/`Di tempat`/`WFO`/`Onsite` → `onsite`.
2. **Judul dan lokasi:** kata `remote`, `(WFH)`, `work from home` → `remote`; `hybrid` → `hybrid`.
3. **Deskripsi (hanya frasa tegas):** `fully remote`, `100% remote`, `remote position`, `work from anywhere`, `kerja jarak jauh penuh` → `remote`; `hybrid`, `WFO … WFH` → `hybrid`; `WFO`, `on-site`, `work from office`, `kerja di kantor` → `onsite`. Kata `remote` biasa di deskripsi (mis. "remote team", "remote servers") **tidak** cukup.
4. Tidak ada sinyal: jika lokasi berupa kota spesifik → `onsite` (disimpulkan), selain itu `unknown`.

### 5.4 Deteksi `tipe_kerja`

| Masukan (case-insensitive) | Nilai |
|----------------------------|-------|
| `full time`, `full-time`, `fulltime`, `penuh waktu`, `FULL_TIME`, `permanent`, `tetap`, `karyawan tetap`, `PKWTT` | `fulltime` |
| `part time`, `part-time`, `paruh waktu`, `PART_TIME` | `parttime` |
| `contract`, `kontrak`, `PKWT`, `temporary`, `temp`, `CONTRACT` | `contract` |
| `freelance`, `lepas`, `project based`, `project-based`, `PROJECT_BASED`, `harian` | `freelance` |
| `internship`, `intern`, `magang`, `INTERNSHIP`, judul memuat `intern`/`magang` | `internship` |
| lainnya/kosong | `unknown` |

Bila beberapa nilai (`Full time, Contract`), ambil yang pertama dan simpan sisanya di `extra`.

### 5.5 Lokasi

Scraper mengirim `location_raw` apa adanya (jangan dipotong). Normalisasi memakai DATABASE §7.3. Pada platform yang memisahkan kota/provinsi/negara dalam field terpisah, gabungkan: `"{kota}, {provinsi}, {negara}"`.

### 5.6 Deskripsi Lengkap (FR-05)

Prosedur wajib pada halaman detail:
1. Muat halaman, tunggu wadah deskripsi muncul.
2. **Klik semua tombol perluasan** sebelum membaca: teks seperti `Show more`, `See more`, `Lihat selengkapnya`, `Baca selengkapnya`, `Selengkapnya`, `Lebih banyak` (gunakan atribut `aria-expanded`/`role=button`, bukan hanya teks). Ulangi hingga tidak ada lagi (maks 3 iterasi).
3. Tunggu panjang teks wadah **stabil** (dua pembacaan berurutan berjarak 300 ms sama).
4. Ekstrak `innerHTML` wadah → simpan sebagai `description_html` (bila `STORE_HTML=true`) dan konversi ke `description_text`:
   - `<br>`/`</p>`/`</div>` → baris baru; `<li>` → `- ` + teks; heading → baris sendiri; tabel → baris dengan ` | `.
   - Hapus elemen non-deskripsi di dalam wadah (tombol lamar, "laporkan lowongan", "lowongan serupa", bagian profil perusahaan **bila** berada di luar wadah deskripsi).
   - Decode entitas HTML, normalisasi spasi/NBSP, batasi baris kosong beruntun maksimum 1.
   - **Jangan** memotong panjang; batas pengaman 100.000 karakter.
5. **Deteksi terpotong** → `description_truncated=1` bila setelah langkah 2–3: teks berakhir `…`/`...`, mengandung sisa teks tombol perluasan, atau panjang < 200 karakter sementara halaman jelas memuat konten lebih banyak. Coba ulang sekali dengan reload. Bila tetap terpotong → simpan dengan flag dan catat log `description_truncated`.
6. Jika halaman detail gagal total setelah retry: **jangan menyimpan lowongan baru** hanya dengan cuplikan daftar (hitung sebagai error). Pengecualian: pengguna memanggil run dengan `fetch_details=false` → simpan cuplikan dan set `description_truncated=1`.

### 5.7 `external_id` dan `url_canonical` per Platform

| Platform | `external_id` | `url_canonical` |
|----------|---------------|-----------------|
| linkedin | angka dari `/jobs/view/<id>` atau `currentJobId` | `https://www.linkedin.com/jobs/view/<id>` |
| jobstreet | angka dari `/job/<id>` `[verifikasi]` | `https://id.jobstreet.com/job/<id>` `[verifikasi pola path]` |
| glints | UUID di akhir path `/opportunities/jobs/<slug>/<uuid>` `[verifikasi]` | URL detail tanpa query |
| kalibrr | angka dari `/c/<company>/jobs/<id>/<slug>` `[verifikasi]` | URL detail tanpa query |
| dealls | slug `<judul>-<n>~<perusahaan>` pada `/loker/<slug>` (atau ID dari API bila tersedia) | `https://dealls.com/loker/<slug>` (tanpa `/en`; seragamkan locale) |
| kitalulus | slug pada `/lowongan/detail/<slug>` | URL detail tanpa query |
| pintarnya | ditentukan saat discovery | URL detail tanpa query |

Aturan umum kanonikalisasi: DATABASE §8.1.

---

## 6. Alur Umum Setiap Scraper

```python
class XxxScraper(BaseScraper):
    platform = "xxx"

    async def iter_listings(self, term: str) -> AsyncIterator[RawListing]:
        # 1. Bangun URL/kueri pencarian: kata kunci = term, urut TERBARU, filter tanggal bila platform mendukung
        #    (pakai ctx.max_age_days → parameter platform terdekat; tetap difilter ulang di pipeline).
        # 2. Untuk page/offset/cursor/scroll ke-n (n ≤ max_pages_per_term):
        #       - jeda acak (§4.1), ambil data (§2: JSON-LD → XHR → API → DOM)
        #       - deteksi tantangan (§4.3)
        #       - parse_listing_payload(...) → list[RawListing]
        #       - yield tiap listing
        #       - hentikan bila halaman kosong / tidak ada halaman berikutnya / ctx.stop_requested
        # 3. Penghentian dini berdasarkan usia (FR-06) dilakukan orchestrator memakai listing.posted_raw;
        #    scraper cukup menyediakan posted_raw sebaik mungkin dan menghormati ctx.stop_requested.
        ...

    async def fetch_detail(self, listing: RawListing) -> RawJob:
        # 1. Buka detail (atau panggil endpoint detail), deteksi tantangan
        # 2. Terapkan prosedur §5.6 untuk deskripsi lengkap
        # 3. parse_detail_payload(...) → RawJob dengan SEMUA field mentah yang tersedia
        ...
```

Catatan:
- `iter_listings` harus **idempoten dan dapat dihentikan** kapan saja (async generator yang menutup page di `finally`).
- Jangan mengubah kata kunci pencarian menjadi query berbahaya; encode dengan `urllib.parse.quote_plus`.
- Pemilihan filter lokasi di sisi platform (mis. "Indonesia", "Jakarta") **opsional** untuk mengurangi volume. Penyaringan final tetap di pipeline (BR-02/03). Pencarian dengan filter negara Indonesia direkomendasikan; **jangan** mempersempit hanya ke Jawa di sisi platform karena lowongan remote Indonesia harus ikut masuk (BR-03).
- Untuk pencarian remote, bila platform mendukung filter sistem kerja, jalankan satu pencarian tambahan khusus remote per `search_term` prioritas tinggi (maks 3 term).

---

## 7. Spesifikasi per Platform

### 7.1 LinkedIn (login wajib; keputusan pemilik D2)

**Keputusan:** memakai akun login agar hasil lengkap; pemilik menerima risiko pembatasan/pemblokiran akun. Mitigasi di bawah **wajib**.

**a. Autentikasi (tanpa menyimpan kata sandi)**
- `scripts/linkedin_login.py`: membuka Chromium **headed** dengan profil bersih, mengarahkan ke halaman login, menunggu pengguna login manual (termasuk 2FA/verifikasi), lalu menyimpan `context.storage_state(path="data/secrets/linkedin_state.json")`. Skrip dijalankan di mesin lokal pemilik, lalu file disalin ke `data/secrets/`.
- Runtime memuat `storage_state`. Aplikasi **tidak** menyimpan/memakai kata sandi dan tidak melakukan login otomatis.
- `check_session()`: buka halaman beranda pekerjaan (`https://www.linkedin.com/jobs/`). Bila redirect ke login/`checkpoint`/`authwall`, atau file state tidak ada → `AuthRequiredError` (sub-run `auth_required`, pesan: "Jalankan scripts/linkedin_login.py").
- `GET /platforms` menampilkan `auth_state`: `missing` (file tidak ada), `valid`/`expired` (hasil `check_session` terakhir).
- **Rekomendasi kepada pemilik (dicantumkan di README):** gunakan **akun khusus/cadangan**, bukan akun utama; login manual dari jaringan yang sama dengan tempat aplikasi berjalan bila memungkinkan; jangan menjalankan banyak instance bersamaan.

**b. Pencarian** `[verifikasi semua parameter]`
- URL dasar: `https://www.linkedin.com/jobs/search/`
- Parameter yang umum diketahui: `keywords=<term>`, `location=Indonesia` (+ `geoId` Indonesia bila ditemukan saat discovery), `f_TPR=r<detik>` (filter waktu posting; mis. `r604800` = 7 hari, `r86400` = 24 jam), `f_WT=<1|2|3>` (1 onsite, 2 remote, 3 hybrid), `sortBy=DD` (terbaru), `start=<offset kelipatan 25>`.
- Strategi per `search_term`: (1) `location=Indonesia`, urut terbaru, `f_TPR` dari `max_age_days` (dibulatkan ke atas ke nilai yang didukung); (2) untuk 3 term prioritas teratas, satu pencarian tambahan `f_WT=2` (remote) agar remote Indonesia tertangkap.
- Hasil berupa daftar di panel kiri dengan scroll/paginasi `start`. Ekstrak: ID (atribut `data-job-id`/`data-occludable-job-id` atau `/jobs/view/<id>` pada tautan), judul, perusahaan, lokasi, teks waktu. Gunakan atribut dan ARIA sebelum kelas CSS.
- Batas: maks `max_pages_per_term` (4) × ±25 hasil per term.

**c. Detail**
- Buka `https://www.linkedin.com/jobs/view/<id>/` (atau klik kartu) dan baca panel detail.
- Klik tombol perluasan deskripsi (`Show more`/`Lihat selengkapnya`) sebelum ekstraksi (§5.6).
- Ambil: judul, perusahaan, lokasi, **teks waktu posting relatif** (`3 days ago`, `2 hari yang lalu`, `Reposted …`), pil sistem kerja (`Remote/On-site/Hybrid` ↔ `Jarak jauh/Di tempat/Hybrid`), tipe kerja (`Full-time/Part-time/Contract/Internship` ↔ `Penuh waktu/Paruh waktu/Kontrak/Magang`), gaji bila ditampilkan, deskripsi.
- Dukung antarmuka **bahasa Inggris dan Indonesia** (pakai atribut/struktur; teks sebagai cadangan dengan kamus dua bahasa).
- Tanggal: relatif → presisi `relative`. Jika terdapat atribut `datetime` pada elemen waktu, pakai (presisi `date`/`exact`).

**d. Pengaman khusus LinkedIn (WAJIB)**
1. Konkurensi 1, jeda 4–9 detik, tanpa navigasi paralel.
2. Batas: `LINKEDIN_MAX_JOBS_PER_RUN` (60) detail per run dan `LINKEDIN_MAX_JOBS_PER_DAY` (150) per hari WIB.
3. Gunakan jalur "lowongan dikenal" (ARCHITECTURE §4.4) secara agresif agar tidak membuka detail berulang.
4. Pre-filter dari kartu (judul/lokasi/usia) **sebelum** membuka detail.
5. Berhenti total pada tanda tantangan (§4.3): `checkpoint`, `authwall`, pesan pembatasan akun, atau status 999/429 beruntun. Status sub-run `blocked`/`auth_required`. **Jangan** mencoba ulang pada run yang sama dan jangan login otomatis.
6. Read-only: tidak menekan `Easy Apply`/`Apply`, `Save`, `Follow`, `Connect`, `Message`, atau "Report".
7. Tidak mengekstrak data rekruter/pemosting.
8. Jalankan sebagai platform **terakhir** pada `scrape/all`.

**e. Pemetaan**

| RawJob | Sumber |
|--------|--------|
| `external_id` | ID numerik lowongan |
| `posted_raw` | teks waktu / atribut `datetime` |
| `work_mode_raw` | pil sistem kerja |
| `employment_type_raw` | pil tipe kerja |
| `salary_raw` | blok gaji (bila ada) |
| `location_raw` | lokasi pada header detail |

**f. Risiko:** tertinggi di antara semua platform (ToS, pembatasan akun). Tulis ringkasan risiko di README dan di `docs/platform_notes/linkedin.md`.

---

### 7.2 JobStreet (Indonesia)

- **Domain:** `https://id.jobstreet.com` (jaringan SEEK). `[verifikasi]`
- **Hipotesis metode:** situs memanggil API JSON/GraphQL internalnya sendiri untuk hasil pencarian dan detail (laporan scraper pihak ketiga menyebut ini). Utamakan **intersepsi respons** atau panggilan `context.request` ke endpoint tersebut bila terbukti dapat dipakai tanpa token tambahan; fallback ke DOM.
- **Pencarian** `[verifikasi]`: path berbentuk `/<kata-kunci>-jobs` (slug) atau `/id/...`; parameter yang lazim di situs SEEK: `daterange=<hari>` (filter usia), `sortmode=ListedDate` (terbaru), `page=<n>`, filter lokasi dan sistem kerja. Gunakan `daterange` dari `max_age_days` bila ada.
- **Field yang diharapkan** (nama JSON `[verifikasi]`): id, judul, nama pengiklan/perusahaan, lokasi, jenis kerja (`Full time/Part time/Contract/Casual`), pengaturan kerja (`On-site/Hybrid/Remote`), label gaji, tanggal listing (ISO) beserta label relatif, cuplikan/teaser, kategori. Detail memuat deskripsi HTML lengkap.
- **Tanggal:** gunakan tanggal listing ISO bila ada → presisi `exact`/`date`; label relatif hanya cadangan.
- **Pemetaan:** `work_mode_raw` ← pengaturan kerja; `employment_type_raw` ← jenis kerja; `salary_raw` ← label gaji; `external_id` ← ID lowongan.
- **Paginasi/penghentian:** urut terbaru + `daterange`; berhenti saat halaman kosong atau semua hasil lebih tua dari batas.
- **Risiko:** respons 403 pada IP yang ditandai (dilaporkan pihak ketiga). Jika terjadi → `BlockedError`; jangan menembus. Pemilik dapat mengatur proxy sendiri di luar cakupan v1.0.
- **Catatan:** lowongan sering menampilkan "gaji" hanya sebagian; jangan menebak.

### 7.3 Glints

- **Domain:** `https://glints.com/id` `[verifikasi]`. Tidak ada API publik resmi; situs publik dapat diakses tanpa login (laporan pihak ketiga).
- **Hipotesis metode (urut):** (1) `__NEXT_DATA__`/data tertanam pada halaman daftar & detail; (2) intersepsi panggilan GraphQL/REST internal (nama operasi mis. pencarian lowongan `[verifikasi]`); (3) DOM.
- **Pencarian** `[verifikasi]`: halaman *explore* dengan parameter kata kunci, negara `ID`, urutan terbaru, filter "terakhir diperbarui/diposting" bila ada, filter sistem kerja (remote/onsite/hybrid), paginasi `page` atau infinite scroll.
- **Keterbatasan yang dilaporkan:** hasil per kueri dapat dibatasi (pihak ketiga menyebut ±30 per halaman/ per kueri). Mitigasi: paginasi sampai habis, **gunakan banyak `search_term`**, dan jalankan pencarian terpisah untuk remote.
- **Field yang diharapkan:** UUID lowongan, judul, perusahaan, hierarki lokasi (kota, provinsi, negara), `workArrangement` (`ONSITE/HYBRID/REMOTE`), tipe (`FULL_TIME/PART_TIME/CONTRACT/INTERNSHIP/PROJECT_BASED`), gaji (min/max/mata uang/periode), skill, deskripsi, tanggal dibuat dan tanggal diperbarui.
- **Tanggal:** gunakan tanggal **dibuat/diposting** (`createdAt/postedAt` `[verifikasi]`). **Jangan** memakai tanggal `updatedAt`/"diperbarui" sebagai tanggal posting (lihat §5.1) kecuali satu-satunya sumber (presisi `relative`, catat).
- **Pemetaan:** `work_mode_raw` ← `workArrangement`; `employment_type_raw` ← tipe; `salary_raw` ← rangkaian teks dari objek gaji (mis. `"IDR 8,000,000 - 12,000,000 / month"`) agar bisa diparse §5.2.
- **Risiko:** rate limit/CAPTCHA pada volume tinggi (disebut pihak ketiga). Patuhi §4.

### 7.4 Kalibrr

- **Domain:** `https://www.kalibrr.com` (job board Indonesia: `/id-ID/job-board/...`) `[verifikasi]`.
- **Hipotesis metode:** aplikasi web memanggil API JSON internal untuk pencarian dan detail → intersepsi respons; fallback DOM. Pola URL detail diduga `/c/<perusahaan>/jobs/<id>/<slug>` `[verifikasi]`.
- **Pencarian:** kata kunci via kotak/URL pencarian; filter negara Indonesia; filter kota/ tipe bila ada; paginasi offset/halaman `[verifikasi]`. Pihak ketiga melaporkan dukungan pencarian kata kunci + kota dan filter "diposting setelah".
- **Field yang dilaporkan tersedia:** judul, perusahaan, kota, gaji (bila ditampilkan), tipe kerja, **tanggal posting**, **batas lamar** (`application_deadline` → `expires_raw`), kategori/fungsi pekerjaan, ID eksternal, URL.
- **Pemetaan:** `posted_raw` ← tanggal posting (ISO bila ada); `expires_raw` ← batas lamar; `extra.categories` ← kategori.
- **Catatan:** lowongan dapat memuat banyak entri non-IT; pre-filter judul penting untuk menghemat request detail.

### 7.5 Dealls

- **Domain:** `https://dealls.com` (`/loker/<slug>~<perusahaan>` untuk detail; varian `/en/...` untuk bahasa Inggris). Seragamkan ke satu locale.
- **Hipotesis metode:** halaman detail bersifat server-rendered (dapat diambil HTTP-first/`page.content()`), sehingga parsing HTML + JSON-LD/data tertanam memadai; halaman **daftar** memuat sebagian hasil di HTML awal dan membutuhkan interaksi tombol **"Lihat Lebih Banyak"/"See More"** untuk memuat tambahan (pihak ketiga menyebut ini). Situs diduga juga memanggil API internal (mis. di bawah domain induk perusahaan) `[verifikasi]`; jika ditemukan dan stabil, gunakan intersepsi.
- **Pencarian:** halaman `loker` dengan filter kata kunci/lokasi/kategori melalui URL `[verifikasi]`; klik "Lihat Lebih Banyak" hingga batas `max_pages_per_term` atau tidak ada tombol.
- **Peringatan tanggal:** halaman menampilkan teks seperti `Rekruter aktif 8j lalu`/`Actively hiring 7d ago` — itu **aktivitas rekruter, bukan tanggal posting**. Cari tanggal posting sebenarnya di JSON-LD (`datePosted`), data tertanam, atau API. Jika benar-benar tidak ada: `posted_at=NULL`, presisi `unknown` (usia dihitung dari `first_seen_at`) dan catat di platform_notes.
- **Field:** judul, perusahaan, lokasi, mode kerja, tipe, rentang gaji (bila ada), deskripsi (Job Description + persyaratan), tentang perusahaan (abaikan dari deskripsi).
- **Catatan:** banyak lowongan menyatakan "Tidak perlu sign up" untuk melamar; tidak relevan bagi scraper (read-only).

### 7.6 KitaLulus

- **Domain:** `https://www.kitalulus.com`; daftar di `/lowongan`, detail di `/lowongan/detail/<slug>` `[verifikasi]`.
- **Hipotesis metode:** HTML awal memuat sebagian lowongan; tambahan dimuat lewat tombol **"load more"** (pihak ketiga menggunakan Playwright hanya untuk ini) → klik berulang hingga `max_pages_per_term`; ekstraksi daftar dari HTML/data tertanam; detail dari halaman detail.
- **Pencarian:** gunakan pencarian situs/URL filter (kata kunci, lokasi) `[verifikasi]`. Karena fokus platform banyak ke lulusan baru dan pekerjaan operasional, volume lowongan IT bisa rendah — normal.
- **Field yang dilaporkan tersedia:** judul, perusahaan, lokasi, gaji, pendidikan minimal, persyaratan, keahlian, benefit, slug/URL, kemungkinan waktu posting `[verifikasi]`.
- **Tanggal:** cari sumber tanggal posting (teks relatif atau metadata). Bila tidak ada → `unknown`.
- **Pemetaan:** pendidikan/benefit/skill masuk `extra` (tidak disimpan di kolom khusus pada v1.0).

### 7.7 Pintarnya

- **Domain:** `https://pintarnya.com` `[verifikasi]`. Pada riset awal **tidak ditemukan** informasi struktur yang memadai tentang situs ini.
- **Wajib:** jalankan Discovery (§3) penuh. Pertanyaan yang harus dijawab: apakah ada daftar lowongan **publik** di web tanpa login/aplikasi? bagaimana pencarian & paginasi? apakah ada tanggal posting, gaji, sistem kerja? apakah ada lowongan bidang IT?
- **Keputusan setelah discovery:**
  - Jika dapat diakses publik → implementasi normal mengikuti §6.
  - Jika hanya tersedia lewat aplikasi/ login berbayar/ CAPTCHA permanen → scraper tetap dibuat sebagai *stub* yang mengembalikan sub-run `skipped` dengan `errors=[{code:"NOT_PUBLICLY_ACCESSIBLE"}]`, dan catat di `docs/platform_notes/pintarnya.md`. Ini **bukan** kegagalan; run keseluruhan tetap `completed`/`partial` sesuai platform lain.
  - Jika lowongan IT nyaris tidak ada → tetap implementasi sederhana; laporkan temuan ke pemilik.

---

## 8. Registry, Pengujian, dan Definisi Selesai

### 8.1 Registry

```python
# scrapers/registry.py
SCRAPERS: dict[str, type[BaseScraper]] = {
    "jobstreet": JobStreetScraper, "glints": GlintsScraper, "kalibrr": KalibrrScraper,
    "dealls": DeallsScraper, "kitalulus": KitaLulusScraper, "linkedin": LinkedInScraper,
    "pintarnya": PintarnyaScraper,
}
```

Menambah platform baru = tambah satu kelas + satu baris registry + entri `platforms.yaml` + fixture + catatan. Tidak ada perubahan di API/pipeline.

### 8.2 Pengujian per Scraper

| Jenis | Isi |
|-------|-----|
| Parser daftar | ≥ 3 fixture halaman/JSON daftar → jumlah dan field `RawListing` sesuai harapan |
| Parser detail | ≥ 5 fixture detail → `RawJob` memuat judul, perusahaan, deskripsi **tidak terpotong**, tanggal (atau `None` yang disengaja), field lain |
| Kasus tepi | tanpa gaji, tanpa perusahaan, deskripsi sangat panjang, karakter Unicode/emoji, HTML berantakan |
| Contract test | hasil parser lolos validasi skema `RawJob` |
| Smoke `live` | `pytest -m live -k <platform>`: 1 kata kunci, ≤ 2 halaman, ≤ 3 detail; memastikan canary lulus. **Dijalankan manual**, tidak di CI |
| Canary | aturan ARCHITECTURE §5.3 |

### 8.3 Definisi Selesai (per platform)

- [ ] `docs/platform_notes/<platform>.md` lengkap dan jujur tentang perbedaan dari dokumen ini.
- [ ] Parser murni + fixture + test hijau.
- [ ] Navigasi mematuhi §4 (jeda, batas, deteksi tantangan).
- [ ] `fetch_detail` memenuhi §5.6; deskripsi tidak terpotong pada sampel 10 lowongan.
- [ ] Tanggal posting benar sesuai §5.1 (atau `unknown` dengan alasan terdokumentasi).
- [ ] Smoke `live` lulus pada saat implementasi.
- [ ] Gagal dengan status yang benar (`blocked`, `auth_required`, `degraded`, `skipped`) tanpa menjatuhkan run.
- [ ] Tidak ada kredensial/cookie/token di log atau repository.

---

## 9. Catatan Riset Awal (1 November 2026)

Ringkasan yang melandasi hipotesis di atas (bukan verifikasi langsung):

- Beberapa scraper komunitas di marketplace Apify melaporkan bahwa **Glints** dapat dibaca publik tanpa login dan tanpa API resmi, dengan batas hasil per kueri, serta risiko rate limit/CAPTCHA.
- Scraper komunitas untuk **JobStreet** menyebut pemakaian API JSON/GraphQL internal situs (jaringan SEEK), dengan field tanggal listing ISO, pengaturan kerja, jenis kerja, dan deskripsi HTML; juga menyebut kemungkinan HTTP 403 pada IP yang diblokir.
- Scraper komunitas untuk **Kalibrr** menyebut field tanggal posting, batas lamar, kategori, dan ID eksternal untuk Indonesia.
- Untuk **Dealls** dan **KitaLulus**, scraper komunitas memakai pendekatan HTTP-first untuk detail dan Playwright hanya untuk tombol "load more/Lihat Lebih Banyak" pada daftar. Halaman Dealls menampilkan label aktivitas rekruter yang berbeda dari tanggal posting.
- Tidak ditemukan sumber yang memadai untuk **Pintarnya**.
- LinkedIn dikenal memiliki proteksi anti-otomasi dan pembatasan akun; mitigasi di §7.1.

Semua butir di atas **harus diverifikasi ulang** pada tahap Discovery karena dapat berubah sewaktu-waktu.
