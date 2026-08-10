from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ChatMessage:
    """
    Immutable domain entity representing a single message turn.

    ``role`` is always one of ``"human"`` or ``"assistant"``.
    ``widget_json`` is the optional SDUI payload emitted by the api_call node.
    """

    id: str
    session_id: str
    role: str           # "human" | "assistant"
    content: str
    created_at: datetime
    widget_json: Any | None = None
