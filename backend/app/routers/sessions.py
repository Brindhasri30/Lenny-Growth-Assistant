"""
Session and message management endpoints.
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import ChatSession, Message, get_db
from app.logging_config import get_logger
from app.schemas import (
    MessageCreate,
    MessageResponse,
    MessagesResponse,
    SessionCreate,
    SessionListResponse,
    SessionResponse,
)

logger = get_logger("sessions_router")
router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=SessionListResponse)
def list_sessions(db: Session = Depends(get_db)):
    """List all active chat sessions, newest first, including message counts."""
    # Query sessions with message count
    stmt = (
        select(
            ChatSession,
            func.count(Message.id).label("message_count"),
        )
        .outerjoin(Message, ChatSession.id == Message.session_id)
        .where(ChatSession.is_active == True)
        .group_by(ChatSession.id)
        .order_by(ChatSession.updated_at.desc())
    )
    results = db.execute(stmt).all()

    session_responses = []
    for chat_session, msg_count in results:
        resp = SessionResponse(
            id=chat_session.id,
            title=chat_session.title,
            provider=chat_session.provider,
            model=chat_session.model,
            created_at=chat_session.created_at,
            updated_at=chat_session.updated_at,
            message_count=msg_count,
        )
        session_responses.append(resp)

    return SessionListResponse(sessions=session_responses, total=len(session_responses))


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    """Create a new chat session with a unique UUID."""
    settings = get_settings()
    provider = session_data.provider or settings.active_provider
    model = session_data.model or settings.active_model

    new_session = ChatSession(
        title=session_data.title or "New Chat",
        provider=provider,
        model=model,
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    logger.info(f"Created chat session: id={new_session.id} title='{new_session.title}'")

    return SessionResponse(
        id=new_session.id,
        title=new_session.title,
        provider=new_session.provider,
        model=new_session.model,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        message_count=0,
    )


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: UUID, db: Session = Depends(get_db)):
    """Retrieve a single session by its unique ID."""
    stmt = (
        select(ChatSession, func.count(Message.id).label("message_count"))
        .outerjoin(Message, ChatSession.id == Message.session_id)
        .where(ChatSession.id == session_id, ChatSession.is_active == True)
        .group_by(ChatSession.id)
    )
    row = db.execute(stmt).first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    chat_session, msg_count = row
    return SessionResponse(
        id=chat_session.id,
        title=chat_session.title,
        provider=chat_session.provider,
        model=chat_session.model,
        created_at=chat_session.created_at,
        updated_at=chat_session.updated_at,
        message_count=msg_count,
    )


@router.delete("/{session_id}", status_code=status.HTTP_200_OK)
def delete_session(session_id: UUID, db: Session = Depends(get_db)):
    """Soft-delete a chat session."""
    session = db.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    session.is_active = False
    db.commit()
    logger.info(f"Deactivated session: id={session_id}")
    return {"message": "Session deleted successfully", "id": str(session_id)}


@router.get("/{session_id}/messages", response_model=MessagesResponse)
def get_session_messages(session_id: UUID, db: Session = Depends(get_db)):
    """Retrieve all messages for a session in chronological order."""
    # Ensure session exists
    session = db.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    messages = (
        db.scalars(
            select(Message)
            .where(Message.session_id == session_id)
            .order_by(Message.created_at.asc())
        )
        .all()
    )

    formatted = [MessageResponse.from_orm_with_citations(m) for m in messages]
    return MessagesResponse(messages=formatted, total=len(formatted))


@router.post("/{session_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def create_session_message(
    session_id: UUID,
    message_data: MessageCreate,
    db: Session = Depends(get_db),
):
    """Persist a message into the specified session."""
    session = db.scalar(select(ChatSession).where(ChatSession.id == session_id, ChatSession.is_active == True))
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found",
        )

    settings = get_settings()
    new_message = Message(
        session_id=session_id,
        role="user",
        content=message_data.content,
        provider=session.provider or settings.active_provider,
        model=session.model or settings.active_model,
        routing_type=message_data.routing_hint or "chat",
    )
    db.add(new_message)

    # Auto-generate title from first user message if still default
    if session.title == "New Chat":
        words = message_data.content.strip().split()
        title_snippet = " ".join(words[:6])
        if len(words) > 6:
            title_snippet += "..."
        session.title = title_snippet[:250]

    db.commit()
    db.refresh(new_message)

    logger.info(f"Persisted message in session={session_id}: id={new_message.id} role={new_message.role}")
    return MessageResponse.from_orm_with_citations(new_message)
