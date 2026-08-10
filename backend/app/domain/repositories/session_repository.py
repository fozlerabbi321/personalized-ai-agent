from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.domain.entities.message import ChatMessage
from app.domain.entities.session import ChatSession


@runtime_checkable
class SessionRepository(Protocol):
    """
    Abstract contract for session and message persistence operations.

    Handles chat_sessions and chat_messages tables as a cohesive aggregate.
    The Application layer depends ONLY on this Protocol.
    """

    async def upsert(
        self,
        session_id: str,
        user_id: str,
        title: str,
    ) -> None:
        """
        Create the session row if it doesn't exist; otherwise bump updated_at.
        Called before saving message turns.
        """
        ...

    async def save_turn(
        self,
        session_id: str,
        human_text: str,
        assistant_text: str,
        widget_json: Any | None,
    ) -> None:
        """Persist both human and assistant messages atomically."""
        ...

    async def list_for_user(self, user_id: str) -> list[ChatSession]:
        """Return all sessions for a user, ordered by updated_at DESC."""
        ...

    async def get_messages(
        self,
        session_id: str,
        user_id: str,
    ) -> list[ChatMessage]:
        """
        Return messages for a session in chronological order.
        Raises NotFoundError if the session doesn't exist or isn't owned by user_id.
        """
        ...

    async def delete(self, session_id: str, user_id: str) -> bool:
        """
        Hard-delete a session and cascade-delete its messages.
        Returns True if deleted, False if not found or not owned by user_id.
        """
        ...
