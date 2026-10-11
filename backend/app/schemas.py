"""
Pydantic request/response schemas for all API endpoints.
"""
import json
from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ── Config ────────────────────────────────────────────────────────────────────

class ConfigResponse(BaseModel):
    active_provider: str
    active_model: str
    ollama_model: str
    ollama_base_url: str
    anthropic_model: str
    openai_model: str
    available_providers: list[str]


class ConfigUpdateRequest(BaseModel):
    provider: str = Field(..., pattern="^(ollama|anthropic|openai)$")
    model: Optional[str] = None


# ── Sessions ──────────────────────────────────────────────────────────────────

class SessionCreate(BaseModel):
    title: Optional[str] = "New Chat"
    provider: Optional[str] = None
    model: Optional[str] = None


class SessionResponse(BaseModel):
    id: UUID
    title: str
    provider: str
    model: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int


# ── Messages ──────────────────────────────────────────────────────────────────

class Citation(BaseModel):
    source_id: str
    title: str
    chunk_id: str
    chunk_index: int
    source_url: Optional[str] = None
    excerpt: str


class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=32000)
    routing_hint: Optional[str] = None  # "essay" | "artifact" | "chat"

    @field_validator("content")
    @classmethod
    def content_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message content cannot be blank")
        return v


class MessageResponse(BaseModel):
    id: UUID
    session_id: UUID
    role: str
    content: str
    provider: Optional[str] = None
    model: Optional[str] = None
    citations: Optional[List[Citation]] = None
    routing_type: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_with_citations(cls, msg) -> "MessageResponse":
        citations = None
        if msg.citations:
            try:
                raw = json.loads(msg.citations)
                citations = [Citation(**c) for c in raw]
            except Exception:
                citations = None
        return cls(
            id=msg.id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            provider=msg.provider,
            model=msg.model,
            citations=citations,
            routing_type=msg.routing_type,
            created_at=msg.created_at,
        )


class MessagesResponse(BaseModel):
    messages: List[MessageResponse]
    total: int


# ── Knowledge / Ingestion ─────────────────────────────────────────────────────

class IngestRequest(BaseModel):
    file_path: str = Field(..., description="Absolute or relative path to transcript file")
    title: str = Field(..., min_length=1, max_length=500)
    source_url: Optional[str] = None
    source_type: str = Field("podcast", pattern="^(podcast|newsletter|other)$")
    episode_number: Optional[str] = None
    published_date: Optional[str] = None
    force_reingest: bool = False


class IngestResponse(BaseModel):
    source_id: str
    title: str
    chunks_created: int
    chunks_updated: int
    message: str


class KnowledgeStatusResponse(BaseModel):
    total_sources: int
    total_chunks: int
    sources: List[dict]
    fts_ready: bool


# ── Artifacts ─────────────────────────────────────────────────────────────────

class ArtifactCreate(BaseModel):
    session_id: Optional[UUID] = None
    title: str = Field(..., min_length=1, max_length=500)
    artifact_type: str = Field(..., pattern="^(markdown|html|brief)$")
    content: str = Field(..., min_length=1)
    citations: Optional[List[Citation]] = None


class ArtifactResponse(BaseModel):
    id: UUID
    session_id: Optional[UUID]
    title: str
    artifact_type: str
    content: str
    citations: Optional[List[Citation]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Health ────────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str


class ReadyResponse(BaseModel):
    status: str
    database: str
    ollama: str
    knowledge_base: str
    details: Optional[dict] = None



# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[Any] = None
    code: Optional[str] = None
