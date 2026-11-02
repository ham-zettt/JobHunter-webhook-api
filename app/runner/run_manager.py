from __future__ import annotations

import asyncio
import ipaddress
import socket
from typing import Any
from urllib.parse import urlsplit

import httpx

from app.core.config import get_settings
from app.core.logging import get_logger
from app.db.repositories import run_repo
from app.db.session import SessionLocal
from app.runner.orchestrator import Orchestrator
from app.scrapers.browser import BrowserPool

log = get_logger("run_manager")

CALLBACK_RETRY_DELAYS = (2, 5, 10)


class CallbackRejectedError(Exception):
    pass


def validate_callback_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.hostname:
        raise CallbackRejectedError("callback_url harus http/https dengan host valid")
    settings = get_settings()
    host = parts.hostname.lower()
    allowed = settings.callback_allowed_host_set
    if allowed:
        if host not in allowed:
            raise CallbackRejectedError("Host callback_url tidak ada di CALLBACK_ALLOWED_HOSTS")
        return url
    if host in ("localhost", "localhost.localdomain") or host.endswith(".local"):
        raise CallbackRejectedError("callback_url ke host lokal tidak diizinkan")

    def blocked(ip: ipaddress._BaseAddress) -> bool:
        return (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        )

    try:
        address = ipaddress.ip_address(host)
        if blocked(address):
            raise CallbackRejectedError("callback_url ke alamat privat tidak diizinkan")
        return url
    except ValueError:
        pass

    try:
        infos = socket.getaddrinfo(host, None)
    except OSError as exc:
        raise CallbackRejectedError(f"Host callback_url tidak dapat di-resolve: {host}") from exc
    for info in infos:
        try:
            if blocked(ipaddress.ip_address(info[4][0])):
                raise CallbackRejectedError("callback_url mengarah ke alamat privat")
        except ValueError:
            continue
    return url


class RunManager:
    def __init__(self) -> None:
        self.queue: asyncio.Queue[str] = asyncio.Queue()
        self.cancel_events: dict[str, asyncio.Event] = {}
        self._worker_task: asyncio.Task | None = None
        self.orchestrator = Orchestrator()
        self.browser_pool = BrowserPool()

    async def start(self) -> None:
        if self._worker_task is not None and not self._worker_task.done():
            return
        self.queue = asyncio.Queue()
        self.cancel_events.clear()
        async with SessionLocal() as session:
            queued = await run_repo.recover(session)
        for run_id in queued:
            self.queue.put_nowait(run_id)
        self._worker_task = asyncio.create_task(self._worker())

    async def stop(self) -> None:
        if self._worker_task is not None:
            self._worker_task.cancel()
            await asyncio.gather(self._worker_task, return_exceptions=True)
            self._worker_task = None
        await self.browser_pool.stop()

    async def enqueue(
        self,
        *,
        run_id: str,
        platforms: list[str],
        params: dict[str, Any],
        trigger: str = "api",
        callback_url: str | None = None,
    ) -> None:
        async with SessionLocal() as session:
            await run_repo.create_run(
                session,
                run_id=run_id,
                platforms=platforms,
                params=params,
                trigger=trigger,
                callback_url=callback_url,
            )
        self.queue.put_nowait(run_id)

    async def cancel(self, run_id: str) -> Any:
        event = self.cancel_events.setdefault(run_id, asyncio.Event())
        event.set()
        async with SessionLocal() as session:
            run = await run_repo.get_run(session, run_id)
            if run is not None and run.status == "queued":
                await run_repo.cancel_run(session, run)
            return run

    async def _worker(self) -> None:
        while True:
            run_id = await self.queue.get()
            try:
                async with SessionLocal() as session:
                    run = await run_repo.get_run(session, run_id)
                if run is None or run.status == "cancelled":
                    continue
                event = self.cancel_events.setdefault(run_id, asyncio.Event())
                await self.orchestrator.run(run_id, event, self.browser_pool)
                async with SessionLocal() as session:
                    run = await run_repo.get_run(session, run_id)
                    if run is not None and run.callback_url:
                        await self._send_callback(session, run)
            except asyncio.CancelledError:  # pragma: no cover - shutdown path
                raise
            except Exception:  # pragma: no cover - safety net
                log.exception("run_worker_failed", run_id=run_id)
            finally:
                self.queue.task_done()
                self.cancel_events.pop(run_id, None)

    async def _send_callback(self, session: Any, run: Any) -> None:
        sources = await run_repo.sources_for(session, run.id)
        payload = run_repo.run_dict(run, sources)
        status = "failed"
        for delay in CALLBACK_RETRY_DELAYS:
            try:
                async with httpx.AsyncClient(timeout=get_settings().callback_timeout_sec) as client:
                    response = await client.post(run.callback_url, json=payload)
                if response.status_code < 500:
                    status = "sent"
                    break
            except httpx.HTTPError:
                pass
            await asyncio.sleep(delay)
        run.callback_status = status
        await session.commit()


run_manager = RunManager()
