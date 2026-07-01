import logging
import time
from collections.abc import Callable

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.responses import Response

from app.api import api_router
from app.core.config import settings
from app.core.database import SessionLocal
from app.core.logging import configure_logging
from app.core.redis import get_redis_client
from app.core.responses import ok
from app.services.provider_factory import get_embedding_provider, get_llm_provider


configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Enterprise Multi-Tool Agent Platform",
    version=settings.version,
    description="Enterprise RAG, SQL Agent, Tool Calling and Agent Planner platform.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.cors_origins],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_log_middleware(request: Request, call_next: Callable) -> Response:
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    logger.info("%s %s %s %.2fms", request.method, request.url.path, response.status_code, duration_ms)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error while processing %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "error": {"code": "internal_error"}},
    )


@app.get("/health")
def health():
    checks = {"database": "unknown", "redis": "unknown"}
    try:
        with SessionLocal() as db:
            db.execute(text("select 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover - health check detail
        checks["database"] = f"error: {exc.__class__.__name__}"

    try:
        get_redis_client().ping()
        checks["redis"] = "ok"
    except Exception as exc:  # pragma: no cover - health check detail
        checks["redis"] = f"error: {exc.__class__.__name__}"

    return {
        "status": "ok" if all(value == "ok" for value in checks.values()) else "degraded",
        "service": settings.service_name,
        "version": settings.version,
        "checks": checks,
    }


@app.get(f"{settings.api_prefix}/version")
def version():
    llm_provider = get_llm_provider()
    embedding_provider = get_embedding_provider()
    return ok(
        {
            "service": settings.service_name,
            "version": settings.version,
            "llm_provider": llm_provider.name,
            "embedding_provider": embedding_provider.name,
        }
    )


app.include_router(api_router, prefix=settings.api_prefix)

