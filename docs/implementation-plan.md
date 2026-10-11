# Lenny Growth Assistant — Implementation Plan

**Project:** Lenny Growth Assistant  
**Developer:** Build managed by Antigravity AI  
**Target Stack:** FastAPI · PostgreSQL · React/Vite · Ollama (llama3.2:3b) · Anthropic/OpenAI  
**Date:** 2026-10-11

---

## Overview

The project is built in 12 sequential milestones. Each milestone has a defined scope, acceptance tests, and a required Git commit. No milestone begins until the previous one is reviewed and approved.

---

## Milestone 1 — Workspace Audit and Git Baseline ✅ (Current)

**Scope**
- Full inspection of existing files, installed tools, venv packages, service statuses
- Create `.gitignore` (excludes venv, node_modules, .env, secrets)
- Create `docs/implementation-plan.md` (this file) and `docs/requirements-checklist.md`
- Initialize Git repository; check for remote
- Report exact state without fabricating results

**Acceptance Tests**
- `git status` shows clean working tree after commit (no secrets, no venv)
- `.gitignore` excludes `backend/venv/`, `node_modules/`, `.env`
- Both docs files exist and are accurate
- Git log shows at least one commit

**Expected Commit:** `chore: workspace audit, .gitignore, and implementation plan`

---

## Milestone 2 — Database Schema and Backend Foundation

> **Status:** ✅ Implemented — Ready for manual/terminal verification by user

**Scope**
- PostgreSQL database creation instructions
- SQLAlchemy models: `chat_sessions`, `messages`, `transcript_sources`, `transcript_chunks`, `artifacts`, `app_config`
- Full-text search (tsvector) GIN index on `transcript_chunks`
- `init_db()` to create all tables
- `.env.example` with all required variables documented
- `backend/requirements.txt` pinning all packages plus additions (`pytest`, `anthropic`)
- `/health` and `/ready` endpoints that test real DB connectivity
- Pydantic schemas for all models
- Structured logging module with API-key redaction

**Acceptance Tests**
- Run `init_db()` against real PostgreSQL; all tables created
- `GET /health` returns `{"status": "ok"}`
- `GET /ready` returns real database status (not fabricated)
- `.env.example` contains no real secrets

**Expected Commit:** `feat: database schema, health endpoints, and environment config`

---

## Milestone 3 — Session and Message Persistence

**Scope**
- `POST /api/sessions` — create new session with unique UUID
- `GET /api/sessions` — list all sessions with message counts
- `GET /api/sessions/{id}` — get single session
- `DELETE /api/sessions/{id}` — soft-delete
- `GET /api/sessions/{id}/messages` — retrieve all messages
- `POST /api/sessions/{id}/messages` — persist message with role, content, timestamp
- Session isolation guaranteed: messages never cross-contaminate
- Input validation via Pydantic; structured 422/404 errors

**Acceptance Tests**
- Create two sessions; verify messages are isolated
- Restart backend; verify messages survive (real persistence)
- Invalid session ID returns 404 with clear error
- Missing required fields return 422 with field-level errors

**Expected Commit:** `feat: session CRUD and message persistence with isolation`

---

## Milestone 4 — Ollama Integration and Provider Abstraction

**Scope**
- `OllamaProvider` using `httpx` to call Ollama `/api/chat`
- `AnthropicProvider` (requires `ANTHROPIC_API_KEY`)
- `OpenAIProvider` (requires `OPENAI_API_KEY`)
- Provider registry with `get_provider(name)` factory
- `GET /api/config` — active provider, model, available providers
- `PUT /api/config` — switch provider/model with validation
- Provider errors surface as 503/400 — never silent fallback
- Missing cloud key = explicit error, not fallback to Ollama

**Acceptance Tests**
- Chat via Ollama with llama3.2:3b returns real response
- Switching to Anthropic without key returns 400 with clear message
- Ollama unavailable returns 503 with helpful text
- `GET /api/config` reflects active provider correctly

**Expected Commit:** `feat: Ollama and cloud provider adapters with explicit error handling`

---

## Milestone 5 — Transcript Ingestion and Retrieval

**Scope**
- `POST /api/knowledge/ingest` — file path, title, metadata
- Text extraction for TXT, MD, JSON, HTML formats
- Chunker: chunk_size=800, chunk_overlap=100
- SHA-256 hash per source for deduplication
- Update tsvector `search_vector` column after ingestion
- `GET /api/knowledge/status` — source count, chunk count, FTS readiness
- `retrieve(query, top_k)` using PostgreSQL `plainto_tsquery`
- Returns chunks with source_id, title, source_url, excerpt
- CLI: `python -m app.ingest <file> --title "..." --url "..."`
- Honest empty-state: no transcripts = empty results, not invented content

**Acceptance Tests**
- Ingest sample .txt file; verify chunks appear in DB
- Re-ingest same file; verify no duplicate sources
- Retrieve with query; verify citations include source title and chunk ID
- Empty KB returns `{"total_sources": 0}` — no invented results

**Expected Commit:** `feat: transcript ingestion pipeline and PostgreSQL full-text retrieval`

---

## Milestone 6 — Grounded Chat with Citations

**Scope**
- Agent orchestration module routing messages to correct handler
- Routing: detect essay intent, artifact intent, general chat
- General chat: retrieve chunks → inject into system prompt → generate
- System prompt instructs model to answer only from retrieved evidence
- Insufficient evidence = honest "not enough evidence" response
- Citations on every assistant message using retrieved evidence
- `POST /api/sessions/{id}/messages` wired to full pipeline
- Log routing decisions, retrieval count, provider used

**Acceptance Tests**
- Ask answerable question; verify citations in response
- Ask unanswerable question; verify evidence-gap message, no citations
- Follow-up in same session uses prior context
- Different session has no context from another session

**Expected Commit:** `feat: grounded chat pipeline with retrieval, citations, and routing`

---

## Milestone 7 — Ship 30 for 30 Writing Skill

**Scope**
- `backend/app/skills/ship_30_for_30.md` skill file
- Essay router triggered by intent signals or `routing_hint: "essay"`
- Uses retrieved transcript evidence as sole source material
- Enforces ~1,250 words, hook, central idea, narrative, headings, bold, examples, takeaways, memorable ending
- Citations required; no fabricated quotes, stats, or attributions
- Evidence-gap response if insufficient transcript coverage
- Essay output stored as DB artifact

**Acceptance Tests**
- Essay on covered topic: ~1,250 words with required structure
- Essay on uncovered topic: evidence-gap response, no invented content
- Essay cites specific transcript sources
- No fabricated content in any essay

**Expected Commit:** `feat: Ship 30 for 30 essay skill with grounded evidence and citations`

---

## Milestone 8 — Artifact Generation and Secure Viewer API

**Scope**
- `POST /api/artifacts` — create/persist artifact (markdown, html, brief)
- `GET /api/artifacts/{id}` — retrieve persisted artifact
- Artifact generation: product briefs, landing page HTML, growth plans
- HTML artifacts flagged for sandboxed rendering
- Security rules documented
- Artifacts in `artifacts` DB table with session association
- Failures return clear error, never silently return empty content

**Acceptance Tests**
- Generate Markdown brief; verify it persists in DB
- Retrieve artifact by ID; verify complete content
- HTML artifact flagged for sandboxed rendering
- Missing `content` field returns 422

**Expected Commit:** `feat: artifact generation API with persistence and security metadata`

---

## Milestone 9 — React Frontend (Core UI)

**Scope**
- Vite + React + JavaScript project in `frontend/`
- Professional light SaaS design: Inter font, clean palette
- Sidebar: New Chat button, conversation history with timestamps
- Main: message bubbles (user right, assistant left), timestamps, loading state
- Model/provider selector in header
- Error states with retry
- Artifact Viewer panel (right on desktop, tab on mobile)
- Citation display below assistant messages
- Responsive: sidebar collapses on mobile
- Accessible: keyboard nav, focus indicators, contrast compliance

**Acceptance Tests**
- Loads at `http://localhost:5173` without console errors
- New Chat creates session; messages persist on page reload
- Loading spinner visible during response
- Error shown if backend unreachable
- Model selector reflects active provider; changing calls `PUT /api/config`

**Expected Commit:** `feat: React frontend with chat UI, sidebar, and provider selector`

---

## Milestone 10 — Frontend Artifact Viewer and Secure Rendering

**Scope**
- Artifact Viewer component beside chat on desktop
- Preview tab: Markdown rendered via DOMPurify-sanitized renderer
- Source tab: raw content with syntax highlighting
- HTML artifacts in `<iframe sandbox="allow-same-origin allow-scripts">`
- No direct innerHTML injection of untrusted HTML into main DOM
- Copy button; Download button (.md or .html)
- Mobile: tab toggle between Chat and Artifact
- Clear error on artifact failure

**Acceptance Tests**
- Markdown renders with formatting (bold, headings, lists)
- HTML artifact in sandboxed iframe, not injected into main DOM
- Copy button copies raw content
- Download triggers file download
- XSS test: `<script>alert(1)</script>` does not execute in main window

**Expected Commit:** `feat: secure artifact viewer with sandboxed HTML and Markdown rendering`

---

## Milestone 11 — Tests, Documentation, and Deployment Config

**Scope**
- `backend/tests/`: pytest tests for health, sessions, messages, retrieval, providers, essays, artifacts
- All external providers mocked in tests (no paid API calls)
- Frontend tests (Vitest + RTL): loading, error, session list, model selector
- `README.md` — zero-to-running setup on Windows
- `docs/PRD.md` — product requirements document
- `docs/design.md` — visual principles, IA, accessibility
- `docs/architecture.md` — full system architecture
- `agent-transcripts/README.md` — transcript ingestion guide
- `Dockerfile` + `docker-compose.yml`
- Native Windows `start.bat` startup script

**Acceptance Tests**
- `pytest backend/tests/` — pass/fail reported honestly
- Frontend test suite — results reported honestly
- `start.bat` starts backend in one command

**Expected Commit:** `docs: full documentation, tests, deployment config, and startup scripts`

---

## Milestone 12 — Final Polish, Demo Script, and Submission

**Scope**
- End-to-end verification of full user flow
- Fix remaining bugs found during E2E
- `agent-transcripts/implementation-log.md` — honest implementation decisions and failures
- `agent-transcripts/demo-script.md` — 2-3 minute camera-on demo script
- Submission URL in README: https://forms.gle/LgotDHNVxW1mbzNE7
- Final Git commit; push to GitHub if remote is configured

**Acceptance Tests**
- Full flow: new chat → grounded question → citations → essay → artifact viewer → copy/download
- Ollama local demo works without any API key
- All documentation files exist and are accurate
- No secrets in any committed file
- Git log shows all milestone commits

**Expected Commit:** `chore: final polish, demo script, and submission preparation`

---

## Risk Register

| Risk | Mitigation |
|---|---|
| Shell execution blocked in Antigravity IDE | All commands documented for manual execution |
| PostgreSQL not yet set up | Step-by-step instructions in README |
| Anthropic SDK Python 3.10 compatibility | Use direct httpx calls to Anthropic REST API |
| Docker Desktop unavailable | Native Windows workflow is primary path |
| No Git remote configured | User must create GitHub repo before push |
