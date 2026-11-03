from __future__ import annotations

import httpx
import pytest
from tenacity import wait_none

from app.scrapers.browser import detect_challenge, save_debug_snapshot
from app.scrapers.common import retry
from app.scrapers.exceptions import BlockedError, TransientNetworkError


def test_detect_challenge_by_url():
    assert detect_challenge("", "https://www.linkedin.com/checkpoint/lg/login")
    assert detect_challenge("", "https://x.test/captcha")
    assert detect_challenge("", "https://x.test/login")


def test_detect_challenge_by_text():
    assert detect_challenge("<html>Just a moment...</html>", "https://x.test/")
    assert detect_challenge("<p>verify you are human</p>", "https://x.test/")
    assert detect_challenge("<p>Aktivitas tidak biasa terdeteksi</p>", "https://x.test/")


def test_detect_challenge_by_iframe():
    html = '<iframe src="https://www.google.com/recaptcha/api2/anchor"></iframe>'
    assert detect_challenge(html, "https://x.test/")
    html = '<iframe src="https://challenges.cloudflare.com/turnstile/v0"></iframe>'
    assert detect_challenge(html, "https://x.test/")


def test_detect_challenge_negative():
    assert not detect_challenge("<html><body>Software Engineer</body></html>", "https://x.test/jobs")
    assert not detect_challenge('<iframe src="https://maps.example.com/embed"></iframe>', "https://x.test/")


def _client(handler) -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=httpx.MockTransport(handler))


async def test_retry_transient_then_success(monkeypatch):
    monkeypatch.setattr(retry, "WAIT", wait_none())
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503)
        return httpx.Response(200, text="ok")

    async with _client(handler) as client:
        response = await retry.fetch_with_retry(client, "https://x.test/a")
    assert response.status_code == 200
    assert calls["n"] == 3


async def test_transient_exhausted_raises(monkeypatch):
    monkeypatch.setattr(retry, "WAIT", wait_none())
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(500)

    async with _client(handler) as client:
        with pytest.raises(TransientNetworkError):
            await retry.fetch_with_retry(client, "https://x.test/a")
    assert calls["n"] == 3


async def test_403_not_retried(monkeypatch):
    monkeypatch.setattr(retry, "WAIT", wait_none())
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(403)

    async with _client(handler) as client:
        with pytest.raises(BlockedError):
            await retry.fetch_with_retry(client, "https://x.test/a")
    assert calls["n"] == 1


async def test_429_retry_after_then_blocked(monkeypatch):
    monkeypatch.setattr(retry, "WAIT", wait_none())
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(429, headers={"Retry-After": "0"})

    async with _client(handler) as client:
        with pytest.raises(BlockedError):
            await retry.fetch_with_retry(client, "https://x.test/a")
    assert calls["n"] == 3


async def test_challenge_not_retried(monkeypatch):
    monkeypatch.setattr(retry, "WAIT", wait_none())
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        return httpx.Response(200, text="<html>Just a moment...</html>")

    async with _client(handler) as client:
        with pytest.raises(BlockedError):
            await retry.fetch_with_retry(client, "https://x.test/a", check_challenge=True)
    assert calls["n"] == 1


class _BoomPage:
    async def screenshot(self, **kwargs: object) -> None:
        raise OSError("disk penuh")

    async def content(self) -> str:
        return "<html></html>"


async def test_snapshot_write_failure_is_safe(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert await save_debug_snapshot(_BoomPage(), "run-x", "jobstreet", "parse_error") is None


async def test_snapshot_html_without_page(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    path = await save_debug_snapshot(None, "run-y", "glints", "parse_error", html="<html>k</html>")
    assert path is not None and path.read_text(encoding="utf-8") == "<html>k</html>"
