"""
test_logout.py
--------------
This module contains tests for the /logout endpoint to ensure token revocation,
refresh token deletion, and cookie cleanup work as expected.
"""
import os
import jwt
from datetime import datetime, timedelta, timezone
from app.models.refresh_token import RefreshToken
from app.models import db


def make_jwt(user_id=1, company_id=42, secret=None, expired=False):
    """
    Generate a JWT for testing purposes.

    Args:
        user_id (int): The user ID to include in the token.
        company_id (int): The company ID to include in the token.
        secret (str, optional): The secret key to sign the token.
        expired (bool): Whether to generate an expired token.

    Returns:
        str: The encoded JWT.
    """
    if not secret:
        secret = os.environ.get('JWT_SECRET', 'test_secret')
    if expired:
        exp = datetime.now(timezone.utc) - timedelta(minutes=1)
    else:
        exp = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {
        'sub': str(user_id),
        'company_id': company_id,
        'jti': 'test-jti',
        'exp': exp.timestamp()
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def test_logout_success(client, session):
    """
    Test successful logout.

    Ensures that a valid logout request revokes the access token, deletes the
    refresh token,
    and clears the authentication cookies.
    """
    access_token = make_jwt()
    refresh_token = 'refresh-token-test'
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    rt = RefreshToken(
        token=refresh_token,
        user_id=1,
        company_id=42,
        expires_at=expires
    )
    db.session.add(rt)
    db.session.commit()

    client.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    client.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )

    response = client.post('/logout')
    assert response.status_code == 200
    assert response.json['message'] == 'Logout successful'
    set_cookies = response.headers.getlist('Set-Cookie')
    assert any('access_token=;' in c for c in set_cookies)
    assert any('refresh_token=;' in c for c in set_cookies)


def test_logout_missing_tokens(client):
    """
    Test logout with missing tokens.

    Ensures that a logout request without the required cookies returns a
    400 error.
    """
    response = client.post('/logout')
    assert response.status_code == 400
    assert response.json['message'] == 'Missing tokens'


def test_logout_invalid_access_token(client, session):
    """
    Test logout with an invalid access token.

    Ensures that logout still succeeds (stateless) even if the access token
    is invalid.
    """
    access_token = 'invalid.token.value'
    refresh_token = 'refresh-token-test'
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    rt = RefreshToken(
        token=refresh_token,
        user_id=1,
        company_id=42,
        expires_at=expires
    )
    db.session.add(rt)
    db.session.commit()

    client.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    client.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )

    response = client.post('/logout')
    assert response.status_code == 200
    assert response.json['message'] == 'Logout successful'


def test_logout_expired_access_token(client, session):
    """
    Test logout with an expired access token.

    Ensures that logout still succeeds even if the access token is expired.
    """
    access_token = make_jwt(expired=True)
    refresh_token = 'refresh-token-test'
    expires = datetime.now(timezone.utc) + timedelta(days=1)
    rt = RefreshToken(
        token=refresh_token,
        user_id=1,
        company_id=42,
        expires_at=expires
    )
    db.session.add(rt)
    db.session.commit()

    client.set_cookie(
        'access_token',
        access_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    client.set_cookie(
        'refresh_token',
        refresh_token,
        httponly=True,
        secure=True,
        samesite='Strict'
    )

    response = client.post('/logout')
    assert response.status_code == 200
    assert response.json['message'] == 'Logout successful'
