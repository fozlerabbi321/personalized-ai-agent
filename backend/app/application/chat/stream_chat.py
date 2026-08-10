from __future__ import annotations

"""
StreamChatUseCase — orchestrates the SSE streaming chat flow.

This use case owns the entire lifecycle of a chat request:
  1. Normalize session/user UUIDs
  2. Run the LangGraph agent via astream_events
  3. Yield SSE-formatted token/widget/done/error events to the caller
  4. Persist the completed conversation turn to the DB
  5. Signal stream completion

The FastAPI router receives the async generator and wraps it in StreamingResponse.
This class has NO FastAPI imports — it is purely a generator factory.
"""

import json
import uuid
from typing import AsyncGenerator, Any

from langchain_core.messages import HumanMessage

from app.agent.constants import STREAMING_NODES
from app.core.utils import extract_text, normalize_uuid
from app.domain.repositories.session_repository import SessionRepository


class StreamChatUseCase:
    """Produce an SSE event stream for a chat message using the LangGraph agent."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self._repo = session_repo

    def execute(
        self,
        message: str,
        session_id: str,
        user_id: str,
        graph: Any,
    ) -> AsyncGenerator[str, None]:
        """
        Return an async generator that yields raw SSE-formatted lines.

        The generator:
          - Yields ``event: token\\ndata: ...`` for each LLM text chunk
          - Yields ``event: widget\\ndata: ...`` if a SDUI widget was produced
          - Yields ``event: done\\ndata: ...`` when the stream completes
          - Yields ``event: error\\ndata: ...`` on any exception

        Args:
            message:    The user's message text.
            session_id: UUID string for the chat thread.
            user_id:    UUID string of the authenticated user.
            graph:      The compiled LangGraph CompiledGraph instance.
        """
        return self._stream(message, session_id, user_id, graph)

    async def _stream(
        self,
        message: str,
        session_id: str,
        user_id: str,
        graph: Any,
    ) -> AsyncGenerator[str, None]:
        safe_session_id = normalize_uuid(session_id)
        safe_user_id    = normalize_uuid(user_id)

        config = {"configurable": {"thread_id": safe_session_id}}
        initial_state = {
            "messages":        [HumanMessage(content=message)],
            "session_id":      safe_session_id,
            "user_id":         safe_user_id,
            "intent":          "",
            "iteration_count": 0,
            "response_text":   "",
            "widget_json":     None,
            "is_final":        False,
        }

        try:
            async for event in graph.astream_events(initial_state, config=config, version="v2"):
                event_type = event.get("event", "")
                node_name  = event.get("metadata", {}).get("langgraph_node", "")

                # Forward LLM token chunks only from response-generating nodes
                if event_type == "on_chat_model_stream" and node_name in STREAMING_NODES:
                    chunk = event["data"].get("chunk")
                    if chunk and getattr(chunk, "content", None):
                        text_content = extract_text(chunk.content)
                        if text_content:
                            payload = json.dumps({"type": "token", "content": text_content})
                            yield f"event: token\ndata: {payload}\n\n"

            # ── Post-stream: read final graph state ───────────────────────────
            final_state   = await graph.aget_state(config)
            values        = final_state.values if final_state else {}
            widget_json   = values.get("widget_json")
            response_text = extract_text(values.get("response_text", ""))

            # Emit widget event if the agent produced one
            if widget_json:
                payload = json.dumps({"type": "widget", "widget_json": widget_json})
                yield f"event: widget\ndata: {payload}\n\n"

            # Persist the conversation turn to the DB
            title = (message[:57] + "...") if len(message) > 60 else message
            await self._repo.upsert(safe_session_id, safe_user_id, title)
            await self._repo.save_turn(safe_session_id, message, response_text, widget_json)

            # Signal stream completion
            done_payload = json.dumps({"type": "done", "session_id": safe_session_id})
            yield f"event: done\ndata: {done_payload}\n\n"

        except Exception as exc:  # noqa: BLE001
            error_payload = json.dumps({"type": "error", "message": str(exc)})
            yield f"event: error\ndata: {error_payload}\n\n"
