# LinkedIn — catatan discovery & implementasi

Tanggal: 2026-11-02/03 · Status: **discovery selesai; parser belum (task 28)** · Acuan: SCRAPER_SPEC §4, §5.7, §7.1

Discovery dijalankan **headed** memakai sesi login manual (`storage_state`), bukan headless
dan bukan login otomatis. Tidak ada checkpoint/CAPTCHA yang ditemui.

## Ringkasan metode

UI baru LinkedIn (SDUI) menampilkan dua panel dalam satu dokumen:
daftar lowongan di kiri dan preview detail lowongan terpilih di kanan.
Tidak ada endpoint/API yang dipakai; data dibaca dari DOM.

- Daftar: `https://www.linkedin.com/jobs/search-results/?keywords=<term>&location=Indonesia&f_TPR=<...>`
- Detail: `https://www.linkedin.com/jobs/view/<id>/` (halaman detail langsung)
- Path lama `/jobs/search/` **jangan dipakai**: ia redirect ke `/jobs/search-results/?currentJobId=...`
  dan mengabaikan `location=Indonesia` (hasil memakai lokasi profil, mis. `Sidoarjo (40 km)`).

## Autentikasi

| Hal | Nilai | Bukti |
|-----|-------|-------|
| Skrip login | `scripts/linkedin_login.py` (headed, profil bersih) | kode |
| State | `data/secrets/linkedin_state.json`, `LINKEDIN_STATE_PATH` | `app/core/config.py:36` |
| Permission | `-rw-------` (600), ditulis atomik `tmp → chmod → replace` | `ls -l` |
| Validasi sebelum simpan | buka `/jobs/`, tolak `/login`, `/checkpoint`, `/authwall`, `/uas/`, `/signup` | kode |
| Isi state | hanya `cookies` + `origins`; tidak ada kata sandi dan isi tidak dicetak | inspeksi kunci |
| `auth_state` | `missing` / `expired` (>30 hari) / `valid` | `_auth_state()` → `valid` |
| Git | `data/` diabaikan (`.gitignore:5`) | `git check-ignore` |

`auth_state` hanya berbasis keberadaan + umur file, **bukan** hasil `check_session()`.
`check_session()` untuk runtime tetap tugas task 28.

Membaca state **tidak** boleh dilakukan di container headless; login hanya di mesin lokal.

## Parameter pencarian (terbukti)

| Param | Nilai | Bukti |
|-------|-------|-------|
| path | `/jobs/search-results/` | `/jobs/search/` redirect & location hilang |
| `keywords` | `<term>` | tetap ada di `final_url`; hasil relevan |
| `location` | `Indonesia` | hasil lintas kota (Bandung, Jakarta, Malang), tanpa radius `(40 km)` |
| `geoId` | `102478259` | hasil identik dengan `location=Indonesia`; alternatif bila lokasi tidak resolve |
| `f_TPR` | `r604800` | chip `1 minggu terakhir`; 6 hasil pada satu run |
| `f_WT` | `2` | chip `Jarak jauh`; kartu `Indonesia (Jarak Jauh)` |

Belum terbukti (jangan dipakai sebagai fakta):
- `sortBy=DD` — hilang dari `final_url`, urutan tidak diverifikasi.
- `start=<offset>` — kontrol paginasi ada di DOM
  (`data-testid="pagination-controls-next-button-visible"`), tetapi parameter offset belum diuji.
- `f_TPR` nilai lain (mis. `r86400`) — hanya `r604800` yang diuji.
- Label UI bahasa Inggris — sesi discovery memakai `locale=id-ID`.

Batas: `max_pages_per_term` 4, 60 detail/run, 150 detail/hari WIB, konkurensi 1, jeda 4–9 dtk.

## Selector (terbukti dari fixture)

Kelas CSS baru **acak** (`b6bk8d`, `b6blrj`, ...) dan berubah antar-deploy. Jangan memakai kelas.
Selector yang stabil hanya `componentkey`, `data-testid`, href, dan struktur/teks.

### Kartu daftar

| Target | Selector |
|--------|----------|
| Kartu | `[componentkey^="job-card-component-ref-"]`; ID = sufiks numerik `componentkey` |
| Judul bersih | di dalam kartu: `p span[aria-hidden="true"]` (span visual memuat prefiks `Dipilih, ` / sufiks `(Pekerjaan terverifikasi)`) |
| Perusahaan | `p` kedua di kartu |
| Lokasi + sistem kerja | `p` ketiga, mis. `Bondowoso (Di Kantor)`, `Indonesia (Jarak Jauh)` |
| Status | teks `Diposting…`, `Disimpan`, `Dilihat`, `Melamar Mudah`, `Meninjau pelamar secara aktif` |
| Tombol abaikan | `button[aria-label^="Abaikan lowongan "]` |

Satu kartu menghasilkan **2–3 node** dengan `componentkey` yang sama → dedupe berdasarkan ID.
Tidak ada `data-job-id`/`data-occludable-job-id` dan tidak ada `<a href="/jobs/view/...">` di kartu;
kartu adalah `div[role="button"]` dan tautan internalnya memakai `?currentJobId=<id>`.

### Panel detail

| Target | Selector |
|--------|----------|
| Judul | `[data-display-contents] p` pertama (tidak ada `<h1>`; judul juga ada di `<title>`) |
| Perusahaan | `a[href^="/company/"]` |
| Lokasi + waktu | `p` berisi pemisah `·`, mis. `Surabaya, Jawa Timur, Indonesia · 1 minggu yang lalu` |
| Deskripsi | `[data-testid="expandable-text-box"]` |
| Tombol perluasan | `[data-testid="expandable-text-button"]`, teks `...lainnya` (Inggris: `...more` — belum diverifikasi) |
| Sistem kerja | teks pil `Di Kantor` / `Jarak jauh` / `Hybrid` |
| Tipe kerja | teks pil `Penuh waktu` / `Paruh waktu` / `Kontrak` / `Magang` |
| Gaji | teks, mis. `Rp6M/month - Rp10M/month` (tidak selalu ada) |
| Waktu | **relatif saja**: tidak ada `<time>` maupun atribut `datetime` |

Teks deskripsi sudah termuat penuh di DOM (dipotong secara visual); klik perluasan tetap
dilakukan sesuai SCRAPER_SPEC §7.1(c) untuk memastikan teks terbuka.

## Fixture

`tests/fixtures/linkedin/` (DOM bersih: script/style/iframe dihapus, URL pelacakan
dinormalisasi, nama akun & kartu orang/rekruter dibuang, email/telepon diredaksi):

- `search_indonesia_week.html` — 25 kartu, `location=Indonesia&f_TPR=r604800`, chip `1 minggu terakhir`.
- `search_remote_filter.html` — 25 kartu, `f_WT=2`, chip `Jarak jauh`, detail remote.
- `search_last_week.html` — 6 kartu (hasil sedikit), chip `1 minggu terakhir`.
- `detail_4481158304.html` — penuh waktu, bergaji.
- `detail_4482985280.html` — penuh waktu, tanpa gaji.
- `detail_4481630924.html` — kontrak, tanpa gaji.
- `detail_4477060658.html` — penuh waktu, tanpa gaji.
- `detail_4484092568.html` — penuh waktu, deskripsi panjang.

Halaman daftar memuat daftar + preview detail pertama; halaman detail langsung hanya detail.

## Risiko

- Risiko tertinggi dari semua platform (ToS, pembatasan/pemblokiran akun). **Gunakan akun
  khusus/cadangan**, bukan akun utama; jangan jalankan banyak instance bersamaan.
- Sesi kedaluwarsa → `auth_required` dengan pesan "Jalankan scripts/linkedin_login.py";
  tanpa login otomatis dan tanpa retry.
- Checkpoint/CAPTCHA/`authwall`/999 → `BlockedError`; **jangan** ditembus.
- Kelas CSS acak dapat berubah; parser harus bergantung pada `componentkey`/`data-testid`/teks
  dan menghasilkan `SiteChangedError` bila kartu/deskripsi tidak ditemukan.
- UI dapat berubah ke single-column atau menonaktifkan `componentkey`; canary wajib.
- Read-only: jangan menekan Apply/Easy Apply/Save/Follow/Connect/Message/Report.
- Jangan menyimpan data rekruter/pemosting; fixture sudah dibersihkan dari kartu orang.

## Perintah discovery (reproduksi)

```bash
uv run python scripts/linkedin_login.py
uv run python scripts/discover_platform.py linkedin --headed --interactive \
  --storage-state data/secrets/linkedin_state.json --wait-ms 8000 --url "<url>"
```

## Sisa untuk task 28

- `check_session()` + `AuthRequiredError` saat state hilang/redirect.
- Verifikasi `start`/paginasi, `sortBy`, UI bahasa Inggris, dan detail remote.
- Parser kartu + detail memakai selector di atas; test offline dari fixture.
