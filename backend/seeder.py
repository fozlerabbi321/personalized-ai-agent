#!/usr/bin/env python3
"""
Nova AI — Database Seeder
==========================
Populates PostgreSQL with dummy users, learning profiles, and chat sessions
(pre-loaded with Nova SDUI widget messages) for immediate testing.

Usage:
    make seed
    docker-compose exec backend python seeder.py

Test credentials:
    alice@example.com / Password123!   (intermediate, Python + DSA learner)
    bob@example.com   / Password123!   (beginner, JavaScript learner)
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
        "subjects":       ["Python", "Data Structures", "Algorithms"],
        "skill_level":    "intermediate",
        "preferred_lang": "en",
        "total_xp":       340,
        "streak_days":    7,
    }},
    {"email": "bob@example.com", "password": "Password123!", "profile": {
        "subjects":       ["JavaScript", "React"],
        "skill_level":    "beginner",
        "preferred_lang": "en",
        "total_xp":       80,
        "streak_days":    2,
    }},
]

MOCK_QUIZ_WIDGET = {
    "widget_type":    "quiz_widget",
    "subject":        "Python",
    "difficulty":     "intermediate",
    "question_no":    1,
    "question":       "What does the `@property` decorator do in Python?",
    "question_type":  "mcq",
    "options": [
        {"id": "A", "text": "Creates a class attribute"},
        {"id": "B", "text": "Makes a method callable as an attribute"},
        {"id": "C", "text": "Caches the function result"},
        {"id": "D", "text": "Marks a method as static"},
    ],
    "correct_answer": "B",
    "explanation":    "@property turns a method into a getter, allowing you to access it like `obj.name` instead of `obj.name()`.",
    "xp_reward":      10,
}

MOCK_CONCEPT_WIDGET = {
    "widget_type":   "concept_table",
    "topic":         "Recursion",
    "definition":    "A function that calls itself to solve a smaller version of the same problem.",
    "analogy":       "Like Russian nesting dolls — each doll contains a smaller version until you reach the smallest one (the base case).",
    "key_terms": [
        {"term": "Base Case",      "definition": "The condition that stops recursion (prevents infinite loop)"},
        {"term": "Recursive Case", "definition": "The part where the function calls itself with a simpler input"},
        {"term": "Call Stack",     "definition": "Memory structure that tracks active function calls"},
    ],
    "example_code":   "def factorial(n):\n    if n == 0:     # base case\n        return 1\n    return n * factorial(n - 1)  # recursive case",
    "code_language":  "Python",
    "related_topics": ["Call Stack", "Dynamic Programming", "Tree Traversal", "Memoization"],
}

MOCK_ROADMAP_WIDGET = {
    "widget_type":    "study_roadmap",
    "subject":        "Python",
    "skill_level":    "beginner",
    "duration_weeks": 6,
    "total_hours":    48,
    "daily_hours":    1.1,
    "milestone":      "Complete Python beginner curriculum",
    "weeks": [
        {"week": 1, "topic": "Python Basics",         "subtopics": ["Variables & Types", "Control Flow", "Functions"],               "hours": 8,  "resources": ["Python.org Tutorial", "Automate the Boring Stuff Ch.1-3"]},
        {"week": 2, "topic": "Data Structures",       "subtopics": ["Lists", "Dicts", "Tuples", "Sets"],                             "hours": 8,  "resources": ["Real Python — Data Structures"]},
        {"week": 3, "topic": "OOP in Python",         "subtopics": ["Classes", "Inheritance", "Encapsulation", "Dunder Methods"],    "hours": 10, "resources": ["Corey Schafer OOP Series"]},
        {"week": 4, "topic": "File I/O & Exceptions", "subtopics": ["File handling", "Try/except", "Context managers"],              "hours": 6,  "resources": ["Python Docs: Errors & Exceptions"]},
        {"week": 5, "topic": "Modules & Packages",    "subtopics": ["Imports", "pip", "Virtual Environments"],                       "hours": 6,  "resources": ["Python Packaging User Guide"]},
        {"week": 6, "topic": "Async & Concurrency",   "subtopics": ["asyncio", "async/await", "Coroutines", "Event Loop"],           "hours": 10, "resources": ["Python asyncio Docs", "Real Python Async IO Guide"]},
    ],
}

SESSIONS_TEMPLATE = [
    {
        "title": "Python Quiz Session",
        "messages": [
            {"role": "human", "content": "Quiz me on Python intermediate level"},
            {
                "role": "assistant",
                "content": "Let's put your Python knowledge to the test! 🧠 Here's an intermediate question on Python decorators — this is a concept that separates good Python devs from great ones. Give it your best shot!",
                "widget_json": MOCK_QUIZ_WIDGET,
            },
            {"role": "human", "content": "The answer is B"},
            {
                "role": "assistant",
                "content": "⭐ Correct! You earned **+10 XP**!\n\n**@property** is one of Python's most elegant features. It lets you define computed attributes — properties that look like regular attributes but execute logic when accessed.\n\n```python\nclass Circle:\n    def __init__(self, radius):\n        self._radius = radius\n    \n    @property\n    def area(self):\n        return 3.14159 * self._radius ** 2\n\nc = Circle(5)\nprint(c.area)  # Looks like an attribute, runs the method\n```\n\nWant another question or should we dive deeper into decorators?",
            },
        ],
    },
    {
        "title": "Recursion Explained",
        "messages": [
            {"role": "human", "content": "Explain recursion to me"},
            {
                "role": "assistant",
                "content": "Great question! Recursion is one of those concepts that feels mind-bending at first but becomes intuitive once it clicks.\n\n**Simple definition:** A recursive function is one that calls itself to solve a smaller version of the same problem.\n\n**The key insight** — every recursive solution needs two things:\n1. **Base case**: When to stop (prevents infinite loops)\n2. **Recursive case**: How to reduce the problem each time\n\nThink of it like Russian nesting dolls — you keep opening dolls until you hit the smallest one (base case).\n\nHere's the classic factorial example:\n```python\ndef factorial(n):\n    if n == 0:        # base case\n        return 1\n    return n * factorial(n - 1)  # recursive case\n```\n\n**Quick question:** What would happen if we removed the `if n == 0` check? 🤔",
                "widget_json": MOCK_CONCEPT_WIDGET,
            },
            {"role": "human", "content": "It would run forever?"},
            {
                "role": "assistant",
                "content": "Exactly right! 🎯 Without the base case, the function would call itself infinitely — until Python raises a **RecursionError** (Python limits the call stack to ~1000 frames by default).\n\n```python\nfact(5) → fact(4) → fact(3) → fact(2) → fact(1) → fact(0) ✅ STOP\n```\n\nThis is why the base case is non-negotiable in any recursive function.\n\n**Next challenge:** Can you write a recursive function that calculates the sum of a list? `sum_list([1, 2, 3, 4])` → `10`",
            },
        ],
    },
    {
        "title": "Python Study Roadmap",
        "messages": [
            {"role": "human", "content": "Give me a 6-week Python study roadmap for beginners"},
            {
                "role": "assistant",
                "content": "Awesome choice — Python is one of the most powerful languages to start with, and 6 weeks is the perfect commitment to build real foundational skills! 🚀\n\nThis roadmap follows the **fundamentals-first philosophy**: we don't rush to advanced topics until the basics are rock-solid. Each week builds on the last, and by week 6, you'll be writing async Python code like a pro.\n\n**Your mission:** 1-2 hours per day, 6 weeks. Let's go!",
                "widget_json": MOCK_ROADMAP_WIDGET,
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

        CREATE TABLE IF NOT EXISTS user_learning_profiles (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subjects        TEXT[]      NOT NULL DEFAULT '{}',
            skill_level     VARCHAR(20) NOT NULL DEFAULT 'beginner',
            preferred_lang  VARCHAR(10) NOT NULL DEFAULT 'en',
            total_xp        INT         NOT NULL DEFAULT 0,
            streak_days     INT         NOT NULL DEFAULT 0,
            last_active_at  TIMESTAMPTZ,
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id)
        );
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject         VARCHAR(100) NOT NULL,
            difficulty      VARCHAR(20),
            question_text   TEXT        NOT NULL,
            user_answer     VARCHAR(10),
            correct_answer  VARCHAR(10) NOT NULL,
            is_correct      BOOLEAN     NOT NULL DEFAULT FALSE,
            xp_earned       INT         NOT NULL DEFAULT 0,
            attempted_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS study_sessions (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            subject         VARCHAR(100) NOT NULL,
            duration_min    INT,
            topics_covered  TEXT[]      NOT NULL DEFAULT '{}',
            notes           TEXT,
            session_date    DATE        NOT NULL DEFAULT CURRENT_DATE
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


async def _seed_learning_profile(conn: asyncpg.Connection, user_id: str, profile: dict) -> None:
    existing = await conn.fetchrow("SELECT id FROM user_learning_profiles WHERE user_id = $1", user_id)
    if existing:
        print("  ℹ️  Learning profile already exists")
        return
    await conn.execute(
        """
        INSERT INTO user_learning_profiles
            (user_id, subjects, skill_level, preferred_lang, total_xp, streak_days, last_active_at)
        VALUES ($1, $2, $3, $4, $5, $6, NOW())
        """,
        user_id,
        profile["subjects"],
        profile["skill_level"],
        profile["preferred_lang"],
        profile["total_xp"],
        profile["streak_days"],
    )
    print(f"  ✅ Learning profile: {profile['skill_level']} · XP {profile['total_xp']} · 🔥 {profile['streak_days']} days")


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
    print("🎓  Nova AI — Database Seeder")
    print("─" * 48)
    print("📡  Connecting to PostgreSQL...")
    conn = await asyncpg.connect(dsn=DATABASE_URL)
    try:
        print("\n📋  Ensuring tables exist...")
        await _ensure_tables(conn)

        for user_data in USERS:
            print(f"\n👤  Seeding: {user_data['email']}")
            user_id = await _seed_user(conn, user_data["email"], user_data["password"])
            await _seed_learning_profile(conn, user_id, user_data["profile"])
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
            print(f"   Level    : {u['profile']['skill_level']} · XP {u['profile']['total_xp']}")
            print()
        print("🚀  Login  → POST http://localhost:8000/api/auth/login")
        print("📖  Docs   → http://localhost:8000/docs")
        print()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
