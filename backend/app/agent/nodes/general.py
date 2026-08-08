from __future__ import annotations

from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.agent.state import AgentState
from app.agent.prompts import build_athena_system_prompt
from app.core.utils import extract_text

_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.7,
)


async def general_response_node(state: AgentState) -> dict:
    """
    Handle general queries with a direct Gemini response as Athena.
    Tokens from this node ARE streamed to the client.
    Athena's persona, dynamic tone rules, and chat history preferences are injected.
    """
    raw_messages = list(state.get("messages", []))
    system_prompt = build_athena_system_prompt(raw_messages)

    messages = [SystemMessage(content=system_prompt)] + raw_messages

    response = await _llm.ainvoke(messages)
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   None,
        "is_final":      True,
    }

