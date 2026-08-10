from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    """
    Immutable domain entity representing an authenticated user.

    ``frozen=True`` ensures User objects cannot be mutated after creation,
    reflecting the principle that a user's core identity is stable.
    """

    id: str
    email: str
    hashed_password: str
    created_at: datetime
