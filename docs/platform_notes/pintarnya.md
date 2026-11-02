# Pintarnya — catatan discovery (2026-11-02)

Status: **discovery (F5)** · Dokumen acuan: SCRAPER_SPEC §3, §7.7, §8.1
Belum ada parser/scraper (task 30).

## Keputusan

**Lowongan publik tersedia tanpa login/aplikasi → implementasi normal** (bukan stub
`skipped`). Kode `NOT_PUBLICLY_ACCESSIBLE` **tidak** dipakai.

Bukti: `GET https://pintarnya.com/` → 200; `GET /q-it-support-lowongan` → 200
(23 hasil); `GET /lowongan/it-support-1160847` → 200 (JSON-LD `JobPosting`);
`GET https://api.pintarnya.com/api/v2/pk/job?...` → 200 di konteks browser.
Tidak ada CAPTCHA/login yang menghalangi.

## Metode terpilih

**JSON API internal tanpa login** untuk daftar + **JSON-LD `JobPosting`** untuk detail.

- Daftar: XHR `https://api.pintarnya.com/api/v2/pk/job` yang dipanggil halaman
  pencarian. Respons `data.list[]` (setiap item punya `sublist[0]`) +
  `data.pagination`.
- Fallback/SSR: `__NEXT_DATA__.props.pageProps.initialJobList` hanya memuat halaman 1.
- Detail: `script[type="application/ld+json"]` `@type: JobPosting` + objek
  `__NEXT_DATA__.props.pageProps.jobData` (`page_header`, `description`).
- Panggilan API dari HTTP polos (curl/httpx) ditolak **403 Cloudflare**; di dalam
  konteks browser (cookies sesi) berhasil 200. Tidak memakai stealth dan tidak
  menembus challenge.

## URL pencarian, urutan, dan filter

| Kebutuhan | URL/parameter | Catatan |
|-----------|---------------|---------|
| Pencarian | `/q-<kata>-lowongan` | multi-kata pakai tanda hubung, mis. `/q-software-engineer-lowongan` |
| Urut terbaru | `sort=-published_at` | label "Terbaru"; default `-recommend` |
| Urut terdekat | `sort=+distance` | butuh lokasi |
| Kategori IT | `job_category=17` | "IT dan Teknisi"; `job_category_id` **diabaikan** |
| Lokasi | `city_id`, `province_id` | `-1` = semua; halaman SEO `/l-<lokasi>-lowongan` |
| Filter tanggal | **tidak ada** | usia diturunkan dari tanggal posting |
| Nomor halaman | `page=N` / `p=N` **diabaikan SSR** | paginasi hanya via scroll/API |

Parameter API: `search`, `city_id`, `province_id`, `job_category`, `sort`,
`page`, `page_size` (default 10). Contoh:

```
GET https://api.pintarnya.com/api/v2/pk/job?city_id=-1&province_id=-1&search=it%20support&sort=-published_at&page=1&page_size=10
```

Anomali: sebagian path pencarian mengembalikan HTTP **410** walau `initialJobList`
berisi hasil (mis. `/q-software-engineer-lowongan` → 1 hasil,
`/q-software-lowongan` → 4 hasil). Parser tidak boleh menganggap 410 = kosong;
gunakan isi `initialJobList`/API.

## Endpoint / selector final

Daftar (API, tanpa login):

- `data.list[].sublist[0]` → `id`, `slug`, `title`, `published_at`, `created_at`,
  `updated_at`, `expired_at`, `min_salary`, `max_salary`, `type_of_work`
  (`Onsite`/`Hybrid`/Remote), `type_of_shift`, `type_of_employments[]`,
  `city.name`, `province.name`, `employer.name`, `job_category_id`,
  `min_education_level`, `years_of_experience`, `is_verified`, `is_promoted`.
- Metadata daftar: `data.pagination` → `page`, `page_size`, `total_page`,
  `total_data`.

Detail:

- URL `https://pintarnya.com/lowongan/<slug>`.
- JSON-LD `JobPosting` → `title`, `description` (teks lengkap), `datePosted`,
  `validThrough`, `employmentType[]`, `jobLocation.address`, `baseSalary.value`
  (`minValue`/`maxValue`, `unitText: MONTH`), `hiringOrganization.name`.
- `jobData.page_header` → `type_of_work`, `type_of_employments`, `salary`,
  `city`, `district`, `subdistrict`, `job_category`, `total_vacancies`, `address`.

## Pagination / infinite scroll

- Scroll terjadi pada **container internal** (bukan `window`), yaitu elemen dengan
  `scrollHeight > clientHeight`; setelah mencapai bawah, halaman memanggil API
  `page=2`, `page=3`, dst. Tidak ada tombol "Selanjutnya"/nomor halaman.
- `?page=`/`?p=` di URL **tidak** mengubah daftar SSR.
- `page_size=10`; halaman 1 dapat berisi **12** item karena item promosi.
  Contoh `it support`: total 23 → halaman 12/10/3 (2 item promosi duplikat).
- Berhenti bila `page >= total_page`, `list` kosong, atau batas
  `max_pages_per_term` (config = 5).
- `total_page` terbesar yang terlihat: 301 (`search=it`, 3002 hasil), tetapi
  konfigurasi membatasi 5 halaman/term.

## Sumber tanggal posting

| Konteks | Sumber | Format | Presisi |
|---------|--------|--------|---------|
| Daftar | `published_at` | ISO UTC `2026-11-02T14:05:19.316Z` | `exact` |
| Detail | JSON-LD `datePosted` | `2026-11-02` (tanggal WIB) | `exact` (hari) |
| Detail | JSON-LD `validThrough` | ISO UTC `2026-12-01T17:00:00.000Z` | expiry |

`created_at` (mis. `2026-07-03`) adalah tanggal pembuatan draft, **bukan** tanggal
posting. Tidak ada filter tanggal; pre-filter usia memakai `published_at`.

## Deskripsi lengkap

JSON-LD `description` dan `jobData.description` berisi teks penuh sejak awal
(contoh 427–1923 karakter); tidak terpotong dan tidak perlu klik "selengkapnya".

## Pemetaan field → RawListing/RawJob

| Target | Sumber | Catatan |
|--------|--------|---------|
| `external_id` | `slug` | mis. `it-support-1160847`; `id` numerik juga tersedia |
| `url` / `url_canonical` | `/lowongan/<slug>` | absolut, tanpa query |
| `title` | `title` / JSON-LD `title` | |
| `company` | `employer.name` / `hiringOrganization.name` | |
| `location_raw` | `city.name` + `province.name` | detail juga `district`/`subdistrict` |
| `posted_raw` | `published_at` / JSON-LD `datePosted` | lihat tabel tanggal |
| `expires_raw` | `expired_at` / JSON-LD `validThrough` | |
| `salary_raw` | `min_salary`–`max_salary` / JSON-LD `baseSalary` | IDR per bulan |
| `work_mode_raw` | `type_of_work.name` / `page_header.type_of_work` | "Onsite"/"Hybrid"/remote |
| `employment_type_raw` | `type_of_employments[].name` / JSON-LD `employmentType` | "Full-Time"/"Contract"/"Internship" |
| `description_html`/`text` | JSON-LD `description` / `jobData.description` | teks penuh |
| `extra.kategori` | `job_category` / `job_category_id` | IT = 17 |
| `extra.pendidikan` | `min_education_level.name` | |
| `extra.pengalaman_tahun` | `years_of_experience` | |
| `extra.promoted` | `is_promoted` / `is_highlighted` | item promosi muncul lintas halaman |

## Volume lowongan IT (2026-11-02)

Kategori eksplisit `job_category=17`: **117 lowongan**.

| `search` | Total | Halaman | Catatan |
|----------|-------|---------|---------|
| programmer | 5 | 1 | semua IT |
| developer | 12 | 2 | IT |
| software | 4 | 1 | campuran (HTTP 410) |
| it support | 23 | 3 | IT |
| data | 34 | 4 | campuran (OB, kernet) |
| network | 50 | 5 | campuran sales |
| qa | 39 | 4 | sebagian bootcamp |
| devops | 0 | 0 | HTTP 410 |
| it (pembanding) | 3002 | 301 | pencarian substring terlalu longgar |

Lowongan IT **ada**, tetapi pencarian teks longgar; gunakan `job_category=17` atau
keyword spesifik.

## Kepatuhan & batas laju

- `https://pintarnya.com/robots.txt`:
  `Allow: /lowongan/`, `Allow: /q-*-lowongan`, `Allow: /l-*-lowongan`,
  `Allow: /*-lowongan`; `Disallow: /login`, `/signup`, `/application`,
  `/perusahaan`, `/cv-review`, `/cc`, `/*?search=*`, `/*?sort=*`.
- Scraper hanya mengakses `/q-*-lowongan`, `/lowongan/<slug>`, dan
  `api.pintarnya.com/api/v2/pk/job`. **Tidak** membuka `/login`, `/signup`,
  `/application`, `/perusahaan`, `/cv-review`, `/cc`, atau halaman lamaran.
- `robots.txt` host API tidak memuat aturan `User-agent` (hanya content signal).
  Untuk menghormati larangan `?sort=` di host web, sort diterapkan pada panggilan
  API, bukan URL halaman web.
- 3 halaman berurutan tanpa 429/403 di konteks browser. Config: konkurensi 1,
  jeda 2–5 dtk, 5 halaman/term, 150 detail/run.
- API menolak HTTP polos dengan **403 Cloudflare**; gunakan konteks browser yang
  sama dengan halaman. Tidak ada CAPTCHA nyata pada sampel (string `recaptcha`
  hanya script/CSP, bukan challenge).
- Fixture dibersihkan: tidak ada email/telepon; data pelamar tidak diambil.

## Fixture

`tests/fixtures/pintarnya/`:

- Daftar (3): `list_page_1.json` (12 item), `list_page_2.json` (10),
  `list_page_3.json` (3) — hasil scroll `q-it-support-lowongan?sort=-published_at`.
- Detail (5): `detail_it-support-1160847.json` (Hybrid, gaji),
  `detail_it-support-1133693.json` (English speaker, gaji tinggi),
  `detail_it-support-1046482.json` (Contract), `detail_it-programmer-762180.json`
  (Software Engineer, deskripsi panjang), `detail_it-programmer-1154844.json`.
- Setiap fixture detail berisi `url`, `status`, `json_ld`, `page_header`; tanpa
  HTML mentah/kontak pribadi.

Parser task 30 diuji offline dari fixture ini.

## Risiko / blokir

- API butuh sesi browser (cookies); permintaan HTTP langsung 403. Bila terlalu
  agresif, Cloudflare dapat menantang → hentikan, jangan tembus.
- Struktur `list[].sublist[0]` dan scroll container dapat berubah.
- Item promosi membuat duplikat antarhalaman; dedupe berdasarkan `slug`.
- Keyword pendek (`it`, `software`) mencocokkan substring dan menghasilkan noise;
  gunakan `job_category=17`.
- Status 410 pada sebagian path pencarian tidak selalu berarti kosong.
- Nomor halaman tidak bisa lewat URL; harus scroll/API.

## Perbedaan dari SCRAPER_SPEC.md

- §7.7: domain terkonfirmasi; daftar lowongan **publik tanpa login** → implementasi
  normal, bukan stub `skipped`.
- §7.7: tanggal posting, gaji, sistem kerja, tipe kerja, dan lowongan IT semuanya
  tersedia; lowongan IT ada (±117 pada kategori 17).
- §3: paginasi berupa **infinite scroll** pada container internal, bukan tombol
  "lebih banyak"/parameter halaman.
- §5.7: `external_id` = slug, URL kanonik `/lowongan/<slug>` tanpa query.
- §8.1: `PintarnyaScraper` sudah terdaftar; task 30 tinggal mengganti placeholder.
