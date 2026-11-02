from __future__ import annotations

import secrets

from fastapi import Header

from app.core.config import get_settings
from app.core.errors import UnauthorizedError


async def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    expected = get_settings().api_key
    if not expected or not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise UnauthorizedError()
