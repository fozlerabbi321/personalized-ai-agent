from __future__ import annotations

"""
challenge_node — Track annual reading goals, habit streaks, and emit a ReadingTracker SDUI payload.

New node for Lumen AI (Book Recommender).
"""

from datetime import datetime
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.prompts import build_lumen_challenge_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


def _build_challenge_widget() -> dict:
    target_books = 12
    completed_books = 5
    pct = round((completed_books / target_books) * 100)

    recent_books = [
        {"title": "Project Hail Mary",      "author": "Andy Weir",       "rating": 5, "finished_date": "2026-07-20"},
        {"title": "The Midnight Library",   "author": "Matt Haig",       "rating": 4, "finished_date": "2026-06-15"},
        {"title": "Atomic Habits",          "author": "James Clear",     "rating": 5, "finished_date": "2026-05-02"},
        {"title": "Dune",                   "author": "Frank Herbert",   "rating": 5, "finished_date": "2026-03-28"},
        {"title": "Klara and the Sun",      "author": "Kazuo Ishiguro",  "rating": 4, "finished_date": "2026-02-10"},
    ]

    return {
        "widget_type":      "reading_tracker",
        "annual_target":    target_books,
        "books_read":       completed_books,
        "completion_pct":   pct,
        "pages_read":       1820,
        "current_streak_days": 14,
        "longest_streak_days": 21,
        "favorite_genre":   "Sci-Fi",
        "recent_books":     recent_books,
        "status_label":     "On Track (+1 book ahead of pace)",
        "year":             datetime.now().year,
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def challenge_node(state: AgentState) -> dict:
    """
    Track reading challenge metrics and emit a ReadingTracker SDUI payload.
    Tokens ARE streamed.
    """
    widget_data = _build_challenge_widget()

    all_messages     = state.get("messages", [])
    challenge_prompt = build_lumen_challenge_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=challenge_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
