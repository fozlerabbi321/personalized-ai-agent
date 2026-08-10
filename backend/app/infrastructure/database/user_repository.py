from __future__ import annotations

"""
Concrete implementation of UserRepository using asyncpg.

This class implements the ``UserRepository`` Protocol defined in the domain layer.
All raw SQL lives here — never in routers or use cases.
"""

import asyncpg

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class AsyncpgUserRepository:
    """asyncpg-backed implementation of the UserRepository protocol."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def find_by_email(self, email: str) -> User | None:
        """Return a User entity matching email, or None if not found."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT id, email, hashed_password, created_at FROM users WHERE email = $1",
                email,
            )
        if not row:
            return None
        return User(
            id=str(row["id"]),
            email=row["email"],
            hashed_password=row["hashed_password"],
            created_at=row["created_at"],
        )

    async def create(
        self,
        user_id: str,
        email: str,
        hashed_password: str,
    ) -> User:
        """Insert a new user row and return the created User entity."""
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO users (id, email, hashed_password)
                VALUES ($1, $2, $3)
                RETURNING id, email, hashed_password, created_at
                """,
                user_id,
                email,
                hashed_password,
            )
        return User(
            id=str(row["id"]),
            email=row["email"],
            hashed_password=row["hashed_password"],
            created_at=row["created_at"],
        )


# Structural subtype assertion — ensures AsyncpgUserRepository fully satisfies the protocol.
def _check() -> None:
    assert isinstance(AsyncpgUserRepository, type)
    _: UserRepository = AsyncpgUserRepository.__new__(AsyncpgUserRepository)  # type: ignore[type-abstract]
