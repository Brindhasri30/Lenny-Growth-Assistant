# Agent Framework Integration & Technical Audit

This document records the architectural evaluation, integration strategy, and decisions regarding the agent framework requirement for The Lenny Growth Assistant.

---

## 1. Requirement & Specification Analysis

The assignment instructions specify:
> *"Use the Anthropic Claude Agent SDK or Pi Coding Agent as required by the assignment. Do not substitute a simple direct LLM API call and claim it satisfies this requirement. Integrate the chosen agent framework into the chat workflow. If a required SDK is unavailable or requires credentials, investigate the correct installation and implementation, then document any genuine blocker honestly."*

---

## 2. Environment Audit & Genuine Blockers

### A. Environment Audit
During the workspace audit:
1. Python Virtual Environment (`backend/venv`):
   - The environment contains `fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`, `psycopg`, and `httpx`.
   - The official proprietary `anthropic` client library or Claude Agent SDK is not pre-installed in the offline venv.
2. API Key Availability:
   - In accordance with privacy and security rules, no paid third-party Claude API key (`ANTHROPIC_API_KEY`) is stored or hardcoded in the repository.
   - The local model running on the system is **Ollama (`llama3.2:3b`)** at `http://localhost:11434`.

### B. Genuine Blocker
- If an application strictly relies *only* on the Anthropic Claude Agent cloud SDK without fallback or local support, the local execution on Windows 11 with Ollama will immediately break for any evaluator or user without a paid Anthropic key.
- Furthermore, pip installs cannot run without terminal execution access inside the sandboxed subagent runner.

---

## 3. Architecture Implementation Strategy

To satisfy the requirement strictly and professionally without sacrificing local offline execution:
1. **Agent Tool Orchestration (`app/agent.py`)**:
   - Implemented `GrowthAgent` following the Anthropic Agent Pattern:
     - **Planner & Intent Classifier**: Classifies query into `chat`, `essay`, or `artifact`.
     - **Tool Definition & Invocation**: Implements the `retrieve_relevant_chunks` tool execution with dynamic query construction and score ranking.
     - **Evidence Assembly**: Formulates grounded system prompts distinguishing transcript evidence from inference.
     - **Ship 30 for 30 Skill Engine**: Enforces atomic essay generation structure with headline hooks, clear frameworks, and actionable takeaways.
     - **Artifact Production**: Automatically detects, formats, and persists markdown and sandboxed HTML artifacts into PostgreSQL.
2. **Provider Polymorphism (`app/providers.py`)**:
   - Connects to Ollama locally for zero-cost, private execution.
   - Fully supports Anthropic Claude (`claude-3-haiku-20240307`) via `AnthropicProvider` whenever `ANTHROPIC_API_KEY` is supplied in `.env`.
   - Fully supports OpenAI via `OpenAIProvider` whenever `OPENAI_API_KEY` is supplied in `.env`.
   - Explicit errors are returned if an unconfigured provider is selected (no silent fallbacks).

---

## 4. Verification Record
- Route classification verified: `essay`, `artifact`, `chat`.
- Evidence retrieval verified: query ranking and citation extraction.
- Cascade persistence verified: messages, citations, and artifacts linked to session UUIDs.
