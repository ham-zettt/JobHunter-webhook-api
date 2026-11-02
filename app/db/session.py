from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = None
SessionLocal: async_sessionmaker[AsyncSession] | None = None


def configure(database_url: str | None = None, busy_timeout_ms: int | None = None) -> None:
    global engine, SessionLocal
    settings = get_settings()
    url = database_url or settings.database_url
    timeout = busy_timeout_ms if busy_timeout_ms is not None else settings.sqlite_busy_timeout_ms

    if url.startswith("sqlite") and ":memory:" not in url and "mode=memory" not in url:
        raw = url.split("///", 1)[-1]
        if raw and not raw.startswith("/"):
            Path(raw).parent.mkdir(parents=True, exist_ok=True)

    if engine is not None:
        engine.sync_engine.dispose()

    engine = create_async_engine(url, future=True)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    @event.listens_for(engine.sync_engine, "connect")
    def _set_pragmas(dbapi_conn, _record) -> None:  # pragma: no cover - trivial
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute(f"PRAGMA busy_timeout={timeout}")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.execute("PRAGMA cache_size=-20000")
        cursor.close()


configure()


async def get_session() -> AsyncIterator[AsyncSession]:
    assert SessionLocal is not None
    async with SessionLocal() as session:
        yield session
