from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.constants import Intent
from app.agent.nodes.llm_decision import llm_decision_node
from app.agent.nodes.quiz import quiz_node
from app.agent.nodes.explain import explain_node
from app.agent.nodes.roadmap import roadmap_node
from app.agent.nodes.summary import summary_node
from app.agent.nodes.general import general_response_node


def _route_intent(state: AgentState) -> str:
    """
    Conditional edge: map `state.intent` → node name.
    Falls back to 'general' for any unrecognised intent value.
    """
    intent = state.get("intent", Intent.GENERAL)
    if intent == Intent.QUIZ:
        return "quiz"
    elif intent == Intent.EXPLAIN:
        return "explain"
    elif intent == Intent.ROADMAP:
        return "roadmap"
    elif intent == Intent.SUMMARY:
        return "summary"
    else:
        return "general"


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    Build and compile the Nova AI agent StateGraph.

    Graph topology:
        START
          └─► llm_decision  (Gemini classifies learning intent)
                  ├─► quiz    ─► END  (quiz question + QuizWidget)
                  ├─► explain ─► END  (concept breakdown + ConceptTable)
                  ├─► roadmap ─► END  (study plan + StudyRoadmapWidget)
                  ├─► summary ─► END  (session recap)
                  └─► general ─► END  (general learning Q&A)

    The checkpointer (PostgresSaver) provides persistent memory across
    sessions via the `thread_id` config key.
    """
    builder = StateGraph(AgentState)

    builder.add_node("llm_decision", llm_decision_node)
    builder.add_node("quiz",         quiz_node)
    builder.add_node("explain",      explain_node)
    builder.add_node("roadmap",      roadmap_node)
    builder.add_node("summary",      summary_node)
    builder.add_node("general",      general_response_node)

    builder.set_entry_point("llm_decision")

    builder.add_conditional_edges(
        "llm_decision",
        _route_intent,
        {
            "quiz":    "quiz",
            "explain": "explain",
            "roadmap": "roadmap",
            "summary": "summary",
            "general": "general",
        },
    )

    builder.add_edge("quiz",    END)
    builder.add_edge("explain", END)
    builder.add_edge("roadmap", END)
    builder.add_edge("summary", END)
    builder.add_edge("general", END)

    return builder.compile(checkpointer=checkpointer)
