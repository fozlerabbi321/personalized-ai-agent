from __future__ import annotations

"""
Module-level app state store.

Avoids circular imports between main.py (lifespan) and api/chat.py (router).
The graph is set once during application startup and read by API endpoints.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from langgraph.graph.graph import CompiledGraph

_graph: "CompiledGraph | None" = None


def set_graph(graph: "CompiledGraph") -> None:
    global _graph
    _graph = graph


def get_graph() -> "CompiledGraph":
    if _graph is None:
        raise RuntimeError("LangGraph agent is not initialized. Check application lifespan.")
    return _graph
