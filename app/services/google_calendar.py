from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from sqlalchemy.orm import Session

from app.models.token import Token
from app.core.config import get_settings

settings = get_settings()

class GoogleCalendarService:
    """Service for Google Calendar API operations."""

    def __init__(self, token: Token):
        """Initialize the Google Calendar service with a token.

        Args:
            token: OAuth token for Google Calendar API.
        """
        self.token = token
        self.credentials = self._create_credentials(token)
        self.service = build('calendar', 'v3', credentials=self.credentials)

    @classmethod
    def _create_credentials(cls, token: Token) -> Credentials:
        """Create Google OAuth credentials from a token.

        Args:
            token: OAuth token for Google Calendar API.

        Returns:
            Credentials: Google OAuth credentials.
        """
        return Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=settings.google_calendar.token_uri,
            client_id=settings.google_calendar.client_id,
            client_secret=settings.google_calendar.client_secret,
            scopes=json.loads(token.scopes),
            expiry=token.expires_at
        )

    def list_calendars(self) -> List[Dict[str, Any]]:
        """List all calendars for the authenticated user.

        Returns:
            List of calendars.
        """
        try:
            result = self.service.calendarList().list().execute()
            return result.get('items', [])
        except HttpError as error:
            raise Exception(f"Error fetching calendars: {error}")

    def get_calendar(self, calendar_id: str) -> Dict[str, Any]:
        """Get a calendar by its ID.

        Args:
            calendar_id: ID of the calendar.

        Returns:
            Calendar details.
        """
        try:
            return self.service.calendars().get(calendarId=calendar_id).execute()
        except HttpError as error:
            raise Exception(f"Error fetching calendar {calendar_id}: {error}")

    def create_calendar(self, summary: str, description: Optional[str] = None,
                      timezone: Optional[str] = None) -> Dict[str, Any]:
        """Create a new calendar.

        Args:
            summary: Title of the calendar.
            description: Description of the calendar.
            timezone: Timezone of the calendar.

        Returns:
            Created calendar details.
        """
        calendar_data = {
            'summary': summary,
        }

        if description:
            calendar_data['description'] = description

        if timezone:
            calendar_data['timeZone'] = timezone

        try:
            return self.service.calendars().insert(body=calendar_data).execute()
        except HttpError as error:
            raise Exception(f"Error creating calendar: {error}")

    def update_calendar(self, calendar_id: str, summary: Optional[str] = None,
                      description: Optional[str] = None, timezone: Optional[str] = None) -> Dict[str, Any]:
        """Update a calendar.

        Args:
            calendar_id: ID of the calendar to update.
            summary: New title for the calendar.
            description: New description for the calendar.
            timezone: New timezone for the calendar.

        Returns:
            Updated calendar details.
        """
        # First get the current calendar
        try:
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
        except HttpError as error:
            raise Exception(f"Error fetching calendar {calendar_id}: {error}")

        # Update the fields that were provided
        if summary:
            calendar['summary'] = summary

        if description:
            calendar['description'] = description

        if timezone:
            calendar['timeZone'] = timezone

        try:
            return self.service.calendars().update(calendarId=calendar_id, body=calendar).execute()
        except HttpError as error:
            raise Exception(f"Error updating calendar {calendar_id}: {error}")

    def delete_calendar(self, calendar_id: str) -> None:
        """Delete a calendar.

        Args:
            calendar_id: ID of the calendar to delete.
        """
        try:
            self.service.calendars().delete(calendarId=calendar_id).execute()
        except HttpError as error:
            raise Exception(f"Error deleting calendar {calendar_id}: {error}")
