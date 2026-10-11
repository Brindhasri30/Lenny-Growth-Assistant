# The Lenny Growth Assistant

An AI-powered growth and product engineering assistant grounded strictly in conversations from *Lenny's Podcast*. Ask tactical questions, produce ~1,250-word Ship 30 for 30 essays, and inspect rich artifacts with verified transcript citations.

---

## 🌟 Key Features
- **Deterministic Transcript Grounding:** Answers are backed by full-text search across interview transcripts with chunk-level citations.
- **Ship 30 for 30 Essay Skill:** Dedicated writing mode producing structured atomic essays (~1,250 words) with high-hook headlines and actionable takeaways.
- **Side-by-Side Artifact Viewer:** View, copy, and download generated Markdown and sandboxed HTML artifacts right beside the conversation.
- **Multi-Model Provider Abstraction:** Runs completely offline and free using local **Ollama (`llama3.2:3b`)**, with seamless switching to Anthropic Claude or OpenAI when keys are configured.
- **PostgreSQL Persistence:** Complete session and message persistence with strict conversation isolation.

---

## 🚀 Quickstart & Local Setup

### 1. Prerequisites
- **Python 3.10+** (existing virtual environment located in `backend/venv`)
- **Node.js 18+** & npm
- **PostgreSQL 14+** running locally on port 5432
- **Ollama** running locally with `llama3.2:3b` model installed

### 2. Configure Environment Variables
Copy `.env.example` to `.env`:
```cmd
copy .env.example .env
```
Ensure your PostgreSQL database password is set in `.env`:
```env
DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost:5432/lenny_assistant
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
ACTIVE_PROVIDER=ollama
```

### 3. Initialize Database & Tables
Create the database and initialize all tables and search indices:
```cmd
psql -U postgres -c "CREATE DATABASE lenny_assistant;"
cd D:\lenny-growth-assistant\backend
venv\Scripts\python.exe -m app.init_db
```

### 4. Ingest Seed Transcripts
Ingest the provided seed episodes into the PostgreSQL knowledge base:
```cmd
cd D:\lenny-growth-assistant\backend
venv\Scripts\python.exe -m app.ingest "..\transcripts\elena_verna_growth.txt" --title "Elena Verna on PLG Loops" --url "https://lennyspodcast.com/elena-verna"
venv\Scripts\python.exe -m app.ingest "..\transcripts\brian_chesky_airbnb.txt" --title "Brian Chesky on Founder Mode" --url "https://lennyspodcast.com/brian-chesky"
venv\Scripts\python.exe -m app.ingest "..\transcripts\shreyas_doshi_product.txt" --title "Shreyas Doshi on Product Sense" --url "https://lennyspodcast.com/shreyas-doshi"
```

### 5. Start Backend
```cmd
cd D:\lenny-growth-assistant\backend
venv\Scripts\uvicorn.exe main:app --reload --port 8000
```
- API Docs: `http://localhost:8000/docs`
- Health probe: `http://localhost:8000/health`
- Readiness probe: `http://localhost:8000/ready`

### 6. Start Frontend
```cmd
cd D:\lenny-growth-assistant\frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## 🧪 Running Automated Tests

Run backend unit and integration tests:
```cmd
cd D:\lenny-growth-assistant\backend
venv\Scripts\python.exe -m unittest discover -s tests -v
```

All tests run using an isolated in-memory test database, covering:
- Configuration and CORS parsing
- Database schema relationships and cascade deletion
- API routes (`/health`, `/ready`, `/api/config`, `/api/sessions`, `/api/knowledge`)
- Grounded AI chat flow with citations
- Ship 30 for 30 essay generation and artifact creation
- Session isolation

---

## 📁 Project Architecture

```
lenny-growth-assistant/
├── backend/
│   ├── app/
│   │   ├── agent.py          # Agent orchestration & Ship 30 essay engine
│   │   ├── config.py         # Pydantic settings & .env loading
│   │   ├── database.py       # SQLAlchemy 2.0 models & PostgreSQL FTS
│   │   ├── ingest.py         # Transcript ingestion CLI
│   │   ├── init_db.py        # Database migration & verification script
│   │   ├── logging_config.py # Structured logging with API key redaction
│   │   ├── providers.py      # Ollama, Anthropic, and OpenAI adapters
│   │   ├── retrieval.py      # Chunking, extraction, and FTS retrieval
│   │   ├── routers/          # Modular API route controllers
│   │   └── schemas.py        # Pydantic request/response validation
│   ├── tests/                # Automated backend test suite
│   ├── requirements.txt      # Pinned Python dependencies
│   └── main.py               # FastAPI entry point & CORS
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ArtifactViewer.jsx # Sandboxed iframe & markdown viewer
│   │   │   └── MessageBubble.jsx  # Chat bubble with expandable citations
│   │   ├── api.js            # Frontend REST API client
│   │   ├── App.jsx           # Main chat & session management layout
│   │   └── index.css         # Modern SaaS CSS design system
│   ├── package.json          # Vite & React dependencies
│   └── vite.config.js        # Vite dev proxy configuration
├── transcripts/              # Seed podcast transcripts & provenance guide
├── docs/
│   ├── PRD.md                # Product requirements document
│   ├── design.md             # UX design specification & a11y standards
│   └── architecture.md       # Technical architecture specification
└── agent-transcripts/        # Decisions log, audit trails, and demo script
```

---

## 🚀 Deployment Notes

### Live Deployment Options:
- **Backend:** Deployable to Render, Railway, or AWS Lightsail using `uvicorn main:app --host 0.0.0.0 --port $PORT` connected to a managed PostgreSQL database.
- **Frontend:** Deployable to Vercel or Netlify (`npm run build`) with `VITE_API_URL` pointing to your deployed backend domain.
- **Local Demonstration (Recommended):** Evaluated and run natively on Windows 11 with PostgreSQL and local Ollama (`llama3.2:3b`).

---

## 📝 Assignment Submission
- **Submission Form:** [https://forms.gle/LgotDHNVxW1mbzNE7](https://forms.gle/LgotDHNVxW1mbzNE7)
- **Demo Script:** Available in [`agent-transcripts/demo-script.md`](file:///d:/lenny-growth-assistant/agent-transcripts/demo-script.md)
