from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class SessionResponse(BaseModel):
    session_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]
    total: int


class MessageResponse(BaseModel):
    message_id: str
    role: str          # "human" | "assistant"
    content: str
    widget_json: Any | None = None
    created_at: datetime


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[MessageResponse]
