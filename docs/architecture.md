# System Architecture & Technical Specifications

## 1. System Overview
The Lenny Growth Assistant is built as a modular, three-tier architecture combining a FastAPI backend, PostgreSQL relational database with Full-Text Search (FTS), and a React + Vite frontend.

```
┌────────────────────────────────────────────────────────┐
│                   React + Vite UI                      │
│     (Chat Panel · Side-by-Side Artifact Viewer)        │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend                       │
│  ┌───────────────────────┬──────────────────────────┐  │
│  │   Routers & Lifespan  │     GrowthAgent Engine   │  │
│  │ (/health, /sessions)  │ (Intent · Tools · Ship30)│  │
│  └───────────┬───────────┴─────────────┬────────────┘  │
│              │                         │               │
│  ┌───────────▼───────────┐ ┌───────────▼────────────┐  │
│  │   Retrieval Service   │ │   Provider Abstraction │  │
│  │ (Chunking · PostgreSQL│ │ (Ollama · Anthropic ·  │  │
│  │  tsvector FTS Engine) │ │         OpenAI)        │  │
│  └───────────┬───────────┘ └───────────┬────────────┘  │
└──────────────┼─────────────────────────┼───────────────┘
               │                         │
┌──────────────▼───────────┐ ┌───────────▼────────────┐
│   PostgreSQL Database    │ │   Local / Cloud LLM    │
│  6 Tables · FTS Indexes  │ │ (Ollama / Claude / OAI)│
└──────────────────────────┘ └────────────────────────┘
```

---

## 2. Core Subsystems

### 2.1. Provider Abstraction Layer (`app/providers.py`)
- Standardized `generate(messages, system) -> str` interface.
- Implementations:
  - `OllamaProvider`: Communicates with `http://localhost:11434/api/chat` using `httpx`.
  - `AnthropicProvider`: Cloud provider using Anthropic Messages API.
  - `OpenAIProvider`: Cloud provider using OpenAI Chat Completions API.
- Error handling: Raises `ProviderError` with clear diagnostic hints (e.g., missing API key, timeout, connection refused).

### 2.2. Ingestion & Retrieval Pipeline (`app/retrieval.py`)
1. **Extraction**: Cleans raw text from `.txt`, `.md`, `.json`, and `.html`.
2. **Chunking**: Splits into 800-character segments with 100-character overlap, respecting sentence boundaries.
3. **Hashing**: SHA-256 fingerprinting to prevent uncontrolled duplicate ingestion.
4. **FTS Indexing**: PostgreSQL `tsvector` column and GIN index (`idx_transcript_chunks_fts`).
5. **Retrieval**: `plainto_tsquery('english', query)` with `ts_rank` scoring.

### 2.3. Agent Orchestration (`app/agent.py`)
- Complies with Anthropic Agent Tool Pattern.
- Classifies query intent (`chat`, `essay`, `artifact`).
- Executes retrieval tool, formulates evidence context, and enforces grounding rules.
- Automatically captures and formats generated HTML/Markdown into PostgreSQL `artifacts`.

### 2.4. Relational Persistence (`app/database.py`)
- Tables:
  1. `chat_sessions`
  2. `messages` (ordered chronologically, foreign key cascade)
  3. `transcript_sources`
  4. `transcript_chunks`
  5. `artifacts`
  6. `app_config`
- Dialect portability: Uses `sqlalchemy.Uuid` ensuring seamless migration between PostgreSQL and SQLite test environments.

---

## 3. Security & Sandboxing
- **Sandboxed Artifacts**: HTML artifacts rendered within `iframe` with `sandbox="allow-scripts"` to isolate DOM and scripts.
- **Credential Hygiene**: Pydantic settings read from `.env`. Sensitive API keys redacted from logs via `RedactingFilter`.
- **Session Isolation**: Messages queried strictly by `session_id`.
