from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.prompts import build_atlas_summary_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_FOCUSED, get_llm


async def summary_node(state: AgentState) -> dict:
    """
    Summarize the full fitness conversation history using Gemini as Atlas.
    Tokens from this node ARE streamed to the client.
    """
    messages = state.get("messages", [])

    # Format all messages except the current summary request
    conversation_parts: list[str] = []
    for msg in messages[:-1]:
        role = "User" if isinstance(msg, HumanMessage) else "Atlas"
        part_text = extract_text(msg.content)
        conversation_parts.append(f"{role}: {part_text}")

    if not conversation_parts:
        response_text = (
            "There's no previous conversation to summarize yet. "
            "Start chatting with me and I'll keep track of your fitness journey!"
        )
    else:
        conversation_text = "\n\n".join(conversation_parts)
        summary_prompt = build_atlas_summary_prompt(messages)
        llm = get_llm(TEMPERATURE_FOCUSED)
        response = await llm.ainvoke([
            SystemMessage(content=summary_prompt),
            HumanMessage(content=f"Conversation to summarize:\n\n{conversation_text}"),
        ])
        response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   None,
        "is_final":      True,
    }
