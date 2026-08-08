from __future__ import annotations

import json
import random
from datetime import datetime, timedelta

from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import settings
from app.agent.state import AgentState
from app.agent.prompts import build_athena_chart_analysis_prompt
from app.core.utils import extract_text

_llm = ChatGoogleGenerativeAI(
    model=settings.GEMINI_MODEL,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=0.4,
)

# Common tickers to detect from the user message
_KNOWN_TICKERS = [
    "AAPL", "GOOGL", "GOOG", "MSFT", "TSLA", "AMZN", "META",
    "NVDA", "NFLX", "AMD", "INTC", "BTC", "ETH", "SPY", "QQQ",
]


def _detect_ticker(message: str) -> str:
    """Extract a ticker symbol from the user's message (case-insensitive)."""
    upper_msg = message.upper()
    for ticker in _KNOWN_TICKERS:
        if ticker in upper_msg:
            return ticker
    return "AAPL"  # default fallback


def _generate_mock_ohlc(ticker: str, days: int = 7) -> dict:
    """
    Generate realistic-looking mock OHLC + volume stock data.
    Uses a random walk anchored around a plausible base price.
    """
    base_prices = {
        "AAPL": 187.0, "GOOGL": 175.0, "GOOG": 175.0, "MSFT": 420.0,
        "TSLA": 245.0, "AMZN": 195.0, "META": 535.0, "NVDA": 880.0,
        "NFLX": 640.0, "AMD": 165.0, "INTC": 35.0,
        "BTC": 67000.0, "ETH": 3500.0, "SPY": 540.0, "QQQ": 470.0,
    }
    base = base_prices.get(ticker, 100.0)
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
        base = close_p  # random walk

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
    (langgraph_node == 'api_call' passes the SSE filter).
    The `widget_json` is captured from the final graph state after streaming.
    """
    last_msg = state["messages"][-1] if state.get("messages") else None
    last_message = extract_text(last_msg.content) if last_msg else ""
    ticker = _detect_ticker(last_message)
    widget_data = _generate_mock_ohlc(ticker)

    data_summary = {
        "ticker":         widget_data["ticker"],
        "current_price":  widget_data["current_price"],
        "7_day_change":   f"{'+' if widget_data['change'] >= 0 else ''}{widget_data['change']} ({'+' if widget_data['change_pct'] >= 0 else ''}{widget_data['change_pct']}%)",
        "7_day_high":     widget_data["seven_day_high"],
        "7_day_low":      widget_data["seven_day_low"],
    }

    all_messages = state.get("messages", [])
    analysis_prompt = build_athena_chart_analysis_prompt(ticker, data_summary, all_messages)

    response = await _llm.ainvoke([HumanMessage(content=analysis_prompt)])
    response_text = extract_text(response.content).strip()

    return {
        "messages":      [AIMessage(content=response_text)],
        "response_text": response_text,
        "widget_json":   widget_data,
        "is_final":      True,
    }
