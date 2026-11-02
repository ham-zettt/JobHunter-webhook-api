# PRD — Job Scraper API

> **Versi:** 1.0 · **Tanggal:** 1 November 2026 · **Status:** Siap dieksekusi AI Agent
> **Dokumen terkait:** [`ARCHITECTURE.md`](./ARCHITECTURE.md) · [`DATABASE.md`](./DATABASE.md) · [`SCRAPER_SPEC.md`](./SCRAPER_SPEC.md)

---

## 0. Cara Membaca Dokumen Ini (untuk AI Agent)

1. Baca keempat dokumen sebelum menulis kode. PRD ini mendefinisikan **APA** yang dibangun; dokumen lain mendefinisikan **BAGAIMANA**.
2. Setiap requirement punya ID (`FR-xx`, `NFR-xx`, `BR-xx`). Gunakan ID tersebut pada commit message, nama test, dan laporan penyelesaian task.
3. Jika dokumen ambigu atau bertentangan, prioritas: **PRD.md > DATABASE.md > ARCHITECTURE.md > SCRAPER_SPEC.md**. Catat konflik di `docs/DECISIONS.md` dan lanjutkan dengan interpretasi paling konservatif. Jangan berhenti hanya karena ambigu.
4. Kata **WAJIB** = harus dipenuhi. **SEBAIKNYA** = dikerjakan jika tidak menambah risiko. **OPSIONAL** = boleh ditunda.
5. Selector CSS, endpoint internal, dan parameter URL platform di `SCRAPER_SPEC.md` adalah **petunjuk awal, bukan fakta final**. Situs berubah. Agent WAJIB melakukan tahap *discovery* (lihat SCRAPER_SPEC §3) dan mencatat hasilnya sebelum menulis scraper.

---

## 1. Ringkasan Produk

**Job Scraper API** adalah layanan backend (tanpa frontend/UI) berbasis **Python + FastAPI + Playwright** yang mengumpulkan lowongan kerja dari beberapa platform ke satu database terpusat, menormalkan datanya, menyaring berdasarkan kriteria pengguna, menghapus duplikat, lalu menyajikannya lewat **REST API** yang dikonsumsi **n8n**.

### 1.1 Latar Belakang

Pengguna mencari pekerjaan di bidang software engineering dan AI di Pulau Jawa. Lowongan tersebar di 7 platform. Membuka satu per satu secara manual memakan waktu, menghasilkan lowongan yang sama berulang kali, dan mudah melewatkan lowongan baru.

### 1.2 Tujuan

| ID | Tujuan | Indikator Keberhasilan |
|----|--------|------------------------|
| G1 | Mengotomatisasi pengumpulan lowongan dari 7 platform | Semua platform bisa di-scrape lewat API; kegagalan satu platform tidak menggagalkan platform lain |
| G2 | Satu sumber data terpusat dan terstruktur | Semua lowongan tersimpan dengan skema seragam (lihat §6) |
| G3 | Hanya lowongan relevan | ≥ 90% lowongan yang dikembalikan sesuai bidang target (diukur manual pada sampel 50 data) |
| G4 | Tidak ada duplikat yang mengganggu | < 3% duplikat lolos pada sampel 100 data |
| G5 | Mudah dikonsumsi n8n | Alur scrape → polling status → ambil lowongan baru dapat dibuat di n8n tanpa kode tambahan |
| G6 | Data tidak lawas | Filter `max_age_days` bekerja di level scraping dan level query |

### 1.3 Non-Goals (di luar cakupan)

- Tidak ada frontend/UI, dashboard, atau halaman web apa pun (kecuali dokumentasi otomatis Swagger/OpenAPI bawaan FastAPI).
- Tidak ada fitur auto-apply, pengiriman lamaran, atau pengelolaan CV.
- Tidak ada multi-user, registrasi, atau role. Satu API key untuk satu pemilik.
- Tidak ada lowongan di luar Pulau Jawa (kecuali remote, lihat BR-03).
- Tidak ada notifikasi sendiri (email/Telegram). Itu tugas n8n.
- Tidak ada penggunaan LLM di dalam aplikasi ini untuk klasifikasi. Pemfilteran berbasis aturan (rule-based) agar deterministik dan murah.

---

## 2. Pengguna dan Konsumen

| Aktor | Peran |
|-------|-------|
| **Pemilik (user)** | Mengatur kata kunci, memicu scraping, mengekspor data. Satu orang. |
| **n8n workflow** | Konsumen utama API: memicu scraping terjadwal, memantau status, mengambil lowongan baru, mengirim notifikasi. |
| **AI Agent developer** | Membangun aplikasi berdasarkan dokumen ini. |

---

## 3. Keputusan Produk yang Sudah Ditetapkan

| # | Keputusan | Detail |
|---|-----------|--------|
| D1 | Database | **SQLite** (file lokal). Mode WAL. Satu proses penulis. |
| D2 | LinkedIn | **Menggunakan akun login** agar hasil lengkap. Pemilik menerima risiko pembatasan/pemblokiran akun. Wajib mitigasi (lihat §11 dan SCRAPER_SPEC §7.1). |
| D3 | Lowongan remote | **Semua remote di Indonesia ikut masuk**, tidak peduli kota perusahaan. |
| D4 | Frontend | Tidak ada. |
| D5 | Integrasi n8n | Mode *pull* (n8n memanggil API) sebagai jalur utama. *Webhook callback* saat run selesai bersifat SEBAIKNYA. |
| D6 | Autentikasi | API key statis lewat header `X-API-Key`. |
| D7 | Eksekusi scraping | Asinkron (background job). Endpoint scrape langsung mengembalikan `run_id`. |
| D8 | Deployment | Docker (satu container, satu worker uvicorn). |

---

## 4. Cakupan Platform

| Platform | Kode `sumber` | Prioritas | Catatan |
|----------|---------------|-----------|---------|
| JobStreet | `jobstreet` | P1 | Domain `id.jobstreet.com` |
| Glints | `glints` | P1 | Domain `glints.com/id` |
| Kalibrr | `kalibrr` | P1 | |
| Dealls | `dealls` | P1 | |
| KitaLulus | `kitalulus` | P2 | |
| LinkedIn | `linkedin` | P2 | Wajib login; paling berisiko |
| Pintarnya | `pintarnya` | P3 | Struktur belum diketahui; wajib discovery. Jika ternyata tidak memuat lowongan IT, tetap diimplementasikan sebatas yang layak dan didokumentasikan |

Prioritas menentukan **urutan implementasi**, bukan kelengkapan. Semua platform masuk cakupan versi 1.0.

---

## 5. Kriteria Pencarian Pengguna

### 5.1 Bidang Pekerjaan Target

- **Software Engineering:** Frontend, Backend, Fullstack, Web Developer, Programmer, Software Engineer.
- **AI:** AI Engineer, Machine Learning Engineer, LLM/GenAI Engineer, **AI Automation** (termasuk n8n, workflow automation, RPA bila berkaitan dengan AI).

### 5.2 Tipe Kerja

Semua: `fulltime`, `parttime`, `contract`, `freelance`, `internship`. Tipe disimpan dan dapat difilter, tetapi **tidak ada tipe yang dibuang** secara default.

### 5.3 Lokasi

- Onsite/hybrid: hanya yang berlokasi di **6 provinsi Pulau Jawa**: Banten, DKI Jakarta, Jawa Barat, Jawa Tengah, DI Yogyakarta, Jawa Timur.
- Remote: **semua remote di Indonesia** ikut masuk (D3).

### 5.4 Kata Kunci

Kata kunci dikelola sebagai data (tabel `keyword_rules`, di-seed dari `config/keywords.yaml`), bukan hard-coded. Contoh awal dari pengguna: `Software Engineer`, `Backend`, `Frontend`, `Fullstack`, `Developer`, `Programmer`, `Web`, `IT`, `Informatika`. Daftar seed lengkap ada di DATABASE.md §6 dan harus mencakup bidang AI.

> **Catatan desain:** kata `IT`, `Web`, `Informatika` sangat umum dan menghasilkan banyak lowongan tidak relevan (IT Support, Admin Web, Web Designer). Karena itu sistem memakai kata kunci **include**, **exclude**, dan tingkat **kekuatan** (strong/weak). Lihat BR-01.

---

## 6. Output Data (Kontrak Utama)

Setiap lowongan di API WAJIB memuat field berikut (nama field bahasa Indonesia sesuai permintaan pengguna):

| Field | Tipe | Nullable | Keterangan |
|-------|------|----------|------------|
| `url` | string | tidak | URL asli lowongan |
| `tanggal_masuk` | string `YYYY-MM-DD` | ya* | Tanggal lowongan diposting. *Null hanya jika benar-benar tidak bisa ditentukan; lihat `tanggal_masuk_presisi` |
| `sumber` | string (enum) | tidak | `linkedin`, `kitalulus`, `glints`, `kalibrr`, `dealls`, `pintarnya`, `jobstreet` |
| `perusahaan` | string | ya | Nama perusahaan |
| `posisi` | string | tidak | Judul posisi |
| `lokasi` | string | ya | Lokasi sebagaimana ditampilkan platform |
| `sistem_kerja` | string (enum) | tidak | `remote`, `onsite`, `hybrid`, `unknown` |
| `gaji` | string | ya | Teks gaji asli; null jika tidak dicantumkan |
| `deskripsi` | string | tidak | Deskripsi **lengkap, tidak terpotong**, teks bersih |

Field tambahan (WAJIB tersedia, untuk kebutuhan filter dan n8n):

`id`, `external_id`, `tanggal_masuk_presisi` (`exact`/`date`/`relative`/`unknown`), `tipe_kerja`, `kota`, `provinsi`, `gaji_min`, `gaji_max`, `gaji_mata_uang`, `gaji_periode`, `kategori_peran`, `kata_kunci_cocok`, `skor_relevansi`, `is_duplikat`, `duplikat_dari_id`, `pertama_dilihat`, `terakhir_dilihat`, `status`.

Contoh respons:

```json
{
  "id": 1042,
  "url": "https://id.jobstreet.com/id/job/12345678",
  "tanggal_masuk": "2026-10-29",
  "tanggal_masuk_presisi": "exact",
  "sumber": "jobstreet",
  "external_id": "12345678",
  "perusahaan": "PT Contoh Teknologi",
  "posisi": "Backend Engineer (Python)",
  "lokasi": "Jakarta Selatan, DKI Jakarta",
  "kota": "Jakarta Selatan",
  "provinsi": "DKI Jakarta",
  "sistem_kerja": "hybrid",
  "tipe_kerja": "fulltime",
  "gaji": "Rp 12.000.000 – Rp 18.000.000 per bulan",
  "gaji_min": 12000000,
  "gaji_max": 18000000,
  "gaji_mata_uang": "IDR",
  "gaji_periode": "month",
  "deskripsi": "Tanggung jawab: ... (teks lengkap)",
  "kategori_peran": "backend",
  "kata_kunci_cocok": ["backend", "python"],
  "skor_relevansi": 130,
  "is_duplikat": false,
  "duplikat_dari_id": null,
  "pertama_dilihat": "2026-11-01T02:10:00Z",
  "status": "active"
}
```

---

## 7. Requirement Fungsional

### 7.1 Scraping

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-01 | **WAJIB** Scraping per platform lewat API | `POST /api/v1/scrape/{platform}` mengembalikan `202` + `run_id`; run berjalan di background |
| FR-02 | **WAJIB** Scraping seluruh platform | `POST /api/v1/scrape/all` membuat satu run dengan sub-status per platform |
| FR-03 | **WAJIB** Isolasi kegagalan | Jika satu platform gagal, platform lain tetap diproses; status run menjadi `partial`; error tercatat per platform |
| FR-04 | **WAJIB** Parameter run | Body menerima: `keywords` (override opsional), `max_age_days`, `max_jobs_per_platform`, `fetch_details` (default `true`), `callback_url` (opsional) |
| FR-05 | **WAJIB** Pengambilan deskripsi lengkap | Setiap lowongan yang disimpan memiliki deskripsi dari halaman detail, bukan potongan dari halaman daftar. Jika terpotong, `status` ditandai dan tercatat di log (SCRAPER_SPEC §5.6) |
| FR-06 | **WAJIB** Berhenti dini berdasarkan usia | Scraper berhenti paginasi saat lowongan lebih tua dari `max_age_days` (untuk daftar yang terurut terbaru) agar hemat waktu dan mengurangi risiko blokir |
| FR-07 | **WAJIB** Status run | `GET /api/v1/scrape/runs/{run_id}` menampilkan status, progres, total ditemukan/baru/diperbarui/disaring/duplikat, dan error per platform |
| FR-08 | **WAJIB** Satu run aktif pada satu waktu | Permintaan scrape saat run lain berjalan akan masuk antrean (`queued`), bukan paralel |
| FR-09 | SEBAIKNYA | Pembatalan run: `POST /api/v1/scrape/runs/{run_id}/cancel` |
| FR-10 | SEBAIKNYA | Webhook: jika `callback_url` diberikan, kirim `POST` ringkasan run saat selesai (dengan retry 3x) |
| FR-11 | OPSIONAL | Penjadwalan internal via env `SCHEDULE_CRON` (default mati; n8n adalah penjadwal utama) |

### 7.2 Penyaringan

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-20 | **WAJIB** Filter kata kunci | Hanya lowongan yang lolos aturan BR-01 yang disimpan sebagai `active` |
| FR-21 | **WAJIB** Filter lokasi | Aturan BR-02 dan BR-03 diterapkan setelah normalisasi lokasi |
| FR-22 | **WAJIB** Filter usia | Aturan BR-04 diterapkan saat scraping **dan** tersedia sebagai query parameter `max_age_days` pada `GET /jobs` |
| FR-23 | **WAJIB** Pengelolaan kata kunci | CRUD lewat `GET/POST/PATCH/DELETE /api/v1/keywords` |
| FR-24 | **WAJIB** Lowongan yang disaring tidak hilang tanpa jejak | Jumlah yang disaring dihitung per run dan per alasan (`keyword`, `location`, `age`, `duplicate`) |

### 7.3 Deduplikasi

| ID | Requirement | Acceptance Criteria |
|----|-------------|---------------------|
| FR-30 | **WAJIB** Dedup identik dalam platform | Scrape ulang lowongan yang sama (platform + external_id, atau URL kanonik) **memperbarui** baris lama, tidak membuat baris baru |
| FR-31 | **WAJIB** Dedup lintas platform | Lowongan yang sama di platform berbeda ditautkan ke satu lowongan kanonik (aturan BR-05) |
| FR-32 | **WAJIB** Membedakan duplikat vs. lowongan berbeda | Aturan pembeda BR-06 diterapkan; ada unit test untuk setiap aturan |
| FR-33 | **WAJIB** Duplikat tidak dihapus | Baris duplikat tetap disimpan dengan `is_duplikat=true`; API default menyembunyikannya (`include_duplicates=false`) |

### 7.4 REST API

| ID | Requirement |
|----|-------------|
| FR-40 | **WAJIB** `GET /api/v1/jobs` — daftar dengan filter, pencarian, sort, paginasi |
| FR-41 | **WAJIB** `GET /api/v1/jobs/{id}` — detail lengkap |
| FR-42 | **WAJIB** `GET /api/v1/jobs/export` — ekspor `json`, `jsonl`, `csv` dengan filter yang sama seperti daftar |
| FR-43 | **WAJIB** `GET /api/v1/platforms` — daftar platform + status terakhir scrape |
| FR-44 | **WAJIB** `GET /health` — tanpa autentikasi; memeriksa DB dan Playwright |
| FR-45 | **WAJIB** Semua endpoint selain `/health` dan `/docs` memerlukan `X-API-Key` |
| FR-46 | **WAJIB** Parameter `first_seen_after` dan `run_id` pada `GET /jobs` agar n8n bisa mengambil **hanya lowongan baru** |
| FR-47 | SEBAIKNYA | `PATCH /api/v1/jobs/{id}` untuk menandai `archived` |

Kontrak endpoint lengkap: **ARCHITECTURE.md §7**.

---

## 8. Aturan Bisnis

### BR-01 — Aturan Kata Kunci

- Ada tiga jenis aturan: `include`, `exclude`, `search_term`.
- `include` memiliki kekuatan **strong** atau **weak**.
  - *Strong* (mis. `software engineer`, `backend`, `frontend`, `fullstack`, `ai engineer`, `machine learning`, `llm`, `ai automation`, `n8n`): cukup spesifik.
  - *Weak* (mis. `IT`, `web`, `developer`, `informatika`, `programmer`): ambigu; hanya sah bila dicocokkan pada **judul**, dengan batas kata (word boundary, case-insensitive), dan tidak terkena `exclude`.
- Pencocokan dilakukan pada `posisi` (bobot tinggi) dan `deskripsi` (bobot rendah). Rumus skor ada di DATABASE.md §6.3.
- Lowongan **diterima** bila: (a) judul cocok minimal satu `include` dan tidak cocok `exclude` pada judul; **atau** (b) judul tidak terkena `exclude` dan deskripsi mengandung ≥ 2 `include` strong berbeda (skor ≥ ambang `RELEVANCE_THRESHOLD`, default 50).
- Judul yang cocok `exclude` **ditolak** tanpa melihat deskripsi (mis. `IT Support`, `Help Desk`, `Sales`, `Marketing`, `Admin`, `Customer Service`, `Graphic Designer`, `Data Entry`).
- Tidak ada filter senioritas. Semua level (intern sampai lead) diterima.

### BR-02 — Aturan Lokasi Onsite/Hybrid

Lowongan `onsite`/`hybrid` diterima hanya bila kota/provinsi hasil normalisasi berada di 6 provinsi Jawa (tabel `location_aliases`, DATABASE.md §7). Contoh: "Tangerang Selatan", "Bekasi", "Depok", "Bogor", "Bandung", "Semarang", "Yogyakarta/Sleman/Bantul", "Surabaya", "Malang", "Sidoarjo", dst.

### BR-03 — Aturan Remote

- `sistem_kerja = remote` dan lokasi **Indonesia** (termasuk lokasi kosong, `Indonesia`, `Remote`, atau kota Indonesia di mana pun) → **diterima**.
- `remote` dengan lokasi/negara eksplisit **bukan Indonesia** (mis. "Singapore", "Remote – US only") → **ditolak**.
- Lokasi tidak bisa ditentukan sama sekali pada lowongan `onsite`/`hybrid`/`unknown` → **diterima dengan penanda** `lokasi_terverifikasi=false` (konfigurasi `KEEP_UNVERIFIED_LOCATION=true`), agar tidak membuang lowongan potensial karena parsing gagal.
- Lowongan di luar Jawa yang bukan remote → ditolak.

### BR-04 — Aturan Usia

- `max_age_days` = jumlah hari maksimum sejak `tanggal_masuk`. Default `DEFAULT_MAX_AGE_DAYS=14`. Batas atas `90`.
- Jika `tanggal_masuk` tidak diketahui, gunakan `pertama_dilihat` sebagai pengganti untuk perhitungan usia dan set `tanggal_masuk_presisi=unknown`.
- Tanggal relatif ("3 hari lalu") dikonversi memakai waktu scraping, zona **Asia/Jakarta (WIB)**, dan ditandai `relative`.

### BR-05 — Aturan Duplikat

Dua lowongan dianggap **postingan yang sama** bila memenuhi salah satu:

1. `platform` sama dan `external_id` sama.
2. `platform` sama dan `url_canonical` sama.
3. (Lintas/antar posting) perusahaan ternormalisasi sama **dan** kemiripan judul tinggi **dan** lokasi kompatibel **dan** kemiripan deskripsi tinggi (ambang di DATABASE.md §8).

### BR-06 — Aturan Pembeda "Duplikat" vs "Lowongan Serupa Berbeda"

Dianggap **BERBEDA** (jangan digabung) bila salah satu benar:

- Kota/provinsi berbeda (perusahaan yang sama membuka posisi sama di Bandung dan Surabaya = dua lowongan).
- Token senioritas berbeda pada judul (`junior`, `senior`, `lead`, `principal`, `intern`, `magang`, `staff`, `manager`).
- Tipe kerja berbeda (fulltime vs kontrak vs magang).
- Kemiripan deskripsi di bawah ambang meskipun judul sama (posisi berbeda dengan nama generik).
- Stack/teknologi utama pada judul berbeda (mis. `Backend (Go)` vs `Backend (Java)`).

Dianggap **repost** (tetap ditautkan sebagai duplikat, `repost_count` bertambah, tidak dihitung lowongan baru) bila konten identik tetapi `external_id` berbeda pada platform yang sama.

### BR-07 — Siklus Hidup Lowongan

- `active`: terlihat pada scrape terakhir atau belum melewati batas usia.
- `expired`: platform menandai kedaluwarsa, atau tidak terlihat pada ≥ 3 run penuh berturut-turut **dan** usia > `max_age_days`.
- `archived`: ditandai manual.
- Lowongan lama **tidak dihapus** otomatis. Pembersihan data > 180 hari bersifat opsional via skrip.

---

## 9. Requirement Non-Fungsional

| ID | Requirement |
|----|-------------|
| NFR-01 | **Kesopanan scraping.** Jeda acak antar-halaman, batas konkurensi, user-agent wajar, backoff pada 429/403. Detail: SCRAPER_SPEC §4 |
| NFR-02 | **Ketahanan.** Satu halaman/lowongan yang gagal diparse tidak menghentikan run; dicatat dan dilanjutkan |
| NFR-03 | **Observabilitas.** Log terstruktur (JSON) dengan `run_id`, `platform`, `url`; screenshot + HTML disimpan ke `data/debug/` saat parse gagal (dengan batas jumlah file) |
| NFR-04 | **Performa API.** `GET /jobs` < 500 ms untuk 50.000 baris dengan indeks yang ditetapkan |
| NFR-05 | **Idempotensi.** Menjalankan scrape dua kali berturut-turut tidak menambah baris duplikat |
| NFR-06 | **Keamanan.** API key dari env; kredensial/sesi LinkedIn tidak di-commit dan tidak muncul di log; `callback_url` divalidasi (hanya http/https; opsional allowlist host) |
| NFR-07 | **Konfigurasi.** Semua batas (jeda, timeout, ambang) lewat env/`.env` dengan default aman |
| NFR-08 | **Testabilitas.** Setiap scraper punya parser yang dapat diuji dengan fixture HTML/JSON tersimpan, tanpa akses jaringan |
| NFR-09 | **Portabilitas.** Berjalan lewat `docker compose up` pada Linux; data di volume `./data` |
| NFR-10 | **Dokumentasi.** OpenAPI otomatis; `README.md` berisi cara menjalankan, login LinkedIn, dan contoh alur n8n |
| NFR-11 | **Ketahanan DB.** SQLite WAL, `busy_timeout`, satu writer; backup berupa salinan file (skrip `scripts/backup_db.sh`) |

---

## 10. Integrasi n8n

Alur yang harus didukung tanpa modifikasi kode:

```text
[Schedule Trigger]
   → [HTTP Request] POST /api/v1/scrape/all  {"max_age_days": 7}      → simpan run_id
   → [Wait] 60 dtk → [HTTP Request] GET /api/v1/scrape/runs/{run_id}
   → [IF] status ∈ {completed, partial} ? lanjut : kembali ke Wait
   → [HTTP Request] GET /api/v1/jobs?run_id={run_id}&only_new=true&include_description=true
   → [Split In Batches] → [Telegram/Email/Notion/Sheets ...]
```

Alternatif (SEBAIKNYA): kirim `callback_url` = URL Webhook node n8n sehingga polling tidak diperlukan.

Persyaratan khusus untuk n8n:
- Respons selalu JSON dengan `Content-Type: application/json; charset=utf-8`.
- Paginasi sederhana (`page`, `limit`, maks `limit=200`) dengan `total` dan `has_more` pada respons.
- Kode error konsisten (lihat ARCHITECTURE §7.6).
- Nama field stabil (kontrak §6 tidak boleh berubah tanpa menaikkan versi API).

---

## 11. Risiko dan Mitigasi

| Risiko | Dampak | Mitigasi |
|--------|--------|----------|
| **Pelanggaran Terms of Service** platform (terutama LinkedIn, juga yang lain) | Akun diblokir, IP dibatasi, potensi masalah hukum | Pemilik menerima risiko (keputusan D2). Gunakan akun LinkedIn **khusus/cadangan**, bukan akun utama. Batasi volume, jeda panjang, hanya data publik lowongan. Tidak mengambil data pribadi pelamar/rekruter |
| **Anti-bot / CAPTCHA** (LinkedIn, JobStreet, Glints) | Scrape gagal | Preferensikan sumber data JSON internal yang sama dengan yang dipakai situs; jeda acak; deteksi halaman tantangan → hentikan platform itu, tandai `needs_attention`, **jangan** mencoba menembus CAPTCHA |
| **Perubahan struktur situs** | Scraper rusak diam-diam | Validasi skema hasil parse; *canary check* (jika 0 hasil atau field wajib kosong > 30% → run platform ditandai `degraded`); fixture test; log + snapshot debug |
| **Data tidak lengkap** (gaji, tanggal) | Filter kurang akurat | Field nullable, `tanggal_masuk_presisi`, fallback `pertama_dilihat` |
| **SQLite concurrency** | Error `database is locked` | Satu writer, WAL, `busy_timeout`, satu run aktif, satu worker uvicorn |
| **False positive/negative kata kunci** | Lowongan tidak relevan / terlewat | Skema include/exclude/strength, skor relevansi, laporan jumlah yang disaring, kata kunci dapat diubah via API |
| **Sesi LinkedIn kedaluwarsa / checkpoint** | LinkedIn gagal | Skrip login manual (headed) menyimpan sesi; status `auth_required` pada platform; platform lain tidak terpengaruh |

---

## 12. Fase Pengembangan

| Fase | Isi | Hasil yang dapat didemokan |
|------|-----|----------------------------|
| F0 | Fondasi: struktur proyek, config, DB + migrasi, auth, `/health` | `docker compose up` jalan; `/health` OK |
| F1 | Pipeline inti: normalizer, filter kata kunci/lokasi/usia, deduper, repository (diuji dengan data fixture) | Test pipeline hijau |
| F2 | Run manager + endpoint scrape + status + endpoint jobs/export | Scrape dengan scraper *fake* end-to-end via API |
| F3 | Scraper P1: JobStreet, Glints, Kalibrr, Dealls | Data nyata masuk dari 4 platform |
| F4 | Scraper P2: KitaLulus, LinkedIn (login) | 6 platform aktif |
| F5 | Scraper P3: Pintarnya + hardening (retry, canary, debug snapshot) | 7 platform |
| F6 | Webhook callback, backup, README, contoh workflow n8n, tuning dedup | Rilis 1.0 |

Folder `plan/` (dibuat terpisah) menurunkan fase ini menjadi file task berurutan untuk AI Agent.

---

## 13. Kriteria Penerimaan Rilis 1.0

- [ ] Ketujuh platform dapat dipicu lewat `POST /scrape/{platform}` dan `POST /scrape/all`; kegagalan satu platform terisolasi.
- [ ] Setiap lowongan memuat 9 field wajib (§6); `deskripsi` lengkap pada ≥ 95% sampel 50 lowongan per platform yang berfungsi.
- [ ] Filter `max_age_days` terbukti bekerja (test otomatis + verifikasi manual).
- [ ] Menjalankan scrape dua kali berturut-turut tidak menambah baris duplikat (NFR-05).
- [ ] Lowongan remote Indonesia masuk; remote luar negeri dan onsite luar Jawa tidak.
- [ ] Kasus pembeda BR-06 teruji (kota berbeda, senioritas berbeda, repost).
- [ ] Alur n8n §10 dapat dijalankan end-to-end.
- [ ] `pytest` hijau tanpa jaringan; ada penanda `live` untuk uji terhadap situs nyata (dijalankan manual).
- [ ] README lengkap, termasuk prosedur login LinkedIn.

---

## 14. Pertanyaan Terbuka (tidak memblokir pekerjaan)

Agent menggunakan **nilai default** di bawah ini. Pemilik dapat mengoreksi kapan saja.

| # | Pertanyaan | Default yang dipakai |
|---|-----------|----------------------|
| Q1 | Apakah magang (internship) dianggap relevan? | Disimpan dan diterima; dapat difilter via `tipe_kerja` |
| Q2 | Apakah hybrid dianggap dekat dengan "onsite" untuk aturan lokasi? | Ya, hybrid mengikuti aturan lokasi onsite (BR-02) |
| Q3 | Berapa usia maksimum default? | 14 hari |
| Q4 | Apakah perlu notifikasi bawaan? | Tidak; ditangani n8n |
| Q5 | Zona waktu tampilan tanggal? | `Asia/Jakarta` untuk `tanggal_masuk`; timestamp lain UTC (ISO 8601) |

---

## 15. Glosarium

| Istilah | Arti |
|---------|------|
| Run | Satu eksekusi scraping (satu atau banyak platform) |
| Sumber | Platform asal lowongan |
| Kanonik | Lowongan induk yang dipertahankan; duplikatnya menaut ke sini |
| Repost | Lowongan yang sama diposting ulang dengan ID baru |
| Discovery | Tahap menyelidiki struktur nyata situs sebelum menulis scraper |
| Canary check | Pemeriksaan otomatis bahwa scraper masih menghasilkan data wajar |
