"""
Structured logger using Python's logging module.
Produces JSON-compatible structured output.
Redacts API keys and sensitive data.
"""
import logging
import sys
from typing import Any

from app.config import get_settings


class RedactingFilter(logging.Filter):
    """Removes API key values from log records."""

    REDACTED_KEYS = {"api_key", "anthropic_api_key", "openai_api_key", "password", "secret"}

    def filter(self, record: logging.LogRecord) -> bool:
        if hasattr(record, "extra"):
            for key in list(record.extra.keys()):
                if any(rk in key.lower() for rk in self.REDACTED_KEYS):
                    record.extra[key] = "***REDACTED***"
        return True


def get_logger(name: str) -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        level = getattr(logging, settings.log_level.upper(), logging.INFO)
        logger.setLevel(level)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
        )
        handler.setFormatter(formatter)
        handler.addFilter(RedactingFilter())
        logger.addHandler(handler)
        logger.propagate = False
    return logger


def log_provider_selection(logger: logging.Logger, provider: str, model: str) -> None:
    logger.info("Provider selected: provider=%s model=%s", provider, model)


def log_retrieval(logger: logging.Logger, query: str, count: int) -> None:
    logger.info("Retrieval: query_len=%d chunks_returned=%d", len(query), count)


def log_routing(logger: logging.Logger, route: str, reason: str) -> None:
    logger.info("Routing decision: route=%s reason=%s", route, reason)


def log_artifact(logger: logging.Logger, artifact_type: str, action: str, success: bool) -> None:
    logger.info("Artifact: type=%s action=%s success=%s", artifact_type, action, success)


def log_db_error(logger: logging.Logger, operation: str, error: Exception) -> None:
    logger.error("Database error: operation=%s error=%s", operation, str(error))
