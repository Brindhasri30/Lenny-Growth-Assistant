"""
Knowledge base status, ingestion, and search retrieval endpoints.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.database import TranscriptChunk, TranscriptSource, get_db, get_engine
from app.logging_config import get_logger
from app.retrieval import ingest_file, retrieve_relevant_chunks
from app.schemas import IngestRequest, IngestResponse, KnowledgeStatusResponse

logger = get_logger("knowledge_router")
router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


@router.get("/status", response_model=KnowledgeStatusResponse)
def get_knowledge_status(db: Session = Depends(get_db)):
    """
    Inspect the knowledge base: count of sources, total chunks,
    and verification of full-text search index readiness.
    Never invents or fabricates source data.
    """
    total_sources = db.scalar(select(func.count(TranscriptSource.id))) or 0
    total_chunks = db.scalar(select(func.count(TranscriptChunk.id))) or 0

    sources = db.scalars(
        select(TranscriptSource).order_by(TranscriptSource.ingested_at.desc()).limit(50)
    ).all()

    sources_data = [
        {
            "id": str(s.id),
            "title": s.title,
            "source_type": s.source_type,
            "episode_number": s.episode_number,
            "chunk_count": s.chunk_count,
            "ingested_at": s.ingested_at.isoformat() if s.ingested_at else None,
        }
        for s in sources
    ]

    # Check FTS index readiness
    fts_ready = False
    try:
        engine = get_engine()
        if engine.dialect.name == "postgresql":
            with engine.connect() as conn:
                res = conn.execute(
                    text(
                        """
                        SELECT 1 FROM pg_indexes 
                        WHERE tablename = 'transcript_chunks' 
                        AND indexname = 'idx_transcript_chunks_fts';
                        """
                    )
                ).fetchone()
                fts_ready = res is not None
        else:
            # Non-postgres dialect (e.g. SQLite test engine)
            fts_ready = True
    except Exception as e:
        logger.warning(f"Could not verify FTS index status: {e}")
        fts_ready = False

    return KnowledgeStatusResponse(
        total_sources=total_sources,
        total_chunks=total_chunks,
        sources=sources_data,
        fts_ready=fts_ready,
    )


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_201_CREATED)
def ingest_transcript(payload: IngestRequest, db: Session = Depends(get_db)):
    """
    Ingest a transcript file (.txt, .md, .json, .html).
    Splits into overlapping chunks, computes SHA-256 hash, and indexes in PostgreSQL.
    """
    try:
        res = ingest_file(
            file_path_str=payload.file_path,
            title=payload.title,
            db=db,
            source_url=payload.source_url,
            source_type=payload.source_type,
            episode_number=payload.episode_number,
            published_date=payload.published_date,
            force_reingest=payload.force_reingest,
        )
        return IngestResponse(**res)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ingestion failed: {e}")


@router.get("/search")
def search_knowledge(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(5, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """Search knowledge base chunks directly for debugging or citation lookup."""
    results = retrieve_relevant_chunks(query=q, db=db, top_k=limit)
    return {"query": q, "count": len(results), "results": results}
