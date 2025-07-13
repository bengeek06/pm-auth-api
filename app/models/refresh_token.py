"""
refresh_token.py
----------------
This module defines the RefreshToken model for storing refresh tokens in
the database.
"""
import uuid
from . import db


class RefreshToken(db.Model):
    """
    SQLAlchemy model for refresh tokens.

    Attributes:
        id (int): Primary key.
        token (str): The refresh token string (unique).
        user_id (int): The ID of the user associated with the token.
        company_id (int): The ID of the company associated with the token.
        created_at (datetime): Timestamp when the token was created.
        expires_at (datetime): Expiration datetime of the token.
        revoked (bool): Whether the token has been revoked.
    """
    __tablename__ = 'refresh_tokens'
    
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    token = db.Column(db.String(512), unique=True, nullable=False)
    user_id = db.Column(db.String(36), nullable=False)
    company_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)
    revoked = db.Column(db.Boolean, default=False)

    def __repr__(self):
        """
        Return a string representation of the RefreshToken instance.

        Returns:
            str: String representation including user_id and revoked status.
        """
        return f"<RefreshToken user_id={self.user_id} revoked={self.revoked}>"
