from __future__ import annotations

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph

from app.agent.state import AgentState
from app.agent.constants import Intent
from app.agent.nodes.llm_decision import llm_decision_node
from app.agent.nodes.interview import interview_node
from app.agent.nodes.resume import resume_node
from app.agent.nodes.roadmap import roadmap_node
from app.agent.nodes.summary import summary_node
from app.agent.nodes.general import general_response_node


def _route_intent(state: AgentState) -> str:
    """
    Conditional edge: map `state.intent` → node name.
    Falls back to 'general' for any unrecognised intent value.
    """
    intent = state.get("intent", Intent.GENERAL)
    if intent == Intent.INTERVIEW:
        return "interview"
    elif intent == Intent.RESUME:
        return "resume"
    elif intent == Intent.ROADMAP:
        return "roadmap"
    elif intent == Intent.SUMMARY:
        return "summary"
    else:
        return "general"


def build_graph(checkpointer: BaseCheckpointSaver):
    """
    Build and compile the Kairo AI agent StateGraph.

    Graph topology:
        START
          └─► llm_decision  (Gemini classifies career intent)
                  ├─► interview ─► END  (interview practice + InterviewWidget)
                  ├─► resume    ─► END  (resume review + ResumeWidget)
                  ├─► roadmap   ─► END  (career roadmap + CareerRoadmapWidget)
                  ├─► summary   ─► END  (conversation recap)
                  └─► general   ─► END  (general career Q&A)
    """
    builder = StateGraph(AgentState)

    builder.add_node("llm_decision", llm_decision_node)
    builder.add_node("interview",    interview_node)
    builder.add_node("resume",       resume_node)
    builder.add_node("roadmap",      roadmap_node)
    builder.add_node("summary",      summary_node)
    builder.add_node("general",      general_response_node)

    builder.set_entry_point("llm_decision")

    builder.add_conditional_edges(
        "llm_decision",
        _route_intent,
        {
            "interview": "interview",
            "resume":    "resume",
            "roadmap":   "roadmap",
            "summary":   "summary",
            "general":   "general",
        },
    )

    builder.add_edge("interview", END)
    builder.add_edge("resume",    END)
    builder.add_edge("roadmap",   END)
    builder.add_edge("summary",   END)
    builder.add_edge("general",   END)

    return builder.compile(checkpointer=checkpointer)
