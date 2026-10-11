# Lenny Growth Assistant

An AI assistant grounded in Lenny's Podcast transcripts. Ask questions, generate essays, and build growth artifacts — all backed by real evidence, not hallucination.

> **Status:** Under active construction (Milestone 1 of 12 complete)

---

## Submission

Assignment submission form: **https://forms.gle/LgotDHNVxW1mbzNE7**

---

## Quick Start (Windows — coming in Milestone 11)

Full setup instructions will be added in Milestone 11. For now, see the sections below for manual setup.

### Prerequisites

| Tool | Required Version | How to Check |
|---|---|---|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 8+ | `npm --version` |
| PostgreSQL | 14+ | `psql --version` |
| Git | Any | `git --version` |
| Ollama | Latest | `ollama --version` |

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/lenny-growth-assistant.git
cd lenny-growth-assistant
```

### 2. Configure environment

```bash
copy .env.example .env
# Edit .env with your PostgreSQL password and optional API keys
```

### 3. Set up PostgreSQL

Open **pgAdmin** or **psql** and run:

```sql
CREATE DATABASE lenny_assistant;
```

Then update `DATABASE_URL` in your `.env` file with your PostgreSQL username and password.

### 4. Set up the Python backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 5. Initialize the database

```bash
python -c "from app.database import init_db; init_db()"
```

### 6. Start Ollama

In a separate terminal:
```bash
ollama serve
```

Make sure the `llama3.2:3b` model is pulled:
```bash
ollama pull llama3.2:3b
```

### 7. Start the backend

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

### 8. Start the frontend (coming in Milestone 9)

```bash
cd frontend
npm install
npm run dev
```

### 9. Ingest transcripts (coming in Milestone 5)

```bash
python -m app.ingest "path\to\transcript.txt" --title "Episode Title"
```

---

## Project Structure

```
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── skills/          # Essay writing skill files
│   │   ├── config.py        # Settings from environment
│   │   ├── database.py      # SQLAlchemy models
│   │   ├── providers.py     # Ollama/Anthropic/OpenAI adapters
│   │   └── schemas.py       # Pydantic request/response models
│   ├── tests/               # pytest test suite
│   ├── main.py              # FastAPI application entry point
│   └── requirements.txt     # Python dependencies
├── frontend/                # React + Vite application
├── docs/
│   ├── implementation-plan.md
│   ├── requirements-checklist.md
│   ├── PRD.md               # Product Requirements Document
│   ├── design.md            # Design system and UX principles
│   └── architecture.md      # System architecture
├── agent-transcripts/       # Implementation logs and demo scripts
├── transcripts/             # Your transcript files (not committed)
├── .env.example             # Environment variable template
├── .gitignore
└── README.md
```

---

## Architecture Overview

- **Frontend:** React + Vite (port 5173)
- **Backend:** Python FastAPI (port 8000)
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Local LLM:** Ollama with llama3.2:3b
- **Cloud LLM:** Anthropic Claude or OpenAI GPT (optional, requires API key)
- **Retrieval:** PostgreSQL full-text search (tsvector/GIN index)

See [docs/architecture.md](docs/architecture.md) for the full architecture document.

---

## Troubleshooting

**Backend won't start:** Check that your `.env` file exists and `DATABASE_URL` is correct.

**Ollama connection refused:** Run `ollama serve` in a separate terminal window.

**Database connection error:** Verify PostgreSQL is running and the database `lenny_assistant` exists.

**Empty knowledge base:** You need to ingest transcript files. See the ingestion instructions above.

---

## Implementation Progress

See [docs/implementation-plan.md](docs/implementation-plan.md) for all 12 milestones.  
See [docs/requirements-checklist.md](docs/requirements-checklist.md) for per-requirement status.
