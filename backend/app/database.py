from __future__ import annotations

"""
Database initialization and connection management.

Two drivers are used intentionally:
  - asyncpg  : High-performance async driver for our application tables
                (users, chat_sessions, chat_messages).
  - psycopg3 : Required by LangGraph's AsyncPostgresSaver checkpointer.
Both connect to the same PostgreSQL instance.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings

# ── asyncpg pool (application tables) ────────────────────────────────────────
_asyncpg_pool: asyncpg.Pool | None = None

# ── psycopg pool + LangGraph checkpointer ────────────────────────────────────
_psycopg_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


async def init_db() -> AsyncPostgresSaver:
    """
    Initialize both DB pools, create application schema tables,
    set up LangGraph checkpointer tables, and return the checkpointer.

    Called once during FastAPI lifespan startup.
    """
    global _asyncpg_pool, _psycopg_pool, _checkpointer

    # 1. asyncpg connection pool ──────────────────────────────────────────────
    _asyncpg_pool = await asyncpg.create_pool(
        dsn=settings.DATABASE_URL,
        min_size=2,
        max_size=20,
        command_timeout=60,
    )

    # 2. Create application tables ────────────────────────────────────────────
    async with _asyncpg_pool.acquire() as conn:
        await _create_app_tables(conn)

    # 3. psycopg async pool for LangGraph ─────────────────────────────────────
    # autocommit=True is required because LangGraph's setup() runs
    # CREATE INDEX CONCURRENTLY which cannot run inside a transaction block.
    _psycopg_pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        max_size=10,
        open=False,
        kwargs={"autocommit": True, "row_factory": dict_row},
    )
    await _psycopg_pool.open()

    # 4. LangGraph PostgresSaver checkpointer ─────────────────────────────────
    _checkpointer = AsyncPostgresSaver(_psycopg_pool)
    await _checkpointer.setup()

    return _checkpointer


async def close_db() -> None:
    """Close all DB connections. Called during FastAPI lifespan shutdown."""
    if _asyncpg_pool:
        await _asyncpg_pool.close()
    if _psycopg_pool:
        await _psycopg_pool.close()


@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[asyncpg.Connection, None]:
    """Async context manager: yields an asyncpg connection from the pool."""
    if _asyncpg_pool is None:
        raise RuntimeError("asyncpg pool is not initialized")
    async with _asyncpg_pool.acquire() as conn:
        yield conn


def get_checkpointer() -> AsyncPostgresSaver:
    if _checkpointer is None:
        raise RuntimeError("LangGraph checkpointer is not initialized")
    return _checkpointer


# ── DDL ───────────────────────────────────────────────────────────────────────

async def _create_app_tables(conn: asyncpg.Connection) -> None:
    """Idempotent schema creation for application tables."""
    await conn.execute("""
        -- Users
        CREATE TABLE IF NOT EXISTS users (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            email           VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );

        -- Chat sessions (one LangGraph thread_id per session)
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title      VARCHAR(500) NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id
            ON chat_sessions(user_id);

        -- Individual messages (human + assistant turns)
        CREATE TABLE IF NOT EXISTS chat_messages (
            id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id  UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role        VARCHAR(50) NOT NULL CHECK (role IN ('human', 'assistant')),
            content     TEXT        NOT NULL,
            widget_json JSONB,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id
            ON chat_messages(session_id);
    """)
