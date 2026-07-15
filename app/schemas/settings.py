from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AppSettingsResponse(BaseModel):
    """User settings response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    timezone: str
    locale: str
    notification_email: bool
    preferences: dict | None
    notes: str | None
    created_at: datetime
    updated_at: datetime


class AppSettingsUpdate(BaseModel):
    """Update user settings."""

    timezone: str | None = Field(default=None, max_length=64)
    locale: str | None = Field(default=None, max_length=16)
    notification_email: bool | None = None
    preferences: dict | None = None
    notes: str | None = None
