from functools import wraps
import asyncio
import inspect
from typing import Callable, Any, TypeVar, Awaitable, ParamSpec

from fastapi import Request
from starlette.concurrency import run_in_threadpool
from types import SimpleNamespace

from app.domain.errors import UnauthorizedError, ForbiddenError
from app.infrastructure.security import decode_token

P = ParamSpec("P")
R = TypeVar("R")


# =========================================================
# Helpers
# =========================================================


def _ensure_request_in_signature(
    func: Callable[..., Any], wrapper: Callable[..., Any]
) -> None:
    """
    Exposes `request: Request` in the endpoint signature so FastAPI can inject it,
    while preserving all original parameters (path, query, body).
    """
    original = inspect.signature(func)

    if "request" in original.parameters:
        wrapper.__signature__ = original
        return

    params = list(original.parameters.values())
    params.append(
        inspect.Parameter(
            "request",
            kind=inspect.Parameter.KEYWORD_ONLY,
            default=None,
            annotation=Request,
        )
    )

    wrapper.__signature__ = original.replace(parameters=params)


def _get_request_from_args(request: Request | None, args, kwargs) -> Request | None:
    if request is not None:
        return request
    for a in args:
        if isinstance(a, Request):
            return a
    kw_request = kwargs.get("request")
    if isinstance(kw_request, Request):
        return kw_request
    return None


def _attach_request_if_needed(
    func: Callable[..., Any], request: Request, kwargs: dict
) -> dict:
    sig = inspect.signature(func)
    if "request" in sig.parameters and "request" not in kwargs:
        kwargs["request"] = request
    return kwargs


def _resolve_user_from_request(req: Request):
    """
    Reads req.state.user or decodes JWT from Authorization header and attaches user to request.
    """
    user = getattr(req.state, "user", None)
    if user:
        return user

    auth_header = req.headers.get("authorization")
    if not auth_header:
        raise UnauthorizedError(message="Not authenticated")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError(message="Not authenticated")

    token = parts[1]
    try:
        claims = decode_token(token)
    except Exception:
        raise UnauthorizedError(message="Invalid or expired token")

    sub = claims.get("sub")
    roles_claim = claims.get("roles") or []

    req.state.user = SimpleNamespace(id=sub, roles=roles_claim)
    return req.state.user


# =========================================================
# Decorators
# =========================================================


def require_auth(func: Callable[P, Awaitable[R] | R]) -> Callable[P, Awaitable[R]]:
    """Ensures the request is authenticated (JWT Bearer)."""
    is_coroutine = asyncio.iscoroutinefunction(func)

    @wraps(func)
    async def wrapper(*args: P.args, request: Request = None, **kwargs: P.kwargs) -> R:
        req = _get_request_from_args(request, args, kwargs)
        if req is None:
            raise UnauthorizedError(message="Not authenticated")

        _resolve_user_from_request(req)

        call_kwargs = dict(kwargs)
        call_kwargs = _attach_request_if_needed(func, req, call_kwargs)

        if is_coroutine:
            return await func(*args, **call_kwargs)
        return await run_in_threadpool(func, *args, **call_kwargs)

    _ensure_request_in_signature(func, wrapper)
    return wrapper


def require_roles(*required_roles: str):
    """Ensures the authenticated user has at least one required role."""
    normalized_required = [r.lower() for r in required_roles]

    def decorator(func: Callable[P, Awaitable[R] | R]) -> Callable[P, Awaitable[R]]:
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def wrapper(
            *args: P.args, request: Request = None, **kwargs: P.kwargs
        ) -> R:
            req = _get_request_from_args(request, args, kwargs)
            if req is None:
                raise UnauthorizedError(message="Not authenticated")

            user = _resolve_user_from_request(req)

            user_roles = getattr(user, "roles", []) or []
            normalized_user_roles: list[str] = []

            for r in user_roles:
                if hasattr(r, "name"):
                    normalized_user_roles.append(r.name.lower())
                else:
                    normalized_user_roles.append(str(r).lower())

            if not any(role in normalized_user_roles for role in normalized_required):
                raise ForbiddenError(message="User does not have required role")

            call_kwargs = dict(kwargs)
            call_kwargs = _attach_request_if_needed(func, req, call_kwargs)

            if is_coroutine:
                return await func(*args, **call_kwargs)
            return await run_in_threadpool(func, *args, **call_kwargs)

        _ensure_request_in_signature(func, wrapper)
        return wrapper

    return decorator


__all__ = ["require_auth", "require_roles"]
