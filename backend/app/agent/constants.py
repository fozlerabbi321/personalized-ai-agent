from __future__ import annotations

"""
Agent constants — centralized configuration for the LangGraph agent.

Previously scattered across:
  - ``api/chat.py``           (_STREAMING_NODES)
  - ``agent/nodes/api_call.py`` (_KNOWN_TICKERS, base_prices dict inline)

Centralizing here ensures a single source of truth and makes it trivial
to add new tickers, widget types, or streaming nodes.
"""

# ── SSE Streaming ─────────────────────────────────────────────────────────────

# Nodes whose LLM output tokens are forwarded to the client as SSE "token" events.
# The llm_decision node is intentionally excluded — its routing tokens are internal.
STREAMING_NODES: frozenset[str] = frozenset({"api_call", "summary", "general"})


# ── Intent Values ─────────────────────────────────────────────────────────────

class Intent:
    """Valid intent values set by the llm_decision_node."""
    API_CALL = "api_call"
    SUMMARY  = "summary"
    GENERAL  = "general"

    ALL: frozenset[str] = frozenset({API_CALL, SUMMARY, GENERAL})


# ── Financial Tickers ─────────────────────────────────────────────────────────

# All known tickers that can be detected from user messages.
# Ordered: longer/more specific tickers first to prevent partial matches.
KNOWN_TICKERS: list[str] = [
    "GOOGL", "GOOG",                            # Alphabet (check before AAPL to avoid overlap)
    "AAPL", "MSFT", "TSLA", "AMZN", "META",
    "NVDA", "NFLX", "AMD", "INTC",
    "BTC", "ETH",
    "SPY", "QQQ",
]

# Anchor prices for mock OHLC random-walk generation.
# Kept here so they're easy to update without digging into node logic.
BASE_PRICES: dict[str, float] = {
    "AAPL":  187.0,
    "GOOGL": 175.0,
    "GOOG":  175.0,
    "MSFT":  420.0,
    "TSLA":  245.0,
    "AMZN":  195.0,
    "META":  535.0,
    "NVDA":  880.0,
    "NFLX":  640.0,
    "AMD":   165.0,
    "INTC":   35.0,
    "BTC":  67000.0,
    "ETH":   3500.0,
    "SPY":   540.0,
    "QQQ":   470.0,
}

DEFAULT_TICKER = "AAPL"
DEFAULT_BASE_PRICE = 100.0
