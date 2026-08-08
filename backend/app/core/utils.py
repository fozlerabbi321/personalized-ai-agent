from __future__ import annotations

from typing import Any


def extract_text(content: Any) -> str:
    """
    Safely extract plain string text from any LangChain message content.

    LangChain message `content` can be:
      - `str`: "Hello"
      - `list`: ["Hello", " world"] or [{"type": "text", "text": "Hello"}]
      - `dict`: {"text": "Hello"}
    """
    if not content:
        return ""

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts: list[str] = []
        for part in content:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict):
                parts.append(str(part.get("text") or part.get("content") or ""))
            else:
                parts.append(str(part))
        return "".join(parts)

    if isinstance(content, dict):
        return str(content.get("text") or content.get("content") or "")

    return str(content)
