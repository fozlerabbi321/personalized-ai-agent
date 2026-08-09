from __future__ import annotations

"""
Domain exception hierarchy.

These are pure Python exceptions — no HTTP status codes, no FastAPI imports.
The Interface layer (FastAPI) maps these to the appropriate HTTP responses
via global exception handlers registered in main.py.

Hierarchy:
    AppError
    ├── NotFoundError       → HTTP 404
    ├── ConflictError       → HTTP 409
    ├── UnauthorizedError   → HTTP 401
    ├── ForbiddenError      → HTTP 403
    └── ValidationError     → HTTP 422
"""


class AppError(Exception):
    """Base class for all application domain errors."""

    def __init__(self, message: str = "An unexpected error occurred") -> None:
        super().__init__(message)
        self.message = message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.message!r})"


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(message)


class ConflictError(AppError):
    """Raised when a create operation conflicts with an existing resource."""

    def __init__(self, message: str = "Resource already exists") -> None:
        super().__init__(message)


class UnauthorizedError(AppError):
    """Raised when authentication credentials are missing or invalid."""

    def __init__(self, message: str = "Authentication required") -> None:
        super().__init__(message)


class ForbiddenError(AppError):
    """Raised when an authenticated user lacks permission for an action."""

    def __init__(self, message: str = "Permission denied") -> None:
        super().__init__(message)


class ValidationError(AppError):
    """Raised when domain-level business validation fails."""

    def __init__(self, message: str = "Validation failed") -> None:
        super().__init__(message)
