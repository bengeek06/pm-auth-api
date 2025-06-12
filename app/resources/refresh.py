"""
refresh.py
----------
This module provides the RefreshResource for handling JWT access token renewal
using a valid refresh token.
"""

import os
from datetime import datetime, timedelta, timezone
import jwt
from flask import request, make_response, jsonify
from flask_restful import Resource

from app.models.refresh_token import RefreshToken
from app.models import db
from app.logger import logger


class RefreshResource(Resource):
    """
    Resource for handling JWT access token refresh.

    POST /refresh:
        - Validates the refresh token from cookies.
        - Issues a new JWT access token if the refresh token is valid and not
          expired.
        - Optionally supports refresh token rotation.
    """
    def post(self):
        """
        Handle access token refresh.

        Expects a valid 'refresh_token' cookie.
        If the refresh token is valid and not expired, generates and returns a
        new JWT access token as a cookie.
        Returns 400 if the refresh token is missing, 401 if invalid or expired.
        """
        logger.info("Token refresh attempt started")
        refresh_token_str = request.cookies.get('refresh_token')
        if not refresh_token_str:
            logger.error("Missing refresh token for refresh")
            return {'message': 'Missing refresh token'}, 400

        refresh_token = RefreshToken.query.filter_by(
            token=refresh_token_str).first()

        if not refresh_token:
            logger.error("Refresh token not found or already revoked")
            return {'message': 'Invalid refresh token'}, 401

        expires_at = refresh_token.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at < datetime.now(timezone.utc):
            logger.error("Refresh token expired")
            db.session.delete(refresh_token)
            db.session.commit()
            return {'message': 'Refresh token expired'}, 401

        # Generate a new access token
        user_id = refresh_token.user_id
        company_id = refresh_token.company_id
        access_token_exp = datetime.now(timezone.utc) + timedelta(minutes=15)
        jti = jwt.utils.base64url_encode(os.urandom(16)).decode('utf-8')
        access_token = jwt.encode(
            {
                'sub': user_id,
                'company_id': company_id,
                'exp': access_token_exp,
                'jti': jti
            },
            os.environ['JWT_SECRET'],
            algorithm='HS256'
        )

        # Optional: refresh token rotation (not implemented here)
        # Delete the old refresh token and create a new one
        db.session.delete(refresh_token)
        new_refresh_token_str = jwt.utils.base64url_encode(
            os.urandom(64)).decode('utf-8')
        new_refresh_token = RefreshToken(
            token=new_refresh_token_str,
            user_id=user_id,
            company_id=company_id,
            expires_at=datetime.now(timezone.utc) + timedelta(days=7)
        )
        db.session.add(new_refresh_token)
        db.session.commit()
        logger.info("New access token generated for user %s", user_id)

        # Set the new access token as an HttpOnly cookie
        response = make_response(jsonify({'message': 'Token refreshed'}))
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            expires=access_token_exp
        )
        return response
