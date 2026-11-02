from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(
        self,
        message: str = "Terjadi kesalahan internal",
        *,
        code: str | None = None,
        details: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code
        self.details = details


class UnauthorizedError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"

    def __init__(self, message: str = "X-API-Key tidak valid atau tidak ada") -> None:
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404
    code = "NOT_FOUND"


class PlatformNotFoundError(NotFoundError):
    code = "PLATFORM_NOT_FOUND"


class RunNotFoundError(NotFoundError):
    code = "RUN_NOT_FOUND"


class ConflictError(AppError):
    status_code = 409


class PlatformDisabledError(ConflictError):
    code = "PLATFORM_DISABLED"


class RunNotCancellableError(ConflictError):
    code = "RUN_NOT_CANCELLABLE"


class ValidationAppError(AppError):
    status_code = 422
    code = "VALIDATION_ERROR"


class ServiceUnavailableError(AppError):
    status_code = 503
    code = "SERVICE_UNAVAILABLE"


def _payload(code: str, message: str, details: list[dict[str, Any]] | None = None) -> dict:
    err: dict[str, Any] = {"code": code, "message": message}
    if details:
        err["details"] = details
    return {"error": err}


def install_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(_: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code, content=_payload(exc.code, exc.message, exc.details)
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {
                "field": ".".join(str(p) for p in e["loc"][1:]) or str(e["loc"][0]),
                "issue": e["type"],
            }
            for e in exc.errors()
        ]
        first = exc.errors()[0] if exc.errors() else {"msg": "Input tidak valid"}
        return JSONResponse(
            status_code=422,
            content=_payload("VALIDATION_ERROR", first.get("msg", "Input tidak valid"), details),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _http(_: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = {401: "UNAUTHORIZED", 404: "NOT_FOUND"}.get(exc.status_code, "INTERNAL_ERROR")
        return JSONResponse(status_code=exc.status_code, content=_payload(code, str(exc.detail)))

    @app.exception_handler(Exception)
    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=500, content=_payload("INTERNAL_ERROR", "Terjadi kesalahan internal")
        )
