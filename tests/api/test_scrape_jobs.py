from __future__ import annotations

import asyncio
import json
import threading
from datetime import timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer

import httpx
import pytest

from app.core.config import get_settings
from app.core.timeutil import wib_today
from app.db.repositories import job_repo, run_repo
from app.db.session import SessionLocal
from app.scrapers.registry import SCRAPERS
from app.seed.loader import seed_all
from tests.fixtures import fake_scrapers

TERMINAL = {"completed", "partial", "failed", "cancelled"}


@pytest.fixture(autouse=True)
def fake_registry(monkeypatch):
    fake_scrapers.reset()
    monkeypatch.setitem(SCRAPERS, "jobstreet", fake_scrapers.FakeJobstreetScraper)
    monkeypatch.setitem(SCRAPERS, "glints", fake_scrapers.FakeGlintsScraper)
    yield


async def seed_keywords():
    async with SessionLocal() as session:
        await seed_all(session)


async def wait_run(client, run_id: str, headers=None, timeout: float = 10.0) -> dict:
    for _ in range(int(timeout / 0.05)):
        response = await client.get(f"/api/v1/scrape/runs/{run_id}", headers=headers)
        body = response.json()
        if "status" not in body:
            raise AssertionError(f"unexpected run response {response.status_code}: {body}")
        if body["status"] in TERMINAL:
            return body
        await asyncio.sleep(0.05)
    raise AssertionError(f"run {run_id} tidak selesai: {body}")


async def scrape(client, headers, platform="jobstreet", **body):
    payload = {"keywords": ["backend"], "max_age_days": 30, **body}
    response = await client.post(f"/api/v1/scrape/{platform}", json=payload, headers=headers)
    assert response.status_code == 202, response.text
    run_id = response.json()["run_id"]
    return run_id, await wait_run(client, run_id, headers)


async def test_scrape_creates_jobs_and_filters(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    run_id, run = await scrape(client, auth_headers)
    assert run["status"] == "completed", run
    assert run["totals"]["found"] == 3
    assert run["totals"]["new"] == 2
    assert run["totals"]["filtered"]["keyword"] == 1

    response = await client.get(f"/api/v1/jobs?run_id={run_id}&only_new=true", headers=auth_headers)
    body = response.json()
    assert body["total"] == 2
    titles = {item["posisi"] for item in body["items"]}
    assert titles == {"Backend Engineer", "AI Engineer"}
    backend = next(i for i in body["items"] if i["posisi"] == "Backend Engineer")
    assert backend["sumber"] == "jobstreet"
    assert backend["kota"] == "Jakarta Selatan"
    assert backend["provinsi"] == "DKI Jakarta"
    assert backend["gaji_min"] == 12_000_000
    assert backend["sistem_kerja"] == "onsite"
    assert backend["skor_relevansi"] >= 100


async def test_scrape_is_idempotent(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    await scrape(client, auth_headers)
    _, second = await scrape(client, auth_headers)
    assert second["totals"]["new"] == 0
    assert second["totals"]["updated"] == 0
    assert second["totals"]["found"] == 3

    async with SessionLocal() as session:
        rows, total = await job_repo.list_jobs(session, job_repo.JobFilters())
    assert total == 2


async def test_description_included_and_detailed(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    _, run = await scrape(client, auth_headers)
    listing = await client.get("/api/v1/jobs", headers=auth_headers)
    item = listing.json()["items"][0]
    assert len(item["deskripsi"]) > 400

    light = await client.get("/api/v1/jobs?include_description=false", headers=auth_headers)
    assert light.json()["items"][0]["deskripsi"] == ""

    detail = await client.get(f"/api/v1/jobs/{item['id']}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["url"] == item["url"]


async def test_search_filter(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    await scrape(client, auth_headers)

    found = await client.get("/api/v1/jobs?q=AI", headers=auth_headers)
    body = found.json()
    assert body["total"] == 1
    assert body["items"][0]["posisi"] == "AI Engineer"


async def test_export_formats(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    await scrape(client, auth_headers)

    csv_resp = await client.get("/api/v1/jobs/export?format=csv", headers=auth_headers)
    assert csv_resp.status_code == 200
    assert "attachment" in csv_resp.headers["content-disposition"]
    assert csv_resp.content.startswith("\ufeff".encode())
    assert "posisi" in csv_resp.text

    jsonl = await client.get("/api/v1/jobs/export?format=jsonl", headers=auth_headers)
    assert jsonl.status_code == 200
    assert len(jsonl.text.strip().splitlines()) == 2

    js = await client.get("/api/v1/jobs/export?format=json", headers=auth_headers)
    assert len(js.json()["items"]) == 2


async def test_archive_job(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    await scrape(client, auth_headers)
    item = (await client.get("/api/v1/jobs", headers=auth_headers)).json()["items"][0]

    patched = await client.patch(
        f"/api/v1/jobs/{item['id']}", json={"status": "archived"}, headers=auth_headers
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "archived"

    active = await client.get("/api/v1/jobs", headers=auth_headers)
    assert all(i["id"] != item["id"] for i in active.json()["items"])


async def test_auth_required(client):
    response = await client.get("/api/v1/jobs")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


async def test_unknown_platform(client, auth_headers):
    response = await client.post("/api/v1/scrape/nope", json={}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "PLATFORM_NOT_FOUND"


async def test_invalid_max_age(client, auth_headers):
    response = await client.post(
        "/api/v1/scrape/jobstreet", json={"max_age_days": 500}, headers=auth_headers
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


async def test_invalid_callback(client, auth_headers):
    response = await client.post(
        "/api/v1/scrape/jobstreet",
        json={"callback_url": "http://127.0.0.1:9999/hook"},
        headers=auth_headers,
    )
    assert response.status_code == 422


async def test_run_not_found(client, auth_headers):
    response = await client.get("/api/v1/scrape/runs/r_does_not_exist", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RUN_NOT_FOUND"


async def test_jobs_max_age_filter(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_sample()
    await scrape(client, auth_headers)

    async with SessionLocal() as session:
        rows, _ = await job_repo.list_jobs(session, job_repo.JobFilters())
        old = next(row for row in rows if row.title == "AI Engineer")
        old.effective_date = (wib_today() - timedelta(days=10)).isoformat()
        await session.commit()

    recent = await client.get("/api/v1/jobs?max_age_days=3", headers=auth_headers)
    body = recent.json()
    assert body["total"] == 1
    assert body["has_more"] is False
    assert body["items"][0]["posisi"] == "Backend Engineer"

    unfiltered = await client.get("/api/v1/jobs", headers=auth_headers)
    assert unfiltered.json()["total"] == 2

    out_of_range = await client.get("/api/v1/jobs?max_age_days=0", headers=auth_headers)
    assert out_of_range.status_code == 422


async def test_scrape_stops_after_five_old_listings(client, auth_headers):
    await seed_keywords()
    fake_scrapers.seed_old_then_new()
    _, run = await scrape(client, auth_headers)
    assert run["totals"]["filtered"]["age"] == 5
    assert run["totals"]["found"] == 5
    assert run["totals"]["new"] == 0


class _CallbackHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        server = self.server
        server.requests.append(json.loads(raw or b"{}"))
        status = server.responses.pop(0) if server.responses else 200
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b"{}")

    def log_message(self, *args: object) -> None:
        pass


class _CallbackServer(HTTPServer):
    def __init__(self, responses: list[int]) -> None:
        super().__init__(("127.0.0.1", 0), _CallbackHandler)
        self.responses = list(responses)
        self.requests: list[dict] = []

    @property
    def url(self) -> str:
        host, port = self.server_address
        return f"http://{host}:{port}/hook"


@pytest.fixture
def callback_server():
    started: list[tuple[_CallbackServer, threading.Thread]] = []

    def make(responses: list[int] | None = None) -> _CallbackServer:
        server = _CallbackServer(responses or [])
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        started.append((server, thread))
        return server

    yield make
    for server, thread in started:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


@pytest.fixture
def callback_env(monkeypatch):
    monkeypatch.setenv("CALLBACK_ALLOWED_HOSTS", "127.0.0.1")
    monkeypatch.setattr("app.runner.run_manager.CALLBACK_RETRY_DELAYS", (0, 0, 0))
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def wait_callback_status(run_id: str, timeout: float = 5.0) -> str:
    status = "pending"
    for _ in range(int(timeout / 0.05)):
        async with SessionLocal() as session:
            run = await run_repo.get_run(session, run_id)
            status = run.callback_status if run else None
            if status in ("sent", "failed"):
                return status
        await asyncio.sleep(0.05)
    raise AssertionError(f"callback {run_id} tidak selesai: {status}")


async def test_callback_sent_after_run(
    client, auth_headers, callback_server, callback_env, monkeypatch
):
    await seed_keywords()
    fake_scrapers.seed_sample()
    server = callback_server()

    seen: dict = {}
    real_client = httpx.AsyncClient

    def spy(*args, **kwargs):
        seen["timeout"] = kwargs.get("timeout")
        return real_client(*args, **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", spy)
    run_id, run = await scrape(client, auth_headers, callback_url=server.url)
    assert run["status"] == "completed"
    assert await wait_callback_status(run_id) == "sent"

    assert len(server.requests) == 1
    body = server.requests[0]
    assert body["run_id"] == run_id
    assert body["status"] == "completed"
    assert body["totals"]["found"] == 3
    assert body["platforms"][0]["platform"] == "jobstreet"
    assert seen["timeout"] == get_settings().callback_timeout_sec


async def test_callback_retries_on_5xx(client, auth_headers, callback_server, callback_env):
    await seed_keywords()
    fake_scrapers.seed_sample()
    server = callback_server([500, 500, 200])
    run_id, _ = await scrape(client, auth_headers, callback_url=server.url)
    assert await wait_callback_status(run_id) == "sent"
    assert len(server.requests) == 3


async def test_callback_failure_does_not_change_run_status(
    client, auth_headers, callback_server, callback_env
):
    await seed_keywords()
    fake_scrapers.seed_sample()
    server = callback_server([500, 500, 500])
    run_id, run = await scrape(client, auth_headers, callback_url=server.url)
    assert run["status"] == "completed"
    assert await wait_callback_status(run_id) == "failed"
    assert len(server.requests) == 3

    after = await client.get(f"/api/v1/scrape/runs/{run_id}", headers=auth_headers)
    assert after.json()["status"] == "completed"
