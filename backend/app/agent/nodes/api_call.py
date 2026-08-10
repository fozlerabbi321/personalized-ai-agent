from __future__ import annotations

"""
api_call_node — Fetch mock financial data and generate Athena's market analysis.

Key improvements over the original:
  - Module-level ``_llm`` removed → uses ``LLMProvider`` singleton
  - ``_detect_ticker`` uses regex word-boundary matching to prevent false positives
    (e.g., "INTC" no longer matches "DISTINCT")
  - ``_KNOWN_TICKERS`` and ``_BASE_PRICES`` moved to ``agent/constants.py``
"""

import random
import re
from datetime import datetime, timedelta

from langchain_core.messages import AIMessage, HumanMessage

from app.agent.constants import BASE_PRICES, DEFAULT_BASE_PRICE, DEFAULT_TICKER, KNOWN_TICKERS
from app.agent.prompts import build_athena_chart_analysis_prompt
from app.agent.state import AgentState
from app.core.utils import extract_text
from app.infrastructure.ai.llm_provider import TEMPERATURE_ANALYTICAL, get_llm

# Pre-compiled regex patterns for ticker detection (word-boundary safe)
# Sorted longest first to avoid partial matches (GOOGL before GOOG)
_TICKER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (ticker, re.compile(rf"\b{re.escape(ticker)}\b", re.IGNORECASE))
    for ticker in KNOWN_TICKERS
]


def _detect_ticker(message: str) -> str:
    """
    Extract the first recognized ticker symbol from the user's message.

    Uses word-boundary regex (``\\b``) to prevent false positives.
    Example: "INTC" will NOT match "DISTINCT".
    Falls back to DEFAULT_TICKER if no known ticker is found.
    """
    for ticker, pattern in _TICKER_PATTERNS:
        if pattern.search(message):
            return ticker
    return DEFAULT_TICKER


def _generate_mock_ohlc(ticker: str, days: int = 7) -> dict:
    """
    Generate realistic-looking mock OHLC + volume data using a random walk.

    Base prices are sourced from ``agent/constants.py`` (single source of truth).
    """
    base = BASE_PRICES.get(ticker, DEFAULT_BASE_PRICE)
    data = []

    for i in range(days):
        date = (datetime.now() - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        volatility = random.uniform(0.01, 0.035)
        open_p  = base * (1 + random.uniform(-volatility, volatility))
        close_p = open_p * (1 + random.uniform(-volatility, volatility))
        high_p  = max(open_p, close_p) * (1 + random.uniform(0, volatility * 0.5))
        low_p   = min(open_p, close_p) * (1 - random.uniform(0, volatility * 0.5))
        volume  = random.randint(8_000_000, 120_000_000)

        data.append({
            "date":   date,
            "open":   round(open_p, 2),
            "high":   round(high_p, 2),
            "low":    round(low_p,  2),
            "close":  round(close_p, 2),
            "volume": volume,
        })
        base = close_p  # random walk — next candle starts from previous close

    current_price = data[-1]["close"]
    start_price   = data[0]["open"]
    change        = round(current_price - start_price, 2)
    change_pct    = round((change / start_price) * 100, 2)

    return {
        "widget_type":    "candlestick_chart",
        "ticker":         ticker,
        "title":          f"{ticker} — 7-Day Price Chart",
        "current_price":  round(current_price, 2),
        "change":         change,
        "change_pct":     change_pct,
        "seven_day_high": round(max(d["high"] for d in data), 2),
        "seven_day_low":  round(min(d["low"]  for d in data), 2),
        "data":           data,
        "metric": {
            "label":     "Current Price",
            "value":     f"${current_price:,.2f}",
            "delta":     f"{'+' if change_pct >= 0 else ''}{change_pct}%",
            "sentiment": "positive" if change_pct >= 0 else "negative",
        },
    }


async def api_call_node(state: AgentState) -> dict:
    """
    Fetch mock financial data and use Gemini to generate a natural analysis.

    Tokens from this node ARE streamed to the client
    (``langgraph_node == 'api_call'`` passes the SSE filter in STREAMING_NODES).
    The ``widget_json`` is captured from the final graph state after streaming completes.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""
    ticker = _detect_ticker(last_message)
    widget_data = _generate_mock_ohlc(ticker)

    data_summary = {
        "ticker":        widget_data["ticker"],
        "current_price": widget_data["current_price"],
        "7_day_change":  f"{'+' if widget_data['change'] >= 0 else ''}{widget_data['change']} ({'+' if widget_data['change_pct'] >= 0 else ''}{widget_data['change_pct']}%)",
        "7_day_high":    widget_data["seven_day_high"],
        "7_day_low":     widget_data["seven_day_low"],
    }

    all_messages = state.get("messages", [])
    analysis_prompt = build_athena_chart_analysis_prompt(ticker, data_summary, all_messages)

    llm = get_llm(TEMPERATURE_ANALYTICAL)
    response = await llm.ainvoke([HumanMessage(content=analysis_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
