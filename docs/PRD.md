# Product Requirements Document (PRD) — The Lenny Growth Assistant

## 1. Executive Summary
**The Lenny Growth Assistant** is an AI-powered growth and product engineering copilot grounded strictly in conversations from *Lenny's Podcast*. It enables product managers, founders, and growth operators to ask tactical questions, analyze product-led growth (PLG) frameworks, produce Ship 30 for 30 essays, and inspect rich artifacts with source citations.

---

## 2. Problem Statement
General LLMs (ChatGPT, Claude) often hallucinate vague or generic startup advice when asked about nuanced growth metrics, freemium mechanics, or founder-mode decision making. Growth practitioners need:
1. **Verifiable Grounding**: Advice directly attributed to real operators (e.g., Elena Verna, Brian Chesky, Shreyas Doshi).
2. **Deterministic Citations**: Direct chunk-level links to real interview transcripts.
3. **Structured Syntheses**: Long-form essays structured around the proven Ship 30 for 30 framework (~1,250 words) rather than bulleted fluff.
4. **Rich Artifact Visuals**: Standalone sandboxed HTML and Markdown artifacts displayed alongside the conversation.
5. **Private Local Operation**: Complete usability using local open-weight models (Ollama `llama3.2:3b`) without requiring paid cloud subscriptions.

---

## 3. User Personas
- **Primary Persona:** Early-Stage Founder & Product Lead
  - Goal: Evaluate whether to build freemium vs. free-trial, prioritize retention metrics, and scale product loops.
  - Frustration: Fluffy AI answers with no backing evidence or attribution.
- **Secondary Persona:** Growth Operator / Content Creator
  - Goal: Produce insightful, structured essays and playbooks synthesizing podcast wisdom for internal distribution.

---

## 4. Key Functional Requirements

### 4.1. Conversational Chat & Persistence
- Every conversation has a persistent UUID session in PostgreSQL.
- Messages, timestamps, provider names, and routing decisions are saved.
- Multi-session sidebar allows switching without losing chat history.
- Sessions are strictly isolated from one another.

### 4.2. Grounded Knowledge Retrieval & Citations
- Multi-format transcript ingestion (`.txt`, `.md`, `.json`, `.html`).
- Overlapping text chunker (800 chars / 100 overlap) with boundary detection.
- PostgreSQL full-text search with `tsvector` and GIN index (`idx_transcript_chunks_fts`).
- Answers must explicitly surface title, chunk index, and excerpt citations.
- If evidence is lacking, the agent explicitly discloses missing data rather than fabricating facts.

### 4.3. Ship 30 for 30 Essay Skill
- Dedicated writing mode producing ~1,250-word atomic essays:
  - Compelling Hook and single core thesis.
  - 3–4 skimmable subheadings.
  - Concrete case studies grounded in interview transcripts.
  - Actionable takeaways and next steps.

### 4.4. Sandboxed Artifact Viewer
- Side-by-side desktop view for generated Markdown and HTML artifacts.
- Sandboxed iframe (`sandbox="allow-scripts"`) preventing XSS or main context leakage.
- Copy to clipboard and download actions.

### 4.5. Model Provider Abstraction
- Local default: Ollama (`llama3.2:3b`) running at `http://localhost:11434`.
- Cloud options: Anthropic Claude (`claude-3-haiku-20240307`) and OpenAI (`gpt-4o-mini`).
- Dynamic provider switcher in UI and `/api/config` endpoint.
- Clear error surfacing (no silent fallbacks).

---

## 5. Non-Functional Requirements
- **Performance:** Sub-100ms retrieval queries on PostgreSQL FTS.
- **Security:** `.env` variables strictly hidden and ignored by Git; HTML sandboxing.
- **Reliability:** Graceful degradation if PostgreSQL or Ollama is temporarily offline.
