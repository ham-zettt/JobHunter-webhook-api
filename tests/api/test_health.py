from __future__ import annotations

from app.api.routers import health as health_router


async def test_health_ok(client, monkeypatch):
    async def fake() -> tuple[bool, str]:
        return True, "ok"

    monkeypatch.setattr(health_router, "check_browser", fake)
    resp = await client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert body["db"] == "ok"
    assert body["browser"] == "ok"
    assert body["version"] == "1.0.0"


async def test_health_browser_failure_returns_503(client, monkeypatch):
    async def fake() -> tuple[bool, str]:
        return False, "error: ExecutableNotFound"

    monkeypatch.setattr(health_router, "check_browser", fake)
    resp = await client.get("/health")
    assert resp.status_code == 503
    assert resp.json()["browser"] == "error: ExecutableNotFound"


async def test_protected_route_requires_api_key(client):
    resp = await client.get("/api/v1/jobs")
    assert resp.status_code in (401, 404)
