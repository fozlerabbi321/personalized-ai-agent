from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.auth import create_access_token, hash_password, verify_password
from app.core.deps import get_current_user
from app.database import get_db_connection
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(body: RegisterRequest) -> TokenResponse:
    """
    Create a new user with hashed password. Returns a JWT access token
    that can be used immediately to authenticate subsequent requests.
    """
    async with get_db_connection() as conn:
        existing = await conn.fetchrow(
            "SELECT id FROM users WHERE email = $1", body.email
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists",
            )

        user_id = str(uuid.uuid4())
        await conn.execute(
            "INSERT INTO users (id, email, hashed_password) VALUES ($1, $2, $3)",
            user_id, body.email, hash_password(body.password),
        )

    token = create_access_token({"sub": user_id, "email": body.email})
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive a JWT token",
)
async def login(body: LoginRequest) -> TokenResponse:
    """
    Verify email + password. Returns a JWT access token on success.
    """
    async with get_db_connection() as conn:
        user = await conn.fetchrow(
            "SELECT id, email, hashed_password FROM users WHERE email = $1",
            body.email,
        )

    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    token = create_access_token({"sub": str(user["id"]), "email": user["email"]})
    return TokenResponse(access_token=token)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user",
)
async def get_me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    """Return the profile of the currently authenticated user (extracted from JWT)."""
    return UserResponse(user_id=current_user["user_id"], email=current_user["email"])
