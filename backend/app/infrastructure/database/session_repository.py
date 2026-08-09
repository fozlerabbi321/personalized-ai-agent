from __future__ import annotations

"""
Concrete implementation of SessionRepository using asyncpg.

All raw SQL for chat_sessions and chat_messages lives here.
Use cases call this via the abstract SessionRepository Protocol.
"""

import json
import uuid
from typing import Any

import asyncpg

from app.domain.entities.message import ChatMessage
from app.domain.entities.session import ChatSession
from app.domain.exceptions import NotFoundError
from app.domain.repositories.session_repository import SessionRepository


class AsyncpgSessionRepository:
    """asyncpg-backed implementation of the SessionRepository protocol."""

    def __init__(self, pool: asyncpg.Pool) -> None:
        self._pool = pool

    async def upsert(
        self,
        session_id: str,
        user_id: str,
        title: str,
    ) -> None:
        """Create the session row if missing; otherwise bump updated_at."""
        async with self._pool.acquire() as conn:
            existing = await conn.fetchrow(
                "SELECT id FROM chat_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                user_id,
            )
            if not existing:
                await conn.execute(
                    "INSERT INTO chat_sessions (id, user_id, title) VALUES ($1, $2, $3)",
                    session_id,
                    user_id,
                    title,
                )
            else:
                await conn.execute(
                    "UPDATE chat_sessions SET updated_at = NOW() WHERE id = $1",
                    session_id,
                )

    async def save_turn(
        self,
        session_id: str,
        human_text: str,
        assistant_text: str,
        widget_json: Any | None,
    ) -> None:
        """Persist both human and assistant message rows atomically."""
        async with self._pool.acquire() as conn:
            await conn.executemany(
                """
                INSERT INTO chat_messages (id, session_id, role, content, widget_json)
                VALUES ($1, $2, $3, $4, $5)
                """,
                [
                    (str(uuid.uuid4()), session_id, "human",     human_text,     None),
                    (str(uuid.uuid4()), session_id, "assistant", assistant_text,
                     json.dumps(widget_json) if widget_json else None),
                ],
            )

    async def list_for_user(self, user_id: str) -> list[ChatSession]:
        """Return all sessions for a user ordered by updated_at DESC."""
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT
                    s.id,
                    s.title,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id)::int AS message_count
                FROM chat_sessions s
                LEFT JOIN chat_messages m ON m.session_id = s.id
                WHERE s.user_id = $1
                GROUP BY s.id
                ORDER BY s.updated_at DESC
                """,
                user_id,
            )
        return [
            ChatSession(
                id=str(r["id"]),
                user_id=user_id,
                title=r["title"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                message_count=r["message_count"],
            )
            for r in rows
        ]

    async def get_messages(
        self,
        session_id: str,
        user_id: str,
    ) -> list[ChatMessage]:
        """
        Return messages for a session in chronological order.
        Raises NotFoundError if session doesn't exist or isn't owned by user.
        """
        async with self._pool.acquire() as conn:
            session = await conn.fetchrow(
                "SELECT id FROM chat_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                user_id,
            )
            if not session:
                raise NotFoundError("Session not found")

            rows = await conn.fetch(
                """
                SELECT id, role, content, widget_json, created_at
                FROM chat_messages
                WHERE session_id = $1
                ORDER BY created_at ASC
                """,
                session_id,
            )

        messages: list[ChatMessage] = []
        for r in rows:
            wj = r["widget_json"]
            if wj and isinstance(wj, str):
                try:
                    wj = json.loads(wj)
                except (json.JSONDecodeError, TypeError):
                    wj = None

            messages.append(
                ChatMessage(
                    id=str(r["id"]),
                    session_id=session_id,
                    role=r["role"],
                    content=r["content"],
                    widget_json=wj,
                    created_at=r["created_at"],
                )
            )
        return messages

    async def delete(self, session_id: str, user_id: str) -> bool:
        """
        Hard-delete a session (messages cascade).
        Returns True if a row was deleted, False if not found.
        """
        async with self._pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM chat_sessions WHERE id = $1 AND user_id = $2",
                session_id,
                user_id,
            )
        return result != "DELETE 0"


# Structural subtype assertion
def _check() -> None:
    _: SessionRepository = AsyncpgSessionRepository.__new__(AsyncpgSessionRepository)  # type: ignore[type-abstract]
