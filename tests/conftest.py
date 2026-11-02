from __future__ import annotations

import os
import tempfile

_tmp = tempfile.mkdtemp(prefix="jobscraper-test-")
os.environ["API_KEY"] = "test-key"
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{_tmp}/test.db"
os.environ["PLAYWRIGHT_HEADLESS"] = "true"
os.environ["CONFIG_DIR"] = os.path.join(os.path.dirname(__file__), "..", "config")

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.schema import ensure_schema  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
async def clean_db():
    await ensure_schema(engine)
    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
    yield


@pytest.fixture
async def client():
    from app.runner.run_manager import run_manager

    await run_manager.start()
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            yield c
    finally:
        await run_manager.stop()


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"X-API-Key": "test-key"}
