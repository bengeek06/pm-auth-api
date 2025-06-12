"""
token_blacklist.py
------------------
This module defines the TokenBlacklist model for storing blacklisted (revoked)
JWT tokens in the database.
"""
from . import db


class TokenBlacklist(db.Model):
    """
    SQLAlchemy model for blacklisted (revoked) JWT tokens.

    Attributes:
        id (int): Primary key.
        jti (str): The unique JWT ID (JTI) of the token.
        user_id (int): The ID of the user associated with the token.
        company_id (int): The ID of the company associated with the token.
        created_at (datetime): Timestamp when the token was blacklisted.
        expires_at (datetime): Expiration datetime of the token.
    """
    __tablename__ = 'token_blacklist'
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    company_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    expires_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        """
        Return a string representation of the TokenBlacklist instance.

        Returns:
            str: String representation including the JTI.
        """
        return f"<TokenBlacklist jti={self.jti}>"
