from __future__ import annotations

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import settings
from app.agent.state import AgentState

# Shared LLM instance — temperature=0 for deterministic routing
_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0,
)

_ROUTER_SYSTEM = """\
You are an intent classifier for an AI assistant. Analyze the user's message and return EXACTLY one word.

Classify as:
- "api_call"  → user asks about stock prices, crypto prices, financial data, OHLC charts, market data, or any real-time financial metric
- "summary"   → user explicitly asks to summarize, recap, or review the conversation
- "general"   → everything else: coding help, questions, explanations, general conversation

Rules:
• Return ONLY one of the three exact lowercase words above.
• No punctuation, no explanation, no surrounding quotes.\
"""


async def llm_decision_node(state: AgentState) -> dict:
    """
    Classify the user's intent and set `state.intent`.
    This node's LLM tokens are intentionally NOT streamed to the client
    (filtered by langgraph_node metadata in the SSE endpoint).
    """
    last_message = state["messages"][-1].content if state["messages"] else ""

    response = await _llm.ainvoke([
        SystemMessage(content=_ROUTER_SYSTEM),
        HumanMessage(content=f"User message: {last_message}"),
    ])

    raw = response.content.strip().lower().strip('"').strip("'")
    intent = raw if raw in ("api_call", "summary", "general") else "general"

    return {
        "intent": intent,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }
