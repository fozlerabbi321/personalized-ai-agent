from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.domain.entities.user import User


@runtime_checkable
class UserRepository(Protocol):
    """
    Abstract contract for user persistence operations.

    The Application layer depends ONLY on this Protocol — never on a concrete
    database implementation. This enables testing with mock implementations
    and swapping DB drivers without touching business logic.
    """

    async def find_by_email(self, email: str) -> User | None:
        """Return a User entity if found, None otherwise."""
        ...

    async def create(
        self,
        user_id: str,
        email: str,
        hashed_password: str,
    ) -> User:
        """Persist a new user and return the created entity."""
        ...
