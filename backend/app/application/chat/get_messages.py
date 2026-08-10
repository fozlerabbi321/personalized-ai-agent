from __future__ import annotations

"""GetSessionMessagesUseCase — retrieve all messages in a chat session."""

from app.domain.entities.message import ChatMessage
from app.domain.repositories.session_repository import SessionRepository


class GetSessionMessagesUseCase:
    """Return the ordered message history for a specific chat session."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self._repo = session_repo

    async def execute(self, session_id: str, user_id: str) -> list[ChatMessage]:
        """
        Args:
            session_id: UUID of the target session.
            user_id:    UUID of the authenticated user (ownership check).

        Returns:
            Chronologically ordered list of ChatMessage entities.

        Raises:
            NotFoundError: If the session doesn't exist or isn't owned by user_id.
        """
        return await self._repo.get_messages(session_id, user_id)
