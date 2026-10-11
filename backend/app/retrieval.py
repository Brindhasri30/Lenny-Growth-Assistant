"""
Text chunking, extraction, and PostgreSQL full-text retrieval service.
Supports TXT, MD, JSON, and HTML.
"""
import hashlib
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import desc, func, select, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import TranscriptChunk, TranscriptSource, get_engine
from app.logging_config import get_logger, log_retrieval
from app.schemas import Citation

logger = get_logger("retrieval_service")


def clean_text(raw: str) -> str:
    """Clean up extracted text by stripping noisy whitespaces and unreadable characters."""
    if not raw:
        return ""
    # Normalize unicode spaces
    cleaned = raw.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ newlines into 2
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    # Collapse multiple inline spaces
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    return cleaned.strip()


def extract_text_from_file(file_path: Path) -> str:
    """Extract readable text from .txt, .md, .json, or .html files."""
    suffix = file_path.suffix.lower()
    content = file_path.read_text(encoding="utf-8", errors="replace")

    if suffix in [".txt", ".md"]:
        return clean_text(content)

    elif suffix == ".html" or suffix == ".htm":
        # Basic regex-based HTML tag stripper
        text_only = re.sub(r"<script.*?>.*?</script>", "", content, flags=re.DOTALL | re.IGNORECASE)
        text_only = re.sub(r"<style.*?>.*?</style>", "", text_only, flags=re.DOTALL | re.IGNORECASE)
        text_only = re.sub(r"<[^>]+>", " ", text_only)
        return clean_text(text_only)

    elif suffix == ".json":
        try:
            data = json.loads(content)
            if isinstance(data, list):
                # Join string entries or extract common text fields
                lines = []
                for item in data:
                    if isinstance(item, str):
                        lines.append(item)
                    elif isinstance(item, dict):
                        speaker = item.get("speaker") or item.get("role") or ""
                        body = item.get("text") or item.get("content") or item.get("message") or ""
                        if speaker:
                            lines.append(f"{speaker}: {body}")
                        else:
                            lines.append(str(body))
                return clean_text("\n\n".join(lines))
            elif isinstance(data, dict):
                transcript = data.get("transcript") or data.get("text") or data.get("content")
                if transcript and isinstance(transcript, str):
                    return clean_text(transcript)
                # Fallback to serializing all values
                return clean_text(json.dumps(data, indent=2))
        except Exception as e:
            logger.warning(f"Failed parsing JSON transcript: {e}")
            return clean_text(content)

    return clean_text(content)


def compute_file_hash(text_content: str) -> str:
    """Calculate SHA-256 hash of transcript text content."""
    return hashlib.sha256(text_content.encode("utf-8")).hexdigest()


def chunk_text(
    text_content: str,
    chunk_size: int = 800,
    chunk_overlap: int = 100,
) -> List[Tuple[str, int, int]]:
    """
    Split text into overlapping chunks, preferring paragraph/sentence boundaries.
    Returns List of (chunk_text, char_start, char_end).
    """
    if not text_content:
        return []

    chunks: List[Tuple[str, int, int]] = []
    total_len = len(text_content)
    start = 0

    while start < total_len:
        end = min(start + chunk_size, total_len)

        # If not at the end of the text, try to find a natural break near the end
        if end < total_len:
            # Look backwards from 'end' for paragraph or sentence break
            break_point = -1
            search_window = text_content[max(start, end - 150):end]
            
            # Check for double newline first (paragraph break)
            para_pos = search_window.rfind("\n\n")
            if para_pos != -1:
                break_point = max(start, end - 150) + para_pos + 2
            else:
                # Check for sentence break (period, question, exclamation + space/newline)
                match = re.search(r"([.!?])(?:\s|\n)[^.!?]*$", search_window)
                if match:
                    break_point = max(start, end - 150) + match.start(1) + 1
                else:
                    # Check for simple newline or space
                    space_pos = search_window.rfind(" ")
                    if space_pos != -1:
                        break_point = max(start, end - 150) + space_pos + 1

            if break_point > start:
                end = break_point

        chunk_str = text_content[start:end].strip()
        if chunk_str:
            chunks.append((chunk_str, start, end))

        # Advance start position with overlap
        if end >= total_len:
            break
        start = max(start + 1, end - chunk_overlap)

    return chunks


def ingest_file(
    file_path_str: str,
    title: str,
    db: Session,
    source_url: Optional[str] = None,
    source_type: str = "podcast",
    episode_number: Optional[str] = None,
    published_date: Optional[str] = None,
    force_reingest: bool = False,
) -> Dict[str, Any]:
    """
    Ingest a file into transcript_sources and transcript_chunks.
    Deduplicates by file hash unless force_reingest is True.
    """
    file_path = Path(file_path_str)
    if not file_path.is_file():
        raise FileNotFoundError(f"Transcript file not found: {file_path_str}")

    settings = get_settings()
    raw_text = extract_text_from_file(file_path)
    if not raw_text:
        raise ValueError(f"Extracted content from {file_path_str} is empty")

    file_hash = compute_file_hash(raw_text)

    # Check for existing source by file_hash or title
    existing = db.scalar(
        select(TranscriptSource).where(
            (TranscriptSource.file_hash == file_hash) | (TranscriptSource.title == title)
        )
    )

    if existing and not force_reingest:
        return {
            "source_id": str(existing.id),
            "title": existing.title,
            "chunks_created": 0,
            "chunks_updated": existing.chunk_count,
            "message": f"Source '{title}' already ingested with {existing.chunk_count} chunks. Pass force_reingest=True to overwrite.",
        }

    # If reingesting, remove old chunks and source
    if existing and force_reingest:
        db.delete(existing)
        db.commit()

    # Create new source
    source = TranscriptSource(
        title=title,
        source_url=source_url,
        source_type=source_type,
        episode_number=episode_number,
        published_date=published_date,
        file_path=str(file_path.resolve()),
        file_hash=file_hash,
    )
    db.add(source)
    db.flush()

    # Split into chunks
    chunks_data = chunk_text(
        raw_text,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )

    created_chunks = []
    for idx, (c_text, c_start, c_end) in enumerate(chunks_data):
        chunk_obj = TranscriptChunk(
            source_id=source.id,
            chunk_index=idx,
            content=c_text,
            char_start=c_start,
            char_end=c_end,
        )
        created_chunks.append(chunk_obj)
        db.add(chunk_obj)

    source.chunk_count = len(created_chunks)
    db.commit()

    # Update PostgreSQL search_vector if on PostgreSQL
    engine = get_engine()
    if engine.dialect.name == "postgresql":
        try:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE transcript_chunks
                        SET search_vector = to_tsvector('english', content)
                        WHERE source_id = :sid;
                        """
                    ),
                    {"sid": source.id},
                )
                conn.commit()
        except Exception as e:
            logger.warning(f"Could not update PostgreSQL FTS tsvector: {e}")

    logger.info(f"Ingested '{title}': created {len(created_chunks)} chunks.")
    return {
        "source_id": str(source.id),
        "title": source.title,
        "chunks_created": len(created_chunks),
        "chunks_updated": 0,
        "message": f"Successfully ingested '{title}' into {len(created_chunks)} chunks.",
    }


def retrieve_relevant_chunks(
    query: str,
    db: Session,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve relevant transcript chunks using full-text search.
    On PostgreSQL: uses plainto_tsquery and ts_rank.
    Fallback (e.g. SQLite tests): uses LIKE keyword match.
    """
    if not query or not query.strip():
        return []

    settings = get_settings()
    effective_top_k = top_k or settings.retrieval_top_k
    engine = get_engine()

    results: List[Dict[str, Any]] = []

    if engine.dialect.name == "postgresql":
        try:
            # PostgreSQL full-text search with ranking
            sql = text(
                """
                SELECT 
                    c.id AS chunk_id,
                    c.source_id AS source_id,
                    c.chunk_index AS chunk_index,
                    c.content AS content,
                    s.title AS source_title,
                    s.source_url AS source_url,
                    ts_rank(c.search_vector, plainto_tsquery('english', :q)) AS rank
                FROM transcript_chunks c
                JOIN transcript_sources s ON c.source_id = s.id
                WHERE c.search_vector @@ plainto_tsquery('english', :q)
                ORDER BY rank DESC
                LIMIT :limit;
                """
            )
            rows = db.execute(sql, {"q": query, "limit": effective_top_k}).all()
            for r in rows:
                results.append({
                    "chunk_id": str(r.chunk_id),
                    "source_id": str(r.source_id),
                    "chunk_index": r.chunk_index,
                    "content": r.content,
                    "source_title": r.source_title,
                    "source_url": r.source_url,
                    "score": float(r.rank) if r.rank else 0.0,
                })
        except Exception as e:
            logger.warning(f"PostgreSQL FTS query failed: {e}. Falling back to ILIKE search.")

    # Fallback keyword matching (used if SQLite, or if FTS returned 0 results)
    if not results:
        keywords = [k.strip() for k in re.split(r"\W+", query) if len(k.strip()) > 3]
        if not keywords:
            keywords = [query.strip()]

        # Query chunks containing keywords
        stmt = (
            select(
                TranscriptChunk.id.label("chunk_id"),
                TranscriptChunk.source_id.label("source_id"),
                TranscriptChunk.chunk_index.label("chunk_index"),
                TranscriptChunk.content.label("content"),
                TranscriptSource.title.label("source_title"),
                TranscriptSource.source_url.label("source_url"),
            )
            .join(TranscriptSource, TranscriptChunk.source_id == TranscriptSource.id)
            .limit(effective_top_k * 3)
        )
        candidates = db.execute(stmt).all()

        scored = []
        for c in candidates:
            c_text_lower = c.content.lower()
            score = sum(1 for kw in keywords if kw.lower() in c_text_lower)
            if score > 0:
                scored.append((score, c))

        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        for score, c in scored[:effective_top_k]:
            results.append({
                "chunk_id": str(c.chunk_id),
                "source_id": str(c.source_id),
                "chunk_index": c.chunk_index,
                "content": c.content,
                "source_title": c.source_title,
                "source_url": c.source_url,
                "score": float(score),
            })

    log_retrieval(logger, query, len(results))
    return results


def format_citations_from_chunks(chunks: List[Dict[str, Any]]) -> List[Citation]:
    """Convert retrieved chunk dictionaries into structured Citation schemas."""
    citations: List[Citation] = []
    for c in chunks:
        # Create concise excerpt (up to 200 chars)
        content_snippet = c["content"][:200].strip()
        if len(c["content"]) > 200:
            content_snippet += "..."

        citations.append(
            Citation(
                source_id=c["source_id"],
                title=c["source_title"],
                chunk_id=c["chunk_id"],
                chunk_index=c["chunk_index"],
                source_url=c.get("source_url"),
                excerpt=content_snippet,
            )
        )
    return citations
