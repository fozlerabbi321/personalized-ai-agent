from __future__ import annotations

"""Chat router — thin SSE streaming interface delegating to StreamChatUseCase."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.application.chat.stream_chat import StreamChatUseCase
from app.core.container import get_stream_chat_use_case
from app.core.deps import get_agent_graph, get_current_user
from app.schemas.chat import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post(
    "/stream",
    summary="Stream a chat response via Server-Sent Events",
    response_description="text/event-stream — see SSE event types in schema",
)
async def chat_stream(
    body: ChatRequest,
    current_user: dict = Depends(get_current_user),
    graph=Depends(get_agent_graph),
    use_case: StreamChatUseCase = Depends(get_stream_chat_use_case),
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
        use_case.execute(
            message=body.message,
            session_id=body.session_id,
            user_id=current_user["user_id"],
            graph=graph,
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control":     "no-cache",
            "X-Accel-Buffering": "no",    # Disable Nginx buffering
            "Connection":        "keep-alive",
        },
    )
