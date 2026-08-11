from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.constants import Intent
from app.agent.nodes.llm_decision import llm_decision_node
from app.agent.nodes.workout import workout_node
from app.agent.nodes.nutrition import nutrition_node
from app.agent.nodes.progress import progress_node
from app.agent.nodes.summary import summary_node
from app.agent.nodes.general import general_response_node


def _route_intent(state: AgentState) -> str:
    """
    Conditional edge: map `state.intent` → node name.
    Falls back to 'general' for any unrecognised intent value.
    """
    match state.get("intent", Intent.GENERAL):
        case Intent.WORKOUT:
            return "workout"
        case Intent.NUTRITION:
            return "nutrition"
        case Intent.PROGRESS:
            return "progress"
        case Intent.SUMMARY:
            return "summary"
        case _:
            return "general"


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    Build and compile the Atlas AI agent StateGraph.

    Graph topology:
        START
          └─► llm_decision  (Gemini classifies fitness intent)
                  ├─► workout   ─► END  (workout plan + WorkoutPlanWidget)
                  ├─► nutrition ─► END  (macro calc + MacroDonutChart)
                  ├─► progress  ─► END  (PR chart + ProgressLineChart)
                  ├─► summary   ─► END  (conversation recap)
                  └─► general   ─► END  (general fitness Q&A)

    The checkpointer (PostgresSaver) provides persistent memory across
    sessions via the `thread_id` config key.
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("llm_decision", llm_decision_node)
    builder.add_node("workout",      workout_node)
    builder.add_node("nutrition",    nutrition_node)
    builder.add_node("progress",     progress_node)
    builder.add_node("summary",      summary_node)
    builder.add_node("general",      general_response_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    builder.set_entry_point("llm_decision")

    # ── Conditional routing ───────────────────────────────────────────────────
    builder.add_conditional_edges(
        "llm_decision",
        _route_intent,
        {
            "workout":   "workout",
            "nutrition": "nutrition",
            "progress":  "progress",
            "summary":   "summary",
            "general":   "general",
        },
    )

    # ── All response nodes terminate the graph ────────────────────────────────
    builder.add_edge("workout",   END)
    builder.add_edge("nutrition", END)
    builder.add_edge("progress",  END)
    builder.add_edge("summary",   END)
    builder.add_edge("general",   END)

    return builder.compile(checkpointer=checkpointer)
