# KitaLulus — catatan discovery (2026-11-02)

Status: **discovery (F4)** · Dokumen acuan: SCRAPER_SPEC §3, §5.0, §5.7, §7.6
Belum ada parser/scraper (task 26).

## Metode terpilih

**HTML SSR (Next.js App Router / RSC flight data)** untuk daftar dan detail, tanpa login.

- Daftar `/lowongan` sudah memuat 30 lowongan pertama di HTML awal (data `vacancyList`).
- Pagination memakai tombol **"Lebih Banyak"** yang dijalankan JavaScript; Playwright hanya
  dipakai untuk mengklik tombol ini (sesuai hipotesis §7.6).
- Detail `/lowongan/detail/<slug>` menyertakan **JSON-LD `JobPosting`** lengkap (deskripsi,
  `datePosted`, `validThrough`, gaji, pendidikan, pengalaman, lokasi).
- GraphQL internal `https://gql.kitalulus.com/graphql` (`VacancyFilters`, `VacancyBySlug`,
  `LocationAreas`, `VacancySearchSuggestions`) tersedia tanpa auth, tetapi memakai
  **persisted query hash** yang dapat berubah saat deploy. Tidak dijadikan jalur utama.
- Tidak ada CAPTCHA/challenge pada Chromium headless saat discovery.

## URL pencarian, urutan, dan filter

| Kebutuhan | URL/parameter | Catatan |
|-----------|---------------|---------|
| Pencarian | `/lowongan?sortBy=isHighlighted&keyword=<term>` | pola URL setelah submit form |
| Urut terbaru | `sortBy=updatedAt` | label "Terbaru"; default `isHighlighted` ("Rekomendasi Kitalulus") |
| Lokasi | `location=<kota/provinsi>` | `keyword=developer&location=Jakarta` → 12 hasil (tanpa lokasi 40) |
| Lokasi (SEO) | `/lowongan/in-provinsi-dki-jakarta?keyword=developer` | hasil sama dengan `location=Jakarta` (12) |
| Filter tanggal | **tidak ada** | usia diturunkan dari tanggal (lihat bawah) |
| Nomor halaman | `page=N` **diabaikan** | `page=2`, `page=3` identik dengan halaman pertama |

Catatan: `locationSite`, `province`, dan `location=dki-jakarta` **tidak** memfilter;
satu-satunya parameter lokasi yang terbukti adalah `location=<nama>`.

## Endpoint / selector final

Daftar (SSR, tanpa browser):

- Data: flight data `vacancyList` → `list[]` (bukan JSON-LD daftar).
- Metadata: `hasNextPage`, `elements` (total hasil), `page` (total halaman; 30/halaman).
- Item: `id`, `slug`, `code`, `positionName`, `isHighlighted`, `isClosed`,
  `educationLevelStr`, `salaryLowerBound`, `salaryUpperBound`, `updatedAtStr`,
  `typeStr`, `company.name`, `province.name`, `city.name`, `jobRole.displayName`.
- Fallback DOM: kartu `a[href^="/lowongan/detail/"]`; `h3` judul; `p[title]` perusahaan.
- Klik "Lebih Banyak": tombol tunggal `button` teks **"Lebih Banyak"**.

Detail (SSR, tanpa browser):

- Sumber utama: `script[type="application/ld+json"]` → objek `@type: "JobPosting"`
  (`title`, `hiringOrganization.name`, `description`, `datePosted`, `validThrough`,
  `employmentType`, `jobLocation.address`, `educationRequirements`,
  `experienceRequirements`, `baseSalary`).
- Fallback DOM: `.html-content` (deskripsi), `.html-content` + label "Persyaratan",
  "Keahlian", "Benefit".
- `baseSalary` hanya ada pada sebagian lowongan; ketiadaannya berarti gaji
  "Dapat Dinegosiasikan" (bukan error).
- GraphQL `VacancyBySlug` menyediakan field tambahan: `salaryLowerBound/UpperBound`,
  `typeStr`, `locationSiteStr`, `skillTags`, `benefits`, `closeDate`,
  `formattedDescription`.

## Pagination / "load more"

- 30 lowongan per halaman. `elements` = total hasil; `page` = total halaman.
- Tombol **"Lebih Banyak"** menambah 30 item berikutnya di DOM (bukan navigasi URL).
- Di balik layar: `GET /lowongan?_rsc=<hash>` (Next.js RSC refresh); URL halaman tidak
  berubah. Karena itu **jangan** mencoba `?page=2` — parameter diabaikan server.
- Berhenti bila `hasNextPage=false` / tombol "Lebih Banyak" hilang.
- Batas praktis: `elements` (contoh `admin` = 1197 hasil / 40 halaman) dan
  `max_pages_per_term` (config = 6 → maksimal 180 daftar/term).
- Contoh: `developer` 40 hasil → klik 1× (30 → 40 item), tombol hilang.

## Sumber tanggal posting

| Konteks | Sumber | Format | Presisi |
|---------|--------|--------|---------|
| Daftar | `updatedAtStr` | teks relatif/absolut: "Terakhir diperbarui hari ini", "… 1 hari yang lalu", "… pada 14 Oct 2026" | perkiraan; **bukan** tanggal posting |
| Detail | JSON-LD `datePosted` | ISO UTC `2026-11-02T14:00:58.000Z` | `exact` |
| Detail | JSON-LD `validThrough` | ISO UTC `2026-11-25T17:00:00.000Z` | `exact` (expiry) |

Daftar tidak pernah menampilkan tanggal posting asli. Pre-filter usia di daftar hanya
boleh memakai `updatedAtStr` sebagai perkiraan longgar; tanggal posting final diambil
dari `datePosted` saat detail. Tidak ada label "Diposting" di halaman detail.

## Pemetaan field → RawListing/RawJob

| Target | Sumber | Catatan |
|--------|--------|---------|
| `external_id` | `slug` | juga URL; `id` RSC opaque tidak dipakai |
| `url` / `url_canonical` | `/lowongan/detail/<slug>` | absolut, tanpa query |
| `title` (listing) | `positionName` | |
| `title` (detail) | JSON-LD `title` | |
| `company` | `company.name` / `hiringOrganization.name` | |
| `location_raw` | `city.name` + `province.name` | contoh "Jakarta Selatan, DKI Jakarta"; DOM juga menampilkan satu baris |
| `posted_raw` (listing) | `updatedAtStr` | label "Terakhir diperbarui", bukan posting |
| `posted_raw` (detail) | JSON-LD `datePosted` | ISO UTC |
| `expires_raw` | JSON-LD `validThrough` / RSC `closeDate` | `closeDate` mikrodetik |
| `salary_raw` | JSON-LD `baseSalary` (`IDR`, `MONTH`, min/max) | fallback `salaryLowerBound/UpperBound`; 0/0 = negosiasi |
| `work_mode_raw` | `locationSiteStr` / teks DOM | mis. "Kerja dari manapun (Remote)", "Kerja dari kantor (WFO)" |
| `employment_type_raw` | JSON-LD `employmentType` (`FULL_TIME`/`CONTRACTOR`/`INTERN`) | listing `typeStr` berbahasa Indonesia ("Full-Time", "Kontrak", "Freelance") |
| `description_html` | JSON-LD `description` / RSC `formattedDescription` | HTML lengkap |
| `description_text` | konversi HTML (parser task 26) | DOM `.html-content` teks sama panjang; tidak terpotong |
| `extra.pendidikan` | `educationLevelStr` / `educationRequirements` | |
| `extra.pengalaman_bulan` | `experienceRequirements.monthsOfExperience` | |
| `extra.skill` | RSC `skillTags` | daftar teks |
| `extra.benefit` | RSC `benefits` (sering `null`) + bagian DOM "Benefit" | |
| `extra.kategori` | `jobRole.displayName` | |
| `extra.promoted` | `isHighlighted` | item "Dipromosikan" muncul lintas keyword |

## Volume lowongan IT (2026-11-02)

| `search_term` | Total hasil | Halaman |
|---------------|-------------|---------|
| software engineer | 2 | 1 |
| developer | 40 | 2 |
| backend developer | 3 | 1 |
| frontend developer | 0 | 0 |
| fullstack developer | 2 | 1 |
| python developer | 0 | 0 |
| web developer | 3 | 1 |
| data analyst | 8 | 1 |
| IT support | 48 | 2 |
| programmer | 5 | 1 |
| devops | 2 | 1 |
| quality assurance | 38 | 2 |
| admin (non-IT, pembanding) | 1197 | 40 |
| desain grafis (non-IT, pembanding) | 118 | 4 |

Volume IT memang rendah (sesuai peringatan §7.6). Hasil pencarian juga memuat item
"Dipromosikan" (mis. Misi Seru) yang tidak selalu relevan dengan keyword.

## Kepatuhan & batas laju

- `robots.txt`: `Disallow: /auth/`, `Disallow: /my/`; sitemap tersedia. Scraper hanya
  mengakses `/lowongan` dan `/lowongan/detail/<slug>`; **tidak** membuka `/auth/`, `/my/`.
- Tanpa login, tanpa stealth, tanpa menembus CAPTCHA (tidak ada challenge pada sampel).
- Batas laju aman yang diamati: permintaan berurutan 1 dtk tidak memicu 429/403.
  Pakai config: konkurensi 1, jeda acak 2–5 dtk, maks 6 halaman/term, 200 detail/run.
- Tidak menyimpan kontak pribadi: email/telepon pada fixture diredaksi menjadi
  `[redacted-email]` / `[redacted-phone]`.

## Fixture

`tests/fixtures/kitalulus/` (HTML asli, kontak diredaksi):

- Daftar (5): `search_developer.html` (40 hasil), `search_developer_page2.html`
  (setelah klik "Lebih Banyak": 40 item), `search_admin.html` (1197 hasil),
  `search_software_engineer.html` (2 hasil), `search_developer_jakarta.html`
  (filter lokasi, 12 hasil).
- Detail (7): `detail_backend-developer-dpfd.html` (full-time, tanpa gaji),
  `detail_fullstack-developer-angular-java-spring-bootout-gdvm.html` (kontrak, gaji
  min/max), `detail_frontend-developer-r5fl.html`, `detail_mobile-developer-intern-vqgu.html`
  (intern), `detail_admin-lsin.html` (non-IT), `detail_quality-assurance-qa-muvz.html`
  (gaji), `detail_misi-seru-remote-hadiah-puluhan-ribu-freelance-dar-xxja.html`
  (freelance/remote).

Parser diuji tanpa jaringan pada task 26.

## Risiko / blokir

- Persisted query hash GraphQL dapat berubah; karena itu jalur utama memakai SSR HTML,
  bukan GraphQL.
- Struktur flight data `vacancyList`/`list` dan teks tombol "Lebih Banyak" dapat berubah
  → parser task 26 harus punya fallback DOM dan mendeteksi perubahan.
- `page=N` diabaikan; jangan mengandalkan paginasi URL.
- Tanggal di daftar adalah "Terakhir diperbarui", bukan tanggal posting. Jangan memakai
  `updatedAtStr` sebagai `posted_at` final bila `datePosted` tersedia.
- `salaryLowerBound/UpperBound = 0/0` berarti negosiasi, bukan gaji 0.
- Sebagian deskripsi memuat nomor telepon/email rekruter; wajib diredaksi saat menyimpan
  fixture, dan tidak boleh masuk DB sebagai kontak.

## Perbedaan dari SCRAPER_SPEC.md

- §7.6: mekanisme "load more" **terkonfirmasi** (tombol "Lebih Banyak", +30 item/klik);
  Playwright hanya untuk klik, bukan untuk ekstraksi.
- §7.6: tanggal posting **tersedia** pada detail lewat JSON-LD `datePosted` (bukan
  `unknown`); daftar tetap hanya punya `updatedAtStr`.
- §5.7: `external_id` = slug (sesuai), URL kanonik `https://www.kitalulus.com/lowongan/detail/<slug>`
  tanpa query; RSC juga punya `id` opaque yang tidak dipakai.
- §3: `?page=` tidak berlaku untuk platform ini; paginasi wajib lewat klik tombol.
