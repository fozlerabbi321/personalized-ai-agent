from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.constants import Intent
from app.agent.nodes.llm_decision import llm_decision_node
from app.agent.nodes.recommend import recommend_node
from app.agent.nodes.review import review_node
from app.agent.nodes.challenge import challenge_node
from app.agent.nodes.summary import summary_node
from app.agent.nodes.general import general_response_node


def _route_intent(state: AgentState) -> str:
    """
    Conditional edge: map `state.intent` → node name.
    Falls back to 'general' for any unrecognised intent value.
    """
    intent = state.get("intent", Intent.GENERAL)
    if intent == Intent.RECOMMEND:
        return "recommend"
    elif intent == Intent.REVIEW:
        return "review"
    elif intent == Intent.CHALLENGE:
        return "challenge"
    elif intent == Intent.SUMMARY:
        return "summary"
    else:
        return "general"


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    Build and compile the Lumen AI agent StateGraph.

    Graph topology:
        START
          └─► llm_decision  (Gemini classifies literary intent)
                  ├─► recommend ─► END  (book recommendations + BookCard)
                  ├─► review    ─► END  (book review + BookReview)
                  ├─► challenge ─► END  (reading tracker + ReadingTracker)
                  ├─► summary   ─► END  (conversation recap)
                  └─► general   ─► END  (general literary Q&A)
    """
    builder = StateGraph(AgentState)

    builder.add_node("llm_decision", llm_decision_node)
    builder.add_node("recommend",    recommend_node)
    builder.add_node("review",       review_node)
    builder.add_node("challenge",    challenge_node)
    builder.add_node("summary",      summary_node)
    builder.add_node("general",      general_response_node)

    builder.set_entry_point("llm_decision")

    builder.add_conditional_edges(
        "llm_decision",
        _route_intent,
        {
            "recommend": "recommend",
            "review":    "review",
            "challenge": "challenge",
            "summary":   "summary",
            "general":   "general",
        },
    )

    builder.add_edge("recommend", END)
    builder.add_edge("review",    END)
    builder.add_edge("challenge", END)
    builder.add_edge("summary",   END)
    builder.add_edge("general",   END)

    return builder.compile(checkpointer=checkpointer)
