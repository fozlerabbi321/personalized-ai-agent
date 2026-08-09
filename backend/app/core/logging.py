from __future__ import annotations

"""
Structured logging configuration using Python's stdlib logging.

Provides a ``get_logger(name)`` factory that returns a consistently configured
logger. All modules should use this instead of ``print()`` or creating their
own ``logging.getLogger()`` calls directly.

Log format: ISO timestamp | level | logger name | message
"""

import logging
import sys


def configure_logging(level: str = "INFO") -> None:
    """
    Configure root logging once at application startup (called from main.py lifespan).

    Args:
        level: Log level string (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
    """
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
    # Suppress noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger.

    Usage:
        from app.core.logging import get_logger
        logger = get_logger(__name__)
        logger.info("User registered", extra={"user_id": user_id})
    """
    return logging.getLogger(name)
