from __future__ import annotations

import json
import uuid
from typing import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage

from app.core.deps import get_agent_graph, get_current_user
from app.core.utils import extract_text
from app.database import get_db_connection
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Nodes whose LLM tokens should be forwarded to the client as SSE "token" events.
# The llm_decision node's internal routing tokens are intentionally suppressed.
_STREAMING_NODES = {"api_call", "summary", "general"}


def _normalize_uuid(val: str) -> str:
    """
    Ensure the string is a valid UUID format for PostgreSQL.
    If a custom string is passed, converts it deterministically via UUID5.
    """
    try:
        return str(uuid.UUID(val))
    except ValueError:
        return str(uuid.uuid5(uuid.NAMESPACE_DNS, val))


# ── Database helpers ──────────────────────────────────────────────────────────

async def _upsert_session(
    conn,
    session_id: str,
    user_id: str,
    first_message: str,
) -> None:
    """Create the session row if it doesn't exist; otherwise bump updated_at."""
    existing = await conn.fetchrow(
        "SELECT id FROM chat_sessions WHERE id = $1 AND user_id = $2",
        session_id, user_id,
    )
    if not existing:
        title = (first_message[:57] + "...") if len(first_message) > 60 else first_message
        await conn.execute(
            "INSERT INTO chat_sessions (id, user_id, title) VALUES ($1, $2, $3)",
            session_id, user_id, title,
        )
    else:
        await conn.execute(
            "UPDATE chat_sessions SET updated_at = NOW() WHERE id = $1",
            session_id,
        )


async def _save_turn(
    session_id: str,
    user_id: str,
    human_text: str,
    assistant_text: str,
    widget_json: dict | None,
) -> None:
    """Persist both the human message and the assistant response to the DB."""
    safe_session_id = _normalize_uuid(session_id)
    safe_user_id = _normalize_uuid(user_id)

    async with get_db_connection() as conn:
        await _upsert_session(conn, safe_session_id, safe_user_id, human_text)
        await conn.executemany(
            "INSERT INTO chat_messages (id, session_id, role, content, widget_json) VALUES ($1, $2, $3, $4, $5)",
            [
                (str(uuid.uuid4()), safe_session_id, "human",     human_text,     None),
                (str(uuid.uuid4()), safe_session_id, "assistant", assistant_text,
                 json.dumps(widget_json) if widget_json else None),
            ],
        )


# ── SSE generator ─────────────────────────────────────────────────────────────

async def _stream_agent(
    message: str,
    session_id: str,
    user_id: str,
    graph,
) -> AsyncGenerator[str, None]:
    """
    Async generator that:
      1. Runs the LangGraph agent via `astream_events`
      2. Yields `token` SSE events for each LLM chunk (from response nodes only)
      3. After the stream ends, retrieves the final state to emit the `widget` event
      4. Persists the turn to PostgreSQL
      5. Yields the `done` event
    """
    config = {"configurable": {"thread_id": session_id}}
    initial_state = {
        "messages":       [HumanMessage(content=message)],
        "session_id":     session_id,
        "user_id":        user_id,
        "intent":         "",
        "iteration_count": 0,
        "response_text":  "",
        "widget_json":    None,
        "is_final":       False,
    }

    try:
        async for event in graph.astream_events(initial_state, config=config, version="v2"):
            event_type = event.get("event", "")
            node_name  = event.get("metadata", {}).get("langgraph_node", "")

            # Forward LLM token chunks only from response-generating nodes
            if event_type == "on_chat_model_stream" and node_name in _STREAMING_NODES:
                chunk = event["data"].get("chunk")
                if chunk and getattr(chunk, "content", None):
                    text_content = extract_text(chunk.content)
                    if text_content:
                        payload = json.dumps({"type": "token", "content": text_content})
                        yield f"event: token\ndata: {payload}\n\n"

        # ── Post-stream: read final state ─────────────────────────────────────
        final_state  = await graph.aget_state(config)
        values       = final_state.values if final_state else {}
        widget_json  = values.get("widget_json")
        response_text = extract_text(values.get("response_text", ""))

        # Emit widget event if the agent produced one
        if widget_json:
            payload = json.dumps({"type": "widget", "widget_json": widget_json})
            yield f"event: widget\ndata: {payload}\n\n"

        # Persist both messages to the DB
        await _save_turn(session_id, user_id, message, response_text, widget_json)

        # Signal stream completion
        done_payload = json.dumps({"type": "done", "session_id": session_id})
        yield f"event: done\ndata: {done_payload}\n\n"

    except Exception as exc:  # noqa: BLE001
        error_payload = json.dumps({"type": "error", "message": str(exc)})
        yield f"event: error\ndata: {error_payload}\n\n"


# ── Route ─────────────────────────────────────────────────────────────────────

@router.post(
    "/stream",
    summary="Stream a chat response via Server-Sent Events",
    response_description="text/event-stream — see SSE event types in schema",
)
async def chat_stream(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    graph=Depends(get_agent_graph),
) -> StreamingResponse:
    """
    Start a streaming AI chat session.

    **SSE Event Types:**
    - `token`  — A text chunk from the LLM (stream as you type)
    - `widget` — A structured SDUI payload for dynamic UI rendering
    - `done`   — Stream has completed; `session_id` is included
    - `error`  — An error occurred during agent execution

    **Authentication:** `Authorization: Bearer <access_token>`
    """
    return StreamingResponse(
        _stream_agent(body.message, body.session_id, current_user["user_id"], graph),
        media_type="text/event-stream",
        headers={
            "Cache-Control":    "no-cache",
            "X-Accel-Buffering": "no",   # Disable Nginx buffering
            "Connection":       "keep-alive",
        },
    )
