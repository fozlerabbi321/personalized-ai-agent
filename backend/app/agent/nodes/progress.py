from __future__ import annotations

"""
progress_node — Retrieve mock workout progress data and emit a ProgressLineChart SDUI payload.

New node for Atlas AI (Fitness Coach).

Workflow:
  1. Parse user message for target exercise / metric to track.
  2. Generate mock PR progression data for the last 8 weeks.
  3. Emit widget_json with type "progress_line_chart" for the frontend ProgressLineChart widget.
  4. Stream LLM progress analysis commentary as SSE "token" events.
"""

import random
from datetime import datetime, timedelta

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.prompts import build_atlas_progress_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Exercise Detection ─────────────────────────────────────────────────────────

_EXERCISE_ANCHORS: dict[str, dict] = {
    "bench press":     {"base_kg": 80,  "unit": "kg", "muscle": "Chest"},
    "squat":           {"base_kg": 100, "unit": "kg", "muscle": "Quads"},
    "deadlift":        {"base_kg": 120, "unit": "kg", "muscle": "Back / Hamstrings"},
    "overhead press":  {"base_kg": 55,  "unit": "kg", "muscle": "Shoulders"},
    "barbell row":     {"base_kg": 70,  "unit": "kg", "muscle": "Back"},
    "pull-up":         {"base_kg": 0,   "unit": "reps", "muscle": "Back / Biceps"},
    "bicep curl":      {"base_kg": 25,  "unit": "kg", "muscle": "Biceps"},
    "hip thrust":      {"base_kg": 90,  "unit": "kg", "muscle": "Glutes"},
    "body weight":     {"base_kg": 80,  "unit": "kg", "muscle": "General"},
}

_DEFAULT_EXERCISE = "bench press"


def _detect_exercise(message: str) -> tuple[str, dict]:
    """Find the exercise the user is tracking from their message."""
    msg_lower = message.lower()
    for exercise, data in _EXERCISE_ANCHORS.items():
        if exercise in msg_lower:
            return exercise, data
    return _DEFAULT_EXERCISE, _EXERCISE_ANCHORS[_DEFAULT_EXERCISE]


def _generate_pr_progression(exercise_name: str, anchor: dict, weeks: int = 8) -> dict:
    """
    Generate a realistic mock PR progression over N weeks using a random walk
    with a slight positive trend (simulating progressive overload).
    """
    base = anchor["base_kg"]
    unit = anchor["unit"]
    is_reps = unit == "reps"
    progression_data = []

    current = base
    for i in range(weeks):
        week_date = (datetime.now() - timedelta(weeks=weeks - 1 - i)).strftime("%Y-%m-%d")
        # Positive bias random walk: +0 to +2.5kg or +0 to +1 rep per week
        if is_reps:
            delta = random.choice([0, 0, 1, 1, 1, 2])
        else:
            delta = round(random.uniform(-1.25, 2.5), 2)

        current = max(base * 0.8, current + delta)
        progression_data.append({
            "date":  week_date,
            "value": round(current) if is_reps else round(current, 1),
            "unit":  unit,
        })

    start_val = progression_data[0]["value"]
    end_val   = progression_data[-1]["value"]
    gain      = round(end_val - start_val, 1)
    gain_pct  = round((gain / start_val) * 100, 1) if start_val else 0
    trend     = "up" if gain > 0 else ("down" if gain < 0 else "flat")

    return {
        "widget_type":    "progress_line_chart",
        "exercise":       exercise_name.title(),
        "muscle_group":   anchor["muscle"],
        "unit":           unit,
        "period_weeks":   weeks,
        "data":           progression_data,
        "current_pr":     end_val,
        "starting_value": start_val,
        "total_gain":     gain,
        "gain_pct":       gain_pct,
        "trend":          trend,
        "trend_label":    f"+{gain}{unit}" if gain >= 0 else f"{gain}{unit}",
        "summary":        f"8-week {exercise_name.title()} progression",
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def progress_node(state: AgentState) -> dict:
    """
    Generate mock workout PR progression and emit a ProgressLineChart SDUI payload.
    Tokens from this node ARE streamed to the client.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    exercise_name, anchor = _detect_exercise(last_message)
    widget_data = _generate_pr_progression(exercise_name, anchor)

    all_messages    = state.get("messages", [])
    analysis_prompt = build_atlas_progress_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
