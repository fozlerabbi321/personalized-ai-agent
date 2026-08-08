from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.nodes.llm_decision import llm_decision_node
from app.agent.nodes.api_call import api_call_node
from app.agent.nodes.summary import summary_node
from app.agent.nodes.general import general_response_node


def _route_intent(state: AgentState) -> str:
    """
    Conditional edge: map `state.intent` → node name.
    Falls back to 'general' for any unrecognised intent value.
    """
    match state.get("intent", "general"):
        case "api_call":
            return "api_call"
        case "summary":
            return "summary"
        case _:
            return "general"


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    Build and compile the personalized AI agent StateGraph.

    Graph topology:
        START
          └─► llm_decision  (Gemini classifies intent)
                  ├─► api_call  ─► END
                  ├─► summary   ─► END
                  └─► general   ─► END

    The checkpointer (PostgresSaver) provides persistent memory across
    sessions via the `thread_id` config key.
    """
    builder = StateGraph(AgentState)

    # ── Register nodes ────────────────────────────────────────────────────────
    builder.add_node("llm_decision", llm_decision_node)
    builder.add_node("api_call",     api_call_node)
    builder.add_node("summary",      summary_node)
    builder.add_node("general",      general_response_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    builder.set_entry_point("llm_decision")

    # ── Conditional routing ───────────────────────────────────────────────────
    builder.add_conditional_edges(
        "llm_decision",
        _route_intent,
        {
            "api_call": "api_call",
            "summary":  "summary",
            "general":  "general",
        },
    )

    # ── All response nodes terminate the graph ────────────────────────────────
    builder.add_edge("api_call", END)
    builder.add_edge("summary",  END)
    builder.add_edge("general",  END)

    return builder.compile(checkpointer=checkpointer)
