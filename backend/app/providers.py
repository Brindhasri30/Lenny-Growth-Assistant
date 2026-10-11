"""
Model provider adapters.

Supports:
- Ollama (local, no API key required)
- Anthropic Claude (cloud, requires ANTHROPIC_API_KEY)
- OpenAI (cloud, requires OPENAI_API_KEY)

Each adapter implements a common interface: generate(messages) -> str
"""
import json
from typing import Any, Dict, List, Optional
from abc import ABC, abstractmethod

import httpx

from app.config import get_settings
from app.logging_config import get_logger, log_provider_selection

logger = get_logger(__name__)


class ProviderError(Exception):
    """Raised when a model provider call fails."""
    def __init__(self, message: str, provider: str, recoverable: bool = True):
        super().__init__(message)
        self.provider = provider
        self.recoverable = recoverable


class BaseProvider(ABC):
    name: str = "base"

    @abstractmethod
    def generate(self, messages: List[Dict[str, str]], system: Optional[str] = None) -> str:
        """Generate a response given a list of messages."""
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """Check if this provider is currently available."""
        ...


# ── Ollama ─────────────────────────────────────────────────────────────────────

class OllamaProvider(BaseProvider):
    name = "ollama"

    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        try:
            with httpx.Client(timeout=5) as client:
                resp = client.get(f"{self.settings.ollama_base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    def generate(self, messages: List[Dict[str, str]], system: Optional[str] = None) -> str:
        settings = get_settings()
        log_provider_selection(logger, "ollama", settings.ollama_model)

        payload: Dict[str, Any] = {
            "model": settings.ollama_model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 2048},
        }
        if system:
            payload["messages"] = [{"role": "system", "content": system}] + messages

        try:
            with httpx.Client(timeout=settings.ollama_timeout) as client:
                resp = client.post(
                    f"{settings.ollama_base_url}/api/chat",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                return data["message"]["content"]
        except httpx.ConnectError:
            raise ProviderError(
                f"Cannot connect to Ollama at {settings.ollama_base_url}. "
                "Ensure Ollama is running: run 'ollama serve' in a terminal.",
                provider="ollama",
                recoverable=True,
            )
        except httpx.TimeoutException:
            raise ProviderError(
                f"Ollama request timed out after {settings.ollama_timeout}s.",
                provider="ollama",
                recoverable=True,
            )
        except httpx.HTTPStatusError as e:
            raise ProviderError(
                f"Ollama returned HTTP {e.response.status_code}: {e.response.text[:200]}",
                provider="ollama",
                recoverable=False,
            )
        except Exception as e:
            raise ProviderError(str(e), provider="ollama", recoverable=False)


# ── Anthropic ──────────────────────────────────────────────────────────────────

class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return bool(self.settings.anthropic_api_key)

    def generate(self, messages: List[Dict[str, str]], system: Optional[str] = None) -> str:
        settings = get_settings()
        if not settings.anthropic_api_key:
            raise ProviderError(
                "Anthropic API key not configured. Set ANTHROPIC_API_KEY in your .env file.",
                provider="anthropic",
                recoverable=False,
            )
        log_provider_selection(logger, "anthropic", settings.anthropic_model)

        # Convert to Anthropic message format
        anthropic_messages = []
        for msg in messages:
            if msg["role"] in ("user", "assistant"):
                anthropic_messages.append({"role": msg["role"], "content": msg["content"]})

        headers = {
            "x-api-key": settings.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": settings.anthropic_model,
            "max_tokens": 4096,
            "messages": anthropic_messages,
        }
        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 401:
                    raise ProviderError(
                        "Invalid Anthropic API key. Check ANTHROPIC_API_KEY in your .env.",
                        provider="anthropic",
                        recoverable=False,
                    )
                if resp.status_code == 429:
                    raise ProviderError(
                        "Anthropic rate limit reached. Please wait and try again.",
                        provider="anthropic",
                        recoverable=True,
                    )
                resp.raise_for_status()
                data = resp.json()
                return data["content"][0]["text"]
        except ProviderError:
            raise
        except httpx.ConnectError:
            raise ProviderError(
                "Cannot connect to Anthropic API. Check your internet connection.",
                provider="anthropic",
                recoverable=True,
            )
        except Exception as e:
            raise ProviderError(str(e), provider="anthropic", recoverable=False)


# ── OpenAI ─────────────────────────────────────────────────────────────────────

class OpenAIProvider(BaseProvider):
    name = "openai"

    def __init__(self):
        self.settings = get_settings()

    def is_available(self) -> bool:
        return bool(self.settings.openai_api_key)

    def generate(self, messages: List[Dict[str, str]], system: Optional[str] = None) -> str:
        settings = get_settings()
        if not settings.openai_api_key:
            raise ProviderError(
                "OpenAI API key not configured. Set OPENAI_API_KEY in your .env file.",
                provider="openai",
                recoverable=False,
            )
        log_provider_selection(logger, "openai", settings.openai_model)

        oai_messages = []
        if system:
            oai_messages.append({"role": "system", "content": system})
        oai_messages.extend(messages)

        headers = {
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload: Dict[str, Any] = {
            "model": settings.openai_model,
            "messages": oai_messages,
            "max_tokens": 4096,
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=60) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                )
                if resp.status_code == 401:
                    raise ProviderError(
                        "Invalid OpenAI API key. Check OPENAI_API_KEY in your .env.",
                        provider="openai",
                        recoverable=False,
                    )
                if resp.status_code == 429:
                    raise ProviderError(
                        "OpenAI rate limit reached. Please wait and try again.",
                        provider="openai",
                        recoverable=True,
                    )
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except ProviderError:
            raise
        except httpx.ConnectError:
            raise ProviderError(
                "Cannot connect to OpenAI API. Check your internet connection.",
                provider="openai",
                recoverable=True,
            )
        except Exception as e:
            raise ProviderError(str(e), provider="openai", recoverable=False)


# ── Provider Registry ──────────────────────────────────────────────────────────

_providers: Dict[str, BaseProvider] = {
    "ollama": OllamaProvider(),
    "anthropic": AnthropicProvider(),
    "openai": OpenAIProvider(),
}


def get_provider(name: Optional[str] = None) -> BaseProvider:
    """Return the active provider or a named provider."""
    settings = get_settings()
    provider_name = name or settings.active_provider
    if provider_name not in _providers:
        raise ProviderError(
            f"Unknown provider '{provider_name}'. Valid options: {list(_providers.keys())}",
            provider=provider_name,
            recoverable=False,
        )
    return _providers[provider_name]


def list_available_providers() -> List[str]:
    """Return list of providers that have necessary credentials."""
    available = ["ollama"]  # Always listed; availability checked at call time
    settings = get_settings()
    if settings.anthropic_api_key:
        available.append("anthropic")
    if settings.openai_api_key:
        available.append("openai")
    return available
