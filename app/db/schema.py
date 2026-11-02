from __future__ import annotations

from sqlalchemy import Connection
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base
from app.db.models import Job, JobRunLink, KeywordRule, LocationAlias, ScrapeRun, ScrapeRunSource  # noqa: F401

FTS_DDL = [
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS jobs_fts USING fts5(
        title, company_name, description_text,
        content='jobs', content_rowid='id',
        tokenize="unicode61 remove_diacritics 2"
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS jobs_ai AFTER INSERT ON jobs BEGIN
        INSERT INTO jobs_fts(rowid, title, company_name, description_text)
        VALUES (new.id, new.title, COALESCE(new.company_name,''), new.description_text);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS jobs_ad AFTER DELETE ON jobs BEGIN
        INSERT INTO jobs_fts(jobs_fts, rowid, title, company_name, description_text)
        VALUES ('delete', old.id, old.title, COALESCE(old.company_name,''),
                old.description_text);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS jobs_au AFTER UPDATE ON jobs BEGIN
        INSERT INTO jobs_fts(jobs_fts, rowid, title, company_name, description_text)
        VALUES ('delete', old.id, old.title, COALESCE(old.company_name,''),
                old.description_text);
        INSERT INTO jobs_fts(rowid, title, company_name, description_text)
        VALUES (new.id, new.title, COALESCE(new.company_name,''), new.description_text);
    END
    """,
]


def ensure_schema_sync(conn: Connection) -> None:
    Base.metadata.create_all(bind=conn)
    for ddl in FTS_DDL:
        conn.exec_driver_sql(ddl)


async def ensure_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(ensure_schema_sync)
