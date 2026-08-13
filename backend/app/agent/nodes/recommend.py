from __future__ import annotations

"""
recommend_node — Generate curated book recommendations and emit a BookCard SDUI payload.

New node for Lumen AI (Book Recommender).
"""

import random
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import GENRES, DEFAULT_GENRE
from app.agent.prompts import build_lumen_recommend_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Curated Book Library ───────────────────────────────────────────────────────

_BOOK_LIBRARY: dict[str, list[dict]] = {
    "Sci-Fi": [
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "rating": 4.7,
            "pages": 688,
            "published_year": 1965,
            "genre": "Sci-Fi",
            "cover_theme": "#D97706",
            "tagline": "A masterpiece of politics, ecology, and prophecy on the desert planet Arrakis.",
            "match_reason": "Perfect for lovers of epic world-building and complex political intrigue.",
            "isbn": "9780441172719",
        },
        {
            "title": "Project Hail Mary",
            "author": "Andy Weir",
            "rating": 4.8,
            "pages": 496,
            "published_year": 2021,
            "genre": "Sci-Fi",
            "cover_theme": "#2563EB",
            "tagline": "A lone astronaut must save Earth from an extinction-level threat.",
            "match_reason": "High-stakes science problem solving paired with unforgettable friendship.",
            "isbn": "9780593135204",
        },
        {
            "title": "Neuromancer",
            "author": "William Gibson",
            "rating": 4.3,
            "pages": 271,
            "published_year": 1984,
            "genre": "Sci-Fi",
            "cover_theme": "#7C3AED",
            "tagline": "The foundational cyberpunk novel that defined cyberspace.",
            "match_reason": "Gritty, atmosphere-rich, and visionary exploration of AI and tech.",
            "isbn": "9780441569564",
        },
    ],
    "Fiction": [
        {
            "title": "The Midnight Library",
            "author": "Matt Haig",
            "rating": 4.5,
            "pages": 304,
            "published_year": 2020,
            "genre": "Fiction",
            "cover_theme": "#4F46E5",
            "tagline": "Between life and death there is a library where every book offers a chance to try another life.",
            "match_reason": "Heartwarming and philosophical exploration of regret, choice, and living fully.",
            "isbn": "9780525559474",
        },
        {
            "title": "Tomorrow, and Tomorrow, and Tomorrow",
            "author": "Gabrielle Zevin",
            "rating": 4.6,
            "pages": 416,
            "published_year": 2022,
            "genre": "Fiction",
            "cover_theme": "#EC4899",
            "tagline": "A dazzling novel about identity, creativity, and a thirty-year friendship born from game design.",
            "match_reason": "A deeply human story of art, love, collaboration, and resilience.",
            "isbn": "9780593321201",
        },
    ],
    "Non-Fiction": [
        {
            "title": "Atomic Habits",
            "author": "James Clear",
            "rating": 4.9,
            "pages": 320,
            "published_year": 2018,
            "genre": "Self-Help / Non-Fiction",
            "cover_theme": "#F59E0B",
            "tagline": "An easy & proven way to build good habits & break bad ones.",
            "match_reason": "Actionable, behavioral-science backed framework for long-term growth.",
            "isbn": "9780735211292",
        },
        {
            "title": "Sapiens: A Brief History of Humankind",
            "author": "Yuval Noah Harari",
            "rating": 4.7,
            "pages": 443,
            "published_year": 2014,
            "genre": "History / Non-Fiction",
            "cover_theme": "#10B981",
            "tagline": "How a mediocre ape species became the ruler of planet Earth.",
            "match_reason": "Mind-bending historical perspective on culture, money, and human imagination.",
            "isbn": "9780062316097",
        },
    ],
    "Fantasy": [
        {
            "title": "The Name of the Wind",
            "author": "Patrick Rothfuss",
            "rating": 4.7,
            "pages": 662,
            "published_year": 2007,
            "genre": "Fantasy",
            "cover_theme": "#059669",
            "tagline": "The tale of Kvothe — musician, arcanist, and legendary hero.",
            "match_reason": "Lyrical prose, rich magic system, and masterclass storytelling.",
            "isbn": "9780756404741",
        },
    ],
}

_DEFAULT_GENRE = "Fiction"


def _detect_genre(message: str) -> str:
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["sci-fi", "science fiction", "space", "cyberpunk", "alien"]):
        return "Sci-Fi"
    if any(kw in msg_lower for kw in ["fantasy", "magic", "dragon", "wizard"]):
        return "Fantasy"
    if any(kw in msg_lower for kw in ["non-fiction", "habit", "history", "self-help", "psychology"]):
        return "Non-Fiction"
    return "Fiction"


def _build_recommendations(genre: str) -> dict:
    pool = _BOOK_LIBRARY.get(genre, _BOOK_LIBRARY["Fiction"])
    selected = random.sample(pool, min(2, len(pool)))

    return {
        "widget_type":    "book_card",
        "genre":          genre,
        "total_matches":  len(selected),
        "books":          selected,
        "recommend_note": f"Curated selections for {genre} enthusiasts",
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def recommend_node(state: AgentState) -> dict:
    """
    Generate book recommendations and emit a BookCard SDUI payload.
    Tokens ARE streamed.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    genre       = _detect_genre(last_message)
    widget_data = _build_recommendations(genre)

    all_messages     = state.get("messages", [])
    recommend_prompt = build_lumen_recommend_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=recommend_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
