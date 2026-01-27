"""
Centralized exception handlers for the API.

Goals:
- Enforce a consistent error envelope (ADR-008)
- Always include request_id (ADR-009)
- Avoid leaking internal details or sensitive data (LGPD)
"""

from __future__ import annotations

from typing import Any, Optional

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette import status

from app.domain.errors import AppError
from app.infrastructure.request_id_middleware import get_request_id


# ----------------------------
# Error envelope helpers
# ----------------------------


def _error_response(
    *,
    request: Request,
    code: str,
    message: str,
    http_status: int,
    details: Optional[list[dict[str, Any]]] = None,
) -> JSONResponse:
    request_id = get_request_id(request)

    payload = {
        "error": {
            "code": code,
            "message": message,
            "details": details or [],
            "request_id": request_id,
        }
    }

    response = JSONResponse(status_code=http_status, content=payload)

    # Propagate correlation id to clients (ADR-009)
    if request_id:
        response.headers["X-Request-Id"] = request_id

    return response


# ----------------------------
# Handlers
# ----------------------------


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """
    Handles predictable domain/application errors using the ADR-008 envelope.
    """
    return _error_response(
        request=request,
        code=exc.code,
        message=exc.message,
        http_status=exc.http_status,
        details=exc.details,
    )


async def validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles FastAPI/Pydantic request validation errors (schema/typing).
    """
    details: list[dict[str, Any]] = []

    for err in exc.errors():
        loc = err.get("loc", ())
        field = str(loc[-1]) if loc else None
        details.append(
            {
                "field": field,
                "reason": err.get("msg", "Invalid value."),
            }
        )

    return _error_response(
        request=request,
        code="VALIDATION_ERROR",
        message="Invalid input.",
        http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        details=details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles unexpected errors. Do not leak internal details.
    The stack trace should be captured by server logs/middleware.
    """
    return _error_response(
        request=request,
        code="INTERNAL_ERROR",
        message="Internal server error.",
        http_status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details=[],
    )


# ----------------------------
# Registration helper
# ----------------------------


def register_exception_handlers(app) -> None:
    """
    Register all exception handlers on the given FastAPI app.
    Call this once during application setup (e.g., in app/main.py).
    """
    app.add_exception_handler(AppError, app_error_handler)
    app.add_exception_handler(RequestValidationError, validation_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
