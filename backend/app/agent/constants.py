from __future__ import annotations

"""
Agent constants — centralized configuration for the Lumen AI LangGraph agent.

Domain: Book Recommender & Literary Guide (Lumen AI)
Branch: feat/lumen-books
"""

# ── SSE Streaming ─────────────────────────────────────────────────────────────

STREAMING_NODES: frozenset[str] = frozenset({
    "recommend", "review", "challenge", "summary", "general"
})


# ── Intent Values ─────────────────────────────────────────────────────────────

class Intent:
    """Valid intent values set by the llm_decision_node."""
    RECOMMEND = "recommend"
    REVIEW    = "review"
    CHALLENGE = "challenge"
    SUMMARY   = "summary"
    GENERAL   = "general"

    ALL: frozenset[str] = frozenset({RECOMMEND, REVIEW, CHALLENGE, SUMMARY, GENERAL})


# ── Literary Domain Constants ──────────────────────────────────────────────────

GENRES: list[str] = [
    "Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Thriller",
    "Romance", "Historical Fiction", "Biography", "Self-Help", "Psychology",
    "Philosophy", "Business", "Technology", "Poetry", "Classics", "YA",
]

READING_PACES: list[str] = ["fast", "moderate", "slow", "casual"]

BOOK_LENGTHS: list[str] = [
    "short (< 200 pages)",
    "medium (200-400 pages)",
    "long (400+ pages)",
]

DEFAULT_GENRE = "Fiction"
DEFAULT_GOAL_BOOKS_PER_YEAR = 12
