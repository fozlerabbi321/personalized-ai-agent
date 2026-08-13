from __future__ import annotations

"""
roadmap_node — Generate career growth roadmap and emit a CareerRoadmapWidget SDUI payload.

New node for Kairo AI (Career Coach).
"""

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.prompts import build_kairo_roadmap_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


def _build_career_roadmap_widget() -> dict:
    return {
        "widget_type":    "career_roadmap",
        "current_role":   "Mid-Level Software Engineer",
        "target_role":    "Senior / Staff Software Engineer",
        "timeframe":      "12-18 Months",
        "salary_range":   "$140,000 - $185,000",
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
        "key_metric": "3 major system ownership wins + 2 mentored engineers promoted",
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def roadmap_node(state: AgentState) -> dict:
    """
    Generate career growth plan and emit a CareerRoadmapWidget SDUI payload.
    Tokens ARE streamed.
    """
    widget_data = _build_career_roadmap_widget()

    all_messages   = state.get("messages", [])
    roadmap_prompt = build_kairo_roadmap_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=roadmap_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
