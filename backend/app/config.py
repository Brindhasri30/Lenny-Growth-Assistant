"""
Application configuration using pydantic-settings.
All values are read from environment variables or .env file.
"""
from functools import lru_cache
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
     env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "Lenny Growth Assistant"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/lenny_assistant"

    # ── Ollama ───────────────────────────────────────────────────────────────
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"
    ollama_timeout: int = 120

    # ── Cloud LLM ────────────────────────────────────────────────────────────
    anthropic_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # ── Active provider ──────────────────────────────────────────────────────
    # "ollama" | "anthropic" | "openai"
    active_provider: str = "ollama"
    active_model: str = "llama3.2:3b"

    # Cloud model names
    anthropic_model: str = "claude-3-haiku-20240307"
    openai_model: str = "gpt-4o-mini"

    # ── Retrieval ────────────────────────────────────────────────────────────
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 5

    # ── CORS ─────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_anthropic_available(self) -> bool:
        return bool(self.anthropic_api_key)

    @property
    def is_openai_available(self) -> bool:
        return bool(self.openai_api_key)


@lru_cache()
def get_settings() -> Settings:
    return Settings()
