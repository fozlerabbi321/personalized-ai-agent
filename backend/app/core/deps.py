from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.security import decode_access_token
from app import state as app_state

_bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict[str, str]:
    """
    FastAPI dependency: validate Bearer JWT and return the user payload.

    Usage in route handlers:
        current_user: dict = Depends(get_current_user)
        user_id = current_user["user_id"]
    """
    try:
        payload = decode_access_token(credentials.credentials)
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload is missing 'sub' claim",
            )
        return {"user_id": user_id, "email": payload.get("email", "")}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_agent_graph():
    """
    FastAPI dependency: return the initialized LangGraph compiled graph.
    Raises HTTP 503 if the graph hasn't been initialized during lifespan.
    """
    try:
        return app_state.get_graph()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
