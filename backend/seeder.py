#!/usr/bin/env python3
"""
Lumen AI — Database Seeder
===========================
Populates PostgreSQL with dummy users, reader profiles, bookshelf items,
and pre-seeded literary chat sessions for immediate testing.

Usage:
    make seed
    docker-compose exec backend python seeder.py

Test credentials:
    alice@example.com / Password123!   (Sci-Fi & Fiction lover)
    bob@example.com   / Password123!   (Non-Fiction & History lover)
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
    {"email": "alice@example.com", "password": "Password123!", "profile": {
        "favorite_genres":   ["Sci-Fi", "Fiction", "Fantasy"],
        "annual_goal_books": 12,
        "reading_pace":      "moderate",
    }},
    {"email": "bob@example.com", "password": "Password123!", "profile": {
        "favorite_genres":   ["Non-Fiction", "History", "Psychology"],
        "annual_goal_books": 24,
        "reading_pace":      "fast",
    }},
]

MOCK_BOOK_CARD_WIDGET = {
    "widget_type":    "book_card",
    "genre":          "Sci-Fi",
    "total_matches":  2,
    "recommend_note": "Curated selections for Sci-Fi enthusiasts",
    "books": [
        {
            "title":          "Project Hail Mary",
            "author":         "Andy Weir",
            "rating":         4.8,
            "pages":          496,
            "published_year": 2021,
            "genre":          "Sci-Fi",
            "cover_theme":    "#2563EB",
            "tagline":        "A lone astronaut must save Earth from an extinction-level threat.",
            "match_reason":   "High-stakes science problem solving paired with unforgettable friendship.",
            "isbn":           "9780593135204",
        },
        {
            "title":          "Dune",
            "author":         "Frank Herbert",
            "rating":         4.7,
            "pages":          688,
            "published_year": 1965,
            "genre":          "Sci-Fi",
            "cover_theme":    "#D97706",
            "tagline":        "A masterpiece of politics, ecology, and prophecy on the desert planet Arrakis.",
            "match_reason":   "Perfect for lovers of epic world-building and political intrigue.",
            "isbn":           "9780441172719",
        },
    ],
}

MOCK_BOOK_REVIEW_WIDGET = {
    "widget_type":        "book_review",
    "title":              "Dune",
    "author":             "Frank Herbert",
    "published_year":     1965,
    "genre":              "Sci-Fi / Epic",
    "rating":             4.7,
    "summary":            "Set on the desert planet Arrakis, Dune tells the story of Paul Atreides as his family assumes stewardship of the galaxy's most valuable resource: spice melange.",
    "themes":             ["Ecological Balance", "Religion as Control", "Political Feudalism", "Fate & Free Will"],
    "key_takeaways": [
        "Power structures exploit religious narratives for political control.",
        "Ecology and human survival are deeply interdependent.",
        "Absolute leadership carries catastrophic unintended consequences.",
    ],
    "memorable_quote":    "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration.",
    "reading_time_hours": 14,
    "target_audience":    "Readers who enjoy intricate world-building, political maneuvering, and philosophical sci-fi.",
}

MOCK_READING_TRACKER_WIDGET = {
    "widget_type":          "reading_tracker",
    "annual_target":        12,
    "books_read":           5,
    "completion_pct":       42,
    "pages_read":           1820,
    "current_streak_days":  14,
    "longest_streak_days":  21,
    "favorite_genre":       "Sci-Fi",
    "status_label":         "On Track (+1 book ahead of pace)",
    "year":                 2026,
    "recent_books": [
        {"title": "Project Hail Mary",    "author": "Andy Weir",     "rating": 5, "finished_date": "2026-07-20"},
        {"title": "The Midnight Library", "author": "Matt Haig",     "rating": 4, "finished_date": "2026-06-15"},
        {"title": "Atomic Habits",        "author": "James Clear",   "rating": 5, "finished_date": "2026-05-02"},
        {"title": "Dune",                 "author": "Frank Herbert", "rating": 5, "finished_date": "2026-03-28"},
    ],
}

SESSIONS_TEMPLATE = [
    {
        "title": "Sci-Fi Book Recommendations",
        "messages": [
            {"role": "human", "content": "Recommend me some great sci-fi books"},
            {
                "role": "assistant",
                "content": "If you're looking to dive into captivating science fiction, I have two absolute standouts for you! 🌌 Whether you want fast-paced orbital survival or deep philosophical world-building, these books will keep you turning pages late into the night.",
                "widget_json": MOCK_BOOK_CARD_WIDGET,
            },
        ],
    },
    {
        "title": "Dune Book Review",
        "messages": [
            {"role": "human", "content": "Can you give me a review and theme analysis of Dune?"},
            {
                "role": "assistant",
                "content": "Frank Herbert's **Dune** is far more than a sci-fi novel — it's an intricate masterwork examining how ecology, religion, and feudal politics intersect. Here is the full literary breakdown and key takeaways for Dune.",
                "widget_json": MOCK_BOOK_REVIEW_WIDGET,
            },
        ],
    },
    {
        "title": "2026 Reading Goal Check",
        "messages": [
            {"role": "human", "content": "How am I doing on my 2026 reading challenge?"},
            {
                "role": "assistant",
                "content": "You are doing fantastic! 📚 You've completed **5 of 12 books** (42% of your goal) and you're currently 1 book ahead of schedule! You also have an active **14-day reading streak**. Keep going!",
                "widget_json": MOCK_READING_TRACKER_WIDGET,
            },
        ],
    },
]


# ─── Helpers ───────────────────────────────────────────────────────────────────

async def _ensure_tables(conn: asyncpg.Connection) -> None:
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

        CREATE TABLE IF NOT EXISTS user_reader_profiles (
            id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id               UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            favorite_genres       TEXT[]      NOT NULL DEFAULT '{}',
            annual_goal_books     INT         NOT NULL DEFAULT 12,
            reading_pace          VARCHAR(20) NOT NULL DEFAULT 'moderate',
            created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id)
        );
        CREATE TABLE IF NOT EXISTS user_bookshelf (
            id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id               UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title                 VARCHAR(255) NOT NULL,
            author                VARCHAR(255) NOT NULL,
            status                VARCHAR(30) NOT NULL DEFAULT 'want_to_read',
            rating                INT         CHECK (rating >= 1 AND rating <= 5),
            user_notes            TEXT,
            added_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            finished_at           TIMESTAMPTZ
        );
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


async def _seed_reader_profile(conn: asyncpg.Connection, user_id: str, profile: dict) -> None:
    existing = await conn.fetchrow("SELECT id FROM user_reader_profiles WHERE user_id = $1", user_id)
    if existing:
        print("  ℹ️  Reader profile already exists")
        return
    await conn.execute(
        """
        INSERT INTO user_reader_profiles (user_id, favorite_genres, annual_goal_books, reading_pace)
        VALUES ($1, $2, $3, $4)
        """,
        user_id,
        profile["favorite_genres"],
        profile["annual_goal_books"],
        profile["reading_pace"],
    )
    print(f"  ✅ Reader profile: Goal {profile['annual_goal_books']} books/year · {profile['favorite_genres']}")


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
                """INSERT INTO chat_messages (id, session_id, role, content, widget_json, created_at)
                   VALUES ($1, $2, $3, $4, $5, $6)""",
                str(uuid.uuid4()), session_id, msg["role"], msg["content"],
                json.dumps(wj) if wj else None, msg_time,
            )
        print(f"  ✅ Session '{session['title']}' — {len(session['messages'])} messages")


# ─── Main ──────────────────────────────────────────────────────────────────────

async def main() -> None:
    print()
    print("📚  Lumen AI — Database Seeder")
    print("─" * 48)
    print("📡  Connecting to PostgreSQL...")
    conn = await asyncpg.connect(dsn=DATABASE_URL)
    try:
        print("\n📋  Ensuring tables exist...")
        await _ensure_tables(conn)

        for user_data in USERS:
            print(f"\n👤  Seeding: {user_data['email']}")
            user_id = await _seed_user(conn, user_data["email"], user_data["password"])
            await _seed_reader_profile(conn, user_id, user_data["profile"])
            if user_data["email"] == "alice@example.com":
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
            print(f"   Goal     : {u['profile']['annual_goal_books']} books/yr · {u['profile']['favorite_genres']}")
            print()
        print("🚀  Login  → POST http://localhost:8000/api/auth/login")
        print("📖  Docs   → http://localhost:8000/docs")
        print()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
