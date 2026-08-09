"""Interface layer — thin FastAPI routers.

Routers are responsible ONLY for:
  1. Parsing and validating the HTTP request (via Pydantic schemas)
  2. Calling the appropriate Use Case with extracted parameters
  3. Mapping the Use Case result to an HTTP response

No business logic, no SQL, no LLM calls belong here.
"""

from app.interface.auth import router as auth_router
from app.interface.chat import router as chat_router
from app.interface.sessions import router as sessions_router

__all__ = ["auth_router", "chat_router", "sessions_router"]
