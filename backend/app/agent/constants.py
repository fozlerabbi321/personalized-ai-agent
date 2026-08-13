from __future__ import annotations

"""
Agent constants — centralized configuration for the Kairo AI LangGraph agent.

Domain: Career Coach & Interview Prep (Kairo AI)
Branch: feat/kairo-career
"""

# ── SSE Streaming ─────────────────────────────────────────────────────────────

STREAMING_NODES: frozenset[str] = frozenset({
    "interview", "resume", "roadmap", "summary", "general"
})


# ── Intent Values ─────────────────────────────────────────────────────────────

class Intent:
    """Valid intent values set by the llm_decision_node."""
    INTERVIEW = "interview"
    RESUME    = "resume"
    ROADMAP   = "roadmap"
    SUMMARY   = "summary"
    GENERAL   = "general"

    ALL: frozenset[str] = frozenset({INTERVIEW, RESUME, ROADMAP, SUMMARY, GENERAL})


# ── Career Domain Constants ───────────────────────────────────────────────────

ROLES: list[str] = [
    "Software Engineer", "Frontend Developer", "Backend Developer",
    "Full-Stack Developer", "Mobile Engineer (Android/Flutter)",
    "DevOps Engineer", "Data Scientist", "ML Engineer",
    "Product Manager", "UI/UX Designer", "System Architect",
]

EXPERIENCE_LEVELS: list[str] = ["entry_level", "mid_level", "senior", "staff_lead"]

INTERVIEW_TYPES: list[str] = [
    "behavioral",      # STAR method
    "technical_coding",# DSA & Live coding
    "system_design",   # Architecture & Scalability
    "resume_walkthrough",
]

DEFAULT_TARGET_ROLE = "Software Engineer"
DEFAULT_LEVEL = "mid_level"
