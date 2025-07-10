import logging
import sys
from dotenv import load_dotenv, find_dotenv

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleCalendarSettings(BaseModel):
    """Google Calendar API settings."""

    client_id: str = ""
    client_secret: str = ""
    redirect_uri: str = "http://localhost:8080/oauth2callback"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    scopes: list[str] = ["https://www.googleapis.com/auth/calendar"]


class DatabaseSettings(BaseModel):
    """Database connection settings."""

    url: str = "sqlite:///./calendar_mcp.db"


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Calendar MCP Server"
    debug: bool = False
    port: int = "8007"
    mcp_transport: str = "stdio"

    # Database - made optional with default for development
    database: DatabaseSettings = DatabaseSettings()

    # Google Calendar - made optional with default for development
    google_calendar: GoogleCalendarSettings = GoogleCalendarSettings()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


def required_envs_missing(settings: Settings):
    missing = []
    # Check database URL
    if (
        not settings.database.url
        or settings.database.url == "sqlite:///./calendar_mcp.db"
    ):
        missing.append("DATABASE__URL")
    # Check Google Calendar client_id and client_secret
    if not settings.google_calendar.client_id:
        missing.append("GOOGLE_CALENDAR__CLIENT_ID")
    if not settings.google_calendar.client_secret:
        missing.append("GOOGLE_CALENDAR__CLIENT_SECRET")
    # Optionally check redirect_uri (warn only)
    if (
        not settings.google_calendar.redirect_uri
        or settings.google_calendar.redirect_uri
        == "http://localhost:8080/oauth2callback"
    ):
        logging.warning(
            "GOOGLE_CALENDAR__REDIRECT_URI is not set or is using the default development value."
        )
    return missing


def get_settings() -> Settings:
    """Get application settings from environment variables."""
    return Settings()


def get_validated_settings() -> Settings:
    """Ensure all required envs are loaded, load .env if needed, fail if still missing."""
    logging.basicConfig(level=logging.INFO)
    settings = get_settings()
    missing = required_envs_missing(settings)
    if missing:
        logging.info(f"Missing required env(s) before loading .env: {missing}")
        try:
            dotenv_path = find_dotenv()
            logging.info(f"find_dotenv() returned: {dotenv_path}")
            load_dotenv()
            logging.info("load_dotenv() succeeded")
        except Exception as e:
            logging.error(f"Error loading .env: {e}")
        # Re-check after loading .env
        settings = get_settings()
        missing = required_envs_missing(settings)
        if missing:
            logging.error(
                f"Still missing required env(s) after loading .env: {missing}"
            )
            sys.exit(1)
        else:
            logging.info("All required envs loaded after .env")
    else:
        logging.info("All required envs already set, skipping .env load.")
    return settings
