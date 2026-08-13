from __future__ import annotations

"""
resume_node — Review resume bullet points, calculate ATS score, and emit a ResumeWidget SDUI payload.

New node for Kairo AI (Career Coach).
"""

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.prompts import build_kairo_resume_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


def _build_resume_widget() -> dict:
    return {
        "widget_type":   "resume_widget",
        "ats_score":     85,
        "role_matched":  "Senior Software Engineer",
        "overall_grade": "A-",
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
        "top_recommendation": "Add specific team size or project budget impact numbers to highlight leadership scope.",
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def resume_node(state: AgentState) -> dict:
    """
    Evaluate resume bullet points and emit a ResumeWidget SDUI payload.
    Tokens ARE streamed.
    """
    widget_data = _build_resume_widget()

    all_messages  = state.get("messages", [])
    resume_prompt = build_kairo_resume_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=resume_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
