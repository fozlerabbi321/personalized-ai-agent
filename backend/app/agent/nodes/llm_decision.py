from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.agent.state import AgentState
from app.agent.prompts import build_athena_router_prompt
from app.core.utils import extract_text

# Shared LLM instance — temperature=0 for deterministic routing
_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
)


async def llm_decision_node(state: AgentState) -> dict:
    """
    Classify the user's intent and set `state.intent`.
    This node's LLM tokens are intentionally NOT streamed to the client
    (filtered by langgraph_node metadata in the SSE endpoint).
    """
    messages = state.get("messages", [])
    last_msg = messages[-1] if messages else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    router_prompt = build_athena_router_prompt(messages)

    response = await _llm.ainvoke([
        SystemMessage(content=router_prompt),
        HumanMessage(content=f"User message: {last_message}"),
    ])

    raw_text = extract_text(response.content)
    raw = raw_text.strip().lower().strip('"').strip("'")
    intent = raw if raw in ("api_call", "summary", "general") else "general"

    return {
        "intent": intent,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }

