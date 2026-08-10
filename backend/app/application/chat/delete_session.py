from __future__ import annotations

"""DeleteSessionUseCase — hard-delete a chat session and its messages."""

from app.domain.exceptions import NotFoundError
from app.domain.repositories.session_repository import SessionRepository


class DeleteSessionUseCase:
    """Delete a chat session. Only the owner can delete their session."""

    def __init__(self, session_repo: SessionRepository) -> None:
        self._repo = session_repo

    async def execute(self, session_id: str, user_id: str) -> None:
        """
        Args:
            session_id: UUID of the session to delete.
            user_id:    UUID of the authenticated user (ownership check).

        Raises:
            NotFoundError: If the session doesn't exist or isn't owned by user_id.
        """
        deleted = await self._repo.delete(session_id, user_id)
        if not deleted:
            raise NotFoundError("Session not found")
