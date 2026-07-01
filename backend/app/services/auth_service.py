from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    TokenType,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    verify_password,
)
from app.db.models.token_blocklist import TokenBlocklist
from app.services.user_service import get_user_by_email
from app.db.models.user import User


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.hashed_password):
        return None
    return user


def get_tokens_for_user(user: User) -> dict[str, str]:
    return {
        "access_token": create_access_token(subject=user.email, role=user.role),
        "refresh_token": create_refresh_token(subject=user.email),
        "token_type": "bearer",
    }


def is_refresh_token_revoked(db: Session, jti: str) -> bool:
    return db.query(TokenBlocklist).filter(TokenBlocklist.jti == jti).first() is not None


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    payload = decode_refresh_token(refresh_token)
    jti = payload["jti"]
    if is_refresh_token_revoked(db, jti):
        return

    db.add(TokenBlocklist(jti=jti))
    db.commit()


def refresh_tokens(db: Session, refresh_token: str) -> dict[str, str]:
    payload = decode_refresh_token(refresh_token)
    jti = payload["jti"]
    if is_refresh_token_revoked(db, jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(db, payload["sub"])
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db.add(TokenBlocklist(jti=jti))
    db.commit()
    return get_tokens_for_user(user)
