"""
FastAPI application entry point for The Lenny Growth Assistant.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import get_settings
from app.database import check_db_connection, init_db
from app.logging_config import get_logger, log_db_error
from app.providers import OllamaProvider, ProviderError
from app.routers.config import router as config_router
from app.routers.health import router as health_router
from app.routers.knowledge import router as knowledge_router
from app.routers.sessions import router as sessions_router

logger = get_logger("main")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager for startup and shutdown lifecycle events."""
    logger.info(
        f"Starting {settings.app_name} v{settings.app_version} "
        f"[Provider: {settings.active_provider}, Model: {settings.active_model}]"
    )

    # 1. Check and initialize database
    connected, error = check_db_connection()
    if connected:
        logger.info("Database connection established. Initializing tables...")
        try:
            init_db()
            logger.info("Database tables and search indices initialized successfully.")
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
    else:
        logger.warning(
            f"Database connection failed on startup: {error}. "
            "Backend will start in degraded mode. Database endpoints will return 503 "
            "until PostgreSQL is running and initialized."
        )

    # 2. Check Ollama reachability
    ollama_ok = OllamaProvider().is_available()
    if ollama_ok:
        logger.info(f"Ollama is reachable at {settings.ollama_base_url}")
    else:
        logger.warning(
            f"Ollama is not reachable at {settings.ollama_base_url}. "
            "Local LLM queries will fail until Ollama is started ('ollama serve')."
        )

    yield

    logger.info("Shutting down Lenny Growth Assistant.")


app = FastAPI(
    title=settings.app_name,
    description="An AI assistant grounded in Lenny's Podcast transcripts.",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ───────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Global Exception Handlers ──────────────────────────────────────────────────
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "detail": exc.errors(),
            "code": "VALIDATION_ERROR",
        },
    )


@app.exception_handler(ProviderError)
async def provider_exception_handler(request: Request, exc: ProviderError):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE if exc.recoverable else status.HTTP_400_BAD_REQUEST
    return JSONResponse(
        status_code=status_code,
        content={
            "error": f"Provider Error ({exc.provider})",
            "detail": str(exc),
            "code": "PROVIDER_ERROR",
        },
    )


@app.exception_handler(SQLAlchemyError)
async def database_exception_handler(request: Request, exc: SQLAlchemyError):
    log_db_error(logger, "request_handler", exc)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Database Service Error",
            "detail": "Database is unreachable or operation failed. Verify PostgreSQL is running.",
            "code": "DATABASE_ERROR",
        },
    )


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health_router)
app.include_router(config_router)
app.include_router(sessions_router)
app.include_router(knowledge_router)


@app.get("/")
def home():
    """Root info endpoint."""
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "status": "online",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
    }
