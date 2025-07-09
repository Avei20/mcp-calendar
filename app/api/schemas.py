from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class CalendarBase(BaseModel):
    """Base model for calendar operations."""
    summary: str = Field(..., description="Title of the calendar")
    description: Optional[str] = Field(None, description="Description of the calendar")
    timezone: Optional[str] = Field(None, description="Timezone of the calendar")


class CalendarCreate(CalendarBase):
    """Schema for creating a calendar."""
    pass


class CalendarUpdate(BaseModel):
    """Schema for updating a calendar."""
    summary: Optional[str] = Field(None, description="New title of the calendar")
    description: Optional[str] = Field(None, description="New description of the calendar")
    timezone: Optional[str] = Field(None, description="New timezone of the calendar")


class Calendar(CalendarBase):
    """Schema for calendar response."""
    id: str = Field(..., description="Calendar ID")
    etag: Optional[str] = Field(None, description="ETag of the resource")
    kind: Optional[str] = Field(None, description="Type of the resource")
    timeZone: Optional[str] = Field(None, description="Timezone of the calendar")
    accessRole: Optional[str] = Field(None, description="User's access role for this calendar")

    class Config:
        """Pydantic config."""
        orm_mode = True
        populate_by_name = True


class TokenRequest(BaseModel):
    """Schema for OAuth token requests."""
    code: str = Field(..., description="Authorization code from Google OAuth flow")
    redirect_uri: Optional[str] = Field(None, description="Redirect URI used in the OAuth flow")


class TokenResponse(BaseModel):
    """Schema for OAuth token responses."""
    access_token: str = Field(..., description="OAuth access token")
    token_type: str = Field(..., description="Token type (usually 'Bearer')")
    expires_in: int = Field(..., description="Seconds until token expiration")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    scope: Optional[str] = Field(None, description="Scopes associated with the token")


class AuthUrl(BaseModel):
    """Schema for authorization URL responses."""
    auth_url: str = Field(..., description="Authorization URL for Google OAuth flow")


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    error: str = Field(..., description="Error message")
    error_description: Optional[str] = Field(None, description="Detailed error description")
