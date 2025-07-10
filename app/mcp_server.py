from mcp.server.fastmcp import Context
from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.google_calendar import GoogleCalendarService
from app.services.token import TokenService
from app.utils.auth import get_auth_url, exchange_code_for_token
from app.core.config import get_settings

settings = get_settings()

# Create an MCP server
mcp = FastMCP("Google Calendar MCP")


@mcp.resource("auth://url")
def auth_url() -> str:
    """Get Google OAuth authorization URL."""
    return get_auth_url()


@mcp.tool(title="Get Authorization URL")
def get_authorization_url() -> Dict[str, str]:
    """Get the authorization URL for Google OAuth flow."""
    auth_uri = get_auth_url()
    return {
        "auth_url": auth_uri,
        "message": "Please visit this URL to authorize the application.",
    }


@mcp.tool(title="Exchange Authorization Code")
def exchange_auth_code(code: str, user_id: str = "default") -> Dict[str, Any]:
    """Exchange authorization code for access token.

    Args:
        code: The authorization code from Google OAuth.
        user_id: User identifier for token storage (default: "default").

    Returns:
        Token information and status.
    """
    try:
        with get_db() as db:
            token_data = exchange_code_for_token(code=code, db=db, user_id=user_id)
            return {
                "success": True,
                "message": "Authorization successful. Token stored.",
                "expires_in": token_data.get("expires_in"),
                "user_id": user_id,
            }
    except Exception as e:
        return {"success": False, "message": f"Authorization failed: {str(e)}"}


@mcp.tool(title="List Calendars")
def list_calendars(user_id: str = "default") -> List[Dict[str, Any]]:
    """List all calendars for the authenticated user.

    Args:
        user_id: User identifier for token retrieval (default: "default").

    Returns:
        List of calendars.
    """
    with get_db() as db:
        token_service = TokenService(db)
        token = token_service.get_token(user_id)

        if not token:
            raise ValueError(
                f"No token found for user {user_id}. Please authorize first."
            )

        if token.is_expired:
            raise ValueError(
                f"Token for user {user_id} is expired. Please authorize again."
            )

        calendar_service = GoogleCalendarService(token)
        return calendar_service.list_calendars()


@mcp.tool(title="Get Calendar")
def get_calendar(calendar_id: str, user_id: str = "default") -> Dict[str, Any]:
    """Get a calendar by its ID.

    Args:
        calendar_id: ID of the calendar to retrieve.
        user_id: User identifier for token retrieval (default: "default").

    Returns:
        Calendar details.
    """
    with get_db() as db:
        token_service = TokenService(db)
        token = token_service.get_token(user_id)

        if not token:
            raise ValueError(
                f"No token found for user {user_id}. Please authorize first."
            )

        if token.is_expired:
            raise ValueError(
                f"Token for user {user_id} is expired. Please authorize again."
            )

        calendar_service = GoogleCalendarService(token)
        return calendar_service.get_calendar(calendar_id)


@mcp.tool(title="Create Calendar")
def create_calendar(
    summary: str,
    description: Optional[str] = None,
    timezone: Optional[str] = None,
    user_id: str = "default",
) -> Dict[str, Any]:
    """Create a new calendar.

    Args:
        summary: Title of the calendar.
        description: Description of the calendar.
        timezone: Timezone of the calendar.
        user_id: User identifier for token retrieval (default: "default").

    Returns:
        Created calendar details.
    """
    with get_db() as db:
        token_service = TokenService(db)
        token = token_service.get_token(user_id)

        if not token:
            raise ValueError(
                f"No token found for user {user_id}. Please authorize first."
            )

        if token.is_expired:
            raise ValueError(
                f"Token for user {user_id} is expired. Please authorize again."
            )

        calendar_service = GoogleCalendarService(token)
        return calendar_service.create_calendar(
            summary=summary, description=description, timezone=timezone
        )


@mcp.tool(title="Update Calendar")
def update_calendar(
    calendar_id: str,
    summary: Optional[str] = None,
    description: Optional[str] = None,
    timezone: Optional[str] = None,
    user_id: str = "default",
) -> Dict[str, Any]:
    """Update an existing calendar.

    Args:
        calendar_id: ID of the calendar to update.
        summary: New title for the calendar.
        description: New description for the calendar.
        timezone: New timezone for the calendar.
        user_id: User identifier for token retrieval (default: "default").

    Returns:
        Updated calendar details.
    """
    with get_db() as db:
        token_service = TokenService(db)
        token = token_service.get_token(user_id)

        if not token:
            raise ValueError(
                f"No token found for user {user_id}. Please authorize first."
            )

        if token.is_expired:
            raise ValueError(
                f"Token for user {user_id} is expired. Please authorize again."
            )

        calendar_service = GoogleCalendarService(token)
        return calendar_service.update_calendar(
            calendar_id=calendar_id,
            summary=summary,
            description=description,
            timezone=timezone,
        )


@mcp.tool(title="Delete Calendar")
def delete_calendar(calendar_id: str, user_id: str = "default") -> Dict[str, Any]:
    """Delete a calendar.

    Args:
        calendar_id: ID of the calendar to delete.
        user_id: User identifier for token retrieval (default: "default").

    Returns:
        Success status.
    """
    with get_db() as db:
        token_service = TokenService(db)
        token = token_service.get_token(user_id)

        if not token:
            raise ValueError(
                f"No token found for user {user_id}. Please authorize first."
            )

        if token.is_expired:
            raise ValueError(
                f"Token for user {user_id} is expired. Please authorize again."
            )

        calendar_service = GoogleCalendarService(token)
        calendar_service.delete_calendar(calendar_id)

        return {
            "success": True,
            "message": f"Calendar {calendar_id} deleted successfully.",
        }
