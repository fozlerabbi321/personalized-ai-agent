from __future__ import annotations

"""
Database connection pool management.

Two drivers are used intentionally:
  - asyncpg  : High-performance async driver for application tables
               (users, chat_sessions, chat_messages).
  - psycopg3 : Required by LangGraph's AsyncPostgresSaver checkpointer.
Both pools connect to the same PostgreSQL instance.

This module is the single source of truth for pool lifecycle.
Pools are initialized in the FastAPI lifespan and accessed via
dependency injection (app/core/container.py).
"""

import asyncpg
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.config import settings


# ── Module-level pool references (set during lifespan startup) ────────────────
_asyncpg_pool: asyncpg.Pool | None = None
_psycopg_pool: AsyncConnectionPool | None = None
_checkpointer: AsyncPostgresSaver | None = None


async def create_pools() -> AsyncPostgresSaver:
    """
    Initialize both DB connection pools.

    1. asyncpg pool for application table queries
    2. psycopg3 pool for LangGraph's AsyncPostgresSaver checkpointer
    3. Run LangGraph checkpointer setup (idempotent)

    Returns the initialized checkpointer, to be stored in the DI container.
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

    # 2. psycopg async pool for LangGraph ─────────────────────────────────────
    # autocommit=True is required because LangGraph's setup() runs
    # CREATE INDEX CONCURRENTLY which cannot run inside a transaction block.
    _psycopg_pool = AsyncConnectionPool(
        conninfo=settings.DATABASE_URL,
        max_size=10,
        open=False,
        kwargs={"autocommit": True, "row_factory": dict_row},
    )
    await _psycopg_pool.open()

    # 3. LangGraph PostgresSaver checkpointer ─────────────────────────────────
    _checkpointer = AsyncPostgresSaver(_psycopg_pool)
    await _checkpointer.setup()

    return _checkpointer


async def close_pools() -> None:
    """Gracefully close all DB connection pools. Called during lifespan shutdown."""
    if _asyncpg_pool:
        await _asyncpg_pool.close()
    if _psycopg_pool:
        await _psycopg_pool.close()


def get_asyncpg_pool() -> asyncpg.Pool:
    """Return the initialized asyncpg pool. Raises if not yet initialized."""
    if _asyncpg_pool is None:
        raise RuntimeError("asyncpg pool is not initialized. Check application lifespan.")
    return _asyncpg_pool


def get_checkpointer() -> AsyncPostgresSaver:
    """Return the initialized LangGraph checkpointer. Raises if not yet initialized."""
    if _checkpointer is None:
        raise RuntimeError("LangGraph checkpointer is not initialized.")
    return _checkpointer


# ── DDL ───────────────────────────────────────────────────────────────────────

async def create_app_tables(pool: asyncpg.Pool) -> None:
    """
    Idempotent schema creation for application tables.

    Used during application startup and by seeder.py.
    All statements use IF NOT EXISTS so they are safe to run multiple times.
    """
    async with pool.acquire() as conn:
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
