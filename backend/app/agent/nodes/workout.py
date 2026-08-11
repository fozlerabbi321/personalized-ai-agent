from __future__ import annotations

"""
workout_node — Generate a personalized workout plan and emit a WorkoutPlanWidget SDUI payload.

Replaces: api_call_node (crypto chart data)
New domain: Fitness Coach (Atlas AI)

Workflow:
  1. Parse user message for goal, muscle group, equipment, duration hints.
  2. Generate a structured workout plan (exercises × sets × reps × rest).
  3. Emit widget_json with type "workout_plan" for the frontend WorkoutPlanWidget.
  4. Stream LLM coaching commentary as SSE "token" events.
"""

import random
import re
from datetime import datetime

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import (
    DEFAULT_GOAL,
    DEFAULT_FITNESS_LEVEL,
    EQUIPMENT_TYPES,
    FITNESS_GOALS,
    FITNESS_LEVELS,
    KNOWN_MUSCLE_GROUPS,
)
from app.agent.prompts import build_atlas_workout_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm


# ── Workout database (exercise library) ───────────────────────────────────────

_EXERCISE_LIBRARY: dict[str, list[dict]] = {
    "chest": [
        {"name": "Barbell Bench Press",   "equipment": "barbell", "type": "compound"},
        {"name": "Incline Dumbbell Press", "equipment": "dumbbells", "type": "compound"},
        {"name": "Cable Chest Fly",        "equipment": "cable_machine", "type": "isolation"},
        {"name": "Push-Up",                "equipment": "bodyweight", "type": "compound"},
        {"name": "Dumbbell Pullover",      "equipment": "dumbbells", "type": "isolation"},
    ],
    "back": [
        {"name": "Barbell Deadlift",    "equipment": "barbell", "type": "compound"},
        {"name": "Pull-Up",             "equipment": "pull_up_bar", "type": "compound"},
        {"name": "Barbell Row",         "equipment": "barbell", "type": "compound"},
        {"name": "Lat Pulldown",        "equipment": "cable_machine", "type": "compound"},
        {"name": "Cable Row",           "equipment": "cable_machine", "type": "compound"},
        {"name": "Dumbbell Row",        "equipment": "dumbbells", "type": "compound"},
    ],
    "shoulders": [
        {"name": "Overhead Barbell Press", "equipment": "barbell", "type": "compound"},
        {"name": "Dumbbell Lateral Raise", "equipment": "dumbbells", "type": "isolation"},
        {"name": "Front Raise",            "equipment": "dumbbells", "type": "isolation"},
        {"name": "Face Pull",              "equipment": "cable_machine", "type": "isolation"},
        {"name": "Arnold Press",           "equipment": "dumbbells", "type": "compound"},
    ],
    "legs": [
        {"name": "Barbell Squat",          "equipment": "barbell", "type": "compound"},
        {"name": "Romanian Deadlift",      "equipment": "barbell", "type": "compound"},
        {"name": "Leg Press",              "equipment": "leg_press_machine", "type": "compound"},
        {"name": "Bulgarian Split Squat",  "equipment": "dumbbells", "type": "compound"},
        {"name": "Leg Curl",               "equipment": "cable_machine", "type": "isolation"},
        {"name": "Calf Raise",             "equipment": "bodyweight", "type": "isolation"},
        {"name": "Hip Thrust",             "equipment": "barbell", "type": "compound"},
    ],
    "biceps": [
        {"name": "Barbell Curl",       "equipment": "barbell", "type": "isolation"},
        {"name": "Dumbbell Curl",      "equipment": "dumbbells", "type": "isolation"},
        {"name": "Hammer Curl",        "equipment": "dumbbells", "type": "isolation"},
        {"name": "Cable Curl",         "equipment": "cable_machine", "type": "isolation"},
    ],
    "triceps": [
        {"name": "Close-Grip Bench Press", "equipment": "barbell", "type": "compound"},
        {"name": "Skull Crusher",          "equipment": "barbell", "type": "isolation"},
        {"name": "Tricep Dip",             "equipment": "bodyweight", "type": "compound"},
        {"name": "Cable Pushdown",         "equipment": "cable_machine", "type": "isolation"},
        {"name": "Overhead Tricep Ext.",   "equipment": "dumbbells", "type": "isolation"},
    ],
    "core": [
        {"name": "Plank",            "equipment": "bodyweight", "type": "isometric"},
        {"name": "Crunch",           "equipment": "bodyweight", "type": "isolation"},
        {"name": "Leg Raise",        "equipment": "bodyweight", "type": "isolation"},
        {"name": "Russian Twist",    "equipment": "bodyweight", "type": "isolation"},
        {"name": "Ab Rollout",       "equipment": "bodyweight", "type": "compound"},
    ],
    "full_body": [
        {"name": "Barbell Squat",    "equipment": "barbell",    "type": "compound"},
        {"name": "Deadlift",         "equipment": "barbell",    "type": "compound"},
        {"name": "Bench Press",      "equipment": "barbell",    "type": "compound"},
        {"name": "Overhead Press",   "equipment": "barbell",    "type": "compound"},
        {"name": "Barbell Row",      "equipment": "barbell",    "type": "compound"},
        {"name": "Pull-Up",          "equipment": "pull_up_bar","type": "compound"},
    ],
}

# rep scheme templates by goal
_REP_SCHEMES: dict[str, dict] = {
    "muscle_gain":    {"sets": 4, "reps": "8-12", "rest_s": 90},
    "strength":       {"sets": 5, "reps": "3-6",  "rest_s": 180},
    "endurance":      {"sets": 3, "reps": "15-20", "rest_s": 45},
    "weight_loss":    {"sets": 3, "reps": "12-15", "rest_s": 60},
    "general_fitness":{"sets": 3, "reps": "10-12", "rest_s": 75},
    "default":        {"sets": 3, "reps": "10-12", "rest_s": 75},
}


# ── Intent Parsers ─────────────────────────────────────────────────────────────

def _detect_muscle_group(message: str) -> str:
    """Detect target muscle group from the user's message."""
    msg_lower = message.lower()
    group_keywords = {
        "chest":    ["chest", "pec", "bench", "push"],
        "back":     ["back", "lat", "row", "pull", "deadlift"],
        "shoulders":["shoulder", "delt", "overhead", "press"],
        "legs":     ["leg", "quad", "hamstring", "glute", "squat", "lunge", "calf"],
        "biceps":   ["bicep", "curl", "arm"],
        "triceps":  ["tricep", "skull", "dip"],
        "core":     ["core", "abs", "abdominal", "plank"],
        "full_body":["full body", "full-body", "compound", "total body"],
    }
    for group, keywords in group_keywords.items():
        if any(kw in msg_lower for kw in keywords):
            return group
    return "full_body"


def _detect_goal(message: str) -> str:
    """Detect workout goal from user message."""
    msg_lower = message.lower()
    goal_keywords = {
        "muscle_gain":    ["muscle", "bulk", "hypertrophy", "gain mass", "build"],
        "strength":       ["strength", "strong", "powerlifting", "1rm", "max"],
        "weight_loss":    ["fat loss", "weight loss", "cut", "lean", "shred", "burn"],
        "endurance":      ["endurance", "cardio", "stamina", "conditioning"],
        "general_fitness":["fit", "general", "healthy", "active"],
    }
    for goal, keywords in goal_keywords.items():
        if any(kw in msg_lower for kw in keywords):
            return goal
    return DEFAULT_GOAL


def _detect_fitness_level(message: str) -> str:
    """Detect fitness level from user message."""
    msg_lower = message.lower()
    if any(kw in msg_lower for kw in ["beginner", "new to", "just started", "novice"]):
        return "beginner"
    if any(kw in msg_lower for kw in ["intermediate", "6 month", "1 year", "some experience"]):
        return "intermediate"
    if any(kw in msg_lower for kw in ["advanced", "experienced", "years", "competitive"]):
        return "advanced"
    return DEFAULT_FITNESS_LEVEL


def _build_workout_plan(muscle_group: str, goal: str, fitness_level: str) -> dict:
    """Build a structured workout plan dict for the given parameters."""
    exercises_pool = _EXERCISE_LIBRARY.get(muscle_group, _EXERCISE_LIBRARY["full_body"])
    scheme = _REP_SCHEMES.get(goal, _REP_SCHEMES["default"])

    # Number of exercises based on fitness level
    exercise_count = {"beginner": 4, "intermediate": 5, "advanced": 6}.get(fitness_level, 5)
    selected = random.sample(exercises_pool, min(exercise_count, len(exercises_pool)))

    # Adjust sets for level
    sets = scheme["sets"] + (1 if fitness_level == "advanced" else 0)
    sets = max(2, sets - 1) if fitness_level == "beginner" else sets

    exercises = []
    for ex in selected:
        is_compound = ex["type"] == "compound"
        rest = scheme["rest_s"] + (30 if is_compound else 0)
        exercises.append({
            "name":         ex["name"],
            "equipment":    ex["equipment"],
            "type":         ex["type"],
            "sets":         sets,
            "reps":         scheme["reps"],
            "rest_seconds": rest,
            "muscle_group": muscle_group,
        })

    # Estimate duration: ~4 min per exercise (sets + rest)
    estimated_min = len(exercises) * (sets * 0.75 + scheme["rest_s"] / 60 * sets)

    return {
        "widget_type":           "workout_plan",
        "title":                 f"{muscle_group.replace('_', ' ').title()} Day — {goal.replace('_', ' ').title()} Focus",
        "goal":                  goal,
        "fitness_level":         fitness_level,
        "muscle_group":          muscle_group,
        "exercises":             exercises,
        "total_exercises":       len(exercises),
        "estimated_duration_min": round(estimated_min),
        "rep_scheme_note":       f"{sets} sets × {scheme['reps']} reps | {scheme['rest_s']}s rest",
        "generated_at":          datetime.now().strftime("%Y-%m-%d"),
    }


# ── Node ───────────────────────────────────────────────────────────────────────

async def workout_node(state: AgentState) -> dict:
    """
    Generate a personalized workout plan and emit a WorkoutPlanWidget SDUI payload.

    Tokens from this node ARE streamed to the client.
    The widget_json is captured from the final graph state after streaming completes.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    muscle_group  = _detect_muscle_group(last_message)
    goal          = _detect_goal(last_message)
    fitness_level = _detect_fitness_level(last_message)

    widget_data = _build_workout_plan(muscle_group, goal, fitness_level)

    all_messages = state.get("messages", [])
    analysis_prompt = build_atlas_workout_prompt(widget_data, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
