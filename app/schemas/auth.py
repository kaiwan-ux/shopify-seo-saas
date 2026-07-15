from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """JWT token pair response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Access token expiry in seconds")


class TokenRefreshRequest(BaseModel):
    """Request body for token refresh."""

    refresh_token: str


class TokenPayload(BaseModel):
    """Decoded JWT payload."""

    sub: str
    exp: int
    type: str
    iat: int | None = None
