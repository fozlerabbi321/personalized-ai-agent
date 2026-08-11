from __future__ import annotations

"""
nutrition_node — Calculate TDEE, macro breakdown, and emit a MacroDonutChart SDUI payload.

New node for Atlas AI (Fitness Coach).

Workflow:
  1. Parse user message for weight, height, age, activity level, and goal hints.
  2. Calculate TDEE using the Mifflin-St Jeor equation.
  3. Apply calorie adjustment based on goal (surplus / deficit / maintenance).
  4. Split adjusted calories into protein, carbs, and fat macros.
  5. Emit widget_json with type "macro_donut_chart" for the frontend MacroDonutChart widget.
  6. Stream LLM nutrition coaching commentary as SSE "token" events.
"""

import re
from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import (
    ACTIVITY_LEVELS,
    DEFAULT_ACTIVITY,
    DEFAULT_GOAL,
    FITNESS_GOALS,
    MACRO_TEMPLATES,
)
from app.agent.prompts import build_atlas_nutrition_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── TDEE Calculator ────────────────────────────────────────────────────────────

_ACTIVITY_MULTIPLIERS: dict[str, float] = {
    "sedentary":        1.2,
    "lightly_active":   1.375,
    "moderately_active":1.55,
    "very_active":      1.725,
    "extra_active":     1.9,
}

_GOAL_CALORIE_ADJUSTMENTS: dict[str, int] = {
    "muscle_gain":    +300,   # lean bulk surplus
    "strength":       +200,   # moderate surplus
    "weight_loss":    -500,   # moderate deficit
    "endurance":       +0,    # maintenance
    "general_fitness": +0,    # maintenance
    "default":         +0,
}


def _extract_number(pattern: str, text: str, default: float) -> float:
    """Extract a numeric value from text using a regex pattern."""
    match = re.search(pattern, text, re.IGNORECASE)
    return float(match.group(1)) if match else default


def _parse_user_metrics(message: str) -> dict:
    """
    Parse weight, height, age, and activity level from the user's message.
    Falls back to sensible defaults if not mentioned.
    """
    weight_kg = _extract_number(r"(\d+(?:\.\d+)?)\s*(?:kg|kilograms?)", message, 75.0)
    height_cm = _extract_number(r"(\d{3})\s*(?:cm|centimeters?)", message, 175.0)
    age       = int(_extract_number(r"(\d{1,2})\s*(?:years?\s*old|yr)", message, 25.0))

    # Detect gender
    gender = "male"
    if any(kw in message.lower() for kw in ["female", "woman", "girl", "she", "her"]):
        gender = "female"

    # Detect activity level
    activity = DEFAULT_ACTIVITY
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["sedentary", "desk", "no exercise", "barely"]):
        activity = "sedentary"
    elif any(kw in msg_lower for kw in ["light", "1-3", "once", "twice"]):
        activity = "lightly_active"
    elif any(kw in msg_lower for kw in ["moderate", "3-5", "most days"]):
        activity = "moderately_active"
    elif any(kw in msg_lower for kw in ["very active", "6-7", "daily", "every day"]):
        activity = "very_active"
    elif any(kw in msg_lower for kw in ["extra active", "athlete", "physical job", "twice a day"]):
        activity = "extra_active"

    return {"weight_kg": weight_kg, "height_cm": height_cm, "age": age, "gender": gender, "activity": activity}


def _detect_goal(message: str) -> str:
    """Detect nutrition goal from user message."""
    msg_lower = message.lower()
    goal_keywords = {
        "muscle_gain":    ["muscle", "bulk", "gain mass", "build", "hypertrophy"],
        "strength":       ["strength", "strong", "powerlifting"],
        "weight_loss":    ["fat loss", "weight loss", "cut", "lean", "shred", "lose weight"],
        "endurance":      ["endurance", "cardio", "stamina", "marathon", "run"],
        "general_fitness":["fit", "general", "healthy", "active", "maintain"],
    }
    for goal, keywords in goal_keywords.items():
        if any(kw in msg_lower for kw in keywords):
            return goal
    return DEFAULT_GOAL


def _calculate_nutrition(metrics: dict, goal: str) -> dict:
    """Calculate TDEE and macro breakdown using Mifflin-St Jeor equation."""
    w = metrics["weight_kg"]
    h = metrics["height_cm"]
    a = metrics["age"]
    gender = metrics["gender"]

    # Mifflin-St Jeor BMR
    if gender == "male":
        bmr = 10 * w + 6.25 * h - 5 * a + 5
    else:
        bmr = 10 * w + 6.25 * h - 5 * a - 161

    activity_mult = _ACTIVITY_MULTIPLIERS.get(metrics["activity"], 1.55)
    tdee = round(bmr * activity_mult)

    # Goal-adjusted target calories
    adjustment = _GOAL_CALORIE_ADJUSTMENTS.get(goal, 0)
    target_calories = tdee + adjustment

    # Macro split
    template = MACRO_TEMPLATES.get(goal, MACRO_TEMPLATES["general_fitness"])
    protein_g = round(target_calories * template["protein_pct"] / 4)  # 4 cal/g
    carbs_g   = round(target_calories * template["carbs_pct"] / 4)    # 4 cal/g
    fat_g     = round(target_calories * template["fat_pct"] / 9)      # 9 cal/g

    # Re-calculate actual calories from macros (rounding correction)
    actual_calories = protein_g * 4 + carbs_g * 4 + fat_g * 9

    calorie_label = {
        "muscle_gain": f"+{adjustment} surplus (lean bulk)",
        "strength":    f"+{adjustment} surplus",
        "weight_loss": f"{adjustment} deficit",
        "endurance":   "maintenance",
        "general_fitness": "maintenance",
    }.get(goal, "maintenance")

    return {
        "widget_type":      "macro_donut_chart",
        "goal":             goal,
        "gender":           gender,
        "weight_kg":        w,
        "height_cm":        h,
        "age":              a,
        "activity_level":   metrics["activity"],
        "bmr":              round(bmr),
        "tdee":             tdee,
        "target_calories":  actual_calories,
        "calorie_strategy": calorie_label,
        "macros": {
            "protein_g":      protein_g,
            "carbs_g":        carbs_g,
            "fat_g":          fat_g,
            "protein_pct":    round(template["protein_pct"] * 100),
            "carbs_pct":      round(template["carbs_pct"] * 100),
            "fat_pct":        round(template["fat_pct"] * 100),
        },
        "meal_timing_tips": [
            "Eat 20-40g protein within 1-2 hours post-workout.",
            "Front-load carbs around training windows.",
            "Keep fat intake consistent throughout the day.",
        ],
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def nutrition_node(state: AgentState) -> dict:
    """
    Calculate TDEE + macro breakdown and emit a MacroDonutChart SDUI payload.
    Tokens from this node ARE streamed to the client.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    metrics     = _parse_user_metrics(last_message)
    goal        = _detect_goal(last_message)
    widget_data = _calculate_nutrition(metrics, goal)

    all_messages   = state.get("messages", [])
    analysis_prompt = build_atlas_nutrition_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
