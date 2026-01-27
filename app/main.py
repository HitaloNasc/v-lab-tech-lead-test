import time
from datetime import datetime, timezone

from fastapi import FastAPI, Request

from app.config.settings import get_settings
from app.infrastructure.logging import JsonLogger, mask_ip, mask_user_id
from app.infrastructure.request_id_middleware import RequestIdMiddleware, get_request_id

from app.presentation.exception_handlers import register_exception_handlers
from app.presentation.offer_router import router as offer_router
from app.presentation.schemas import ErrorEnvelope

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
register_exception_handlers(app)
app.add_middleware(RequestIdMiddleware)
app.include_router(
    offer_router,
    responses={
        422: {"model": ErrorEnvelope},
        409: {"model": ErrorEnvelope},
        403: {"model": ErrorEnvelope},
        500: {"model": ErrorEnvelope},
    },
)

logger = JsonLogger(service="main")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/")
def root():
    return {"message": "V-Lab API running"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    error_code = None
    error_type = None

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as exc:
        status_code = 500
        error_code = getattr(exc, "error_code", None)
        error_type = exc.__class__.__name__
        raise
    finally:
        duration_ms = int((time.perf_counter() - start) * 1000)
        request_id = get_request_id(request)
        client_ip = mask_ip(request.client.host if request.client else None)

        route = request.scope.get("route")
        path_template = getattr(route, "path", request.url.path)

        user_id = None

        logger.info(
            "request_completed",
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": request_id,
                "http.method": request.method,
                "http.path": request.url.path,
                "http.route": path_template,
                "http.status_code": status_code,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "user_id": mask_user_id(user_id) if user_id else None,
                "error.code": error_code,
                "error.type": error_type,
            },
        )
