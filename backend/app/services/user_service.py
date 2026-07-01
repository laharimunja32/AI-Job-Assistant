from sqlalchemy.orm import Session

from app.core.security import get_password_hash
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserRole


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_create: UserCreate, role: UserRole = UserRole.USER) -> User:
    user = User(
        email=user_create.email,
        hashed_password=get_password_hash(user_create.password),
        full_name=user_create.full_name,
        role=role.value,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, user: User, user_update: UserUpdate) -> User:
    if user_update.full_name is not None:
        user.full_name = user_update.full_name
    if user_update.password is not None:
        user.hashed_password = get_password_hash(user_update.password)

    db.add(user)
    db.commit()
    db.refresh(user)
    return user
