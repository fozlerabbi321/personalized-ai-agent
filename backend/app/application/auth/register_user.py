from __future__ import annotations

"""
RegisterUserUseCase — business logic for creating a new user account.

Responsibilities:
  1. Check email uniqueness (delegates to UserRepository)
  2. Hash the password via security utility
  3. Create the user record
  4. Return a signed JWT access token

This class knows NOTHING about HTTP, FastAPI, or asyncpg.
The router calls it and maps the result to an HTTP response.
"""

import uuid

from app.core.security import create_access_token, hash_password
from app.domain.exceptions import ConflictError
from app.domain.repositories.user_repository import UserRepository


class RegisterUserUseCase:
    """Create a new user account and return a JWT token."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def execute(self, email: str, password: str) -> str:
        """
        Execute the registration flow.

        Args:
            email:    Validated email address (pre-validated by Pydantic schema).
            password: Plain-text password (min 6 chars, enforced by schema).

        Returns:
            A signed JWT access token string.

        Raises:
            ConflictError: If an account with this email already exists.
        """
        if await self._repo.find_by_email(email):
            raise ConflictError("An account with this email already exists")

        user_id = str(uuid.uuid4())
        await self._repo.create(
            user_id=user_id,
            email=email,
            hashed_password=hash_password(password),
        )
        return create_access_token({"sub": user_id, "email": email})
