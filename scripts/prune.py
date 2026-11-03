#!/usr/bin/env python3
"""Retensi DB sesuai DATABASE.md §10.2.

Hapus `job_run_links` untuk run > 90 hari dan `jobs` `expired` dengan
`effective_date` > 180 hari; opsional `--include-archived`. VACUUM di luar
transaksi setelah penghapusan.
"""
from __future__ import annotations

import argparse
import datetime as dt
import sqlite3

LINK_MAX_AGE_DAYS = 90
JOB_MAX_AGE_DAYS = 180


def _ts(days_ago: int) -> str:
    t = dt.datetime.now(dt.UTC) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def _date(days_ago: int) -> str:
    t = dt.datetime.now(dt.UTC) - dt.timedelta(days=days_ago)
    return t.strftime("%Y-%m-%d")


def prune(
    db_path: str, *, include_archived: bool = False, dry_run: bool = False
) -> dict[str, int]:
    link_cut = _ts(LINK_MAX_AGE_DAYS)
    job_cut = _date(JOB_MAX_AGE_DAYS)
    statuses = ["expired"] + (["archived"] if include_archived else [])
    ph = ",".join("?" * len(statuses))
    job_params = (*statuses, job_cut)

    con = sqlite3.connect(db_path)
    try:
        con.execute("PRAGMA foreign_keys=ON")
        links = con.execute(
            "SELECT COUNT(*) FROM job_run_links l JOIN scrape_runs r ON r.id = l.run_id "
            "WHERE r.created_at < ?",
            (link_cut,),
        ).fetchone()[0]
        jobs = con.execute(
            f"SELECT COUNT(*) FROM jobs WHERE status IN ({ph}) AND effective_date < ?",
            job_params,
        ).fetchone()[0]
        if not dry_run:
            with con:
                con.execute(
                    "DELETE FROM job_run_links WHERE run_id IN "
                    "(SELECT id FROM scrape_runs WHERE created_at < ?)",
                    (link_cut,),
                )
                con.execute(
                    f"DELETE FROM jobs WHERE status IN ({ph}) AND effective_date < ?",
                    job_params,
                )
            con.execute("VACUUM")
        return {"links": links, "jobs": jobs}
    finally:
        con.close()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Retensi DB: hapus data lama (§10.2).")
    p.add_argument("--db", default="data/jobs.db")
    p.add_argument("--include-archived", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args(argv)
    r = prune(a.db, include_archived=a.include_archived, dry_run=a.dry_run)
    verb = "akan dihapus" if a.dry_run else "dihapus"
    print(f"{verb}: job_run_links={r['links']} jobs={r['jobs']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
