from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class ChatSession:
    """
    Immutable domain entity representing a chat conversation thread.

    One ChatSession maps 1-to-1 to a LangGraph ``thread_id`` used
    by the PostgresSaver checkpointer for persistent memory.
    """

    id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = field(default=0)
