from __future__ import annotations

"""
Agent constants — centralized configuration for the Atlas AI LangGraph agent.

Domain: Fitness Coach & Nutrition Advisor (Atlas AI)
Previously: Bitcoin/Crypto Expert (Athena AI)

Centralizing here ensures a single source of truth and makes it trivial
to add new exercises, muscle groups, equipment types, or streaming nodes.
"""

# ── SSE Streaming ─────────────────────────────────────────────────────────────

# Nodes whose LLM output tokens are forwarded to the client as SSE "token" events.
# The llm_decision node is intentionally excluded — its routing tokens are internal.
STREAMING_NODES: frozenset[str] = frozenset({
    "workout", "nutrition", "progress", "summary", "general"
})


# ── Intent Values ─────────────────────────────────────────────────────────────

class Intent:
    """Valid intent values set by the llm_decision_node."""
    WORKOUT   = "workout"
    NUTRITION = "nutrition"
    PROGRESS  = "progress"
    SUMMARY   = "summary"
    GENERAL   = "general"

    ALL: frozenset[str] = frozenset({WORKOUT, NUTRITION, PROGRESS, SUMMARY, GENERAL})


# ── Fitness Domain Constants ───────────────────────────────────────────────────

KNOWN_MUSCLE_GROUPS: list[str] = [
    "chest", "back", "shoulders", "biceps", "triceps",
    "quads", "hamstrings", "glutes", "calves", "core", "forearms",
]

KNOWN_EXERCISES: list[str] = [
    "bench_press", "incline_press", "chest_fly",
    "squat", "leg_press", "leg_extension", "leg_curl",
    "deadlift", "rdl", "good_morning",
    "overhead_press", "lateral_raise", "front_raise",
    "barbell_row", "cable_row", "lat_pulldown",
    "pull_up", "chin_up",
    "bicep_curl", "hammer_curl",
    "tricep_dip", "skull_crusher", "tricep_pushdown",
    "hip_thrust", "glute_bridge",
    "lunge", "bulgarian_split_squat", "step_up",
    "plank", "crunch", "leg_raise", "russian_twist",
    "calf_raise", "face_pull", "shrug",
]

EQUIPMENT_TYPES: list[str] = [
    "barbell", "dumbbells", "kettlebell", "resistance_bands",
    "cable_machine", "smith_machine", "pull_up_bar", "dip_bar",
    "bench", "squat_rack", "leg_press_machine", "bodyweight",
]

FITNESS_GOALS: list[str] = [
    "weight_loss", "muscle_gain", "strength", "endurance",
    "flexibility", "general_fitness", "athletic_performance",
]

FITNESS_LEVELS: list[str] = ["beginner", "intermediate", "advanced", "elite"]

ACTIVITY_LEVELS: list[str] = [
    "sedentary",          # little or no exercise
    "lightly_active",     # 1-3 days/week
    "moderately_active",  # 3-5 days/week
    "very_active",        # 6-7 days/week
    "extra_active",       # physical job + training
]

# Macronutrient ratio templates per goal
MACRO_TEMPLATES: dict[str, dict[str, float]] = {
    "muscle_gain":    {"protein_pct": 0.30, "carbs_pct": 0.45, "fat_pct": 0.25},
    "weight_loss":    {"protein_pct": 0.35, "carbs_pct": 0.35, "fat_pct": 0.30},
    "strength":       {"protein_pct": 0.30, "carbs_pct": 0.45, "fat_pct": 0.25},
    "endurance":      {"protein_pct": 0.20, "carbs_pct": 0.55, "fat_pct": 0.25},
    "general_fitness":{"protein_pct": 0.25, "carbs_pct": 0.45, "fat_pct": 0.30},
}

DEFAULT_GOAL          = "general_fitness"
DEFAULT_FITNESS_LEVEL = "beginner"
DEFAULT_ACTIVITY      = "moderately_active"
