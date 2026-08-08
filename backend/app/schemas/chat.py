from __future__ import annotations

import uuid

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4096, description="The user's message")
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="UUID v4 session identifier. Auto-generated if omitted.",
    )


class SSETokenEvent(BaseModel):
    type: str = "token"
    content: str


class SSEWidgetEvent(BaseModel):
    type: str = "widget"
    widget_json: dict


class SSEDoneEvent(BaseModel):
    type: str = "done"
    session_id: str


class SSEErrorEvent(BaseModel):
    type: str = "error"
    message: str
