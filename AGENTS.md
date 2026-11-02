## Proyek

Job Scraper API: Python 3.12 + FastAPI + Playwright + SQLite. Tanpa frontend.
Spesifikasi: `PRD.md`, `DATABASE.md`, `ARCHITECTURE.md`, `SCRAPER_SPEC.md`
(prioritas: PRD > DATABASE > ARCHITECTURE > SCRAPER_SPEC). Keputusan: `docs/DECISIONS.md`.

## Perintah

```bash
uv run pytest <path> 2>&1 | tail -3   # pyproject sudah addopts "-q": JANGAN tambah -q
uv run pytest 2>&1 | tail -3          # suite penuh (offline; live dikecualikan)
uv run ruff check app tests
uv run python scripts/codemap.py      # regenerasi docs/CODEMAP.md
graphify update .                     # setelah kode berubah (AST-only)
```

## Peta folder

- `app/api/` router + schema Pydantic · `app/services/` validasi/query/ekspor
- `app/runner/` RunManager + Orchestrator · `app/scrapers/` BaseScraper, BrowserPool, registry, `platforms/`
- `app/pipeline/` normalizer, lokasi, classifier, usia, deduper · `app/db/` model, FTS5, repository
- `config/` seed keyword, alias lokasi, batas platform · `plan/` README, PROGRESS, NOTES

## Aturan keras

- Scraper TIDAK menyentuh DB; hanya menghasilkan `RawListing`/`RawJob`.
- Filter, dedup, keputusan bisnis HANYA di `app/pipeline/`.
- Nama field, tabel, enum, env variable PERSIS seperti dokumen sumber.
- Selector/endpoint tanpa discovery (`docs/platform_notes/<platform>.md`) DILARANG.
  Pertahankan penanda `[verifikasi]`.
- Jangan menembus CAPTCHA/checkpoint, memakai stealth, atau menyimpan kredensial.
- Jangan menandai task `[x]` tanpa bukti file + test lulus.
- Jangan menjalankan test `live`.

## Efisiensi token (WAJIB, prioritas tertinggi)

Setiap turn mengirim ulang seluruh konteks. Biaya utama = JUMLAH turn, bukan ukuran output.
Target: task L ≤ 22 turn, task M/S ≤ 12 turn.

1. **Tool call paralel.** Semua read/grep/bash yang tidak saling bergantung
   dikirim dalam SATU turn. Dilarang membaca file satu per satu antar turn.
2. **Fase Baca = 1-2 turn.** Turn 1: dalam SATU blok paralel, baca file task,
   semua file di "File yang perlu dibaca" (read utuh bila ≤250 baris; bila lebih,
   offset+limit ≤250), bagian SPEC/ARCH yang dirujuk (`grep -n` heading + `sed -n`
   rentang pasti dalam satu bash), dan `head -5` + `grep -n '\[~\]\|\[ \]'` PROGRESS.md.
   Setelah itu LANGSUNG menulis kode.
3. **Jangan baca ulang** file yang sudah dibaca dan tidak berubah. Catat fakta
   penting (nama fungsi, signature, nomor baris) di pikiran, bukan dengan membaca lagi.
4. **Graphify OPSIONAL.** Pakai `graphify query` hanya untuk pertanyaan terbuka
   ("di mana X dipakai?") saat file tidak disebut. Bila task sudah mencantumkan file,
   LEWATI graphify dan grep. Jangan menyebut daftar navigasi di jawaban.
5. **Grep sebelum baca besar.** File >250 baris: `grep -n` dulu, lalu baca
   rentang sekitar hasil. File ≤250 baris: baca utuh dalam turn paralel.
6. **Probe data = 1 skrip.** Uji semua fixture/variasi dalam SATU skrip yang
   mencetak tabel (kunci + 1 contoh nilai ≤80 karakter, total ≤40 baris).
   Dilarang payload mentah dan skrip probe berulang per file.
7. **Tulis sekali, tepat.** Tulis file kode dan test utuh dalam sesedikit turn
   (idealnya 1 write per file). Hindari rangkaian edit kecil; gabungkan perbaikan
   dalam satu edit multi-bagian.
8. **Thinking singkat.** Perbaikan mekanis (test gagal, lint) = baca error sekali,
   perbaiki, jalankan ulang, tanpa analisis panjang. Maksimal 2 percobaan per
   hipotesis; bila gagal, catat dan lanjut atau berhenti dan laporkan.
9. **Test hemat.** Selama kerja: hanya file test relevan (`... | tail -3`).
   Suite penuh + ruff SEKALI di akhir, hanya bila `app/` atau `tests/` berubah,
   digabung dalam satu bash: `uv run pytest 2>&1 | tail -3; uv run ruff check app tests`.
10. **Dilarang tanpa diminta:** `git status`/`git diff`, membaca ulang file hasil
    tulis sendiri, menjalankan `--collect-only`, menulis jumlah test di PROGRESS.md.

## Alur sesi

1. Fase Baca (aturan 2). Jangan membaca dokumen spesifikasi utuh, hanya bagian yang dirujuk task.
2. Implementasi sesuai langkah task; patuhi "Yang TIDAK boleh dilakukan" di file task.
3. Fase Selesai (di bawah).

## Fase Selesai (maksimal 2 turn)

Turn A, satu bash call berisi semuanya:

```bash
uv run pytest 2>&1 | tail -3; uv run ruff check app tests; \
uv run python scripts/codemap.py >/dev/null 2>&1 && echo codemap-ok; \
graphify update . 2>&1 | tail -2; \
grep -n '^## ' plan/NOTES.md | tail -3; grep -n '^- \[ \] <NN>\|^- \[~\] <NN>' plan/PROGRESS.md
```

(`codemap` hanya bila file/API berubah; `graphify update` hanya bila kode berubah.)

Turn B, edit paralel dalam satu turn (tanpa membaca ulang file penuh):

- `plan/PROGRESS.md`: ubah SATU baris task (status, bukti file+test, masalah terbuka).
- `plan/NOTES.md` dan `docs/DECISIONS.md`: tambahkan penyimpangan/keputusan baru
  dengan menambah di akhir file (append via bash `cat >> file <<'EOF'`), tanpa head/tail terpisah.

Setelah itu tulis ringkasan akhir (≤10 baris) dan berhenti.
