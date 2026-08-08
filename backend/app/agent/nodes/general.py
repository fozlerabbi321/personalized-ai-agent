from __future__ import annotations

from langchain_core.messages import AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.agent.state import AgentState

_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.7,
)

_SYSTEM_PROMPT = """\
You are Aria — a helpful, knowledgeable, and friendly AI assistant.
You provide clear, accurate, and thoughtful responses.

Guidelines:
- Be concise but thorough. Avoid unnecessary padding.
- Use markdown formatting (code blocks, bullet points, bold) when it helps clarity.
- If a user asks about stock prices or financial data, let them know you can fetch that
  information — they just need to mention a ticker symbol (e.g., "AAPL stock price").
- Be warm and approachable in tone.\
"""


async def general_response_node(state: AgentState) -> dict:
    """
    Handle general queries with a direct Gemini response.
    Tokens from this node ARE streamed to the client.
    The full conversation history is passed to maintain context.
    """
    # Prepend system message to the full conversation history
    messages = [SystemMessage(content=_SYSTEM_PROMPT)] + list(state.get("messages", []))

    response = await _llm.ainvoke(messages)
    response_text = response.content.strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   None,
        "is_final":      True,
    }
