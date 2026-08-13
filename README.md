# 💪 Atlas AI — Personalized Fitness Coach

> **A Full-Stack AI Fitness Coaching System powered by FastAPI, LangGraph, Google Gemini, PostgreSQL, and Next.js 14 with Server-Driven UI (SDUI) Streaming.**

---

## 🌿 Project Variants — Multi-Branch Portfolio

This repository contains **4 fully independent AI agent variants**, each on its own Git branch. All variants share the same battle-tested infrastructure (FastAPI, LangGraph, SSE Streaming, PostgreSQL, JWT Auth, SDUI). Only the **domain layer** (prompts, nodes, widgets, DB schema) changes per branch.

| Branch | Agent | Domain | Theme | Status |
|---|---|---|---|---|
| [`dev`](../../tree/dev) | 💪 **Atlas** | Fitness Coach & Nutrition Advisor | 🟠 Charcoal + Orange | 🟢 **Active Development** |
| [`feat/nova-learning`](../../tree/feat/nova-learning) | 🎓 **Nova** | Personalized Learning Tutor | 🟣 Indigo + Violet | 🔵 Planned |
| [`feat/lumen-books`](../../tree/feat/lumen-books) | 📚 **Lumen** | Book Recommender & Literary Guide | 🟡 Amber + Gold | 🔵 Planned |
| [`feat/kairo-career`](../../tree/feat/kairo-career) | 💼 **Kairo** | Career Coach & Interview Prep | 🔵 Navy + Gold | 🔵 Planned |
| [`feat/athena-bitcoin`](../../tree/feat/athena-bitcoin) | ₿ **Athena** | Bitcoin Trader Coach & Market Analyst | 💰 Yellow + Gold | 🔵 Planned |
> **Currently viewing:** `dev` branch — **Atlas AI (Fitness Coach)**. Switch branches above to explore other agent variants.

---

## 🌟 Overview

**Atlas AI** is an enterprise-grade, full-stack AI fitness coaching application. It features a **stateful agentic core** built on **LangGraph** and **FastAPI**, communicating with a modern **Next.js 14 (App Router)** client via **Server-Sent Events (SSE)**.

Atlas pioneers a **Server-Driven UI (SDUI)** approach: the AI backend determines the user's fitness intent (workout, nutrition, progress), executes domain logic, and dynamically streams both text tokens and rich interactive UI components — **Workout Plan tables**, **Macro Donut Charts**, and **Progress Line Charts** — directly into the chat interface without hardcoded frontend logic.

Atlas remembers your fitness goals, equipment, training history, and preferences across sessions via **LangGraph's PostgresSaver** persistent memory — getting smarter and more personalized with every conversation.

---

## 🖼️ Application Showcase & Screenshots

<div align="center">

### 1. **Atlas AI Assistant & Real-Time Chat Interface**
![Atlas AI Chat Interface](screenshorts/image_1.png)
*Interactive chat window featuring multi-turn conversation memory, stream status indicators, and prompt recommendations.*

<br/>

### 2. **Server-Driven UI (SDUI) — Interactive Charts & Analytics**
![Server-Driven UI Candlestick Widget](screenshorts/image_2.png)
*Dynamic SDUI widget rendering interactive by the LangGraph backend.*

<br/>

### 3. **Authentication & Session History Management**
![Authentication & Session Sidebar](screenshorts/image_3.png)
*JWT-authenticated user dashboard with persistent thread history, session switching, and single-click chat deletion.*

</div>

---

## 🔥 Key Technical Highlights

- 🧠 **LangGraph Stateful Agent**: 5-node DAG — `llm_decision` → `workout` / `nutrition` / `progress` / `summary` / `general`. Each node is a domain-specialized Gemini invocation.
- 🎨 **Server-Driven UI (SDUI)**: Backend streams structured `widget_json` payloads via SSE. The Next.js client dynamically renders `WorkoutPlanWidget`, `MacroDonutChart`, and `ProgressLineChart` based on intent — zero hardcoded frontend logic.
- 💾 **Persistent Memory**: LangGraph `PostgresSaver` checkpointer preserves full conversation state (goals, PRs, preferences) across server restarts using thread IDs.
- ⚡ **Real-Time SSE Streaming**: Async token streaming via FastAPI `StreamingResponse` + custom `TextDecoder` SSE reader on the frontend.
- 🏋️ **Domain Intelligence**: Intent-aware routing — automatically detects if user wants a workout plan, macro calculation, progress tracking, or general coaching advice.
- 🔐 **JWT Auth & Security**: `bcrypt` password hashing + `Bearer` token middleware on all protected API routes.
- 🐳 **Dockerized Infrastructure**: Single-command full-stack startup (FastAPI + PostgreSQL 16 + auto DDL + seeder).
- 📁 **Clean Architecture**: Feature-first, SOLID-compliant codebase on both backend (`app/`) and frontend (`src/features/`).

---

## 🏗️ System Architecture & Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           ATLAS AI — FITNESS COACH                           │
├────────────────────────────┬─────────────────────────────────────────────────┤
│     FRONTEND (Next.js)     │          BACKEND (FastAPI + LangGraph)          │
│                            │                                                 │
│  ┌──────────────────────┐  │  ┌─────────────┐     ┌──────────────────────┐   │
│  │  Chat Page (RSC)     │  │  │  FastAPI    │     │    LangGraph Agent   │   │
│  │  ├─ ChatWindow       │  │  │  ┌────────┐ │     │                      │   │
│  │  │   ├─ MessageList  │◄─┼──┼─►│  SSE   │◄├─────┤  ┌──────────────┐    │   │
│  │  │   └─ InputBar     │  │  │  │ /chat  │ │     │  │ LLM Decision │    │   │
│  │  └─ SessionSidebar   │  │  │  │/stream │ │     │  │   (Gemini)   │    │   │
│  │                      │  │  │  └────────┘ │     │  └──────┬───────┘    │   │
│  │  ┌──────────────────┐│  │  │  ┌────────┐ │     │         │ route      │   │
│  │  │ WidgetRenderer   ││  │  │  │  Auth  │ │     │  ┌──────▼────────┐   │   │
│  │  │ (SDUI Engine)    ││  │  │  │  JWT   │ │     │  │ workout /     │   │   │
│  │  │  ├─ WorkoutPlan  ││  │  │  └────────┘ │     │  │ nutrition /   │   │   │
│  │  │  ├─ MacroDonut   ││  │  └─────────────┘     │  │ progress /    │   │   │
│  │  │  └─ ProgressLine ││  │         │            │  │ summary /     │   │   │
│  │  └──────────────────┘│  │  ┌──────▼──────┐     │  │ general node  │   │   │
│  └──────────────────────┘  │  │  PostgreSQL  │     │  └───────────────┘   │   │
│                            │  │  (Docker)    │     └──────────────────────┘   │
│   EventSource / Stream     │  │ LangGraph    │                                │
│   + ReadableStream Reader  │  │ Checkpointer │                                │
└────────────────────────────┴──┴──────────────┴────────────────────────────────┘
```

---

## 🤖 Atlas AI — Agent Features

### 💪 Workout Planning
Ask Atlas for any workout and it generates a structured, personalized plan based on your muscle group, goal, fitness level, and available equipment.
- **Supported goals:** Muscle Gain, Strength, Weight Loss, Endurance, General Fitness
- **Exercise library:** 30+ exercises across all muscle groups
- **Output:** `WorkoutPlanWidget` — interactive table with sets × reps, rest times, equipment, and checkboxes

### 🥗 Nutrition & Macros
Atlas calculates your TDEE using the Mifflin-St Jeor equation and splits macros based on your goal.
- **Inputs:** Weight, height, age, gender, activity level, goal
- **Calorie strategy:** Lean bulk surplus / Cutting deficit / Maintenance
- **Output:** `MacroDonutChart` — animated SVG donut with protein/carbs/fat breakdown

### 📈 Progress Tracking
Ask Atlas about your performance on any lift and it shows your progression over time.
- **Tracks:** Bench Press, Squat, Deadlift, Overhead Press, and more
- **Output:** `ProgressLineChart` — SVG sparkline with trend indicator, gain %, and PR highlight

### 💬 General Coaching
Atlas answers any fitness question — form cues, recovery science, programming philosophy, motivation — in natural conversation with full memory of your history.

---

## 🛠️ Tech Stack

| Layer | Technologies & Tools |
|---|---|
| **Backend Framework** | FastAPI (Python 3.12+), Uvicorn, Pydantic v2 |
| **AI & Agentic Framework** | LangGraph, LangChain, Google Gemini (`gemini-1.5-flash`) |
| **Database & Persistence** | PostgreSQL 16 (Dockerized), `asyncpg`, `psycopg3`, `PostgresSaver` |
| **Authentication** | JWT (`python-jose`), `bcrypt` password hashing |
| **Streaming Protocol** | Server-Sent Events (SSE) via `text/event-stream` |
| **Frontend Framework** | Next.js 14 (App Router), TypeScript, React 18 |
| **Styling & Icons** | Tailwind CSS v4, Lucide React, Glassmorphism UI |
| **DevOps & Tooling** | Docker, Docker Compose, Makefile, Bash script (`setup.sh`) |

---

## 🚀 Quick Start & Installation

### 1. Prerequisites
- [Docker & Docker Compose](https://www.docker.com/)
- [Node.js 18+](https://nodejs.org/)
- `make` CLI utility

---

### 2. Environment Setup
```bash
make setup
```
Copies `.env.example` templates to `backend/.env` and `frontend/.env.local`.

Edit `backend/.env` and insert your **Google Gemini API Key**:
```env
GOOGLE_API_KEY=your_actual_google_gemini_api_key
SECRET_KEY=generate_a_secure_32_character_secret_key
```
> 💡 *Get a free Gemini key at [Google AI Studio](https://aistudio.google.com/app/apikey).*

---

### 3. Run Full Application
```bash
make dev
```
Starts FastAPI + PostgreSQL (Docker) + Next.js frontend in one command.

| Service | URL |
|---|---|
| 🌐 Web Client | [http://localhost:3000](http://localhost:3000) |
| ⚙️ Backend API | [http://localhost:8000](http://localhost:8000) |
| 📖 Swagger Docs | [http://localhost:8000/docs](http://localhost:8000/docs) |

---

### 4. Seed Database
```bash
make seed
```
Populates PostgreSQL with test users, fitness profiles, personal records, and 3 chat sessions pre-loaded with Atlas SDUI widget messages.

**Pre-seeded Test Credentials:**

| Email | Password | Profile |
|---|---|---|
| `alice@example.com` | `Password123!` | Intermediate · Muscle Gain · 4 days/week |
| `bob@example.com` | `Password123!` | Beginner · Weight Loss · 3 days/week |

---

## 📋 Makefile Commands Reference

| Command | Action |
|---|---|
| `make dev` | Start complete stack (Docker Backend + Next.js Frontend) |
| `make backend` | Start Docker backend only (FastAPI + PostgreSQL) |
| `make frontend` | Start Next.js development server only |
| `make setup` | Initialize environment files (`.env`) |
| `make seed` | Populate PostgreSQL with fitness test data |
| `make stop` | Stop all running Docker containers |
| `make logs` | Tail real-time logs from Docker containers |
| `make clean` | Remove Docker containers and volumes (Full Reset) |

---

## 📡 API Reference

### 🔐 Auth Endpoints
- `POST /api/auth/register` — Register a new account (returns JWT token).
- `POST /api/auth/login` — Authenticate credentials (returns JWT token).
- `GET /api/auth/me` — Retrieve authenticated user's profile.

### 💬 Chat & Streaming Endpoints
- `POST /api/chat/stream` — **SSE Streaming Endpoint** (requires `Bearer <token>`). Emits:
  - `event: token` — LLM text chunk streamed in real-time.
  - `event: widget` — Structured SDUI payload (`WorkoutPlanWidget` / `MacroDonutChart` / `ProgressLineChart`).
  - `event: done` — Stream completion signal with final `session_id`.

### 📂 Session History Endpoints
- `GET /api/sessions` — List all chat sessions for authenticated user.
- `GET /api/sessions/{session_id}/messages` — Fetch full message history for a thread.
- `DELETE /api/sessions/{session_id}` — Hard-delete a conversation thread.

---

## 📂 Folder Structure (Feature-First Architecture)

```
personalized-ai-agent/
├── Makefile
├── setup.sh
├── docker-compose.yml
│
├── backend/                        # FastAPI + LangGraph Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── seeder.py                   # Standalone DB seeder (fitness data)
│   └── app/
│       ├── main.py                 # FastAPI setup & lifespan
│       ├── config.py               # Pydantic settings & CORS
│       ├── database.py             # asyncpg + PostgresSaver + fitness tables
│       ├── agent/
│       │   ├── state.py            # AgentState TypedDict
│       │   ├── graph.py            # LangGraph 5-node StateGraph
│       │   ├── prompts.py          # Atlas AI prompt engineering
│       │   ├── constants.py        # Fitness domain constants (exercises, macros)
│       │   └── nodes/
│       │       ├── llm_decision.py # Intent classifier (workout/nutrition/progress/...)
│       │       ├── workout.py      # Workout plan generator + WorkoutPlanWidget
│       │       ├── nutrition.py    # TDEE + macro calculator + MacroDonutChart
│       │       ├── progress.py     # PR progression + ProgressLineChart
│       │       ├── summary.py      # Conversation recap node
│       │       └── general.py      # General fitness coaching node
│       ├── api/                    # API Route Handlers
│       ├── core/                   # JWT Auth & utility functions
│       └── schemas/                # Pydantic Request/Response models
│
└── frontend/                       # Next.js 14 Frontend
    ├── package.json
    ├── next.config.ts
    └── src/
        ├── app/                    # App Router Pages & Layouts
        ├── features/
        │   ├── auth/               # Login & Auth Context
        │   ├── sessions/           # Sidebar & Chat Threads
        │   ├── chat/               # SSE Chat Window & Message List
        │   └── widgets/            # SDUI Engine & Component Registry
        │       ├── WorkoutPlanWidget.tsx
        │       ├── MacroDonutChart.tsx
        │       ├── ProgressLineChart.tsx
        │       ├── ExerciseCard.tsx
        │       └── StreakHeatmap.tsx
        └── shared/                 # Reusable UI Primitives & Utilities
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Developed with ❤️ by [Fozle Rabbi](https://fozlerabbi321.github.io)**

</div>
