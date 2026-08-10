from __future__ import annotations

"""Auth router — thin interface delegating to auth use cases."""

from fastapi import APIRouter, Depends, status

from app.application.auth.login_user import LoginUserUseCase
from app.application.auth.register_user import RegisterUserUseCase
from app.core.container import get_login_use_case, get_register_use_case
from app.core.deps import get_current_user
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
) -> TokenResponse:
    """
    Create a new user with hashed password. Returns a JWT access token
    that can be used immediately to authenticate subsequent requests.
    """
    token = await use_case.execute(body.email, body.password)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT token",
)
async def login(
    body: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_use_case),
) -> TokenResponse:
    """Verify email + password. Returns a JWT access token on success."""
    token = await use_case.execute(body.email, body.password)
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """Return the profile of the currently authenticated user (extracted from JWT)."""
    return UserResponse(user_id=current_user["user_id"], email=current_user["email"])
