# Lenny Growth Assistant — Requirements Checklist

**Source:** Assignment specification  
**Status key:** ⬜ Not started · 🔄 In progress · ✅ Done · ❌ Blocked

---

## 1. Architecture and Stack

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 1.1 | Frontend: React + Vite + JavaScript | ⬜ | M9 |
| 1.2 | Responsive CSS (no Tailwind unless requested) | ⬜ | M9 |
| 1.3 | Backend: Python FastAPI | 🔄 | M2 |
| 1.4 | Database: PostgreSQL with SQLAlchemy | 🔄 | M2 |
| 1.5 | Migrations or documented schema init method | ⬜ | M2 |
| 1.6 | Agent integration: Anthropic Claude Agent SDK or Pi Coding Agent (real API, not mock) | ⬜ | M4 |
| 1.7 | Local LLM: Ollama with llama3.2:3b | ⬜ | M4 |
| 1.8 | Cloud LLM: at least one provider (Anthropic or OpenAI) | ⬜ | M4 |
| 1.9 | Retrieval: searchable transcript knowledge base with chunking and citations | ⬜ | M5 |
| 1.10 | Pytest backend tests | ⬜ | M11 |
| 1.11 | Frontend automated tests | ⬜ | M11 |
| 1.12 | .env.example, no committed credentials | ⬜ | M2 |
| 1.13 | Structured logs | ⬜ | M2 |
| 1.14 | Modular, understandable components | 🔄 | All |

---

## 2. Core User Experience

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 2.1 | Application name and clear navigation | ⬜ | M9 |
| 2.2 | New Chat button | ⬜ | M9 |
| 2.3 | Conversation history sidebar | ⬜ | M9 |
| 2.4 | Main conversational chat area | ⬜ | M9 |
| 2.5 | User and assistant message bubbles | ⬜ | M9 |
| 2.6 | Message timestamps | ⬜ | M9 |
| 2.7 | Loading state | ⬜ | M9 |
| 2.8 | Error states | ⬜ | M9 |
| 2.9 | Retry behavior for recoverable errors | ⬜ | M9 |
| 2.10 | Model/provider selector in UI | ⬜ | M9 |
| 2.11 | Clear source citations on grounded answers | ⬜ | M6 |
| 2.12 | Follow-up questions using session context | ⬜ | M6 |
| 2.13 | Artifact Viewer beside chat on desktop | ⬜ | M10 |
| 2.14 | Chat/artifact tab toggle on mobile | ⬜ | M10 |
| 2.15 | Copy and download actions for artifacts | ⬜ | M10 |
| 2.16 | Accessible design: contrast, keyboard nav, focus indicators | ⬜ | M9 |
| 2.17 | Sensible empty states | ⬜ | M9 |
| 2.18 | Light, clean, modern SaaS visual style | ⬜ | M9 |

---

## 3. PostgreSQL Persistence

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 3.1 | Table: chat_sessions | ✅ | M2 |
| 3.2 | Table: messages | ✅ | M2 |
| 3.3 | Table: transcript_sources | ✅ | M2 |
| 3.4 | Table: transcript_chunks | ✅ | M2 |
| 3.5 | Table: artifacts | ✅ | M2 |
| 3.6 | Table: app_config (optional) | ✅ | M2 |
| 3.7 | Every new chat has a unique session ID | 🔄 | M3 |
| 3.8 | Messages belong to correct session | 🔄 | M3 |
| 3.9 | Messages and timestamps saved persistently | 🔄 | M3 |
| 3.10 | Page reload does not erase conversations | ⬜ | M3 |
| 3.11 | Opening old session restores its messages | ⬜ | M3 |
| 3.12 | Session context isolation (no cross-contamination) | 🔄 | M3 |
| 3.13 | API input validated; structured useful errors | ✅ | M3 |
| 3.14 | /health endpoint | ✅ | M2 |
| 3.15 | /ready endpoint (DB readiness check) | ✅ | M2 |
| 3.16 | DB connection failures handled gracefully | ✅ | M2 |
| 3.17 | Connection details from env vars, never hardcoded | ✅ | M2 |
| 3.18 | Missing credentials report exact configuration steps | ✅ | M2 |


---

## 4. Flexible Model Configuration

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 4.1 | Provider abstraction (switch without code changes) | 🔄 | M4 |
| 4.2 | Ollama local provider | ⬜ | M4 |
| 4.3 | At least one cloud provider | ⬜ | M4 |
| 4.4 | llama3.2:3b as default local model | 🔄 | M4 |
| 4.5 | Cloud API keys from env vars | 🔄 | M4 |
| 4.6 | Active provider shown in UI | ⬜ | M9 |
| 4.7 | Provider/model changeable via config endpoint + UI | ⬜ | M4/M9 |
| 4.8 | Request timeouts configured | 🔄 | M4 |
| 4.9 | Ollama unavailable: clear error, not silent fallback | ⬜ | M4 |
| 4.10 | Missing cloud key: explicit error, not fallback | ⬜ | M4 |
| 4.11 | Rate limit handling | ⬜ | M4 |
| 4.12 | No silent fallback between providers | ⬜ | M4 |
| 4.13 | Local Ollama mode usable without paid API key | ⬜ | M4 |

---

## 5. Transcript Ingestion and Grounded Retrieval

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 5.1 | Ingestion pipeline for Lenny's transcripts | ⬜ | M5 |
| 5.2 | Supports TXT, MD, JSON, HTML input formats | ⬜ | M5 |
| 5.3 | Source title and metadata captured | ⬜ | M5 |
| 5.4 | Source URL captured | ⬜ | M5 |
| 5.5 | Text extraction and cleanup | ⬜ | M5 |
| 5.6 | Chunking with overlap | ⬜ | M5 |
| 5.7 | Persistent indexing in PostgreSQL | ⬜ | M5 |
| 5.8 | Refresh/re-ingestion without uncontrolled duplicates | ⬜ | M5 |
| 5.9 | PostgreSQL full-text search as baseline | ⬜ | M5 |
| 5.10 | Retrieval interface (vector search can be added later) | ⬜ | M5 |
| 5.11 | Source traceability for every retrieved chunk | ⬜ | M5 |
| 5.12 | Every KB answer: retrieve first, then generate | ⬜ | M6 |
| 5.13 | Model instructed to answer only from retrieved evidence | ⬜ | M6 |
| 5.14 | Citations: source title + locator (URL or chunk ID) | ⬜ | M6 |
| 5.15 | Evidence vs. inference distinguished in responses | ⬜ | M6 |
| 5.16 | Insufficient evidence: say so, don't invent | ⬜ | M6 |
| 5.17 | Empty KB: honest state, ingestion instructions shown | ⬜ | M6 |
| 5.18 | CLI or API endpoint to ingest/refresh KB | ⬜ | M5 |
| 5.19 | No fabricated transcript content or citations | ⬜ | M5/M6 |

---

## 6. Agent Integration and Routing

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 6.1 | Anthropic Claude Agent SDK or Pi Coding Agent integration | ⬜ | M4 |
| 6.2 | Dedicated agent module | ⬜ | M6 |
| 6.3 | Component: agent orchestration | ⬜ | M6 |
| 6.4 | Component: model provider adapters | 🔄 | M4 |
| 6.5 | Component: retrieval service | ⬜ | M5 |
| 6.6 | Component: conversation/session service | ⬜ | M3 |
| 6.7 | Component: essay-writing skill | ⬜ | M7 |
| 6.8 | Component: artifact generation | ⬜ | M8 |
| 6.9 | Component: persistence | 🔄 | M2/M3 |
| 6.10 | Component: API routes | ⬜ | M3 |
| 6.11 | Routing: grounded question answering | ⬜ | M6 |
| 6.12 | Routing: follow-up questions | ⬜ | M6 |
| 6.13 | Routing: essay generation | ⬜ | M7 |
| 6.14 | Routing: artifact generation | ⬜ | M8 |
| 6.15 | Routing: insufficient evidence | ⬜ | M6 |
| 6.16 | Log routing decisions (no keys or sensitive content) | ⬜ | M6 |

---

## 7. Ship 30 for 30 Writing Skill

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 7.1 | Skill file at `backend/app/skills/ship_30_for_30.md` | ⬜ | M7 |
| 7.2 | Not a one-off prompt — reusable skill | ⬜ | M7 |
| 7.3 | Essay ~1,250 words | ⬜ | M7 |
| 7.4 | Compelling opening hook | ⬜ | M7 |
| 7.5 | Clear central idea | ⬜ | M7 |
| 7.6 | Narrative progression | ⬜ | M7 |
| 7.7 | Short, readable paragraphs | ⬜ | M7 |
| 7.8 | Useful headings and selective bold emphasis | ⬜ | M7 |
| 7.9 | Concrete examples supported by transcript evidence | ⬜ | M7 |
| 7.10 | Specific, actionable takeaways | ⬜ | M7 |
| 7.11 | Memorable ending | ⬜ | M7 |
| 7.12 | Citations to transcript sources | ⬜ | M7 |
| 7.13 | No fabricated quotations, statistics, or attributions | ⬜ | M7 |
| 7.14 | Evidence-gap explanation when topic not covered | ⬜ | M7 |
| 7.15 | Exposed via chat action or recognizable request | ⬜ | M7 |
| 7.16 | Result displayed in Artifact Viewer | ⬜ | M10 |
| 7.17 | Markdown download supported | ⬜ | M10 |

---

## 8. Artifact Generation and Secure Viewer

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 8.1 | Generate Markdown documents | ⬜ | M8 |
| 8.2 | Generate complete HTML/CSS artifacts | ⬜ | M8 |
| 8.3 | Generate product briefs, landing pages, growth plans | ⬜ | M8 |
| 8.4 | Dedicated Artifact Viewer beside chat | ⬜ | M10 |
| 8.5 | Preview tab (rendered output) | ⬜ | M10 |
| 8.6 | Source tab (raw code) | ⬜ | M10 |
| 8.7 | Copy and download actions | ⬜ | M10 |
| 8.8 | Artifacts persisted in DB | ⬜ | M8 |
| 8.9 | Clear indication of artifact generation failures | ⬜ | M8 |
| 8.10 | HTML rendered in sandboxed iframe (not injected into DOM) | ⬜ | M10 |
| 8.11 | Restrictive sandbox config (documented) | ⬜ | M10 |
| 8.12 | Markdown rendering sanitized against XSS | ⬜ | M10 |
| 8.13 | Backend secrets not exposed to generated artifacts | ⬜ | M10 |

---

## 9. API Endpoints

| # | Endpoint | Status | Milestone |
|---|---|---|---|
| 9.1 | GET /health | 🔄 | M2 |
| 9.2 | GET /ready | ⬜ | M2 |
| 9.3 | GET /api/config | ⬜ | M4 |
| 9.4 | PUT /api/config | ⬜ | M4 |
| 9.5 | POST /api/sessions | ⬜ | M3 |
| 9.6 | GET /api/sessions | ⬜ | M3 |
| 9.7 | GET /api/sessions/{id} | ⬜ | M3 |
| 9.8 | DELETE /api/sessions/{id} | ⬜ | M3 |
| 9.9 | GET /api/sessions/{id}/messages | ⬜ | M3 |
| 9.10 | POST /api/sessions/{id}/messages | ⬜ | M6 |
| 9.11 | POST /api/knowledge/ingest | ⬜ | M5 |
| 9.12 | GET /api/knowledge/status | ⬜ | M5 |
| 9.13 | POST /api/artifacts | ⬜ | M8 |
| 9.14 | GET /api/artifacts/{id} | ⬜ | M8 |

---

## 10. Operational Readiness

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 10.1 | .env.example | ⬜ | M2 |
| 10.2 | .gitignore | ✅ | M1 |
| 10.3 | README.md with Windows setup commands | ⬜ | M11 |
| 10.4 | docs/PRD.md | ⬜ | M11 |
| 10.5 | docs/design.md | ⬜ | M11 |
| 10.6 | docs/architecture.md | ⬜ | M11 |
| 10.7 | agent-transcripts/README.md | ⬜ | M11 |
| 10.8 | Backend tests (pytest) | ⬜ | M11 |
| 10.9 | Frontend tests | ⬜ | M11 |
| 10.10 | Manual UI test plan | ⬜ | M11 |
| 10.11 | Dockerfile | ⬜ | M11 |
| 10.12 | docker-compose.yml | ⬜ | M11 |
| 10.13 | Native Windows startup (one command) | ⬜ | M11 |
| 10.14 | Structured logs: API errors, provider selection, retrieval count, DB errors, agent routing, artifact events | ⬜ | M2/M6 |
| 10.15 | No API keys or conversation content in logs | ⬜ | M2 |
| 10.16 | Graceful handling: empty retrieval, missing keys, Ollama down, DB failure, timeouts | ⬜ | M4/M6 |

---

## 11. Tests

| # | Test | Status | Milestone |
|---|---|---|---|
| 11.1 | Health and readiness endpoints | ⬜ | M11 |
| 11.2 | Request validation | ⬜ | M11 |
| 11.3 | Session creation and isolation | ⬜ | M11 |
| 11.4 | Message persistence and timestamps | ⬜ | M11 |
| 11.5 | Retrieval and source attribution | ⬜ | M11 |
| 11.6 | Insufficient-evidence behavior | ⬜ | M11 |
| 11.7 | Provider selection and missing-key behavior | ⬜ | M11 |
| 11.8 | Ollama failure handling | ⬜ | M11 |
| 11.9 | Essay routing and skill invocation | ⬜ | M11 |
| 11.10 | Artifact generation | ⬜ | M11 |
| 11.11 | Artifact HTML isolation/security | ⬜ | M11 |
| 11.12 | Frontend: loading state | ⬜ | M11 |
| 11.13 | Frontend: error state | ⬜ | M11 |
| 11.14 | Frontend: session history | ⬜ | M11 |
| 11.15 | Frontend: model selection | ⬜ | M11 |
| 11.16 | Frontend: artifact display | ⬜ | M11 |

---

## 12. Documentation

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 12.1 | PRD: primary user and problem | ⬜ | M11 |
| 12.2 | PRD: user jobs and pain points | ⬜ | M11 |
| 12.3 | PRD: measurable success metrics | ⬜ | M11 |
| 12.4 | PRD: assumptions, scope, exclusions | ⬜ | M11 |
| 12.5 | PRD: user flows and acceptance criteria | ⬜ | M11 |
| 12.6 | PRD: risks and trade-offs | ⬜ | M11 |
| 12.7 | design.md: visual principles, IA, interaction states | ⬜ | M11 |
| 12.8 | design.md: responsive behavior, accessibility | ⬜ | M11 |
| 12.9 | architecture.md: components, DB schema, API contracts | ⬜ | M11 |
| 12.10 | architecture.md: ingestion/retrieval flow | ⬜ | M11 |
| 12.11 | architecture.md: agent/skill routing | ⬜ | M11 |
| 12.12 | architecture.md: model config and fallback | ⬜ | M11 |
| 12.13 | architecture.md: artifact security | ⬜ | M11 |
| 12.14 | architecture.md: deployment topology | ⬜ | M11 |
| 12.15 | README: Windows setup, prerequisites, config | ⬜ | M11 |
| 12.16 | README: DB setup, Ollama setup, transcript ingestion | ⬜ | M11 |
| 12.17 | README: startup, tests, troubleshooting, extending | ⬜ | M11 |

---

## 13. Agent Transcripts and Submission

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 13.1 | agent-transcripts/implementation-log.md (honest log) | ⬜ | M12 |
| 13.2 | agent-transcripts/demo-script.md | ⬜ | M12 |
| 13.3 | Demo: 2-3 min video, camera-on, Ollama demo, trade-off | ⬜ | M12 (user records) |
| 13.4 | Submission form URL in README | ⬜ | M12 |
| 13.5 | No fabricated history of tool calls | ✅ | All |
| 13.6 | Credentials redacted from all logs | ✅ | All |

---

## 14. Deployment

| # | Requirement | Status | Milestone |
|---|---|---|---|
| 14.1 | Public GitHub repository | ⬜ | User action required |
| 14.2 | Application deployed and accessible (Render/Railway etc.) | ⬜ | User action required |
| 14.3 | Live URL in README | ⬜ | User action required |

---

## Notes on Partial Progress

The previous conversation session created the following files which are being preserved and reviewed:

- `backend/main.py` — original FastAPI stub (22 lines, preserved)
- `backend/venv/` — Python 3.10.8 venv with packages installed (preserved, not committed)
- `backend/app/__init__.py` — package init (created earlier, reviewed)
- `backend/app/config.py` — settings via pydantic-settings (created earlier, reviewed)
- `backend/app/database.py` — SQLAlchemy models (created earlier, needs review in M2)
- `backend/app/logging_config.py` — logging (created earlier, needs review in M2)
- `backend/app/providers.py` — provider adapters (created earlier, needs review in M4)
- `backend/app/schemas.py` — Pydantic schemas (created earlier, needs review in M2)

These files will be reviewed and completed as part of their respective milestones. None of them are currently running or tested.
