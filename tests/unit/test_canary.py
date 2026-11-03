from __future__ import annotations

from types import SimpleNamespace

from app.db.repositories import run_repo
from app.db.session import SessionLocal
from app.runner.orchestrator import Orchestrator


def _source(found: int = 10, errors: int = 0) -> SimpleNamespace:
    return SimpleNamespace(found_count=found, error_count=errors)


def test_canary_zero_found_is_degraded():
    assert Orchestrator._canary("completed", _source(found=0), [], 0, 0) == "degraded"


def test_canary_median_description_short_is_degraded():
    assert Orchestrator._canary("completed", _source(), [100, 120, 130], 3, 0) == "degraded"


def test_canary_missing_required_is_degraded():
    assert Orchestrator._canary("completed", _source(), [500, 500], 10, 4) == "degraded"


def test_canary_healthy_stays_completed():
    assert Orchestrator._canary("completed", _source(), [500, 600], 10, 1) == "completed"


def test_canary_error_streak_is_degraded():
    assert Orchestrator._canary("completed", _source(errors=5), [500, 600], 10, 0) == "degraded"


async def _seed_productive_run(run_id: str, platform: str, term: str) -> None:
    async with SessionLocal() as session:
        await run_repo.create_run(session, run_id=run_id, platforms=[platform], params={})
        source = await run_repo.get_source(session, run_id, platform)
        source.search_terms = f'["{term}"]'
        source.found_count = 5
        await run_repo.finish_source(session, source, "completed")


async def test_baseline_zero_on_productive_term_is_degraded():
    await _seed_productive_run("prev-1", "glints", "backend")
    async with SessionLocal() as session:
        assert await Orchestrator._baseline_degraded(session, "glints", {"backend": 0}) is True
        assert await Orchestrator._baseline_degraded(session, "glints", {"backend": 3}) is False


async def test_baseline_without_history_is_ok():
    async with SessionLocal() as session:
        assert await Orchestrator._baseline_degraded(session, "glints", {"backend": 0}) is False
        assert await Orchestrator._baseline_degraded(session, "glints", {}) is False
