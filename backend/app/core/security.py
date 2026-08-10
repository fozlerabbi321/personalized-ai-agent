from __future__ import annotations

"""
Security utilities — password hashing and JWT operations.

Renamed from ``core/auth.py`` to ``core/security.py`` to avoid naming
collision with the ``app/interface/auth.py`` router module.
"""

from datetime import datetime, timedelta, timezone

import bcrypt
from jose import jwt

from app.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def hash_password(plain_password: str) -> str:
    """Hash a plain-text password using bcrypt (cost factor 12)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain_password.encode("utf-8"), salt).decode("utf-8")


def create_access_token(payload: dict) -> str:
    """
    Encode a JWT with an expiry derived from ACCESS_TOKEN_EXPIRE_MINUTES.
    The ``sub`` claim should be the user's UUID string.
    """
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT.
    Raises ``jose.JWTError`` on invalid or expired tokens.
    """
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
