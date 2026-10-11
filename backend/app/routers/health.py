"""
Health and readiness check endpoints.
"""
from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import check_db_connection, get_db, TranscriptChunk
from app.providers import OllamaProvider
from app.schemas import HealthResponse, ReadyResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def get_health():
    """Liveness probe: verifies the FastAPI application process is alive."""
    settings = get_settings()
    return HealthResponse(status="ok", version=settings.app_version)


@router.get("/ready", response_model=ReadyResponse)
def get_ready(response: Response, db: Session = Depends(get_db)):
    """
    Readiness probe: checks real database connectivity, Ollama reachability,
    and knowledge base availability. Never returns fabricated results.
    """
    settings = get_settings()
    details = {}

    # 1. Database check
    db_connected, db_error = check_db_connection()
    if db_connected:
        db_status = "connected"
    else:
        db_status = f"disconnected: {db_error}"
        details["database_error"] = db_error

    # 2. Ollama check
    ollama_provider = OllamaProvider()
    ollama_ok = ollama_provider.is_available()
    ollama_status = "connected" if ollama_ok else "unavailable"
    details["ollama_endpoint"] = settings.ollama_base_url
    details["ollama_model"] = settings.ollama_model

    # 3. Knowledge base check (real count from database if connected)
    kb_status = "empty"
    chunk_count = 0
    if db_connected:
        try:
            chunk_count = db.scalar(select(func.count(TranscriptChunk.id))) or 0
            kb_status = f"{chunk_count} chunks indexed" if chunk_count > 0 else "empty (0 chunks)"
        except Exception as e:
            kb_status = f"error: {str(e)}"
    else:
        kb_status = "database unavailable"

    details["chunk_count"] = chunk_count

    # Determine overall status
    if not db_connected:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        overall_status = "not_ready"
    elif not ollama_ok or chunk_count == 0:
        overall_status = "degraded"
    else:
        overall_status = "ready"

    return ReadyResponse(
        status=overall_status,
        database=db_status,
        ollama=ollama_status,
        knowledge_base=kb_status,
        details=details,
    )
