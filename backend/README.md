# personalized_ai_agent — Backend

> FastAPI · LangGraph · Google Gemini · PostgreSQL · JWT Auth

---

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (only needed if running locally without Docker)
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (free tier)

---

### 1. Clone & Setup

```bash
# From the monorepo root
make setup
```

This copies `backend/.env.example` → `backend/.env`.

**Edit `backend/.env`** and fill in your values:

```bash
# Generate a strong secret key
python3 -c "import secrets; print(secrets.token_hex(32))"
```

```env
SECRET_KEY=<paste generated key here>
GOOGLE_API_KEY=<your Gemini API key>
```

---

### 2. Start All Services

```bash
make dev        # Docker (FastAPI + PostgreSQL) + Next.js frontend
# OR
make backend    # Docker only (FastAPI + PostgreSQL)
```

Services start at:
| Service    | URL                              |
|------------|----------------------------------|
| FastAPI    | http://localhost:8000            |
| API Docs   | http://localhost:8000/docs       |
| PostgreSQL | localhost:5432                   |
| Next.js    | http://localhost:3000 (Phase 3)  |

---

### 3. Seed the Database

```bash
make seed
```

Creates two test users:

| Email                | Password      |
|----------------------|---------------|
| alice@example.com    | Password123!  |
| bob@example.com      | Password123!  |

Each user gets 3 seeded sessions with realistic messages and widget data.

---

## API Reference

### Authentication

| Method | Endpoint            | Auth  | Description                 |
|--------|---------------------|-------|-----------------------------|
| POST   | /api/auth/register  | ❌    | Register → returns JWT      |
| POST   | /api/auth/login     | ❌    | Login → returns JWT         |
| GET    | /api/auth/me        | ✅ JWT | Get current user profile    |

### Chat (SSE Streaming)

| Method | Endpoint            | Auth  | Description                 |
|--------|---------------------|-------|-----------------------------|
| POST   | /api/chat/stream    | ✅ JWT | Stream AI response via SSE  |

### Sessions

| Method | Endpoint                          | Auth  | Description              |
|--------|-----------------------------------|-------|--------------------------|
| GET    | /api/sessions                     | ✅ JWT | List user's sessions     |
| GET    | /api/sessions/{id}/messages       | ✅ JWT | Get session messages     |
| DELETE | /api/sessions/{id}                | ✅ JWT | Delete session + messages|

---

## cURL Testing Guide

### Step 1 — Login (get your token)
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "Password123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

echo "✅ Token: ${TOKEN:0:40}..."
```

### Step 2 — Stream a general chat message
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Explain how LangGraph works.", "session_id": "test-session-001"}'
```

### Step 3 — Stream a financial query (triggers widget)
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me the NVDA stock chart.", "session_id": "test-session-001"}'
```

Expected output:
```
event: token
data: {"type": "token", "content": "NVDA is currently..."}

event: widget
data: {"type": "widget", "widget_json": {"widget_type": "candlestick_chart", ...}}

event: done
data: {"type": "done", "session_id": "test-session-001"}
```

### Step 4 — Request a summary
```bash
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Summarize our conversation so far.", "session_id": "test-session-001"}'
```

### Step 5 — List sessions
```bash
curl -s http://localhost:8000/api/sessions \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

### Step 6 — Get messages from a session
```bash
SESSION_ID="<id from step 5>"
curl -s "http://localhost:8000/api/sessions/$SESSION_ID/messages" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

---

## Environment Variables

| Variable                   | Required | Default           | Description                        |
|----------------------------|----------|-------------------|------------------------------------|
| `SECRET_KEY`               | ✅       | —                 | JWT signing secret (≥32 chars)     |
| `GOOGLE_API_KEY`           | ✅       | —                 | Google Gemini API key              |
| `DATABASE_URL`             | ✅       | —                 | PostgreSQL DSN                     |
| `GEMINI_MODEL`             | ❌       | gemini-1.5-flash  | Gemini model name                  |
| `ALGORITHM`                | ❌       | HS256             | JWT algorithm                      |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | ❌   | 10080 (7 days)    | Token TTL                          |
| `LANGCHAIN_TRACING_V2`     | ❌       | false             | Enable LangSmith tracing           |
| `LANGCHAIN_API_KEY`        | ❌       | —                 | LangSmith API key                  |
| `LANGCHAIN_PROJECT`        | ❌       | personalized-ai-agent | LangSmith project name         |
| `CORS_ORIGINS`             | ❌       | http://localhost:3000 | Comma-separated allowed origins|
| `DEBUG`                    | ❌       | false             | Enable debug mode                  |

---

## LangGraph Agent Flow

```
User message
     │
     ▼
llm_decision_node (Gemini)
     │  classifies intent
     ├── "api_call"  ──► api_call_node  (mock OHLC + Gemini analysis)
     ├── "summary"   ──► summary_node   (Gemini summarizes history)
     └── "general"   ──► general_node   (Gemini direct response)
                               │
                        PostgresSaver
                    (persistent memory per session_id)
```

### SSE Event Types

| Event    | Payload                                          |
|----------|--------------------------------------------------|
| `token`  | `{"type": "token", "content": "chunk..."}`       |
| `widget` | `{"type": "widget", "widget_json": {...}}`       |
| `done`   | `{"type": "done", "session_id": "..."}`          |
| `error`  | `{"type": "error", "message": "..."}`            |

---

## Makefile Commands

```bash
make dev       # Full stack dev (Docker + Next.js)
make backend   # Docker only
make frontend  # Next.js only
make setup     # Copy .env files
make seed      # Seed database
make stop      # Stop Docker services
make logs      # Tail logs
make clean     # Remove volumes (full reset)
```

---

## Folder Structure

```
backend/
├── Dockerfile
├── requirements.txt
├── .env.example
├── seeder.py
└── app/
    ├── main.py          # FastAPI app + lifespan
    ├── config.py        # Pydantic Settings
    ├── database.py      # asyncpg + LangGraph checkpointer
    ├── state.py         # Module-level graph reference
    ├── agent/
    │   ├── state.py     # AgentState TypedDict
    │   ├── graph.py     # StateGraph builder
    │   └── nodes/
    │       ├── llm_decision.py
    │       ├── api_call.py
    │       ├── summary.py
    │       └── general.py
    ├── api/
    │   ├── auth.py      # /api/auth/*
    │   ├── chat.py      # /api/chat/stream (SSE)
    │   └── sessions.py  # /api/sessions/*
    ├── core/
    │   ├── auth.py      # JWT + bcrypt
    │   └── deps.py      # FastAPI dependencies
    └── schemas/
        ├── auth.py
        ├── chat.py
        └── session.py
```
