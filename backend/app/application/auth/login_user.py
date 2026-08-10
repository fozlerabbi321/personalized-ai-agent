from __future__ import annotations

"""
LoginUserUseCase — business logic for authenticating an existing user.

Responsibilities:
  1. Fetch user by email (delegates to UserRepository)
  2. Verify plain password against bcrypt hash
  3. Return a signed JWT access token on success

Raises ``UnauthorizedError`` for both "email not found" and "wrong password"
cases to prevent user enumeration attacks.
"""

from app.core.security import create_access_token, verify_password
from app.domain.exceptions import UnauthorizedError
from app.domain.repositories.user_repository import UserRepository

_AUTH_ERROR = "Invalid email or password"


class LoginUserUseCase:
    """Authenticate an existing user and return a JWT token."""

    def __init__(self, user_repo: UserRepository) -> None:
        self._repo = user_repo

    async def execute(self, email: str, password: str) -> str:
        """
        Execute the login flow.

        Args:
            email:    User's email address.
            password: Plain-text password to verify.

        Returns:
            A signed JWT access token string.

        Raises:
            UnauthorizedError: If credentials are invalid (intentionally vague
                               to prevent user enumeration).
        """
        user = await self._repo.find_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError(_AUTH_ERROR)

        return create_access_token({"sub": user.id, "email": user.email})
