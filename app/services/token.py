from datetime import datetime, timedelta
import json
from typing import Optional
from sqlalchemy.orm import Session

from app.models.token import Token
from app.core.config import get_settings

settings = get_settings()


class TokenService:
    """Service for managing OAuth tokens."""

    def __init__(self, db: Session):
        """Initialize the token service with a database session.

        Args:
            db: Database session.
        """
        self.db = db

    def get_token(self, user_id: str) -> Optional[Token]:
        """Get a token for a user.

        Args:
            user_id: User ID.

        Returns:
            Token if found, None otherwise.
        """
        return self.db.query(Token).filter(
            Token.user_id == user_id,
            Token.is_active == True
        ).order_by(Token.created_at.desc()).first()

    def save_token(
        self,
        user_id: str,
        access_token: str,
        token_type: str,
        expires_in: int,
        refresh_token: Optional[str] = None,
        scopes: Optional[list[str]] = None,
    ) -> Token:
        """Save a token for a user.

        Args:
            user_id: User ID.
            access_token: OAuth access token.
            token_type: Token type (e.g., Bearer).
            expires_in: Seconds until token expiration.
            refresh_token: OAuth refresh token.
            scopes: OAuth scopes.

        Returns:
            Saved token.
        """
        # Deactivate any existing tokens for this user
        existing_tokens = self.db.query(Token).filter(
            Token.user_id == user_id,
            Token.is_active == True
        ).all()

        for token in existing_tokens:
            token.is_active = False

        # Create new token
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)

        # Default to calendar scopes if none provided
        if scopes is None:
            scopes = settings.google_calendar.scopes

        token = Token(
            user_id=user_id,
            access_token=access_token,
            token_type=token_type,
            expires_at=expires_at,
            refresh_token=refresh_token,
            scopes=json.dumps(scopes),
            is_active=True,
        )

        self.db.add(token)
        self.db.commit()
        self.db.refresh(token)

        return token

    def update_token(self, token: Token, access_token: str, expires_in: int) -> Token:
        """Update an existing token with a new access token.

        Args:
            token: Existing token to update.
            access_token: New access token.
            expires_in: Seconds until token expiration.

        Returns:
            Updated token.
        """
        token.access_token = access_token
        token.expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        token.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(token)

        return token

    def deactivate_token(self, token: Token) -> Token:
        """Deactivate a token.

        Args:
            token: Token to deactivate.

        Returns:
            Deactivated token.
        """
        token.is_active = False
        token.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(token)

        return token
