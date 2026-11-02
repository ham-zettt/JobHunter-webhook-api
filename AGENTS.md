## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## Proyek
Job Scraper API: Python 3.12 + FastAPI + Playwright + SQLite. Tanpa frontend.
Spesifikasi: `PRD.md`, `DATABASE.md`, `ARCHITECTURE.md`, `SCRAPER_SPEC.md`
(prioritas: PRD > DATABASE > ARCHITECTURE > SCRAPER_SPEC). Keputusan: `docs/DECISIONS.md`.

## Perintah
```bash
uv run pytest -q                 # test offline; live dikecualikan
uv run pytest --cov=app          # coverage
uv run pytest -m live            # manual, menyentuh situs nyata
uv run ruff check app tests      # lint
uv run uvicorn app.main:app --port 8000 --workers 1
uv run python scripts/codemap.py # regenerasi docs/CODEMAP.md
./scripts/backup_db.sh           # backup SQLite
```

## Peta folder
- `app/api/` — router + schema Pydantic (kontrak REST).
- `app/services/` — validasi/query/ekspor; jembatan API ke runner/repo.
- `app/runner/` — `RunManager` (antrean, callback) + `Orchestrator` (alur run).
- `app/scrapers/` — `BaseScraper`, `BrowserPool`, registry, platform per situs.
- `app/pipeline/` — normalizer, lokasi, classifier, usia, deduper, orkestrasi.
- `app/db/` — model, schema/FTS5, session/PRAGMA, repository.
- `config/` — seed keyword, alias lokasi, batas per platform.
- `plan/` — `README.md` indeks task, `PROGRESS.md` status, `NOTES.md` penyimpangan.

## Aturan keras
- Scraper TIDAK menyentuh DB. Scraper hanya menghasilkan `RawListing`/`RawJob`.
- Filter, dedup, dan keputusan bisnis HANYA di `app/pipeline/`.
- Nama field, tabel, enum, env variable PERSIS seperti dokumen sumber.
- Selector/endpoint platform tanpa discovery (`docs/platform_notes/<platform>.md`)
  DILARANG. Pertahankan penanda `[verifikasi]`.
- Jangan menembus CAPTCHA/checkpoint, memakai stealth, atau menyimpan kredensial.
- Jangan membaca seluruh dokumen spesifikasi; baca hanya bagian yang dirujuk task.

## Alur sesi
1. Baca `plan/PROGRESS.md` → `docs/CODEMAP.md`.
2. Buka file task di `plan/NN-*.md` + bagian dokumen yang dirujuk.
3. Sebelum membuka file sumber, coba `graphify query "<pertanyaan>"`.
4. Hanya buka file di bagian "File yang perlu dibaca" task, kecuali terbukti perlu.
5. Jangan menandai task `[x]` tanpa bukti file + test lulus.

## Alur selesai
1. `uv run pytest -q` hijau dan `uv run ruff check app tests` bersih.
2. `uv run python scripts/codemap.py` bila ada file/API berubah.
3. `graphify update .` bila kode berubah.
4. Perbarui `plan/PROGRESS.md` (status, bukti, masalah terbuka).
5. Catat penyimpangan/keputusan baru di `plan/NOTES.md` dan `docs/DECISIONS.md`.
