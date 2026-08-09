#!/usr/bin/env python3
"""
personalized_ai_agent — Database Seeder
========================================
Populates PostgreSQL with dummy users, sessions, and messages
so you can test the full system immediately after ``make dev``.

Usage:
    make seed                                   ← (recommended, runs inside Docker)
    docker-compose exec backend python seeder.py
    python seeder.py                            ← (local, ensure DATABASE_URL is set)

Test credentials created:
    alice@example.com / Password123!
    bob@example.com   / Password123!
"""
from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timedelta, timezone

import asyncpg
import bcrypt

DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql://ai_agent_user:ai_agent_pass@localhost:5432/ai_agent_db",
)


# ─── Seed fixtures ─────────────────────────────────────────────────────────────

USERS = [
    {"email": "alice@example.com", "password": "Password123!"},
    {"email": "bob@example.com",   "password": "Password123!"},
]

MOCK_WIDGET = {
    "widget_type":    "candlestick_chart",
    "ticker":         "AAPL",
    "title":          "AAPL — 7-Day Price Chart",
    "current_price":  187.42,
    "change":          4.32,
    "change_pct":      2.36,
    "seven_day_high": 189.10,
    "seven_day_low":  182.50,
    "data": [
        {"date": "2025-07-28", "open": 183.10, "high": 184.50, "low": 182.00, "close": 183.80, "volume": 45_000_000},
        {"date": "2025-07-29", "open": 183.80, "high": 186.00, "low": 183.20, "close": 185.50, "volume": 52_000_000},
        {"date": "2025-07-30", "open": 185.50, "high": 187.00, "low": 184.80, "close": 186.20, "volume": 48_000_000},
        {"date": "2025-07-31", "open": 186.20, "high": 188.00, "low": 185.50, "close": 187.00, "volume": 61_000_000},
        {"date": "2025-08-01", "open": 187.00, "high": 189.10, "low": 186.00, "close": 188.30, "volume": 55_000_000},
        {"date": "2025-08-04", "open": 188.30, "high": 189.00, "low": 186.90, "close": 187.80, "volume": 42_000_000},
        {"date": "2025-08-05", "open": 187.80, "high": 188.50, "low": 186.50, "close": 187.42, "volume": 38_000_000},
    ],
    "metric": {
        "label":     "Current Price",
        "value":     "$187.42",
        "delta":     "+2.36%",
        "sentiment": "positive",
    },
}

SESSIONS_TEMPLATE = [
    {
        "title": "AAPL Stock Analysis",
        "messages": [
            {
                "role":    "human",
                "content": "What is the AAPL stock price today?",
            },
            {
                "role":        "assistant",
                "content":     (
                    "AAPL is currently trading at **$187.42**, up **+2.36%** over the last 7 days. "
                    "The stock has shown steady upward momentum with a 7-day high of $189.10. "
                    "Here's the interactive chart for your reference."
                ),
                "widget_json": MOCK_WIDGET,
            },
            {
                "role":    "human",
                "content": "What about NVDA?",
            },
            {
                "role":    "assistant",
                "content": (
                    "NVDA is trading at approximately **$882.15**, with a **+3.1%** gain over the past 7 days. "
                    "The stock has benefited from strong AI-driven demand for its GPU products. "
                    "The 7-day high was $891.00 and the low was $851.00."
                ),
                "widget_json": {
                    **MOCK_WIDGET,
                    "ticker": "NVDA",
                    "title":  "NVDA — 7-Day Price Chart",
                    "current_price": 882.15,
                    "change":         26.5,
                    "change_pct":      3.1,
                },
            },
        ],
    },
    {
        "title": "Python async/await explained",
        "messages": [
            {
                "role":    "human",
                "content": "Can you explain async/await in Python?",
            },
            {
                "role":    "assistant",
                "content": (
                    "**async/await** in Python enables writing concurrent code without threads.\n\n"
                    "- `async def` defines a **coroutine** — a function that can be paused and resumed.\n"
                    "- `await` suspends the current coroutine until the awaited operation completes.\n"
                    "- The event loop (`asyncio.run()`) orchestrates all concurrent coroutines.\n\n"
                    "This is ideal for **I/O-bound** tasks like network requests, DB queries, and file I/O "
                    "where you'd otherwise block waiting for responses."
                ),
            },
            {
                "role":    "human",
                "content": "Show me a practical example.",
            },
            {
                "role":    "assistant",
                "content": (
                    "```python\nimport asyncio\nimport httpx\n\n"
                    "async def fetch(url: str) -> dict:\n"
                    "    async with httpx.AsyncClient() as client:\n"
                    "        response = await client.get(url)\n"
                    "        return response.json()\n\n"
                    "async def main():\n"
                    "    # Run two requests concurrently\n"
                    "    results = await asyncio.gather(\n"
                    "        fetch('https://api.github.com/users/torvalds'),\n"
                    "        fetch('https://api.github.com/users/gvanrossum'),\n"
                    "    )\n"
                    "    for user in results:\n"
                    "        print(user['login'], user['public_repos'])\n\n"
                    "asyncio.run(main())\n```\n\n"
                    "Both requests run **concurrently** — total time ≈ max(t1, t2), not t1 + t2."
                ),
            },
        ],
    },
    {
        "title": "Conversation Summary",
        "messages": [
            {
                "role":    "human",
                "content": "Can you summarize our conversation?",
            },
            {
                "role":    "assistant",
                "content": (
                    "Here's a summary of what we covered:\n\n"
                    "**📈 Financial Data**\n"
                    "- AAPL is trading at $187.42 (+2.36% / 7 days)\n"
                    "- NVDA is trading at $882.15 (+3.1% / 7 days)\n\n"
                    "**🐍 Python Async/Await**\n"
                    "- `async def` defines coroutines; `await` suspends execution\n"
                    "- Best for I/O-bound concurrency (HTTP requests, DB calls)\n"
                    "- `asyncio.gather()` runs multiple coroutines concurrently"
                ),
            },
        ],
    },
]


# ─── Helpers ───────────────────────────────────────────────────────────────────


async def _ensure_tables(conn: asyncpg.Connection) -> None:
    """
    Create application tables if they don't exist.
    Schema definition mirrors app/infrastructure/database/connection.py (single source).
    """
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            email           VARCHAR(255) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id         UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title      VARCHAR(500) NOT NULL DEFAULT 'New Chat',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
        CREATE TABLE IF NOT EXISTS chat_messages (
            id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id  UUID        NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role        VARCHAR(50) NOT NULL CHECK (role IN ('human', 'assistant')),
            content     TEXT        NOT NULL,
            widget_json JSONB,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
    """)
    print("  ✅ Tables verified")



async def _seed_user(conn: asyncpg.Connection, email: str, password: str) -> str:
    existing = await conn.fetchrow("SELECT id FROM users WHERE email = $1", email)
    if existing:
        print(f"  ℹ️  User {email} already exists")
        return str(existing["id"])

    user_id = str(uuid.uuid4())
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    await conn.execute(
        "INSERT INTO users (id, email, hashed_password) VALUES ($1, $2, $3)",
        user_id, email, hashed,
    )
    print(f"  ✅ Created user: {email}")
    return user_id


async def _seed_sessions(conn: asyncpg.Connection, user_id: str) -> None:
    for idx, session in enumerate(SESSIONS_TEMPLATE):
        session_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc) - timedelta(days=len(SESSIONS_TEMPLATE) - idx)

        await conn.execute(
            "INSERT INTO chat_sessions (id, user_id, title, created_at, updated_at) VALUES ($1, $2, $3, $4, $4)",
            session_id, user_id, session["title"], created_at,
        )

        for msg_idx, msg in enumerate(session["messages"]):
            msg_time = created_at + timedelta(minutes=msg_idx * 3)
            wj = msg.get("widget_json")
            await conn.execute(
                """
                INSERT INTO chat_messages (id, session_id, role, content, widget_json, created_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                """,
                str(uuid.uuid4()),
                session_id,
                msg["role"],
                msg["content"],
                json.dumps(wj) if wj else None,
                msg_time,
            )

        print(f"  ✅ Session '{session['title']}' — {len(session['messages'])} messages")


# ─── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    print()
    print("🌱  personalized_ai_agent — Database Seeder")
    print("─" * 48)
    print(f"📡  Connecting to PostgreSQL...")

    conn = await asyncpg.connect(dsn=DATABASE_URL)
    try:
        print("\n📋  Ensuring tables exist...")
        await _ensure_tables(conn)

        for user_data in USERS:
            print(f"\n👤  Seeding: {user_data['email']}")
            user_id = await _seed_user(conn, user_data["email"], user_data["password"])
            await _seed_sessions(conn, user_id)

        print()
        print("─" * 48)
        print("✅  Seeding complete!")
        print()
        print("🔑  Test Credentials")
        print("─" * 48)
        for u in USERS:
            print(f"   Email    : {u['email']}")
            print(f"   Password : {u['password']}")
            print()
        print("🚀  Login  → POST http://localhost:8000/api/auth/login")
        print("📖  Docs   → http://localhost:8000/docs")
        print()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
