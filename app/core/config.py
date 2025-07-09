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


def get_settings() -> Settings:
    """Get application settings from environment variables."""
    return Settings()
