from mcp.server.fastmcp import Context
from fastmcp import FastMCP
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.services.google_calendar import GoogleCalendarService

# Create an MCP server
mcp = FastMCP("Google Calendar MCP")

import logging
from datetime import datetime

def validate_google_token(token: dict) -> bool:
    # Basic validation: check for access_token and expiry
    if not token or "access_token" not in token or "expires_in" not in token:
        logging.warning("Token missing required fields.")
        return False
    # Check expiry (assuming token has 'expires_at' or calculate from 'expires_in')
    expires_at = token.get("expires_at")
    if expires_at:
        if datetime.utcnow() > datetime.utcfromtimestamp(expires_at):
            logging.warning("Token is expired.")
            return False
    else:
        # If only 'expires_in' is present, assume token was issued now
        issued_at = token.get("issued_at", datetime.utcnow().timestamp())
        if datetime.utcnow() > datetime.utcfromtimestamp(issued_at + token["expires_in"]):
            logging.warning("Token is expired.")
            return False
    return True

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
def list_calendars(token: dict) -> List[Dict[str, Any]]:
    """List all calendars for the authenticated user.

    Args:
        token: Google OAuth token (JSON).

    Returns:
        List of calendars.
    """
    logging.info(f"List Calendars called with token: {token}")
    calendar_service = GoogleCalendarService(token)
    return calendar_service.list_calendars()


@mcp.tool(title="Get Calendar")
def get_calendar(calendar_id: str, token: dict) -> Dict[str, Any]:
    """Get a calendar by its ID.

    Args:
        calendar_id: ID of the calendar to retrieve.
        token: Google OAuth token (JSON).

    Returns:
        Calendar details.
    """
    logging.info(f"Get Calendar called with token: {token}")
    calendar_service = GoogleCalendarService(token)
    return calendar_service.get_calendar(calendar_id)


@mcp.tool(title="Create Calendar")
def create_calendar(
    summary: str,
    description: Optional[str] = None,
    timezone: Optional[str] = None,
    token: dict = None,
) -> Dict[str, Any]:
    """Create a new calendar.

    Args:
        summary: Title of the calendar.
        description: Description of the calendar.
        timezone: Timezone of the calendar.
        token: Google OAuth token (JSON).

    Returns:
        Created calendar details.
    """
    logging.info(f"Create Calendar called with token: {token}")
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
    token: dict = None,
) -> Dict[str, Any]:
    """Update an existing calendar.

    Args:
        calendar_id: ID of the calendar to update.
        summary: New title for the calendar.
        description: New description for the calendar.
        timezone: New timezone for the calendar.
        token: Google OAuth token (JSON).

    Returns:
        Updated calendar details.
    """
    logging.info(f"Update Calendar called with token: {token}")
    calendar_service = GoogleCalendarService(token)
    return calendar_service.update_calendar(
        calendar_id=calendar_id,
        summary=summary,
        description=description,
        timezone=timezone,
    )


@mcp.tool(title="Delete Calendar")
def delete_calendar(calendar_id: str, token: dict) -> Dict[str, Any]:
    """Delete a calendar.

    Args:
        calendar_id: ID of the calendar to delete.
        token: Google OAuth token (JSON).

    Returns:
        Success status.
    """
    logging.info(f"Delete Calendar called with token: {token}")
    calendar_service = GoogleCalendarService(token)
    calendar_service.delete_calendar(calendar_id)

    return {
        "success": True,
        "message": f"Calendar {calendar_id} deleted successfully.",
    }
