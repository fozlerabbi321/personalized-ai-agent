# 💼 Kairo AI — Career Coach & Interview Prep

> **A Full-Stack AI Career System powered by FastAPI, LangGraph, Google Gemini, PostgreSQL, and Next.js 14 with Server-Driven UI (SDUI) Streaming.**

---

## 🌿 Project Variants — Multi-Branch Portfolio

This repository contains **4 fully independent AI agent variants**, each on its own Git branch. All variants share the same battle-tested infrastructure (FastAPI, LangGraph, SSE Streaming, PostgreSQL, JWT Auth, SDUI). Only the **domain layer** (prompts, nodes, widgets, DB schema) changes per branch.

| Branch | Agent | Domain | Theme | Status |
|---|---|---|---|---|
| [`dev`](../../tree/dev) | 💪 **Atlas** | Fitness Coach & Nutrition Advisor | 🟠 Charcoal + Orange | 🟢 Complete |
| [`feat/nova-learning`](../../tree/feat/nova-learning) | 🎓 **Nova** | Personalized Learning Tutor | 🟣 Indigo + Violet | 🟢 Complete |
| [`feat/lumen-books`](../../tree/feat/lumen-books) | 📚 **Lumen** | Book Recommender & Literary Guide | 🟡 Amber + Gold | 🟢 Complete |
| [`feat/kairo-career`](../../tree/feat/kairo-career) | 💼 **Kairo** | Career Coach & Interview Prep | 🔵 Navy + Gold | 🟢 **Active Development** |

> **Currently viewing:** `feat/kairo-career` branch — **Kairo AI (Career Coach)**. Switch branches above to explore other agent variants.

---

## 🌟 Overview

**Kairo AI** is an enterprise-grade, full-stack AI career strategist, interview coach, and resume optimizer. It features a **stateful agentic core** built on **LangGraph** and **FastAPI**, communicating with a modern **Next.js 14 (App Router)** client via **Server-Sent Events (SSE)**.

Kairo pioneers a **Server-Driven UI (SDUI)** approach: the AI backend determines the job seeker's query intent (mock interviews, resume ATS evaluation, career growth roadmaps), executes recruiting domain logic, and dynamically streams both text tokens and rich interactive UI components — **Interactive Interview Practice Cards**, **Resume ATS Evaluators with Metric Rewrites**, and **Career Growth Roadmaps** — directly into the chat interface without hardcoded frontend logic.

Kairo remembers your target role, experience level, tech stack, and career goals across sessions via **LangGraph's PostgresSaver** persistent memory.

---

## 🔥 Key Technical Highlights

- 🧠 **LangGraph Stateful Agent**: 5-node DAG — `llm_decision` → `interview` / `resume` / `roadmap` / `summary` / `general`. Each node is a domain-specialized Gemini invocation.
- 🎨 **Server-Driven UI (SDUI)**: Backend streams structured `widget_json` payloads via SSE. The Next.js client renders dynamic React widgets (`InterviewWidget`, `ResumeWidget`, `CareerRoadmapWidget`) based on backend intent.
- 💾 **Persistent Memory**: LangGraph `PostgresSaver` checkpointer preserves candidate profile, target role, and practice history across sessions via thread IDs.
- ⚡ **Real-Time SSE Streaming**: Async token streaming via FastAPI `StreamingResponse` + custom `TextDecoder` SSE reader on frontend.
- 🎯 **FAANG/Tier-1 Hiring Standards**: Mock interviews with STAR framework guidance, ATS checklist scoring, and metric-driven bullet point rewrites.
- 🔐 **JWT Auth & Security**: `bcrypt` password hashing + `Bearer` token middleware protection across all API routes.
- 🐳 **Dockerized Infrastructure**: Single-command orchestrator managing PostgreSQL 16, FastAPI backend, auto DDL table creation, and seeders.
- 📁 **Clean Architecture**: Feature-first, SOLID-compliant codebase on both backend (`app/`) and frontend (`src/features/`).

---

## 🏗️ System Architecture & Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       KAIRO AI — CAREER COACH                                │
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
│  │  │ (SDUI Engine)    ││  │  │  │  JWT   │ │     │  │ interview /   │   │   │
│  │  │  ├─ Interview    ││  │  │  └────────┘ │     │  │ resume /      │   │   │
│  │  │  ├─ ResumeWidget ││  │  └─────────────┘     │  │ roadmap /     │   │   │
│  │  │  └─ CareerRoadmap││  │         │            │  │ summary /     │   │   │
│  │  └──────────────────┘│  │  ┌──────▼──────┐     │  │ general node  │   │   │
│  └──────────────────────┘  │  │  PostgreSQL  │     │  └───────────────┘   │   │
│                            │  │  (Docker)    │     └──────────────────────┘   │
│   EventSource / Stream     │  │ LangGraph    │                                │
│   + ReadableStream Reader  │  │ Checkpointer │                                │
└────────────────────────────┴──┴──────────────┴────────────────────────────────┘
```

---

## 🤖 Kairo AI — Agent Features

### 💼 Mock Interview Practice
Practice technical, behavioral, and system design interview questions tailored to your target role.
- **Output:** `InterviewWidget` — question card with evaluation criteria, STAR framework guide (Situation, Task, Action, Result), and impact keywords.

### 📄 Resume ATS Review & Metric Rewrites
Get ATS readiness scores and metric-driven bullet point rewrites for maximum recruiter impact.
- **Output:** `ResumeWidget` — ATS score (0-100), grade badge, before/after impact rewrites, and readiness checklist.

### 🗺️ Career Growth Roadmaps
Plan your transition (e.g. Mid-Level to Senior Engineer or Tech Lead) with step-by-step milestones.
- **Output:** `CareerRoadmapWidget` — multi-phase growth plan with timelines, key skills to acquire, salary targets, and promotion metrics.

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

---

### 3. Run Full Application
```bash
make dev
```

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
Populates PostgreSQL with test users, career profiles, and 3 chat sessions pre-loaded with Kairo SDUI widget messages.

**Pre-seeded Test Credentials:**

| Email | Password | Profile |
|---|---|---|
| `alice@example.com` | `Password123!` | Senior Software Engineer candidate |
| `bob@example.com` | `Password123!` | Frontend Tech Lead candidate |

---

## 📋 Makefile Commands Reference

| Command | Action |
|---|---|
| `make dev` | Start complete stack (Docker Backend + Next.js Frontend) |
| `make backend` | Start Docker backend only (FastAPI + PostgreSQL) |
| `make frontend` | Start Next.js development server only |
| `make setup` | Initialize environment files (`.env`) |
| `make seed` | Populate PostgreSQL with career test data |
| `make stop` | Stop all running Docker containers |
| `make logs` | Tail real-time logs from Docker containers |
| `make clean` | Remove Docker containers and volumes (Full Reset) |

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

<div align="center">

**Developed with ❤️ by [Fozle Rabbi](https://fozlerabbi321.github.io)**

</div>
