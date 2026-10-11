"""
Model and application configuration endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import AppConfig, get_db
from app.logging_config import get_logger
from app.providers import list_available_providers
from app.schemas import ConfigResponse, ConfigUpdateRequest

logger = get_logger("config_router")
router = APIRouter(prefix="/api/config", tags=["Configuration"])


@router.get("", response_model=ConfigResponse)
def get_config(db: Session = Depends(get_db)):
    """Retrieve the current active provider, model, and available providers."""
    settings = get_settings()

    # Check for overrides stored in DB app_config
    active_provider = settings.active_provider
    active_model = settings.active_model
    try:
        provider_cfg = db.scalar(select(AppConfig).where(AppConfig.key == "active_provider"))
        if provider_cfg:
            active_provider = provider_cfg.value
        model_cfg = db.scalar(select(AppConfig).where(AppConfig.key == "active_model"))
        if model_cfg:
            active_model = model_cfg.value
    except Exception as e:
        logger.warning(f"Could not read config from DB: {e}")

    return ConfigResponse(
        active_provider=active_provider,
        active_model=active_model,
        ollama_model=settings.ollama_model,
        ollama_base_url=settings.ollama_base_url,
        anthropic_model=settings.anthropic_model,
        openai_model=settings.openai_model,
        available_providers=list_available_providers(),
    )


@router.put("", response_model=ConfigResponse)
def update_config(update: ConfigUpdateRequest, db: Session = Depends(get_db)):
    """
    Update active provider and/or model.
    Validates provider credentials before saving.
    """
    settings = get_settings()
    available = list_available_providers()

    if update.provider not in ["ollama", "anthropic", "openai"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider '{update.provider}'. Choose from: ollama, anthropic, openai",
        )

    # Validate cloud provider keys
    if update.provider == "anthropic" and not settings.anthropic_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot select Anthropic: ANTHROPIC_API_KEY is not configured in .env",
        )
    if update.provider == "openai" and not settings.openai_api_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot select OpenAI: OPENAI_API_KEY is not configured in .env",
        )

    # Determine default model for provider if not explicitly given
    model = update.model
    if not model:
        if update.provider == "ollama":
            model = settings.ollama_model
        elif update.provider == "anthropic":
            model = settings.anthropic_model
        elif update.provider == "openai":
            model = settings.openai_model

    # Persist to database app_config
    try:
        p_row = db.scalar(select(AppConfig).where(AppConfig.key == "active_provider"))
        if not p_row:
            p_row = AppConfig(key="active_provider", value=update.provider)
            db.add(p_row)
        else:
            p_row.value = update.provider

        m_row = db.scalar(select(AppConfig).where(AppConfig.key == "active_model"))
        if not m_row:
            m_row = AppConfig(key="active_model", value=model)
            db.add(m_row)
        else:
            m_row.value = model

        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to persist config update to DB: {e}")

    logger.info(f"Updated configuration: provider={update.provider}, model={model}")

    return ConfigResponse(
        active_provider=update.provider,
        active_model=model,
        ollama_model=settings.ollama_model,
        ollama_base_url=settings.ollama_base_url,
        anthropic_model=settings.anthropic_model,
        openai_model=settings.openai_model,
        available_providers=list_available_providers(),
    )
