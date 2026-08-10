from __future__ import annotations

"""
Dependency Injection container — wires infrastructure to application layer.

Uses FastAPI's built-in dependency injection (``Depends``) rather than a
third-party container library, keeping the dependency footprint minimal
while achieving full IoC.

Pattern:
  - Factory functions (``get_*``) are declared here
  - FastAPI routers use ``Depends(get_*)`` to receive injected instances
  - The container reads from the already-initialized infrastructure pools

This is the only place that knows about both infrastructure AND application layers.
"""

import asyncpg

from app.infrastructure.database.connection import get_asyncpg_pool
from app.infrastructure.database.user_repository import AsyncpgUserRepository
from app.infrastructure.database.session_repository import AsyncpgSessionRepository
from app.application.auth.register_user import RegisterUserUseCase
from app.application.auth.login_user import LoginUserUseCase
from app.application.chat.stream_chat import StreamChatUseCase
from app.application.chat.list_sessions import ListSessionsUseCase
from app.application.chat.get_messages import GetSessionMessagesUseCase
from app.application.chat.delete_session import DeleteSessionUseCase


# ── Repository factories ──────────────────────────────────────────────────────

def get_pool() -> asyncpg.Pool:
    """Provide the initialized asyncpg connection pool."""
    return get_asyncpg_pool()


def get_user_repository(pool: asyncpg.Pool = None) -> AsyncpgUserRepository:  # type: ignore[assignment]
    """Provide a UserRepository instance backed by asyncpg."""
    return AsyncpgUserRepository(pool or get_pool())


def get_session_repository(pool: asyncpg.Pool = None) -> AsyncpgSessionRepository:  # type: ignore[assignment]
    """Provide a SessionRepository instance backed by asyncpg."""
    return AsyncpgSessionRepository(pool or get_pool())


# ── Auth use case factories ───────────────────────────────────────────────────

def get_register_use_case() -> RegisterUserUseCase:
    """Provide a fully wired RegisterUserUseCase."""
    return RegisterUserUseCase(user_repo=get_user_repository())


def get_login_use_case() -> LoginUserUseCase:
    """Provide a fully wired LoginUserUseCase."""
    return LoginUserUseCase(user_repo=get_user_repository())


# ── Chat / session use case factories ────────────────────────────────────────

def get_stream_chat_use_case() -> StreamChatUseCase:
    """Provide a fully wired StreamChatUseCase."""
    return StreamChatUseCase(session_repo=get_session_repository())


def get_list_sessions_use_case() -> ListSessionsUseCase:
    """Provide a fully wired ListSessionsUseCase."""
    return ListSessionsUseCase(session_repo=get_session_repository())


def get_session_messages_use_case() -> GetSessionMessagesUseCase:
    """Provide a fully wired GetSessionMessagesUseCase."""
    return GetSessionMessagesUseCase(session_repo=get_session_repository())


def get_delete_session_use_case() -> DeleteSessionUseCase:
    """Provide a fully wired DeleteSessionUseCase."""
    return DeleteSessionUseCase(session_repo=get_session_repository())
