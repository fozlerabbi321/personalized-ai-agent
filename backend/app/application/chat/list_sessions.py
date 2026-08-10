from __future__ import annotations

"""ListSessionsUseCase — retrieve all chat sessions for an authenticated user."""

from app.domain.entities.session import ChatSession
from app.domain.repositories.session_repository import SessionRepository


class ListSessionsUseCase:
    """Return all chat sessions belonging to the authenticated user."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self._repo = session_repo

    async def execute(self, user_id: str) -> list[ChatSession]:
        """
        Args:
            user_id: UUID string of the authenticated user.

        Returns:
            List of ChatSession entities ordered by updated_at DESC.
        """
        return await self._repo.list_for_user(user_id)
