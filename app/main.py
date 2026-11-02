from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from app.api.router import api_router
from app.api.routers import health
from app.core.config import get_settings
from app.core.errors import install_handlers
from app.core.logging import setup_logging
from app.core.security import require_api_key
from app.db.schema import ensure_schema
from app.db.session import SessionLocal, engine
from app.runner.run_manager import run_manager
from app.seed.loader import seed_all


@asynccontextmanager
async def lifespan(_: FastAPI):
    setup_logging()
    get_settings()
    await ensure_schema(engine)
    async with SessionLocal() as session:
        await seed_all(session)
    await run_manager.start()
    yield
    await run_manager.stop()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Job Scraper API",
        version="1.0.0",
        description="Agregasi lowongan kerja Software Engineering & AI dari 7 platform.",
        lifespan=lifespan,
    )
    install_handlers(application)
    application.include_router(health.router)
    application.include_router(
        api_router, prefix="/api/v1", dependencies=[Depends(require_api_key)]
    )
    return application


app = create_app()
