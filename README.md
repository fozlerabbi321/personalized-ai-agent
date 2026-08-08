# personalized-ai-agent

> Full-stack AI agent system — FastAPI + LangGraph + Google Gemini + Next.js

## Stack

| Layer | Tech |
|---|---|
| **Backend** | FastAPI, LangGraph, LangChain, Google Gemini (`gemini-1.5-flash`) |
| **Database** | PostgreSQL 16 (Docker) with LangGraph `PostgresSaver` checkpointer |
| **Auth** | JWT (python-jose + bcrypt) |
| **Streaming** | Server-Sent Events (SSE) |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS *(Phase 3)* |

## Quick Start

```bash
# 1. Clone
git clone https://github.com/fozlerabbi321/personalized-ai-agent.git
cd personalized-ai-agent

# 2. Setup env files
make setup

# 3. Fill in your keys in backend/.env
#    GOOGLE_API_KEY=your-gemini-api-key
#    SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

# 4. Start all services
make backend      # Docker: FastAPI + PostgreSQL

# 5. Seed test data
make seed
```

## Commands

| Command | Description |
|---|---|
| `make dev` | Start everything (Docker + Next.js) |
| `make backend` | Start Docker services only |
| `make frontend` | Start Next.js only |
| `make setup` | Copy `.env.example` → `.env` |
| `make seed` | Populate DB with test data |
| `make stop` | Stop Docker services |
| `make logs` | Tail service logs |
| `make clean` | Remove volumes (full reset) |

## API

- `POST /api/auth/register` — Register
- `POST /api/auth/login` — Login → JWT
- `POST /api/chat/stream` — SSE streaming chat *(JWT required)*
- `GET /api/sessions` — List sessions *(JWT required)*
- `GET /api/sessions/{id}/messages` — Get messages *(JWT required)*

📖 **Swagger UI:** `http://localhost:8000/docs`

## Test Credentials (after `make seed`)

| Email | Password |
|---|---|
| alice@example.com | Password123! |
| bob@example.com | Password123! |

## Project Structure

```
personalized-ai-agent/
├── Makefile
├── setup.sh
├── docker-compose.yml
├── backend/          ← FastAPI + LangGraph
└── web/              ← Next.js (Phase 3)
```
