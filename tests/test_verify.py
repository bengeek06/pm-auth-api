"""
test_verify.py
--------------
This module contains tests for the /verify endpoint to ensure access token
validation,
blacklist handling, expiration, and error responses work as expected.
"""
import os
from datetime import datetime, timedelta, timezone
import jwt
from app.models.token_blacklist import TokenBlacklist
from app.models import db


def make_access_token(
    user_id=1,
    company_id=42,
    email='test@example.com',
    jti='test-jti',
    secret=None,
    expired=False):
    """
    Generate a JWT access token for testing.

    Args:
        user_id (int): The user ID to include in the token.
        company_id (int): The company ID to include in the token.
        email (str): The user's email address.
        jti (str): The JWT ID.
        secret (str, optional): The secret key to sign the token.
        expired (bool): Whether to generate an expired token.

    Returns:
        str: The encoded JWT access token.
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
        'email': email,
        'jti': jti,
        'exp': exp.timestamp()
    }
    return jwt.encode(payload, secret, algorithm='HS256')


def test_verify_success(client):
    """
    Test successful verification of a valid access token.

    Ensures that a valid access token returns a 200 status, a validity flag,
    and the correct user information.
    """
    access_token = make_access_token()
    client.set_cookie('access_token', access_token)
    response = client.get('/verify')
    assert response.status_code == 200
    assert response.json['valid'] is True
    assert response.json['user_id'] == '1'
    assert response.json['company_id'] == 42
    assert response.json['email'] == 'test@example.com'


def test_verify_missing_token(client):
    """
    Test verification with a missing access token.

    Ensures that a request without an access token returns a 401 error.
    """
    response = client.get('/verify')
    assert response.status_code == 401
    assert response.json['message'] == 'Missing access token'


def test_verify_invalid_token(client):
    """
    Test verification with an invalid access token.

    Ensures that a request with an invalid access token returns a 401 error.
    """
    client.set_cookie(
        'access_token',
        'invalid.token.value',
        httponly=True,
        secure=True,
        samesite='Strict'
    )
    response = client.get('/verify')
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid token'


def test_verify_expired_token(client):
    """
    Test verification with an expired access token.

    Ensures that a request with an expired access token returns a 401 error.
    """
    access_token = make_access_token(expired=True)
    client.set_cookie('access_token', access_token)
    response = client.get('/verify')
    assert response.status_code == 401
    assert response.json['message'] == 'Token expired'


def test_verify_blacklisted_token(client):
    """
    Test verification with a blacklisted (revoked) access token.

    Ensures that a request with a blacklisted access token returns a 401 error.
    """
    jti = 'blacklisted-jti'
    access_token = make_access_token(jti=jti)
    tb = TokenBlacklist(
        jti=jti,
        user_id=1,
        company_id=42,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    db.session.add(tb)
    db.session.commit()
    client.set_cookie('access_token', access_token)
    response = client.get('/verify')
    assert response.status_code == 401
    assert response.json['message'] == 'Token revoked'
