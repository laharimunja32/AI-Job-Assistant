from pydantic import BaseModel, EmailStr, Field, constr


class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type returned by the API")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Registered user email address")
    password: constr(min_length=8) = Field(..., description="User password")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token returned by the login endpoint")
