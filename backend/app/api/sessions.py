from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps import get_current_user
from app.database import get_db_connection
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
) -> SessionListResponse:
    """Return all chat sessions belonging to the authenticated user, newest first."""
    async with get_db_connection() as conn:
        rows = await conn.fetch(
            """
            SELECT
                s.id,
                s.title,
                s.created_at,
                s.updated_at,
                COUNT(m.id)::int AS message_count
            FROM chat_sessions s
            LEFT JOIN chat_messages m ON m.session_id = s.id
            WHERE s.user_id = $1
            GROUP BY s.id
            ORDER BY s.updated_at DESC
            """,
            current_user["user_id"],
        )

    sessions = [
        SessionResponse(
            session_id=str(r["id"]),
            title=r["title"],
            created_at=r["created_at"],
            updated_at=r["updated_at"],
            message_count=r["message_count"],
        )
        for r in rows
    ]
    return SessionListResponse(sessions=sessions, total=len(sessions))


@router.get(
    "/{session_id}/messages",
    response_model=SessionMessagesResponse,
    summary="Get all messages in a session",
)
async def get_session_messages(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> SessionMessagesResponse:
    """Return chronologically ordered messages for a specific session (must be owned by caller)."""
    async with get_db_connection() as conn:
        # Verify ownership
        session = await conn.fetchrow(
            "SELECT id FROM chat_sessions WHERE id = $1 AND user_id = $2",
            session_id, current_user["user_id"],
        )
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        rows = await conn.fetch(
            """
            SELECT id, role, content, widget_json, created_at
            FROM chat_messages
            WHERE session_id = $1
            ORDER BY created_at ASC
            """,
            session_id,
        )

    messages = []
    for r in rows:
        wj = r["widget_json"]
        if wj and isinstance(wj, str):
            try:
                wj = json.loads(wj)
            except (json.JSONDecodeError, TypeError):
                wj = None

        messages.append(
            MessageResponse(
                message_id=str(r["id"]),
                role=r["role"],
                content=r["content"],
                widget_json=wj,
                created_at=r["created_at"],
            )
        )
    return SessionMessagesResponse(session_id=session_id, messages=messages)


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session and all its messages",
)
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
) -> None:
    """
    Hard-delete a chat session. All messages are removed via cascade.
    Only the session owner can delete it.
    """
    async with get_db_connection() as conn:
        result = await conn.execute(
            "DELETE FROM chat_sessions WHERE id = $1 AND user_id = $2",
            session_id, current_user["user_id"],
        )
    if result == "DELETE 0":
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
