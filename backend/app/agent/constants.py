from __future__ import annotations

"""
Agent constants — centralized configuration for the Nova AI LangGraph agent.

Domain: Personalized Learning & Language Tutor (Nova AI)
Branch: feat/nova-learning
"""

# ── SSE Streaming ─────────────────────────────────────────────────────────────

STREAMING_NODES: frozenset[str] = frozenset({
    "quiz", "explain", "roadmap", "summary", "general"
})


# ── Intent Values ─────────────────────────────────────────────────────────────

class Intent:
    """Valid intent values set by the llm_decision_node."""
    QUIZ    = "quiz"
    EXPLAIN = "explain"
    ROADMAP = "roadmap"
    SUMMARY = "summary"
    GENERAL = "general"

    ALL: frozenset[str] = frozenset({QUIZ, EXPLAIN, ROADMAP, SUMMARY, GENERAL})


# ── Learning Domain Constants ──────────────────────────────────────────────────

KNOWN_SUBJECTS: list[str] = [
    # Programming
    "Python", "JavaScript", "TypeScript", "Kotlin", "Dart", "Java",
    "C++", "C", "Go", "Rust", "Swift", "PHP",
    # CS Fundamentals
    "Data Structures", "Algorithms", "System Design", "Computer Science",
    "Operating Systems", "Networking", "Database",
    # Math & Science
    "Mathematics", "Linear Algebra", "Statistics", "Calculus", "Probability",
    "Physics", "Chemistry", "Biology",
    # AI/ML
    "Machine Learning", "Deep Learning", "Computer Vision",
    "Natural Language Processing", "LLMs", "Data Science",
    # Web & Mobile
    "React", "Next.js", "Flutter", "Android", "iOS",
    # Languages
    "English", "Bengali", "Spanish", "French", "German", "Japanese",
    # Other
    "History", "Economics", "Philosophy", "Psychology",
]

DIFFICULTY_LEVELS: list[str] = ["beginner", "intermediate", "advanced", "expert"]

QUESTION_TYPES: list[str] = [
    "mcq",           # Multiple choice (4 options)
    "true_false",    # True / False
    "fill_blank",    # Fill in the blank
    "short_answer",  # Open-ended short answer
    "code_challenge",# Write / debug code
]

XP_PER_CORRECT: int = 10
XP_PER_ROADMAP: int = 25
STREAK_BONUS_XP: int = 5

DEFAULT_SKILL_LEVEL = "beginner"
DEFAULT_LANGUAGE    = "en"
