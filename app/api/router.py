from fastapi import APIRouter

from app.api.routers import jobs, keywords, platforms, scrape

api_router = APIRouter()
api_router.include_router(scrape.router)
api_router.include_router(jobs.router)
api_router.include_router(platforms.router)
api_router.include_router(keywords.router)
