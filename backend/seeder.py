#!/usr/bin/env python3
"""
Atlas AI — Database Seeder
===========================
Populates PostgreSQL with dummy users, fitness profiles, workout sessions,
and SDUI widget messages so you can test the full system immediately after ``make dev``.

Usage:
    make seed                                   ← (recommended, runs inside Docker)
    docker-compose exec backend python seeder.py
    python seeder.py                            ← (local, ensure DATABASE_URL is set)

Test credentials created:
    alice@example.com / Password123!   (intermediate, muscle gain)
    bob@example.com   / Password123!   (beginner, weight loss)
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
        "fitness_level": "intermediate",
        "goal":          "muscle_gain",
        "weight_kg":     65.0,
        "height_cm":     168.0,
        "age":           26,
        "activity_level":"moderately_active",
        "available_equip":["barbell", "dumbbells", "cable_machine", "pull_up_bar", "bench"],
        "workout_days_pw": 4,
        "dietary_pref":  "none",
    }},
    {"email": "bob@example.com", "password": "Password123!", "profile": {
        "fitness_level": "beginner",
        "goal":          "weight_loss",
        "weight_kg":     90.0,
        "height_cm":     180.0,
        "age":           30,
        "activity_level":"lightly_active",
        "available_equip":["dumbbells", "resistance_bands", "bodyweight"],
        "workout_days_pw": 3,
        "dietary_pref":  "none",
    }},
]

MOCK_WORKOUT_WIDGET = {
    "widget_type":            "workout_plan",
    "title":                  "Back Day — Muscle Gain Focus",
    "goal":                   "muscle_gain",
    "fitness_level":          "intermediate",
    "muscle_group":           "back",
    "exercises": [
        {"name": "Pull-Up",          "equipment": "pull_up_bar",   "type": "compound",  "sets": 4, "reps": "8-12", "rest_seconds": 120, "muscle_group": "back"},
        {"name": "Barbell Row",      "equipment": "barbell",       "type": "compound",  "sets": 4, "reps": "8-12", "rest_seconds": 120, "muscle_group": "back"},
        {"name": "Lat Pulldown",     "equipment": "cable_machine", "type": "compound",  "sets": 4, "reps": "8-12", "rest_seconds": 90,  "muscle_group": "back"},
        {"name": "Cable Row",        "equipment": "cable_machine", "type": "compound",  "sets": 4, "reps": "8-12", "rest_seconds": 90,  "muscle_group": "back"},
        {"name": "Dumbbell Row",     "equipment": "dumbbells",     "type": "compound",  "sets": 4, "reps": "8-12", "rest_seconds": 90,  "muscle_group": "back"},
    ],
    "total_exercises":        5,
    "estimated_duration_min": 60,
    "rep_scheme_note":        "4 sets × 8-12 reps | 90-120s rest",
    "generated_at":           "2026-08-11",
}

MOCK_MACRO_WIDGET = {
    "widget_type":      "macro_donut_chart",
    "goal":             "muscle_gain",
    "gender":           "female",
    "weight_kg":        65.0,
    "height_cm":        168.0,
    "age":              26,
    "activity_level":   "moderately_active",
    "bmr":              1487,
    "tdee":             2305,
    "target_calories":  2608,
    "calorie_strategy": "+300 surplus (lean bulk)",
    "macros": {
        "protein_g": 196,
        "carbs_g":   293,
        "fat_g":     72,
        "protein_pct": 30,
        "carbs_pct":   45,
        "fat_pct":     25,
    },
    "meal_timing_tips": [
        "Eat 20-40g protein within 1-2 hours post-workout.",
        "Front-load carbs around training windows.",
        "Keep fat intake consistent throughout the day.",
    ],
}

MOCK_PROGRESS_WIDGET = {
    "widget_type":    "progress_line_chart",
    "exercise":       "Bench Press",
    "muscle_group":   "Chest",
    "unit":           "kg",
    "period_weeks":   8,
    "data": [
        {"date": "2026-06-16", "value": 65.0,  "unit": "kg"},
        {"date": "2026-06-23", "value": 66.25, "unit": "kg"},
        {"date": "2026-06-30", "value": 66.25, "unit": "kg"},
        {"date": "2026-07-07", "value": 68.75, "unit": "kg"},
        {"date": "2026-07-14", "value": 70.0,  "unit": "kg"},
        {"date": "2026-07-21", "value": 70.0,  "unit": "kg"},
        {"date": "2026-07-28", "value": 71.25, "unit": "kg"},
        {"date": "2026-08-04", "value": 72.5,  "unit": "kg"},
    ],
    "current_pr":     72.5,
    "starting_value": 65.0,
    "total_gain":     7.5,
    "gain_pct":       11.5,
    "trend":          "up",
    "trend_label":    "+7.5kg",
    "summary":        "8-week Bench Press progression",
}

SESSIONS_TEMPLATE = [
    {
        "title": "Back Day Workout Plan",
        "messages": [
            {
                "role":    "human",
                "content": "Can you give me a back workout for muscle gain?",
            },
            {
                "role":        "assistant",
                "content": (
                    "**Pull from every angle — here's your back day.** "
                    "This session is built around vertical and horizontal pulling movements to hit your lats, rhomboids, and traps. "
                    "Focus on a controlled 3-second eccentric (lowering phase) on every rep — that's where the growth happens. "
                    "Keep rest periods strict to maintain intensity."
                ),
                "widget_json": MOCK_WORKOUT_WIDGET,
            },
            {
                "role":    "human",
                "content": "How much protein should I eat for muscle gain?",
            },
            {
                "role":        "assistant",
                "content": (
                    "**Your TDEE is ~2,305 kcal — here's your muscle gain nutrition plan.** "
                    "At a +300 kcal lean bulk surplus, you're targeting **2,608 kcal/day** to build muscle without excessive fat gain. "
                    "Hit **196g protein** first (that's your non-negotiable), then fill carbs around your workout windows — "
                    "your muscles will thank you for that glycogen. "
                    "Prioritize whole foods: chicken, rice, eggs, Greek yogurt, oats."
                ),
                "widget_json": MOCK_MACRO_WIDGET,
            },
        ],
    },
    {
        "title": "Bench Press Progress Check",
        "messages": [
            {
                "role":    "human",
                "content": "Show me my bench press progress over the last 8 weeks.",
            },
            {
                "role":        "assistant",
                "content": (
                    "**Impressive — +7.5kg on your bench press in 8 weeks!** "
                    "That's an 11.5% strength increase, which is excellent for an intermediate lifter. "
                    "Your progression has been consistent with two slight plateaus (weeks 2-3 and 5-6), which is completely normal — "
                    "those are your body consolidating strength gains. "
                    "**Next step:** consider a micro-load to 73.75kg next session and aim for 3×5 before moving to 4×8-12."
                ),
                "widget_json": MOCK_PROGRESS_WIDGET,
            },
            {
                "role":    "human",
                "content": "What should I do to break my plateau?",
            },
            {
                "role":    "assistant",
                "content": (
                    "Plateaus are data, not failure. Here's the Atlas protocol to break through:\n\n"
                    "**1. Deload Week** — Reduce load by 40-50% for one week. This dissipates accumulated fatigue and often results in a PR the following week.\n\n"
                    "**2. Variation** — Swap flat bench for incline or close-grip bench for 3-4 weeks. "
                    "This addresses weak points (upper chest or triceps) that may be limiting your main lift.\n\n"
                    "**3. Micro-loading** — Use 0.5-1.25kg micro-plates instead of jumping 2.5kg. "
                    "Smaller increments sustain progress longer.\n\n"
                    "**4. RPE-based loading** — Train to RPE 8-9 (2 reps in reserve) rather than fixed weights. "
                    "This auto-regulates load based on daily readiness.\n\n"
                    "Which approach do you want to try first?"
                ),
            },
        ],
    },
    {
        "title": "Beginner Workout Q&A",
        "messages": [
            {
                "role":    "human",
                "content": "I'm a complete beginner. Where do I even start?",
            },
            {
                "role":    "assistant",
                "content": (
                    "Welcome — this is where the transformation starts. Here's the Atlas beginner blueprint:\n\n"
                    "**Phase 1: Foundation (Weeks 1-8)**\n"
                    "- Train **3 days/week** (Mon/Wed/Fri or similar) — full body each session.\n"
                    "- Master 5 movements: **Squat, Hinge, Push, Pull, Core**.\n"
                    "- Start lighter than you think you need to — perfect form is the #1 priority.\n\n"
                    "**The Big 5 to learn first:**\n"
                    "- Goblet Squat → Bodyweight Squat → Barbell Squat\n"
                    "- Romanian Deadlift → Conventional Deadlift\n"
                    "- Push-Up → Dumbbell Press → Bench Press\n"
                    "- Assisted Pull-Up → Lat Pulldown → Pull-Up\n"
                    "- Plank → Dead Bug → Ab Wheel\n\n"
                    "**Progression rule:** Add 2.5kg when you complete all reps with perfect form. Simple, effective.\n\n"
                    "Want me to generate your first week's full body workout plan?"
                ),
            },
        ],
    },
]

PERSONAL_RECORDS_ALICE = [
    {"exercise": "Bench Press",   "weight_kg": 72.5, "reps": 5},
    {"exercise": "Barbell Squat", "weight_kg": 95.0, "reps": 5},
    {"exercise": "Deadlift",      "weight_kg": 110.0,"reps": 3},
    {"exercise": "Overhead Press","weight_kg": 45.0, "reps": 5},
    {"exercise": "Barbell Row",   "weight_kg": 60.0, "reps": 5},
]


# ─── Helpers ───────────────────────────────────────────────────────────────────

async def _ensure_tables(conn: asyncpg.Connection) -> None:
    """Create all application tables (core + Atlas fitness) if they don't exist."""
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

        -- Atlas fitness tables
        CREATE TABLE IF NOT EXISTS user_fitness_profiles (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            fitness_level   VARCHAR(20) NOT NULL DEFAULT 'beginner',
            goal            VARCHAR(30) NOT NULL DEFAULT 'general_fitness',
            weight_kg       FLOAT,
            height_cm       FLOAT,
            age             INT,
            activity_level  VARCHAR(30) NOT NULL DEFAULT 'moderately_active',
            available_equip TEXT[]      NOT NULL DEFAULT '{}',
            workout_days_pw INT         NOT NULL DEFAULT 3,
            dietary_pref    VARCHAR(50),
            created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id)
        );
        CREATE TABLE IF NOT EXISTS workout_logs (
            id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id         UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            exercise_name   VARCHAR(100) NOT NULL,
            muscle_group    VARCHAR(50),
            sets            INT,
            reps            INT,
            weight_kg       FLOAT,
            duration_min    INT,
            rpe             INT,
            notes           TEXT,
            logged_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS meal_logs (
            id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id     UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            meal_name   VARCHAR(150) NOT NULL,
            meal_type   VARCHAR(20),
            calories    INT,
            protein_g   FLOAT,
            carbs_g     FLOAT,
            fat_g       FLOAT,
            logged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS personal_records (
            id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id          UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            exercise_name    VARCHAR(100) NOT NULL,
            record_weight_kg FLOAT,
            record_reps      INT,
            achieved_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(user_id, exercise_name)
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


async def _seed_fitness_profile(conn: asyncpg.Connection, user_id: str, profile: dict) -> None:
    existing = await conn.fetchrow("SELECT id FROM user_fitness_profiles WHERE user_id = $1", user_id)
    if existing:
        print("  ℹ️  Fitness profile already exists")
        return

    await conn.execute(
        """
        INSERT INTO user_fitness_profiles
            (user_id, fitness_level, goal, weight_kg, height_cm, age,
             activity_level, available_equip, workout_days_pw, dietary_pref)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        user_id,
        profile["fitness_level"],
        profile["goal"],
        profile["weight_kg"],
        profile["height_cm"],
        profile["age"],
        profile["activity_level"],
        profile["available_equip"],
        profile["workout_days_pw"],
        profile["dietary_pref"],
    )
    print(f"  ✅ Fitness profile: {profile['goal']} / {profile['fitness_level']}")


async def _seed_personal_records(conn: asyncpg.Connection, user_id: str) -> None:
    for pr in PERSONAL_RECORDS_ALICE:
        existing = await conn.fetchrow(
            "SELECT id FROM personal_records WHERE user_id = $1 AND exercise_name = $2",
            user_id, pr["exercise"]
        )
        if existing:
            continue
        await conn.execute(
            """
            INSERT INTO personal_records (user_id, exercise_name, record_weight_kg, record_reps)
            VALUES ($1, $2, $3, $4)
            """,
            user_id, pr["exercise"], pr["weight_kg"], pr["reps"],
        )
    print(f"  ✅ Personal records: {len(PERSONAL_RECORDS_ALICE)} PRs seeded")


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
    print("🏋️  Atlas AI — Database Seeder")
    print("─" * 48)
    print(f"📡  Connecting to PostgreSQL...")

    conn = await asyncpg.connect(dsn=DATABASE_URL)
    try:
        print("\n📋  Ensuring tables exist...")
        await _ensure_tables(conn)

        for user_data in USERS:
            print(f"\n👤  Seeding: {user_data['email']}")
            user_id = await _seed_user(conn, user_data["email"], user_data["password"])
            await _seed_fitness_profile(conn, user_id, user_data["profile"])

            # Only seed PRs and full sessions for Alice (primary test user)
            if user_data["email"] == "alice@example.com":
                await _seed_personal_records(conn, user_id)
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
            print(f"   Goal     : {u['profile']['goal']} / {u['profile']['fitness_level']}")
            print()
        print("🚀  Login  → POST http://localhost:8000/api/auth/login")
        print("📖  Docs   → http://localhost:8000/docs")
        print()

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
