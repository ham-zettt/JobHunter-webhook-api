# Kalibrr — catatan discovery (2026-11-02)

Status: **implemented (task 22)** · Scraper: `app/scrapers/platforms/kalibrr.py` · Dokumen acuan: SCRAPER_SPEC §3, §5.0, §5.7, §7.4, §8.1

## Metode terpilih

**Daftar: XHR/JSON API internal. Detail: HTML + `__NEXT_DATA__`.**

- Keduanya dapat diakses tanpa login dan tanpa cookie (cukup `User-Agent` biasa),
  memakai `httpx`/`curl`; browser tidak diperlukan.
- JSON-XHR dipilih untuk daftar karena bentuknya stabil, memuat semua field kartu,
  dan paginasi berbasis `offset`.
- Detail dibaca dari `script#__NEXT_DATA__` → `props.pageProps.job`. JSON-LD di halaman
  detail hanya `WebSite`, **bukan** `JobPosting`, jadi tidak bisa dipakai.
- Endpoint Next data (`/_next/data/<buildId>/...json`) mengembalikan payload yang sama,
  tetapi `buildId` berubah tiap deploy. HTML + `__NEXT_DATA__` dipilih agar tidak
  bergantung pada `buildId`.

Headless Chromium juga memuat halaman pencarian/detail tanpa tantangan, tetapi tidak
dipakai karena API/HTML biasa sudah cukup.

Semua endpoint/selector di bawah sudah diverifikasi pada 2026-11-02; tidak ada penanda
`[verifikasi]` yang tersisa untuk item yang dipakai.

## URL pencarian

Halaman publik: `https://www.kalibrr.com/id-ID/home/te/<kata-kunci>`

- `/id-ID/job-board/...` (dugaan §7.4) **308 redirect** ke `/id-ID/home`.
- `?query=...`, `?page=2`, `?offset=15`, dan `/home/te/<term>/2` **diabaikan** oleh SSR;
  satu-satunya bentuk yang bekerja adalah segmen path `te/<kata-kunci>`.
- `?sort=Freshness` bekerja di SSR (halaman pertama).
- Filter negara Indonesia di API: `country=Indonesia` (count turun 324 → 287 pada
  kueri contoh).
- Tidak ada parameter filter tanggal/rentang tanggal yang ditemukan.

| Param API | Nilai | Catatan |
|-----------|-------|---------|
| `text` | kata kunci | contoh `software+engineer`; sama dengan segmen `te/` |
| `limit` | 15 (default), diuji 100/1000 | `1000` mengembalikan seluruh `count` (324) |
| `offset` | 0, 15, 30, ... | paginasi; lihat bagian Pagination |
| `country` | `Indonesia` | filter negara |
| `is_work_from_home` | boolean | filter remote |
| `is_hybrid` | boolean | filter hybrid |
| `tenure` | `Full time`, `Contractual`, ... | tipe kerja |
| `function` | `IT and Software`, ... | kategori/fungsi |
| `location` | nama lokasi | filter lokasi |
| `sort` | — | **tidak didukung** endpoint XHR (diabaikan) |

Endpoint final:

```text
# daftar (paginasi)
GET https://www.kalibrr.com/kjs/job_board/search?limit=15&offset=0&text=software+engineer&country=Indonesia

# detail
GET https://www.kalibrr.com/id-ID/c/<company.code>/jobs/<id>/<slug>
GET https://www.kalibrr.com/_next/data/<buildId>/id-ID/c/<company.code>/jobs/<id>/<slug>.json?code=<company.code>&param=<id>&param=<slug>
```

`<company.code>`, `<id>`, dan `<slug>` berasal dari respons daftar (`company.code`,
`id`, `slug`). `<buildId>` dibaca dari `__NEXT_DATA__.buildId` bila memakai endpoint
Next data.

## Pagination

- Mekanisme: **offset-based**. UI menampilkan tombol `Load more jobs`; klik memicu
  `GET /kjs/job_board/search?limit=15&offset=<n>&text=<term>`.
- Respons memuat `count` total dan `jobs[]` (15 item pada `limit=15`).
- Berhenti bila `offset >= count`, `jobs` kosong, atau batas internal scraper tercapai.
- `limit=1000` mengembalikan seluruh hasil (324/324) — tidak ada cap yang teramati.
  Untuk kesopanan gunakan `limit` kecil (15–50) dan offset bertahap.
- **Jebakan penting:** `offset` melewati `count` **mengabaikan `text`** dan jatuh ke
  feed umum. Contoh: `text=software engineer&offset=1000` → `count=1941`, 15 lowongan
  umum. Karena itu paginasi wajib dibatasi oleh `count` dari halaman pertama.
- Cakupan per kueri = `count` saat itu: kueri contoh `software engineer` = 324,
  tanpa `text` = ±1941. Tidak ada batas keras selain `count`.

## Urutan terbaru dan filter tanggal

- Nilai `sort` yang tersedia di UI: `Relevance`, `Alphabetical`, `Salary`,
  `Expiry Date`, `Freshness`.
- `?sort=Freshness` **bekerja di SSR** halaman pertama: 15 lowongan pertama terurut
  `activationDate` terbaru.
- Endpoint XHR **mengabaikan sort**: `sort=Freshness`, `sort=freshness`,
  `sort_by=Freshness`, dan `order_by=activation_date` semuanya mengembalikan urutan
  relevance yang sama. Jadi untuk halaman 2+ tidak ada jaminan urutan terbaru dari API.
- Tidak ada filter tanggal (`daterange`/`from`/`to`) yang ditemukan. `max_age_days`
  harus diterapkan lokal dari `activation_date` (pre-filter/henti-dini), bukan dikirim
  ke platform.

## Sumber tanggal posting

| Keperluan | Field daftar | Field detail | Format |
|-----------|--------------|--------------|--------|
| tanggal posting | `activation_date` | `activationDate` | ISO 8601 UTC, mis. `2026-11-02T06:39:13.540414+00:00` |
| batas lamar | `application_end_date` | `applicationEndDate` | ISO 8601 UTC, mis. `2026-12-31T17:00:00+00:00` |
| dibuat (bukan posting) | `created_at` | `createdAt` | ISO 8601 UTC, lebih awal dari aktivasi |

`posted_raw` = `activation_date`/`activationDate` (presisi `exact` setelah parser tanggal).
`expires_raw` = `application_end_date`/`applicationEndDate`. Nilai `17:00:00+00:00`
berarti 00:00 WIB hari berikutnya; parser harus menghormati offset, bukan memotong tanggal.

## Lokasi deskripsi dan kelengkapan

- Detail menyimpan deskripsi dalam dua field HTML terpisah:
  `description` dan `qualifications`.
- Deskripsi lengkap = `description` + `qualifications` (urutan dipertahankan).
  Field `duties`, `responsibilities`, `requirements` ada tetapi `null` pada 5 sampel;
  bila terisi, ikut digabung.
- Tidak ada tombol "selengkapnya" dan tidak ada pemotongan pada 5 sampel detail.
  `description_html` diisi gabungan HTML tersebut; teks dihasilkan lewat
  `app/scrapers/common/text.html_to_text` pada task 22.
- Daftar XHR juga membawa `description`/`qualifications`, tetapi detail tetap dipakai
  agar konsisten dan mendapat `formattedAddress`.

## Pemetaan field → `RawJob`

| Sumber daftar (XHR) | Sumber detail (`__NEXT_DATA__`) | Target |
|---------------------|----------------------------------|--------|
| `id` | `job.id` | `external_id` (angka) |
| `name` | `job.name` | `title` |
| `company_name` | `job.companyInfo.name` | `company` |
| `google_location.address_components` | `job.googleLocation.addressComponents` / `formattedAddress` | `location_raw` |
| `activation_date` | `job.activationDate` | `posted_raw` |
| `application_end_date` | `job.applicationEndDate` | `expires_raw` |
| `tenure` | `job.tenure` | `employment_type_raw` |
| `is_work_from_home`, `is_hybrid` | idem | `work_mode_raw` (`Remote`/`Hybrid`/`On-site`) |
| `salary_shown`, `minimum_salary`, `maximum_salary`, `salary_currency`, `salary_interval` | `job.salaryShown`, `minimumSalary`, `maximumSalary`, `salaryCurrency`, `salaryInterval` | `salary_raw`; bila `salaryShown=true` tetapi angka `null`, isi `None` |
| `description`, `qualifications` | `job.description`, `job.qualifications` | `description_html`/`description_text` |
| `function`, `education_level`, `work_experience`, `perks` | `job.function`, `educationLevel`, `workExperience`, `perks` | `extra` |
| — | URL detail | `url`/`url_canonical` |

URL kanonik dari `<link rel="canonical">`: **tanpa locale**, yaitu
`https://www.kalibrr.com/c/<company.code>/jobs/<id>/<slug>` (tanpa query).
`/id-ID/...` adalah alternate `id-ID`; keduanya `200`. Pola `external_id` = angka `<id>`
pada path, sesuai §5.7.

## Batas laju aman yang diamati

- 8 permintaan API beruntun tanpa jeda: semuanya `200`, latensi 0,5–7,1 dtk,
  tanpa `429`, `403`, `Retry-After`, atau CAPTCHA.
- Halaman HTML via `curl` dan headless Chromium juga `200` tanpa challenge.
- `robots.txt`: `User-agent: *` hanya `Disallow: /root` dan `/candidate/profile`.
  Halaman pencarian, API `/kjs/job_board/search`, dan detail lowongan tidak dilarang.
- Tetap pakai batas `config/platforms.yaml` (jeda acak, konkurensi 2) pada task 22;
  discovery ini tidak menetapkan batas baru.

## Risiko / blokir yang ditemui

- `__NEXT_DATA__` dan bentuk API dapat berubah; parser harus gagal sebagai
  `SiteChangedError`, bukan menghasilkan data kosong.
- `sort=Freshness` hanya berlaku SSR halaman pertama; API XHR mengabaikan sort.
- `offset` melewati `count` mengembalikan feed umum (bukan kosong) → wajib guard `count`.
- `salaryShown=true` tidak menjamin `minimumSalary`/`maximumSalary` terisi.
- Banyak hasil non-IT untuk kata kunci umum (Sales, Civil Engineer, Marketing);
  pre-filter judul/fungsi tetap wajib di pipeline.
- `applicationEndDate` memakai offset UTC `17:00`; konversi WIB menggeser tanggal.
- Detail tidak punya JSON-LD `JobPosting`; jangan mengandalkan JSON-LD.

## Fixture

`tests/fixtures/kalibrr/`:

- `search_p1.json`, `search_p2.json`, `search_p3.json` — respons asli
  `/kjs/job_board/search` offset 0/15/30 (`count=324`, 15 lowongan/halaman).
- `search_software_engineer.html` — halaman SSR `?sort=Freshness`; data 15 lowongan
  pertama ada di `__NEXT_DATA__` (bukti route pencarian dan fallback SSR).
- `detail_275125.html` — Contractual; `salaryShown=true` tetapi angka gaji `null`.
- `detail_263888.html` — Full time, WFH (`isWorkFromHome=true`).
- `detail_272823.html` — Full time, hybrid (`isHybrid=true`).
- `detail_275079.html` — Full time, `salaryShown=false`, `maximumSalary=15000000`.
- `detail_272018.html` — Contractual, `applicationEndDate` hari discovery.

Semua detail memuat `script#__NEXT_DATA__`. Tidak ada nama/kontak rekruter, email
pribadi, atau nomor telepon; satu-satunya email adalah alamat generik Kalibrr
(`hirenow@kalibrr.com`) di chrome halaman.

## Perbedaan dari SCRAPER_SPEC.md

- §7.4 menduga `/id-ID/job-board/...`; kenyataannya `/id-ID/job-board` **redirect**
  ke `/id-ID/home`, dan pencarian memakai `/id-ID/home/te/<kata-kunci>`.
- §7.4 menduga "API JSON internal"; terbukti endpoint-nya
  `GET https://www.kalibrr.com/kjs/job_board/search` (tanpa token/kredensial).
- §5.7 menyebut `external_id` angka dari `/c/<company>/jobs/<id>/<slug>` — **sesuai**.
  Hanya saja URL kanonik situs tidak memakai locale: `https://www.kalibrr.com/c/...`.
- JSON-LD di halaman detail hanya `WebSite`, bukan `JobPosting`; data detail wajib dari
  `__NEXT_DATA__`.
- Tidak ada filter tanggal di platform; `sort=Freshness` hanya bekerja di SSR halaman
  pertama, tidak di endpoint paginasi.
- Deskripsi detail terbagi menjadi `description` + `qualifications`; keduanya harus
  digabung agar deskripsi tidak terpotong.
- Parameter URL `?query=`, `?page=`, dan `?offset=` pada halaman HTML diabaikan SSR.
