from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.auth_service import (
    authenticate_user,
    get_tokens_for_user,
    refresh_tokens,
    revoke_refresh_token,
)
from app.services.user_service import create_user, get_user_by_email
from app.schemas.user import UserRole

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    response_description="The newly created user profile",
)
def register_user(*, user_create: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    if get_user_by_email(db, user_create.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    user = create_user(db, user_create, role=UserRole.USER)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate a user and receive JWT tokens",
    response_description="Access and refresh tokens for authenticated users",
)
def login_user(*, credentials: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, credentials.email, credentials.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active",
        )

    return get_tokens_for_user(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access and refresh tokens",
    response_description="New JWT tokens returned after refresh",
)
def refresh_user_token(*, token_request: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return refresh_tokens(db, token_request.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout and revoke refresh token",
    response_description="No content returned on successful logout",
)
def logout_user(*, token_request: RefreshTokenRequest, db: Session = Depends(get_db)) -> Response:
    revoke_refresh_token(db, token_request.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
