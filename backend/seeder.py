#!/usr/bin/env python3
"""
Kairo AI — Database Seeder
===========================
Populates PostgreSQL with dummy users, career profiles, and pre-seeded
career coaching chat sessions for immediate testing.

Usage:
    make seed
    docker-compose exec backend python seeder.py

Test credentials:
    alice@example.com / Password123!   (Software Engineer → Senior/Staff)
    bob@example.com   / Password123!   (Frontend Developer → Tech Lead)
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
        "target_role":      "Senior Software Engineer",
        "experience_level": "mid_level",
        "target_salary":    "$160,000 - $190,000",
        "primary_stack":    ["Python", "FastAPI", "PostgreSQL", "LangGraph", "Docker"],
    }},
    {"email": "bob@example.com", "password": "Password123!", "profile": {
        "target_role":      "Frontend Tech Lead",
        "experience_level": "senior",
        "target_salary":    "$170,000 - $200,000",
        "primary_stack":    ["React", "Next.js", "TypeScript", "Tailwind CSS"],
    }},
]

MOCK_INTERVIEW_WIDGET = {
    "widget_type":          "interview_widget",
    "target_role":          "Software Engineer",
    "question_no":          1,
    "question":             "Tell me about a time you had to deal with a severe production outage. How did you diagnose and resolve it under pressure?",
    "question_type":        "behavioral",
    "category":             "Crisis Management & System Resilience",
    "evaluation_criteria": [
        "Clear STAR structure (Situation, Task, Action, Result)",
        "Focus on systematic debugging over panic",
        "Mentioning post-mortem and preventative measures",
    ],
    "star_guide": {
        "situation": "Define system scale & impact (e.g. 500k active users affected)",
        "task":      "Your immediate responsibility during the incident",
        "action":    "Metrics analyzed, rollback vs fix decision, communication protocol",
        "result":    "MTTR (Mean Time to Recovery), root cause identified, long-term fix deployed",
    },
    "sample_keywords":      ["MTTR", "latency reduction", "post-mortem", "root cause analysis", "monitoring"],
}

MOCK_RESUME_WIDGET = {
    "widget_type":   "resume_widget",
    "ats_score":     85,
    "role_matched":  "Senior Software Engineer",
    "overall_grade": "A-",
    "top_recommendation": "Add specific team size or project budget impact numbers to highlight leadership scope.",
    "bullet_rewrites": [
        {
            "original":   "Worked on the backend API and made it faster.",
            "improved":   "Engineered asynchronous FastAPI microservices, reducing P99 latency by 45% (280ms → 154ms) under 10k RPS load.",
            "impact_type":"Performance / Scale",
            "keywords":   ["FastAPI", "P99 latency", "microservices", "RPS"],
        },
        {
            "original":   "Added state management to the React application.",
            "improved":   "Architected Zustand client state store with URL parameter synchronization, eliminating prop-drilling across 14 component trees.",
            "impact_type":"Architecture / Maintainability",
            "keywords":   ["Zustand", "State Management", "Architecture"],
        },
        {
            "original":   "Fixed bugs and wrote automated tests for the team.",
            "improved":   "Established Pytest integration test suite with CI/CD GitHub Actions pipeline, elevating code coverage from 58% to 92%.",
            "impact_type":"Quality / Automation",
            "keywords":   ["Pytest", "CI/CD", "GitHub Actions", "Test Coverage"],
        },
    ],
    "ats_checklist": [
        {"item": "Quantifiable metrics (% / $ / scale)", "status": "pass"},
        {"item": "Strong action verbs at start of bullets", "status": "pass"},
        {"item": "Role-relevant technical keywords", "status": "pass"},
        {"item": "Clean formatting without tables/images", "status": "pass"},
        {"item": "Concise bullet length (1-2 lines max)", "status": "warning"},
    ],
}

MOCK_ROADMAP_WIDGET = {
    "widget_type":    "career_roadmap",
    "current_role":   "Mid-Level Software Engineer",
    "target_role":    "Senior / Staff Software Engineer",
    "timeframe":      "12-18 Months",
    "salary_range":   "$140,000 - $185,000",
    "key_metric":     "3 major system ownership wins + 2 mentored engineers promoted",
    "phases": [
        {
            "phase": 1,
            "title": "Technical Mastery & System Ownership",
            "timeframe": "Months 1-4",
            "milestones": [
                "Take end-to-end ownership of a core microservice or sub-system.",
                "Master distributed caching, database indexing, and query optimization.",
                "Drive technical debt reduction initiatives.",
            ],
            "skills_to_acquire": ["System Architecture", "Redis Caching", "Database Tuning"],
        },
        {
            "phase": 2,
            "title": "Cross-Team Leadership & Mentorship",
            "timeframe": "Months 5-9",
            "milestones": [
                "Lead architecture design docs (RFCs) for new multi-month features.",
                "Mentor junior engineers through pair programming and code reviews.",
                "Establish team engineering standards and CI/CD best practices.",
            ],
            "skills_to_acquire": ["Technical Design (RFCs)", "Engineering Mentorship", "CI/CD Protocols"],
        },
        {
            "phase": 3,
            "title": "Strategic Business Impact & Executive Presence",
            "timeframe": "Months 10-14",
            "milestones": [
                "Align technical roadmap decisions with product & business KPIs.",
                "Present architecture strategy to engineering leadership.",
                "Build promotion case document highlighting high-leverage business results.",
            ],
            "skills_to_acquire": ["Business Acumen", "Executive Presentation", "Promotion Packet Prep"],
        },
    ],
}

SESSIONS_TEMPLATE = [
    {
        "title": "Behavioral Mock Interview",
        "messages": [
            {"role": "human", "content": "Let's do a behavioral interview question for a Software Engineer position"},
            {
                "role": "assistant",
                "content": "Welcome to your mock interview session! 🎯 Top tech companies evaluate behavioral questions to see how you perform under pressure, handle ambiguity, and drive technical outcomes. Here is your question — frame your answer using the STAR method.",
                "widget_json": MOCK_INTERVIEW_WIDGET,
            },
        ],
    },
    {
        "title": "Resume Review & Impact Rewrites",
        "messages": [
            {"role": "human", "content": "Can you review my resume bullet points and suggest improvements?"},
            {
                "role": "assistant",
                "content": "Your resume has a strong foundation (**ATS Score: 85/100**)! However, recruiters spend an average of 6 seconds per resume — weak bullet points like 'Worked on API' get skipped. Here are transformed high-impact metric rewrites.",
                "widget_json": MOCK_RESUME_WIDGET,
            },
        ],
    },
    {
        "title": "Senior Engineer Growth Roadmap",
        "messages": [
            {"role": "human", "content": "How can I transition from Mid-Level to Senior Software Engineer?"},
            {
                "role": "assistant",
                "content": "Moving from Mid-Level to Senior isn't just about writing more code — it's about shifting from **task execution** to **system ownership & technical leadership**. Here is your 12-18 month strategic growth roadmap.",
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

        CREATE TABLE IF NOT EXISTS user_career_profiles (
            id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            target_role         VARCHAR(100) NOT NULL DEFAULT 'Software Engineer',
            experience_level    VARCHAR(30) NOT NULL DEFAULT 'mid_level',
            target_salary       VARCHAR(50),
            primary_stack       TEXT[]      NOT NULL DEFAULT '{}',
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id)
        );
        CREATE TABLE IF NOT EXISTS interview_practice_logs (
            id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id             UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            question            TEXT        NOT NULL,
            interview_type      VARCHAR(50) NOT NULL,
            feedback_score      INT         CHECK (feedback_score >= 1 AND feedback_score <= 100),
            user_notes          TEXT,
            practiced_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
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


async def _seed_career_profile(conn: asyncpg.Connection, user_id: str, profile: dict) -> None:
    existing = await conn.fetchrow("SELECT id FROM user_career_profiles WHERE user_id = $1", user_id)
    if existing:
        print("  ℹ️  Career profile already exists")
        return
    await conn.execute(
        """
        INSERT INTO user_career_profiles (user_id, target_role, experience_level, target_salary, primary_stack)
        VALUES ($1, $2, $3, $4, $5)
        """,
        user_id,
        profile["target_role"],
        profile["experience_level"],
        profile["target_salary"],
        profile["primary_stack"],
    )
    print(f"  ✅ Career profile: {profile['target_role']} ({profile['experience_level']})")


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
    print("💼  Kairo AI — Database Seeder")
    print("─" * 48)
    print("📡  Connecting to PostgreSQL...")
    conn = await asyncpg.connect(dsn=DATABASE_URL)
    try:
        print("\n📋  Ensuring tables exist...")
        await _ensure_tables(conn)

        for user_data in USERS:
            print(f"\n👤  Seeding: {user_data['email']}")
            user_id = await _seed_user(conn, user_data["email"], user_data["password"])
            await _seed_career_profile(conn, user_data["profile"])
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
            print(f"   Target   : {u['profile']['target_role']} ({u['profile']['experience_level']})")
            print()
        print("🚀  Login  → POST http://localhost:8000/api/auth/login")
        print("📖  Docs   → http://localhost:8000/docs")
        print()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
