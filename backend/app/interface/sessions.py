from __future__ import annotations

"""Sessions router — thin CRUD interface delegating to session use cases."""

from fastapi import APIRouter, Depends, status

from app.application.chat.delete_session import DeleteSessionUseCase
from app.application.chat.get_messages import GetSessionMessagesUseCase
from app.application.chat.list_sessions import ListSessionsUseCase
from app.core.container import (
    get_delete_session_use_case,
    get_list_sessions_use_case,
    get_session_messages_use_case,
)
from app.core.deps import get_current_user
from app.schemas.session import (
    MessageResponse,
    SessionListResponse,
    SessionMessagesResponse,
    SessionResponse,
)

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get(
    "",
    response_model=SessionListResponse,
    summary="List all sessions for the current user",
)
async def list_sessions(
    current_user: dict = Depends(get_current_user),
    use_case: ListSessionsUseCase = Depends(get_list_sessions_use_case),
) -> SessionListResponse:
    """Return all chat sessions belonging to the authenticated user, newest first."""
    sessions = await use_case.execute(current_user["user_id"])
    session_responses = [
        SessionResponse(
            session_id=s.id,
            title=s.title,
            created_at=s.created_at,
            updated_at=s.updated_at,
            message_count=s.message_count,
        )
        for s in sessions
    ]
    return SessionListResponse(sessions=session_responses, total=len(session_responses))


@router.get(
    "/{session_id}/messages",
    response_model=SessionMessagesResponse,
    summary="Get all messages in a session",
)
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    use_case: GetSessionMessagesUseCase = Depends(get_session_messages_use_case),
) -> SessionMessagesResponse:
    """Return chronologically ordered messages for a specific session (must be owned by caller)."""
    messages = await use_case.execute(session_id, current_user["user_id"])
    message_responses = [
        MessageResponse(
            message_id=m.id,
            role=m.role,
            content=m.content,
            widget_json=m.widget_json,
            created_at=m.created_at,
        )
        for m in messages
    ]
    return SessionMessagesResponse(session_id=session_id, messages=message_responses)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session and all its messages",
)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
    use_case: DeleteSessionUseCase = Depends(get_delete_session_use_case),
) -> None:
    """Hard-delete a chat session. All messages are removed via cascade. Owner-only."""
    await use_case.execute(session_id, current_user["user_id"])
