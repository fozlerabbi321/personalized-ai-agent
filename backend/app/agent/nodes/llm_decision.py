from __future__ import annotations

from langchain_core.messages import HumanMessage, SystemMessage

from app.agent.constants import Intent
from app.agent.prompts import build_lumen_router_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_DETERMINISTIC, get_llm


async def llm_decision_node(state: AgentState) -> dict:
    """
    Classify user literary intent and set `state.intent`.
    Tokens from this node are NOT streamed.
    """
    messages = state.get("messages", [])
    last_msg = messages[-1] if messages else None
    last_message = extract_text(last_msg.content) if last_msg else ""

    router_prompt = build_lumen_router_prompt(messages)

    llm = get_llm(TEMPERATURE_DETERMINISTIC)
    response = await llm.ainvoke([
        SystemMessage(content=router_prompt),
        HumanMessage(content=f"User message: {last_message}"),
    ])

    raw_text = extract_text(response.content)
    raw = raw_text.strip().lower().strip('"').strip("'")
    intent = raw if raw in Intent.ALL else Intent.GENERAL

    return {
        "intent": intent,
        "iteration_count": state.get("iteration_count", 0) + 1,
    }
