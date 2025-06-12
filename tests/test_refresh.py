"""
test_refresh.py
---------------
This module contains tests for the /refresh endpoint to ensure access token renewal,
refresh token validation, and error handling work as expected.
"""
from datetime import datetime, timedelta, timezone
from app.models.refresh_token import RefreshToken
from app.models import db

def make_refresh_token(user_id=1, company_id=42, expires=None):
    """
    Create and store a refresh token in the database for testing.

    Args:
        user_id (int): The user ID to associate with the token.
        company_id (int): The company ID to associate with the token.
        expires (datetime, optional): Expiration datetime for the token.

    Returns:
        str: The refresh token string.
    """
    if not expires:
        expires = datetime.now(timezone.utc) + timedelta(days=1)
    token = 'refresh-token-test'
    rt = RefreshToken(
        token=token,
        user_id=user_id,
        company_id=company_id,
        expires_at=expires
        )
    db.session.add(rt)
    db.session.commit()
    return token

def test_refresh_success(client):
    """
    Test successful access token refresh with a valid refresh token.

    Ensures that a valid refresh token returns a 200 status, a success message,
    and sets a new access token cookie.
    """
    refresh_token = make_refresh_token()
    client.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )

    response = client.post('/refresh')
    assert response.status_code == 200
    assert response.json['message'] == 'Token refreshed'
    cookies = response.headers.getlist('Set-Cookie')
    assert any('access_token=' in c for c in cookies)

def test_refresh_missing_token(client):
    """
    Test refresh with missing refresh token.

    Ensures that a request without the refresh token returns a 400 error.
    """
    response = client.post('/refresh')
    assert response.status_code == 400
    assert response.json['message'] == 'Missing refresh token'

def test_refresh_invalid_token(client):
    """
    Test refresh with an invalid refresh token.

    Ensures that a request with an invalid refresh token returns a 401 error.
    """
    client.set_cookie(
        'refresh_token',
        'invalid-token',
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    response = client.post('/refresh')
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid refresh token'

def test_refresh_expired_token(client):
    """
    Test refresh with an expired refresh token.

    Ensures that a request with an expired refresh token returns a 401 error.
    """
    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    refresh_token = make_refresh_token(expires=expired)
    client.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    response = client.post('/refresh')
    assert response.status_code == 401
    assert response.json['message'] == 'Refresh token expired'
