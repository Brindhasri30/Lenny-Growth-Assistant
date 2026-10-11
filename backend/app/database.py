"""
SQLAlchemy database models and engine setup.
Tables: chat_sessions, messages, transcript_sources, transcript_chunks, artifacts, app_config.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Tuple

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    Uuid,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, relationship, sessionmaker

from app.config import get_settings


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False, default="New Chat")
    provider = Column(String(50), nullable=False, default="ollama")
    model = Column(String(100), nullable=False, default="llama3.2:3b")
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)
    is_active = Column(Boolean, nullable=False, default=True)

    messages = relationship(
        "Message", back_populates="session", cascade="all, delete-orphan", order_by="Message.created_at"
    )
    artifacts = relationship(
        "Artifact", back_populates="session", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id = Column(Uuid, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # "user" | "assistant" | "system"
    content = Column(Text, nullable=False)
    provider = Column(String(50), nullable=True)
    model = Column(String(100), nullable=True)
    citations = Column(Text, nullable=True)  # JSON array stored as text
    routing_type = Column(String(50), nullable=True)  # "chat" | "essay" | "artifact" | "retrieval"
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    session = relationship("ChatSession", back_populates="messages")


class TranscriptSource(Base):
    __tablename__ = "transcript_sources"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    source_url = Column(String(2000), nullable=True)
    source_type = Column(String(50), nullable=False, default="podcast")  # podcast | newsletter
    episode_number = Column(String(50), nullable=True)
    published_date = Column(String(50), nullable=True)
    file_path = Column(String(1000), nullable=True)
    file_hash = Column(String(64), nullable=True)  # SHA-256 to detect re-ingestion
    chunk_count = Column(Integer, nullable=False, default=0)
    ingested_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)

    chunks = relationship(
        "TranscriptChunk", back_populates="source", cascade="all, delete-orphan"
    )


class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    source_id = Column(Uuid, ForeignKey("transcript_sources.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    char_start = Column(Integer, nullable=True)
    char_end = Column(Integer, nullable=True)
    # search_vector (tsvector) added on PostgreSQL via init_db for FTS
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    source = relationship("TranscriptSource", back_populates="chunks")


class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    session_id = Column(Uuid, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(500), nullable=False)
    artifact_type = Column(String(50), nullable=False)  # "markdown" | "html" | "brief"
    content = Column(Text, nullable=False)
    citations = Column(Text, nullable=True)  # JSON
    created_at = Column(DateTime(timezone=True), nullable=False, default=utcnow)

    session = relationship("ChatSession", back_populates="artifacts")


class AppConfig(Base):
    __tablename__ = "app_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=utcnow, onupdate=utcnow)


# ── Engine / Session factory ───────────────────────────────────────────────────

_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
            echo=settings.debug,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def get_db():
    """FastAPI dependency that yields a DB session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def reset_engine():
    """Reset the cached engine and sessionmaker (used in tests)."""
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None


def check_db_connection(engine_instance=None) -> Tuple[bool, Optional[str]]:
    """Test database connectivity. Returns (is_connected, error_message)."""
    try:
        engine = engine_instance or get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, None
    except Exception as e:
        return False, str(e)


def init_db(engine_instance=None):
    """Create all tables and set up full-text search index."""
    engine = engine_instance or get_engine()
    Base.metadata.create_all(bind=engine)

    # Dialect-specific optimizations
    if engine.dialect.name == "postgresql":
        with engine.connect() as conn:
            conn.execute(
                text(
                    """
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.columns
                            WHERE table_name = 'transcript_chunks' AND column_name = 'search_vector'
                        ) THEN
                            ALTER TABLE transcript_chunks ADD COLUMN search_vector tsvector;
                        END IF;
                    END $$;
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_transcript_chunks_fts
                    ON transcript_chunks USING GIN(search_vector);
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_messages_session
                    ON messages(session_id, created_at);
                    """
                )
            )
            conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_chunks_source
                    ON transcript_chunks(source_id, chunk_index);
                    """
                )
            )
            conn.commit()
