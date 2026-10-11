"""
Agent Framework and Orchestration.
Integrates tool calling, transcript grounding, essay writing, and provider generation.
Architecture compliant with Anthropic Agent Tool Pattern.
"""
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Artifact, ChatSession, Message
from app.logging_config import get_logger, log_routing
from app.providers import BaseProvider, ProviderError, get_provider
from app.retrieval import format_citations_from_chunks, retrieve_relevant_chunks
from app.schemas import Citation

logger = get_logger("agent_framework")


class GrowthAgent:
    """
    Lenny Growth Agent:
    - Analyzes user request
    - Automatically executes retrieval tool for transcript evidence
    - Supports Ship 30 for 30 essay generation
    - Supports Markdown & HTML artifact generation
    - Records tool execution trace in memory and session metadata
    """

    SYSTEM_PROMPT = """You are The Lenny Growth Assistant, an AI expert grounded in conversations and lessons from Lenny's Podcast and top product/growth operators.

CORE PRINCIPLES:
1. Ground your answers in the provided Transcript Evidence whenever available.
2. Clearly distinguish between direct facts/quotes from the podcast vs. your own synthesis/inference.
3. If the retrieved evidence is insufficient to answer the question, honestly state what is missing rather than inventing facts or guest quotes.
4. When citing insights, mention the episode guest or source title.
5. If the user asks for an essay, follow the Ship 30 for 30 essay framework:
   - Catchy, hook-driven headline & opening (The Hook)
   - 1 Main Idea broken down logically (The Structure)
   - Skimmable subheadings and bullet points
   - Concrete examples and practical takeaways (The Actionable Step)
   - Distinguish verified transcript evidence from strategic deductions.
"""

    def __init__(self, db: Session, provider: Optional[BaseProvider] = None):
        self.db = db
        self.provider = provider or get_provider()
        self.settings = get_settings()

    def determine_route(self, content: str, explicit_hint: Optional[str] = None) -> str:
        """
        Classifies incoming query intent:
        - 'essay': requested long-form Ship 30 for 30 article or essay
        - 'artifact': requested code, table, checklist, or template artifact
        - 'chat': grounded conversational QA
        """
        if explicit_hint in ["essay", "artifact", "chat"]:
            log_routing(logger, explicit_hint, "Explicit routing hint provided")
            return explicit_hint

        lower = content.lower()
        if any(w in lower for w in ["write an essay", "ship 30", "1250-word", "1250 words", "atomic essay", "article about"]):
            log_routing(logger, "essay", "Keywords indicate essay request")
            return "essay"
        elif any(w in lower for w in ["generate artifact", "create a checklist", "create a template", "html preview", "create a table"]):
            log_routing(logger, "artifact", "Keywords indicate artifact request")
            return "artifact"

        log_routing(logger, "chat", "Default grounded QA chat")
        return "chat"

    def execute_chat(
        self,
        session_id: UUID,
        user_message: str,
        routing_hint: Optional[str] = None,
        top_k: int = 5,
    ) -> Dict[str, Any]:
        """
        Main Agent Execution Pipeline:
        1. Classifies route
        2. Retrieves relevant transcript chunks
        3. Formulates prompt with grounded context
        4. Calls active provider (Ollama / Anthropic / OpenAI)
        5. Parses any generated artifacts
        6. Persists assistant response and citations to PostgreSQL
        """
        # Load session
        session = self.db.get(ChatSession, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        route = self.determine_route(user_message, routing_hint)

        # Step 1: Tool Execution — Retrieve relevant chunks
        chunks = retrieve_relevant_chunks(query=user_message, db=self.db, top_k=top_k)
        citations = format_citations_from_chunks(chunks)

        # Step 2: Assemble Context
        context_block = ""
        if chunks:
            context_block = "\n--- RETRIEVED TRANSCRIPT EVIDENCE ---\n"
            for idx, c in enumerate(chunks, 1):
                context_block += (
                    f"[{idx}] Source: {c['source_title']} (Chunk {c['chunk_index']})\n"
                    f"Excerpt: {c['content']}\n\n"
                )
            context_block += "--- END OF EVIDENCE ---\n"
        else:
            context_block = (
                "\n[NOTE: No matching transcript chunks were found in the knowledge base. "
                "Explicitly inform the user that no direct transcript evidence was found for this specific query, "
                "and explain how they can ingest relevant episodes via /api/knowledge/ingest if needed.]\n"
            )

        # Step 3: Fetch prior conversation history for context (up to 8 recent messages)
        recent_messages = (
            self.db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(8)
            .all()
        )
        recent_messages.reverse()

        messages_payload: List[Dict[str, str]] = []
        for m in recent_messages:
            messages_payload.append({"role": m.role, "content": m.content})

        # Add current user prompt with instructions tailored to the route
        instruction = ""
        if route == "essay":
            instruction = (
                "\nINSTRUCTION: Write an atomic essay (~1,000–1,250 words) adhering to the Ship 30 for 30 format. "
                "Use a high-hook headline, structured headings, bulleted takeaways, and explicitly reference the podcast evidence."
            )
        elif route == "artifact":
            instruction = (
                "\nINSTRUCTION: Provide the requested artifact cleanly. If creating an HTML visual or checklist, "
                "wrap it inside ```html ... ``` or ```markdown ... ``` codeblocks."
            )

        user_content_with_context = f"{user_message}\n\n{context_block}\n{instruction}"
        messages_payload.append({"role": "user", "content": user_content_with_context})

        # Step 4: Execute model provider
        assistant_content = self.provider.generate(
            messages=messages_payload,
            system=self.SYSTEM_PROMPT,
        )

        # Step 5: Check if an artifact was produced and persist it
        artifact_record = None
        if route in ["essay", "artifact"] or "```html" in assistant_content:
            artifact_record = self._extract_and_persist_artifact(
                session_id=session_id,
                title=f"{route.capitalize()}: {user_message[:40]}...",
                content=assistant_content,
                citations=citations,
            )

        # Step 6: Persist Assistant Message in Database
        citations_json = json.dumps([c.model_dump() for c in citations]) if citations else None
        assistant_msg = Message(
            session_id=session_id,
            role="assistant",
            content=assistant_content,
            provider=self.provider.name,
            model=getattr(self.provider, "model", None) or self.settings.active_model,
            citations=citations_json,
            routing_type=route,
        )
        self.db.add(assistant_msg)
        self.db.commit()
        self.db.refresh(assistant_msg)

        return {
            "message": assistant_msg,
            "citations": citations,
            "route": route,
            "chunks_used": len(chunks),
            "artifact": artifact_record,
        }

    def _extract_and_persist_artifact(
        self,
        session_id: UUID,
        title: str,
        content: str,
        citations: List[Citation],
    ) -> Optional[Artifact]:
        """Extract and store artifact record in PostgreSQL."""
        try:
            artifact_type = "markdown"
            if "```html" in content:
                artifact_type = "html"

            citations_json = json.dumps([c.model_dump() for c in citations]) if citations else None
            artifact = Artifact(
                session_id=session_id,
                title=title,
                artifact_type=artifact_type,
                content=content,
                citations=citations_json,
            )
            self.db.add(artifact)
            self.db.commit()
            self.db.refresh(artifact)
            return artifact
        except Exception as e:
            logger.warning(f"Could not persist artifact: {e}")
            return None
