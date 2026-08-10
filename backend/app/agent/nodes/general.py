from __future__ import annotations

from langchain_core.messages import AIMessage, SystemMessage

from app.agent.prompts import build_athena_system_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_BALANCED, get_llm


async def general_response_node(state: AgentState) -> dict:
    """
    Handle general queries with a direct Gemini response as Athena.
    Tokens from this node ARE streamed to the client.
    Athena's persona, dynamic tone rules, and chat history preferences are injected.
    """
    raw_messages = list(state.get("messages", []))
    system_prompt = build_athena_system_prompt(raw_messages)

    messages = [SystemMessage(content=system_prompt)] + raw_messages

    llm = get_llm(TEMPERATURE_BALANCED)
    response = await llm.ainvoke(messages)
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   None,
        "is_final":      True,
    }

