# app/domain/errors.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AppError(Exception):
    """
    Base exception for domain/application errors.

    This exception is framework-agnostic and must be translated to HTTP
    responses by the Presentation layer.
    """

    code: str
    message: str
    http_status: int
    details: Optional[list[dict[str, Any]]] = None

    def __post_init__(self) -> None:
        super().__init__(self.message)
        if self.details is None:
            self.details = []


# -----------------------------
# Validation / Business rules
# -----------------------------

class ValidationError(AppError):
    def __init__(
        self,
        message: str = "Invalid input.",
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "VALIDATION_ERROR",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=422,
            details=details,
        )


class BusinessRuleViolation(AppError):
    """
    Explicit semantic business rule violation (still 422).
    Useful when you want a more explicit domain signal than ValidationError.
    """

    def __init__(
        self,
        message: str,
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "BUSINESS_RULE_VIOLATION",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=422,
            details=details,
        )


# -----------------------------
# Resource / access errors
# -----------------------------

class NotFoundError(AppError):
    def __init__(
        self,
        message: str = "Resource not found.",
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "NOT_FOUND",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=404,
            details=details,
        )


class ConflictError(AppError):
    def __init__(
        self,
        message: str = "Conflict.",
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "CONFLICT",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=409,
            details=details,
        )


class UnauthorizedError(AppError):
    def __init__(
        self,
        message: str = "Unauthorized.",
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "UNAUTHORIZED",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=401,
            details=details,
        )


class ForbiddenError(AppError):
    def __init__(
        self,
        message: str = "Forbidden.",
        details: Optional[list[dict[str, Any]]] = None,
        code: str = "FORBIDDEN",
    ) -> None:
        super().__init__(
            code=code,
            message=message,
            http_status=403,
            details=details,
        )
