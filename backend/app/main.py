from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, init_db
from app.agent.graph import build_graph
from app import state as app_state
from app.api import auth_router, chat_router, sessions_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Startup:
      1. Initialize asyncpg + psycopg pools
      2. Create / verify application schema tables
      3. Set up LangGraph PostgresSaver checkpointer tables
      4. Build and compile the LangGraph agent graph
      5. Store graph in module-level state (app.state)

    Shutdown:
      - Close all DB connection pools gracefully
    """
    checkpointer = await init_db()
    graph = build_graph(checkpointer)
    app_state.set_graph(graph)
    yield
    await close_db()


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description=(
        "**Personalized AI Agent** — FastAPI + LangGraph + Google Gemini.\n\n"
        "Authenticate via `/api/auth/login`, then use the `Bearer` token on protected endpoints.\n"
        "Use `/api/chat/stream` for real-time SSE streaming responses."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(sessions_router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"], summary="Service health check")
async def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": "1.0.0"}
