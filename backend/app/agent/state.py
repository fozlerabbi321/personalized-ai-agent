from __future__ import annotations

from typing import Annotated

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """
    The shared state object that flows through every LangGraph node.

    - `messages`       : Full conversation history. LangGraph's `add_messages`
                         reducer appends new messages instead of overwriting.
    - `session_id`     : Maps to the PostgresSaver thread_id (persistent memory).
    - `user_id`        : Extracted from the validated JWT token.
    - `intent`         : Set by `llm_decision_node` to route execution.
    - `iteration_count`: Guards against runaway loops (incremented each cycle).
    - `response_text`  : The final assistant text (saved to DB after stream ends).
    - `widget_json`    : Structured SDUI payload emitted as a `widget` SSE event.
    - `is_final`       : True once a response node has produced its output.
    """

    messages: Annotated[list[BaseMessage], add_messages]

    # Request context (passed in by the API endpoint)
    session_id: str
    user_id: str

    # Routing
    intent: str           # "api_call" | "summary" | "general"
    iteration_count: int

    # Output payload
    response_text: str
    widget_json: dict | None
    is_final: bool
