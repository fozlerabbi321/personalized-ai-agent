# 📚 Lumen AI — Book Recommender & Literary Guide

> **A Full-Stack AI Literary System powered by FastAPI, LangGraph, Google Gemini, PostgreSQL, and Next.js 14 with Server-Driven UI (SDUI) Streaming.**

---

## 🌿 Project Variants — Multi-Branch Portfolio

This repository contains **4 fully independent AI agent variants**, each on its own Git branch. All variants share the same battle-tested infrastructure (FastAPI, LangGraph, SSE Streaming, PostgreSQL, JWT Auth, SDUI). Only the **domain layer** (prompts, nodes, widgets, DB schema) changes per branch.

| Branch | Agent | Domain | Theme | Status |
|---|---|---|---|---|
| [`dev`](../../tree/dev) | 💪 **Atlas** | Fitness Coach & Nutrition Advisor | 🟠 Charcoal + Orange | 🟢 Complete |
| [`feat/nova-learning`](../../tree/feat/nova-learning) | 🎓 **Nova** | Personalized Learning Tutor | 🟣 Indigo + Violet | 🟢 Complete |
| [`feat/lumen-books`](../../tree/feat/lumen-books) | 📚 **Lumen** | Book Recommender & Literary Guide | 🟡 Amber + Gold | 🟢 **Active Development** |
| [`feat/kairo-career`](../../tree/feat/kairo-career) | 💼 **Kairo** | Career Coach & Interview Prep | 🔵 Navy + Gold | 🔵 Planned |

> **Currently viewing:** `feat/lumen-books` branch — **Lumen AI (Book Recommender)**. Switch branches above to explore other agent variants.

---

## 🌟 Overview

**Lumen AI** is an enterprise-grade, full-stack AI literary assistant and reading coach. It features a **stateful agentic core** built on **LangGraph** and **FastAPI**, communicating with a modern **Next.js 14 (App Router)** client via **Server-Sent Events (SSE)**.

Lumen pioneers a **Server-Driven UI (SDUI)** approach: the AI backend determines the reader's query intent (book recommendations, book reviews/theme analysis, reading challenges), executes literary domain logic, and dynamically streams both text tokens and rich interactive UI components — **Curated Book Cards**, **Book Review Summaries**, and **Annual Reading Trackers** — directly into the chat interface without hardcoded frontend logic.

Lumen remembers your favorite genres, books you've read, rating history, and annual reading goals across sessions via **LangGraph's PostgresSaver** persistent memory.

---

## 🔥 Key Technical Highlights

- 🧠 **LangGraph Stateful Agent**: 5-node DAG — `llm_decision` → `recommend` / `review` / `challenge` / `summary` / `general`. Each node is a domain-specialized Gemini invocation.
- 🎨 **Server-Driven UI (SDUI)**: Backend streams structured `widget_json` payloads via SSE. The Next.js client renders dynamic React widgets (`BookCard`, `BookReview`, `ReadingTracker`) based on backend intent.
- 💾 **Persistent Memory**: LangGraph `PostgresSaver` checkpointer preserves reader context, bookshelf history, and challenge progress across sessions via thread IDs.
- ⚡ **Real-Time SSE Streaming**: Async token streaming via FastAPI `StreamingResponse` + custom `TextDecoder` SSE reader on frontend.
- 📚 **Literary Intelligence**: Matches books by mood, theme, page count, and genre preferences. Provides spoiler-free thematic reviews and quotes.
- 🔐 **JWT Auth & Security**: `bcrypt` password hashing + `Bearer` token middleware protection across all API routes.
- 🐳 **Dockerized Infrastructure**: Single-command orchestrator managing PostgreSQL 16, FastAPI backend, auto DDL table creation, and seeders.
- 📁 **Clean Architecture**: Feature-first, SOLID-compliant codebase on both backend (`app/`) and frontend (`src/features/`).

---

## 🏗️ System Architecture & Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                      LUMEN AI — BOOK RECOMMENDER                             │
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
│  │  │ (SDUI Engine)    ││  │  │  │  JWT   │ │     │  │ recommend /   │   │   │
│  │  │  ├─ BookCard     ││  │  │  └────────┘ │     │  │ review /      │   │   │
│  │  │  ├─ BookReview   ││  │  └─────────────┘     │  │ challenge /   │   │   │
│  │  │  └─ ReadingTrack ││  │         │            │  │ summary /     │   │   │
│  │  └──────────────────┘│  │  ┌──────▼──────┐     │  │ general node  │   │   │
│  └──────────────────────┘  │  │  PostgreSQL  │     │  └───────────────┘   │   │
│                            │  │  (Docker)    │     └──────────────────────┘   │
│   EventSource / Stream     │  │ LangGraph    │                                │
│   + ReadableStream Reader  │  │ Checkpointer │                                │
└────────────────────────────┴──┴──────────────┴────────────────────────────────┘
```

---

## 🤖 Lumen AI — Agent Features

### 📖 Book Recommendations
Ask Lumen for recommendations based on genre, mood, page length, or favorite authors.
- **Output:** `BookCard` — curated book recommendations with cover theme, rating, pages, tagline, and match reason.

### 📝 Book Reviews & Theme Analysis
Ask Lumen to review a book or analyze its themes.
- **Output:** `BookReview` — synopsis, memorable quotes, central themes, key takeaways, and estimated reading time.

### 🏆 Reading Challenge & Tracker
Track your annual reading goals, pages read, and reading streak.
- **Output:** `ReadingTracker` — visual progress bar, streak counter, books completed list, and annual target status.

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
Populates PostgreSQL with test users, reader profiles, bookshelf items, and 3 chat sessions pre-loaded with Lumen SDUI widget messages.

**Pre-seeded Test Credentials:**

| Email | Password | Profile |
|---|---|---|
| `alice@example.com` | `Password123!` | Sci-Fi & Fiction · 12 books/yr goal |
| `bob@example.com` | `Password123!` | Non-Fiction & History · 24 books/yr goal |

---

## 📋 Makefile Commands Reference

| Command | Action |
|---|---|
| `make dev` | Start complete stack (Docker Backend + Next.js Frontend) |
| `make backend` | Start Docker backend only (FastAPI + PostgreSQL) |
| `make frontend` | Start Next.js development server only |
| `make setup` | Initialize environment files (`.env`) |
| `make seed` | Populate PostgreSQL with literary test data |
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
