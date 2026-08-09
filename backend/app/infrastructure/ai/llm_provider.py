from __future__ import annotations

"""
LLM Provider — singleton factory for Google Gemini via LangChain.

Problem solved:
  Previously, each agent node (api_call, general, summary, llm_decision) instantiated
  its own ChatGoogleGenerativeAI object at module import time. This created 4 separate
  API client objects and made temperature configuration scattered across files.

Solution:
  A single ``get_llm(temperature)`` factory cached by temperature value.
  All agent nodes import from here, ensuring:
  - One API client instance per distinct temperature value (memory efficient)
  - Temperature config is centralized and explicit
  - Easy to swap LLM provider (mock for tests, different model for prod)
"""

from functools import lru_cache

from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings

# Standard temperatures used across agent nodes
TEMPERATURE_DETERMINISTIC = 0.0   # llm_decision: must be deterministic for routing
TEMPERATURE_ANALYTICAL    = 0.4   # api_call: precise financial analysis
TEMPERATURE_BALANCED      = 0.7   # general: conversational but coherent
TEMPERATURE_FOCUSED       = 0.2   # summary: factual, low creativity


@lru_cache(maxsize=8)
def get_llm(temperature: float = TEMPERATURE_BALANCED) -> ChatGoogleGenerativeAI:
    """
    Return a cached ChatGoogleGenerativeAI instance for the given temperature.

    Uses ``functools.lru_cache`` keyed on temperature — same temperature value
    always returns the same object, avoiding redundant client instantiation.

    Usage in agent nodes:
        from app.infrastructure.ai.llm_provider import get_llm, TEMPERATURE_ANALYTICAL
        llm = get_llm(TEMPERATURE_ANALYTICAL)
    """
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
    )
