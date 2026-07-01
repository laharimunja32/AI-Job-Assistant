from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, constr


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr = Field(..., description="User email address")
    full_name: str | None = Field(default=None, description="User full name")


class UserCreate(UserBase):
    """Schema for creating a user."""

    password: constr(min_length=8) = Field(..., description="User password")


class UserUpdate(BaseModel):
    """Schema for updating the current user profile."""

    full_name: str | None = Field(default=None, description="New user full name")
    password: constr(min_length=8) | None = Field(
        default=None,
        description="New password for the user. Minimum 8 characters.",
    )


class UserRead(UserBase):
    """Schema for reading a user."""

    id: int
    is_active: bool
    role: UserRole

    model_config = ConfigDict(from_attributes=True)
