from __future__ import annotations

"""
FastAPI application factory.

Startup sequence (lifespan):
  1. Configure structured logging
  2. Initialize asyncpg + psycopg pools and create app schema tables
  3. Set up LangGraph PostgresSaver checkpointer tables
  4. Build and compile the LangGraph agent graph
  5. Store graph in module-level state (app.state)

Shutdown:
  - Close all DB connection pools gracefully

Global exception handlers map domain exceptions → HTTP responses,
keeping business error semantics out of the router layer.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.domain.exceptions import (
    AppError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.infrastructure.database.connection import (
    close_pools,
    create_app_tables,
    create_pools,
    get_asyncpg_pool,
)
from app.agent.graph import build_graph
from app import state as app_state
from app.interface import auth_router, chat_router, sessions_router

logger = get_logger(__name__)

__version__ = "1.0.0"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager — startup and shutdown."""
    # ── Startup ───────────────────────────────────────────────────────────────
    configure_logging("DEBUG" if settings.DEBUG else "INFO")
    logger.info("Starting %s v%s", settings.APP_NAME, __version__)

    checkpointer = await create_pools()
    pool = get_asyncpg_pool()
    await create_app_tables(pool)

    graph = build_graph(checkpointer)
    app_state.set_graph(graph)

    logger.info("Application startup complete — ready to serve requests")
    yield

    # ── Shutdown ──────────────────────────────────────────────────────────────
    logger.info("Shutting down — closing database pools")
    await close_pools()


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.APP_NAME,
    version=__version__,
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

# ── Global Exception Handlers ─────────────────────────────────────────────────
# Maps domain exceptions to HTTP responses. Routers raise domain exceptions;
# these handlers translate them to consistent JSON error responses.

@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": exc.message})


@app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError) -> JSONResponse:
    return JSONResponse(status_code=409, content={"detail": exc.message})


@app.exception_handler(UnauthorizedError)
async def unauthorized_handler(request: Request, exc: UnauthorizedError) -> JSONResponse:
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message},
        headers={"WWW-Authenticate": "Bearer"},
    )


@app.exception_handler(ForbiddenError)
async def forbidden_handler(request: Request, exc: ForbiddenError) -> JSONResponse:
    return JSONResponse(status_code=403, content={"detail": exc.message})


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": exc.message})


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    logger.error("Unhandled AppError: %s", exc.message, exc_info=exc)
    return JSONResponse(status_code=500, content={"detail": exc.message})


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(sessions_router)


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["health"], summary="Service health check")
async def health() -> dict:
    return {"status": "ok", "service": settings.APP_NAME, "version": __version__}
