# 🎓 Nova AI — Personalized Learning & Language Tutor

> **A Full-Stack AI Learning System powered by FastAPI, LangGraph, Google Gemini, PostgreSQL, and Next.js 14 with Server-Driven UI (SDUI) Streaming.**

---

## 🌿 Project Variants — Multi-Branch Portfolio

This repository contains **4 fully independent AI agent variants**, each on its own Git branch. All variants share the same battle-tested infrastructure (FastAPI, LangGraph, SSE Streaming, PostgreSQL, JWT Auth, SDUI). Only the **domain layer** (prompts, nodes, widgets, DB schema) changes per branch.

| Branch | Agent | Domain | Theme | Status |
|---|---|---|---|---|
| [`dev`](../../tree/dev) | 💪 **Atlas** | Fitness Coach & Nutrition Advisor | 🟠 Charcoal + Orange | 🟢 Complete |
| [`feat/nova-learning`](../../tree/feat/nova-learning) | 🎓 **Nova** | Personalized Learning Tutor | 🟣 Indigo + Violet | 🟢 **Active Development** |
| [`feat/lumen-books`](../../tree/feat/lumen-books) | 📚 **Lumen** | Book Recommender & Literary Guide | 🟡 Amber + Gold | 🔵 Planned |
| [`feat/kairo-career`](../../tree/feat/kairo-career) | 💼 **Kairo** | Career Coach & Interview Prep | 🔵 Navy + Gold | 🔵 Planned |

> **Currently viewing:** `feat/nova-learning` branch — **Nova AI (Learning Tutor)**. Switch branches above to explore other agent variants.

---

## 🌟 Overview

**Nova AI** is an enterprise-grade, full-stack AI learning assistant and language tutor. It features a **stateful agentic core** built on **LangGraph** and **FastAPI**, communicating with a modern **Next.js 14 (App Router)** client via **Server-Sent Events (SSE)**.

Nova pioneers a **Server-Driven UI (SDUI)** approach: the AI backend determines the learner's query intent (quiz, concept explanation, study roadmap), executes Socratic domain logic, and dynamically streams both text tokens and rich interactive UI components — **Interactive Quiz Widgets**, **Concept Tables**, and **Study Roadmaps** — directly into the chat interface without hardcoded frontend logic.

Nova adapts to your skill level, tracks your XP progress, remembers topics you find tricky, and creates tailored learning plans across programming, computer science, mathematics, AI/ML, and languages.

---

## 🔥 Key Technical Highlights

- 🧠 **LangGraph Stateful Agent**: 5-node DAG — `llm_decision` → `quiz` / `explain` / `roadmap` / `summary` / `general`. Each node is a Socratic-prompted Gemini execution context.
- 🎨 **Server-Driven UI (SDUI)**: Backend streams structured `widget_json` payloads via SSE. The Next.js client renders dynamic React widgets (`QuizWidget`, `ConceptTable`, `StudyRoadmap`) based on backend intent.
- 💾 **Persistent Memory**: LangGraph `PostgresSaver` checkpointer preserves conversation state, learning history, and progress metrics across sessions via thread IDs.
- ⚡ **Real-Time SSE Streaming**: Async token streaming via FastAPI `StreamingResponse` + custom `TextDecoder` SSE reader on frontend.
- 🎓 **Socratic Method**: Nova asks guided questions, provides step-by-step concept breakdowns with analogies, and checks for understanding.
- 🔐 **JWT Auth & Security**: `bcrypt` password hashing + `Bearer` token middleware protection across all API routes.
- 🐳 **Dockerized Infrastructure**: Single-command orchestrator managing PostgreSQL 16, FastAPI backend, auto DDL table creation, and seeders.
- 📁 **Clean Architecture**: Feature-first, SOLID-compliant codebase on both backend (`app/`) and frontend (`src/features/`).

---

## 🏗️ System Architecture & Workflow

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                       NOVA AI — LEARNING TUTOR                               │
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
│  │  │ (SDUI Engine)    ││  │  │  │  JWT   │ │     │  │ quiz /        │   │   │
│  │  │  ├─ QuizWidget   ││  │  │  └────────┘ │     │  │ explain /     │   │   │
│  │  │  ├─ ConceptTable ││  │  └─────────────┘     │  │ roadmap /     │   │   │
│  │  │  └─ StudyRoadmap ││  │         │            │  │ summary /     │   │   │
│  │  └──────────────────┘│  │  ┌──────▼──────┐     │  │ general node  │   │   │
│  └──────────────────────┘  │  │  PostgreSQL  │     │  └───────────────┘   │   │
│                            │  │  (Docker)    │     └──────────────────────┘   │
│   EventSource / Stream     │  │ LangGraph    │                                │
│   + ReadableStream Reader  │  │ Checkpointer │                                │
└────────────────────────────┴──┴──────────────┴────────────────────────────────┘
```

---

## 🤖 Nova AI — Agent Features

### 🧠 Interactive Quizzes & Gamified XP
Ask Nova to test your knowledge on any subject (Python, DSA, Algorithms, ML, JS) at beginner, intermediate, or advanced level.
- **Output:** `QuizWidget` — interactive question card with selectable options, instant feedback, explanations, and XP rewards (+10 XP).

### 📚 Deep Concept Explanations
Ask Nova "Explain X" or "What is Y" to get structured, intuitive explanations.
- **Output:** `ConceptTable` — definition, real-world analogy, key terms, collapsible code examples, and "Learn Next" topics.

### 🗺️ Study Roadmaps
Ask Nova for a study plan (e.g. "6-week Python roadmap for beginners").
- **Output:** `StudyRoadmap` — week-by-week timeline with subtopics, study hours, resources, and milestone badges.

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
Populates PostgreSQL with test users, learning profiles, quiz history, and 3 chat sessions pre-loaded with Nova SDUI widget messages.

**Pre-seeded Test Credentials:**

| Email | Password | Profile |
|---|---|---|
| `alice@example.com` | `Password123!` | Intermediate · Python/DSA · 340 XP |
| `bob@example.com` | `Password123!` | Beginner · JavaScript · 80 XP |

---

## 📋 Makefile Commands Reference

| Command | Action |
|---|---|
| `make dev` | Start complete stack (Docker Backend + Next.js Frontend) |
| `make backend` | Start Docker backend only (FastAPI + PostgreSQL) |
| `make frontend` | Start Next.js development server only |
| `make setup` | Initialize environment files (`.env`) |
| `make seed` | Populate PostgreSQL with learning test data |
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
