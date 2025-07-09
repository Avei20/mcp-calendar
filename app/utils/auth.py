from typing import Dict, Optional
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.token import Token
from app.services.token import TokenService

settings = get_settings()


def create_oauth_flow(redirect_uri: Optional[str] = None) -> Flow:
    """Create a Google OAuth flow.

    Args:
        redirect_uri: Redirect URI for the OAuth flow.

    Returns:
        Flow: Google OAuth flow.
    """
    client_config = {
        "web": {
            "client_id": settings.google_calendar.client_id,
            "client_secret": settings.google_calendar.client_secret,
            "auth_uri": settings.google_calendar.auth_uri,
            "token_uri": settings.google_calendar.token_uri,
        }
    }

    if redirect_uri:
        client_config["web"]["redirect_uris"] = [redirect_uri]

    flow = Flow.from_client_config(
        client_config,
        scopes=settings.google_calendar.scopes,
        redirect_uri=redirect_uri or settings.google_calendar.redirect_uri,
    )

    return flow


def get_auth_url(redirect_uri: Optional[str] = None) -> str:
    """Get the authorization URL for Google OAuth.

    Args:
        redirect_uri: Redirect URI for the OAuth flow.

    Returns:
        str: Authorization URL.
    """
    flow = create_oauth_flow(redirect_uri)
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return auth_url


def exchange_code_for_token(code: str, redirect_uri: Optional[str] = None, db: Session = None, user_id: str = None) -> Dict:
    """Exchange an authorization code for an access token.

    Args:
        code: Authorization code from Google OAuth.
        redirect_uri: Redirect URI used in the OAuth flow.
        db: Database session.
        user_id: User ID for token storage.

    Returns:
        Dict: Token information.
    """
    flow = create_oauth_flow(redirect_uri)
    flow.fetch_token(code=code)
    credentials = flow.credentials

    token_data = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_type": "Bearer",
        "expires_in": credentials.expiry.timestamp() - Flow._clock() if credentials.expiry else 3600,
        "scope": " ".join(credentials.scopes) if credentials.scopes else "",
    }

    # Save token in database if database session and user_id are provided
    if db and user_id:
        token_service = TokenService(db)
        token_service.save_token(
            user_id=user_id,
            access_token=token_data["access_token"],
            token_type=token_data["token_type"],
            expires_in=token_data["expires_in"],
            refresh_token=token_data["refresh_token"],
            scopes=credentials.scopes,
        )

    return token_data


def create_credentials_from_token(token: Token) -> Credentials:
    """Create Google OAuth credentials from a token.

    Args:
        token: OAuth token.

    Returns:
        Credentials: Google OAuth credentials.
    """
    import json

    return Credentials(
        token=token.access_token,
        refresh_token=token.refresh_token,
        token_uri=settings.google_calendar.token_uri,
        client_id=settings.google_calendar.client_id,
        client_secret=settings.google_calendar.client_secret,
        scopes=json.loads(token.scopes),
        expiry=token.expires_at
    )
