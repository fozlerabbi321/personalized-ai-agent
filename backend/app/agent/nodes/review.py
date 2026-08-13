from __future__ import annotations

"""
review_node — Generate a detailed book review/analysis and emit a BookReview SDUI payload.

New node for Lumen AI (Book Recommender).
"""

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.prompts import build_lumen_review_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Detailed Book Reviews Knowledge Base ───────────────────────────────────────

_REVIEW_KB: dict[str, dict] = {
    "dune": {
        "title": "Dune",
        "author": "Frank Herbert",
        "published_year": 1965,
        "genre": "Sci-Fi / Epic",
        "rating": 4.7,
        "summary": "Set on the desert planet Arrakis, Dune tells the story of Paul Atreides as his family assumes stewardship of the galaxy's most valuable resource: spice melange.",
        "themes": ["Ecological Balance", "Religion as Control", "Political Feudalism", "Fate & Free Will"],
        "key_takeaways": [
            "Power structures exploit religious narratives for political control.",
            "Ecology and human survival are deeply interdependent.",
            "Absolute leadership carries catastrophic unintended consequences.",
        ],
        "memorable_quote": "I must not fear. Fear is the mind-killer. Fear is the little-death that brings total obliteration.",
        "reading_time_hours": 14,
        "target_audience": "Readers who enjoy intricate world-building, political maneuvering, and philosophical sci-fi.",
    },
    "atomic habits": {
        "title": "Atomic Habits",
        "author": "James Clear",
        "published_year": 2018,
        "genre": "Self-Help / Behavioral Psychology",
        "rating": 4.9,
        "summary": "Atomic Habits provides a proven framework for improving every day by focusing on tiny 1% changes that compound into massive results over time.",
        "themes": ["Identity-Based Habits", "System vs Goal", "The 4 Laws of Behavior Change", "Compounding Effect"],
        "key_takeaways": [
            "You do not rise to the level of your goals, you fall to the level of your systems.",
            "Focus on who you want to become, not what you want to achieve.",
            "Small 1% improvements every day equal 37x growth in a year.",
        ],
        "memorable_quote": "Every action you take is a vote for the type of person you wish to become.",
        "reading_time_hours": 6,
        "target_audience": "Anyone seeking practical, science-backed strategies for personal productivity and habit building.",
    },
}

_DEFAULT_REVIEW = _REVIEW_KB["dune"]


def _detect_book_title(message: str) -> str:
    msg_lower = message.lower()
    for key in _REVIEW_KB:
        if key in msg_lower:
            return key
    return "dune"


def _build_review_widget(book_key: str) -> dict:
    review = _REVIEW_KB.get(book_key, _DEFAULT_REVIEW)
    return {
        "widget_type":        "book_review",
        "title":              review["title"],
        "author":             review["author"],
        "published_year":     review["published_year"],
        "genre":              review["genre"],
        "rating":             review["rating"],
        "summary":            review["summary"],
        "themes":             review["themes"],
        "key_takeaways":      review["key_takeaways"],
        "memorable_quote":    review["memorable_quote"],
        "reading_time_hours": review["reading_time_hours"],
        "target_audience":    review["target_audience"],
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def review_node(state: AgentState) -> dict:
    """
    Generate a book review and emit a BookReview SDUI payload.
    Tokens ARE streamed.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    book_key    = _detect_book_title(last_message)
    widget_data = _build_review_widget(book_key)

    all_messages  = state.get("messages", [])
    review_prompt = build_lumen_review_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=review_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
