# Personalized AI Agent — Full Setup & Architecture Guide

This guide provides step-by-step instructions for configuring third-party services (Google Gemini API, LangSmith), setting up the environment, understanding the LangGraph agent architecture, and running the full application.

---

## Table of Contents
1. [Third-Party Services Setup](#1-third-party-services-setup)
   - [Google Gemini API (Free Tier)](#a-google-gemini-api-free-tier)
   - [LangSmith Observability (Optional)](#b-langsmith-observability-optional)
2. [LLM & LangGraph Architecture](#2-llm--langgraph-architecture)
   - [Gemini LLM Integration](#a-gemini-llm-integration)
   - [LangGraph State Schema (`AgentState`)](#b-langgraph-state-schema-agentstate)
   - [Graph Nodes & Edges Workflow](#c-graph-nodes--edges-workflow)
   - [PostgreSQL Checkpointer (`PostgresSaver`)](#d-postgresql-checkpointer-postgressaver)
3. [Environment Variables Cheat Sheet](#3-environment-variables-cheat-sheet)
   - [Backend `.env`](#backend-env)
   - [Frontend `.env.local`](#frontend-envlocal)
4. [Step-by-Step Installation & Running](#4-step-by-step-installation--running)
   - [Prerequisites](#prerequisites)
   - [Step 1: Environment Initialization](#step-1-environment-initialization)
   - [Step 2: Configure API Keys](#step-2-configure-api-keys)
   - [Step 3: Launch System (`make dev`)](#step-3-launch-system-make-dev)
   - [Step 4: Seed Database (`make seed`)](#step-4-seed-database-make-seed)
5. [Testing & Verification](#5-testing--verification)
   - [Accessing Web UI](#accessing-web-ui)
   - [cURL & API Swagger Verification](#curl--api-swagger-verification)
6. [Troubleshooting & Common Issues](#6-troubleshooting--common-issues)

---

## 1. Third-Party Services Setup

### A. Google Gemini API (Free Tier)
The system uses Google Gemini (`gemini-1.5-flash`) via `langchain-google-genai` for intent classification, stock data analysis, summarization, and general conversation.

1. **Go to Google AI Studio**:
   Open [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) in your browser.
2. **Sign In**:
   Log in with your Google account.
3. **Create API Key**:
   - Click **"Create API key"**.
   - Select an existing Google Cloud project or click **"Create API key in new project"**.
   - Copy the generated API key string (e.g. `AIzaSy...`).
4. **Paste key in `.env`**:
   Open `backend/.env` and paste your key:
   ```env
   GOOGLE_API_KEY=AIzaSyYourActualKeyHere
   GEMINI_MODEL=gemini-1.5-flash
   ```

---

### B. LangSmith Observability (Optional)
LangSmith provides full tracing and telemetry for your LangGraph nodes and Gemini LLM calls.

1. **Go to LangSmith**:
   Open [https://smith.langchain.com](https://smith.langchain.com).
2. **Create Account / Sign In**:
   Sign in with GitHub or email.
3. **Create API Key**:
   - Navigate to **Settings** → **API Keys**.
   - Click **"Create API Key"** and copy the value.
4. **Configure in `backend/.env`**:
### C. Do I Need a LangGraph API Key? (Important Clarification)
**NO, a LangGraph API key is NOT required.**

- **LangGraph Python Library (`langgraph`)**: It is a 100% free, open-source Python framework that runs directly inside your FastAPI Docker container.
- **Self-Hosted Persistence**: Our PostgreSQL database (`PostgresSaver`) handles memory and thread checkpoints locally.
- **Which key is actually required?**: You only need the **Google Gemini API Key (`GOOGLE_API_KEY`)** because LangGraph delegates intelligent reasoning and text generation to Gemini.
- **Optional Observability Key**: If you want visual execution traces on web dashboards, you can optionally provide a **LangSmith Key (`LANGCHAIN_API_KEY`)**.

## 2. LLM & LangGraph Architecture

### A. Gemini LLM Integration
In `backend/app/agent/nodes/`, LLM calls are powered by `ChatGoogleGenerativeAI`:

```python
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.7,
)
```

---

### B. LangGraph State Schema (`AgentState`)
Defined in `backend/app/agent/state.py`:

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # Managed history
    session_id: str                                       # Thread identifier
    user_id: str                                          # JWT User ID
    intent: str                                           # "api_call" | "summary" | "general"
    iteration_count: int                                  # Loop safety guard
    response_text: str                                    # Text response payload
    widget_json: dict | None                              # Server-Driven UI widget
    is_final: bool                                        # Completion flag
```

---

### C. Graph Nodes & Edges Workflow
Defined in `backend/app/agent/graph.py`:

```
                       ┌─────────────────────────┐
                       │          START          │
                       └────────────┬────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │  llm_decision_node  │  (Classifies Intent)
                         └──────────┬──────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           │                        │                        │
  intent=="api_call"       intent=="summary"        intent=="general"
           │                        │                        │
  ┌────────▼────────┐      ┌────────▼────────┐      ┌────────▼────────┐
  │  api_call_node  │      │  summary_node   │      │  general_node   │
  │ (Mock OHLC +    │      │ (Recaps full    │      │ (Direct Gemini  │
  │  Gemini review) │      │  conversation)  │      │  response)      │
  └────────┬────────┘      └────────┬────────┘      └────────┬────────┘
           │                        │                        │
           └────────────────────────┼────────────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │         END         │
                         └─────────────────────┘
```

1. **`llm_decision_node`**: Classifies incoming query into `api_call` (financial/charts), `summary` (recap requests), or `general` (all other queries).
2. **`api_call_node`**: Generates OHLC financial data + Server-Driven UI widget (`widget_json`) and streams Gemini's analysis.
3. **`summary_node`**: Condenses conversation history into key bullet points.
4. **`general_response_node`**: Handles general queries using Gemini with full conversation context.

---

### D. PostgreSQL Checkpointer (`PostgresSaver`)
LangGraph automatically persists conversation memory per `session_id` into PostgreSQL checkpointer tables using `AsyncPostgresSaver` in `backend/app/database.py`.

---

## 3. Environment Variables Cheat Sheet

### Backend `.env` (`backend/.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `SECRET_KEY` | **Yes** | `dev-secret-key...` | JWT signature key (32+ chars) |
| `GOOGLE_API_KEY` | **Yes** | `""` | Google Gemini API Key |
| `GEMINI_MODEL` | No | `gemini-1.5-flash` | Gemini Model identifier |
| `DATABASE_URL` | **Yes** | `postgresql://...` | PostgreSQL connection DSN |
| `CORS_ORIGINS` | No | `http://localhost:3000` | Allowed origins |
| `LANGCHAIN_TRACING_V2` | No | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | No | `""` | LangSmith API Key |
| `LANGCHAIN_PROJECT` | No | `personalized-ai-agent` | LangSmith project name |

### Frontend `.env.local` (`web/.env.local`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `NEXT_PUBLIC_API_URL` | **Yes** | `http://localhost:8000` | FastAPI backend base URL |

---

## 4. Step-by-Step Installation & Running

### Prerequisites
- **Docker & Docker Compose** installed
- **Node.js 18+** (for running frontend locally)
- **Make** CLI utility

### Step 1: Environment Initialization
Run the setup script to generate `.env` files for both backend and web:
```bash
make setup
```

### Step 2: Configure API Keys
Edit `backend/.env`:
```bash
# Add your Google Gemini Key
GOOGLE_API_KEY=AIzaSyYourActualKeyHere

# (Optional) Generate a secure secret key
SECRET_KEY=e8c459b71a2d46e39812fbc4501a921d7b3200ab43c19d123456789abcdef012
```

### Step 3: Launch System (`make dev`)
Start both Docker backend services (FastAPI + PostgreSQL) and the Next.js frontend:
```bash
make dev
```

*Or launch backend & frontend separately:*
```bash
# Terminal 1: Start Backend (Docker)
make backend

# Terminal 2: Start Frontend (Next.js)
make frontend
```

### Step 4: Seed Database (`make seed`)
Populate PostgreSQL with dummy users, chat threads, and financial widget data:
```bash
make seed
```

**Seeded Credentials**:
- User 1: `alice@example.com` / `Password123!`
- User 2: `bob@example.com` / `Password123!`

---

## 5. Testing & Verification

### Accessing Web UI
Open your browser at: **[http://localhost:3000](http://localhost:3000)**
- Sign in with `alice@example.com` / `Password123!`.
- Send a message: `"Show me AAPL stock price"`.
- Observe the real-time SSE stream and interactive **Candlestick Chart Widget**.

### cURL & API Swagger Verification
Interactive OpenAPI Swagger Docs: **[http://localhost:8000/docs](http://localhost:8000/docs)**

**Authenticate & Stream via cURL**:
```bash
# 1. Obtain JWT Token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "Password123!"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Stream SSE Chat
curl -N -X POST http://localhost:8000/api/chat/stream \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the AAPL stock price?", "session_id": "test-session-1"}'
```

---

## 6. Troubleshooting & Common Issues

| Symptom | Cause | Solution |
|---|---|---|
| `Google API key not found` | `GOOGLE_API_KEY` missing in `backend/.env` | Add key to `backend/.env` and restart (`make stop && make backend`) |
| `Cannot connect to PostgreSQL` | Postgres container not ready | Run `make logs` to verify health or restart (`make stop && make backend`) |
| `Port 8000 or 5432 in use` | Conflicting service on host | Stop existing postgres/fastapi services on port 5432 or 8000 |
| `Token expired / 401 Unauthorized` | Invalid or expired JWT | Login again via `/api/auth/login` to obtain a fresh token |
