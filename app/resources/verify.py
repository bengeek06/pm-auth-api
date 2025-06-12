"""
verify.py
---------
This module provides the VerifyResource for handling JWT access token
verification.
"""
import os
from datetime import datetime, timezone
import jwt
from flask import request, jsonify
from flask_restful import Resource

from app.models.token_blacklist import TokenBlacklist
from app.logger import logger


class VerifyResource(Resource):
    """
    Resource for verifying the validity of a JWT access token.

    GET /verify:
        - Checks the presence and validity of the access token from cookies.
        - Verifies the token signature, expiration, and blacklist status.
        - Returns user information if the token is valid.
    """
    def get(self):
        """
        Handle access token verification.

        Expects an 'access_token' cookie.
        If the token is valid, returns user information and a validity flag.
        Returns 401 with an error message if the token is missing, invalid,
        expired, or revoked.
        """
        logger.info("Token verification attempt started")
        access_token = request.cookies.get('access_token')
        if not access_token:
            logger.error("Missing access token for verification")
            return {'message': 'Missing access token'}, 401

        try:
            payload = jwt.decode(
                access_token,
                os.environ['JWT_SECRET'],
                algorithms=['HS256']
            )
            jti = payload.get('jti')
            if not jti:
                logger.error("No JTI in token")
                return {'message': 'Invalid token'}, 401

            # Check if the token is blacklisted
            blacklisted = TokenBlacklist.query.filter_by(jti=jti).first()
            if blacklisted:
                logger.warning("Token is blacklisted")
                return {'message': 'Token revoked'}, 401

            # Check expiration
            exp = payload.get('exp')
            if exp and datetime.fromtimestamp(
                    exp, tz=timezone.utc) < datetime.now(timezone.utc):
                logger.warning("Token expired")
                return {'message': 'Token expired'}, 401

            # Successful authentication
            return jsonify({
                'user_id': payload.get('sub'),
                'company_id': payload.get('company_id'),
                'email': payload.get('email'),
                'valid': True
            })

        except jwt.ExpiredSignatureError:
            logger.warning("Token expired (jwt.ExpiredSignatureError)")
            return {'message': 'Token expired'}, 401
        except jwt.InvalidTokenError as e:
            logger.error("Invalid token: %s", e)
            return {'message': 'Invalid token'}, 401
