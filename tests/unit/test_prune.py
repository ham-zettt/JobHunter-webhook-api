from __future__ import annotations

import datetime as dt
import os
import shutil
import sqlite3
import subprocess
from pathlib import Path

import pytest
from sqlalchemy import create_engine

from app.db.schema import ensure_schema_sync
from scripts.prune import prune

ROOT = Path(__file__).resolve().parents[2]


def _ts(days_ago: int = 0) -> str:
    t = dt.datetime.now(dt.UTC) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(days_ago: int = 0) -> str:
    t = dt.datetime.now(dt.UTC) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%d")


def _make_db(path: Path) -> Path:
    engine = create_engine(f"sqlite:///{path}")
    with engine.begin() as conn:
        ensure_schema_sync(conn)
    engine.dispose()
    return path


def _run(con: sqlite3.Connection, run_id: str, days_ago: int) -> None:
    con.execute(
        "INSERT INTO scrape_runs (id, trigger, status, requested_platforms, params, created_at) "
        "VALUES (?, 'api', 'completed', '[]', '{}', ?)",
        (run_id, _ts(days_ago)),
    )


def _job(
    con: sqlite3.Connection,
    job_id: int,
    status: str,
    effective_days_ago: int,
) -> None:
    now = _ts()
    con.execute(
        "INSERT INTO jobs (id, platform, url, url_canonical, title, title_normalized, "
        "description_text, description_hash, effective_date, fingerprint, status, "
        "first_seen_at, last_seen_at, created_at, updated_at) "
        "VALUES (?, 'glints', ?, ?, 'Backend', 'backend', 'desc', 'h', ?, 'f', ?, ?, ?, ?, ?)",
        (
            job_id,
            f"https://e/{job_id}",
            f"https://e/{job_id}",
            _date(effective_days_ago),
            status,
            now,
            now,
            now,
            now,
        ),
    )


def _link(con: sqlite3.Connection, run_id: str, job_id: int) -> None:
    con.execute(
        "INSERT INTO job_run_links (run_id, job_id, action, created_at) "
        "VALUES (?, ?, 'seen', ?)",
        (run_id, job_id, _ts()),
    )


def _counts(path: Path) -> tuple[int, int]:
    con = sqlite3.connect(path)
    try:
        jobs = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
        links = con.execute("SELECT COUNT(*) FROM job_run_links").fetchone()[0]
        return jobs, links
    finally:
        con.close()


def test_prune_removes_old_links_and_expired_jobs(tmp_path):
    db = _make_db(tmp_path / "p.db")
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    _run(con, "old", 100)
    _run(con, "new", 1)
    _job(con, 1, "expired", 200)
    _job(con, 2, "active", 1)
    _link(con, "old", 1)
    _link(con, "new", 2)
    con.commit()
    con.close()

    r = prune(str(db))
    assert r == {"links": 1, "jobs": 1}
    jobs, links = _counts(db)
    assert (jobs, links) == (1, 1)
    con = sqlite3.connect(db)
    assert con.execute("SELECT id FROM jobs").fetchone()[0] == 2
    assert con.execute("SELECT run_id FROM job_run_links").fetchone()[0] == "new"
    con.close()


def test_prune_keeps_recent_jobs(tmp_path):
    db = _make_db(tmp_path / "p.db")
    con = sqlite3.connect(db)
    _job(con, 1, "expired", 10)
    _job(con, 2, "archived", 200)
    con.commit()
    con.close()

    r = prune(str(db))
    assert r == {"links": 0, "jobs": 0}
    assert _counts(db)[0] == 2


def test_prune_include_archived(tmp_path):
    db = _make_db(tmp_path / "p.db")
    con = sqlite3.connect(db)
    _job(con, 1, "archived", 200)
    con.commit()
    con.close()

    assert prune(str(db))["jobs"] == 0
    assert prune(str(db), include_archived=True)["jobs"] == 1
    assert _counts(db)[0] == 0


def test_prune_dry_run_deletes_nothing(tmp_path):
    db = _make_db(tmp_path / "p.db")
    con = sqlite3.connect(db)
    con.execute("PRAGMA foreign_keys=ON")
    _run(con, "old", 100)
    _job(con, 1, "expired", 200)
    _link(con, "old", 1)
    con.commit()
    con.close()

    before = _counts(db)
    r = prune(str(db), dry_run=True)
    assert r == {"links": 1, "jobs": 1}
    assert _counts(db) == before


@pytest.mark.skipif(not shutil.which("sqlite3"), reason="sqlite3 CLI tidak tersedia")
def test_backup_script_creates_openable_db(tmp_path):
    db = _make_db(tmp_path / "src.db")
    dest = tmp_path / "backups"
    env = {**os.environ, "DATABASE_PATH": str(db), "BACKUP_DIR": str(dest)}
    subprocess.run([str(ROOT / "scripts" / "backup_db.sh")], env=env, check=True)
    backups = sorted(dest.glob("jobs_*.db"))
    assert len(backups) == 1

    con = sqlite3.connect(backups[0])
    tables = {row[0] for row in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    con.close()
    assert "jobs" in tables

    for i in range(7):
        (dest / f"jobs_2000010{i}_000000.db").write_bytes(b"")
    subprocess.run([str(ROOT / "scripts" / "backup_db.sh")], env=env, check=True)
    assert len(list(dest.glob("jobs_*.db"))) == 7
