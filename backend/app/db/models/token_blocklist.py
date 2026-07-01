from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TokenBlocklist(Base):
    """Revoked JWT refresh token entry."""

    __tablename__ = "token_blocklist"

    jti: Mapped[str] = mapped_column(String(255), primary_key=True, index=True, nullable=False)
