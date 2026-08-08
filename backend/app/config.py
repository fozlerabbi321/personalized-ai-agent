from __future__ import annotations

import json
import os

from pydantic import field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ── Application ───────────────────────────────────────────────────────────
    APP_NAME: str = "Personalized AI Agent"
    DEBUG: bool = False
    # Default dev key — ALWAYS override in production
    SECRET_KEY: str = "dev-secret-key-change-in-production-please-use-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days

    # ── Google Gemini ─────────────────────────────────────────────────────────
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"

    # ── LangSmith ─────────────────────────────────────────────────────────────
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "personalized-ai-agent"

    # ── Database ──────────────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://ai_agent_user:ai_agent_pass@localhost:5432/ai_agent_db"

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Stored as a plain str to avoid pydantic-settings v2 JSON pre-parsing issues.
    # Use `settings.cors_origins_list` for the parsed list.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001"

    @property
    def cors_origins_list(self) -> list[str]:
        """
        Returns CORS_ORIGINS as a Python list.
        Handles comma-separated strings and JSON arrays.
        """
        v = self.CORS_ORIGINS.strip()
        if v.startswith("["):
            try:
                return [str(o).strip() for o in json.loads(v) if str(o).strip()]
            except (json.JSONDecodeError, TypeError):
                pass
        return [o.strip() for o in v.split(",") if o.strip()]

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()

# Propagate LangSmith settings to os.environ so LangChain picks them up.
if settings.LANGCHAIN_TRACING_V2 and settings.LANGCHAIN_API_KEY:
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
    os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
