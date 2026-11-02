#!/usr/bin/env python3
"""Login LinkedIn manual (headed) lalu simpan storage_state.

Jalankan di mesin lokal (bukan container headless):
    uv run python scripts/linkedin_login.py

Salin data/secrets/linkedin_state.json ke volume ./data/secrets milik container.
Tidak menyimpan kata sandi. Jangan commit file state.
"""

from __future__ import annotations

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

STATE_PATH = Path(os.getenv("LINKEDIN_STATE_PATH", "./data/secrets/linkedin_state.json"))
LOGIN_URL = "https://www.linkedin.com/login"
JOBS_URL = "https://www.linkedin.com/jobs/"
SESSION_BAD_MARKERS = ("/login", "/checkpoint", "/authwall", "/uas/", "/signup")


async def main() -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context(locale="id-ID", timezone_id="Asia/Jakarta")
        page = await context.new_page()
        await page.goto(LOGIN_URL)
        print("Login manual di jendela Chromium (termasuk 2FA).")
        input("Tekan Enter setelah berhasil login... ")
        await page.goto(JOBS_URL)
        if any(marker in page.url.lower() for marker in SESSION_BAD_MARKERS):
            await browser.close()
            raise SystemExit(f"Sesi belum valid: diarahkan ke {page.url}. State lama tidak diubah.")
        await context.storage_state(path=str(tmp))
        os.chmod(tmp, 0o600)
        tmp.replace(STATE_PATH)
        await browser.close()
    print(f"Sesi valid & disimpan: {STATE_PATH} (permission 600)")


if __name__ == "__main__":
    asyncio.run(main())
