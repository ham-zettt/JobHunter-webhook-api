#!/usr/bin/env python3
"""Alat bantu discovery SCRAPER_SPEC §3.

Menyimpan HTML halaman + payload JSON XHR ke data/discovery/<platform>/.
Jalankan headed bila memungkinkan agar halaman tampil seperti pengguna biasa.

    uv run python scripts/discover_platform.py jobstreet \
        --url "https://id.jobstreet.com/id/software-engineer-jobs" --headed

Platform berlogin (LinkedIn): tambahkan `--storage-state` dan `--interactive`
(tekan Enter setelah halaman siap/panel diperluas).

    uv run python scripts/discover_platform.py linkedin --headed --interactive \
        --storage-state data/secrets/linkedin_state.json --url "<url>"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

from playwright.async_api import Response, async_playwright

API_HINTS = ("/api/", "graphql", "jobsearch", "jobs/v", "search")
CHALLENGE_MARKERS = (
    "just a moment",
    "verify you are human",
    "access denied",
    "unusual activity",
    "aktivitas tidak biasa",
    "captcha",
    "challenge",
)


def _slug(text: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", text)[:120].strip("_") or "index"


def _is_json(response: Response) -> bool:
    ctype = (response.headers or {}).get("content-type", "")
    return "json" in ctype


async def _capture(response: Response, outdir: Path, saved: list[str]) -> None:
    if not _is_json(response):
        return
    url = response.url
    if not any(hint in url for hint in API_HINTS):
        return
    try:
        payload = await response.json()
    except Exception:
        return
    name = f"json_{len(saved):03d}_{_slug(url.split('?')[0].split('/')[-1])}.json"
    path = outdir / name
    path.write_text(
        json.dumps({"url": url, "payload": payload}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    saved.append(name)
    print(f"  JSON {response.status} {url} -> {name}")


async def discover(
    platform: str,
    url: str,
    headed: bool,
    wait_ms: int,
    storage_state: str | None,
    interactive: bool,
) -> None:
    outdir = Path("data/discovery") / platform
    outdir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    saved: list[str] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=not headed)
        context = await browser.new_context(
            viewport={"width": 1366, "height": 768},
            locale="id-ID",
            timezone_id="Asia/Jakarta",
            storage_state=storage_state,
        )
        page = await context.new_page()
        page.on("response", lambda r: asyncio.create_task(_capture(r, outdir, saved)))
        response = await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await page.wait_for_timeout(wait_ms)
        if interactive:
            await asyncio.to_thread(input, "Klik kartu/perluasan bila perlu, lalu tekan Enter... ")

        html_path = outdir / f"html_{stamp}.html"
        html_path.write_text(await page.content(), encoding="utf-8")
        title = await page.title()

        meta = {
            "platform": platform,
            "url": url,
            "final_url": page.url,
            "status": response.status if response else None,
            "title": title,
            "json_files": saved,
            "html": html_path.name,
            "captured_at": datetime.now().isoformat(timespec="seconds"),
        }
        (outdir / f"meta_{stamp}.json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        body = (await page.content()).lower()
        challenge = [m for m in CHALLENGE_MARKERS if m in body]
        print(
            json.dumps(
                {
                    "title": title,
                    "status": meta["status"],
                    "final_url": page.url,
                    "json_files": len(saved),
                    "challenge_markers": challenge,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        await browser.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("platform")
    parser.add_argument("--url", required=True)
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--wait-ms", type=int, default=6000)
    parser.add_argument("--storage-state", default=None)
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()
    asyncio.run(
        discover(
            args.platform,
            args.url,
            args.headed,
            args.wait_ms,
            args.storage_state,
            args.interactive,
        )
    )


if __name__ == "__main__":
    main()
