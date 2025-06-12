"""
logout.py
---------
This module provides the LogoutResource for handling user logout, token
revocation, and cookie cleanup.
"""
import os
from datetime import datetime, timezone
import jwt
from flask import request, make_response, jsonify
from flask_restful import Resource

from app.models.token_blacklist import TokenBlacklist
from app.models.refresh_token import RefreshToken
from app.models import db
from app.logger import logger


class LogoutResource(Resource):
    """
    Resource for handling user logout.

    POST /logout:
        - Blacklists the access token (if valid).
        - Deletes the refresh token from the database.
        - Removes authentication cookies from the client.
    """
    def post(self):
        """
        Handle user logout.

        Expects 'access_token' and 'refresh_token' cookies.
        Blacklists the access token, deletes the refresh token from the
        database, and clears the cookies on the client side.
        Returns 400 if tokens are missing, otherwise always returns a success
        message.
        """
        logger.info("Logout attempt started")
        access_token = request.cookies.get('access_token')
        refresh_token_str = request.cookies.get('refresh_token')

        if not access_token or not refresh_token_str:
            logger.error("Missing tokens for logout")
            return {'message': 'Missing tokens'}, 400

        # Blacklist the access token
        try:
            payload = jwt.decode(
                access_token,
                os.environ['JWT_SECRET'],
                algorithms=['HS256']
            )
            jti = payload.get('jti')
            user_id = payload.get('sub')
            company_id = payload.get('company_id')
            expires_at = datetime.fromtimestamp(
                payload['exp'],
                tz=timezone.utc
                )
            if jti:
                blacklist_entry = TokenBlacklist(
                    jti=jti,
                    user_id=user_id,
                    company_id=company_id,
                    expires_at=expires_at
                )
                db.session.add(blacklist_entry)
        except jwt.ExpiredSignatureError:
            logger.warning("Access token expired during logout")
        except jwt.InvalidTokenError as e:
            logger.warning("Invalid access token during logout: %s", e)
        except Exception as e:
            logger.error("Unexpected error during logout: %s", e)

        # Delete the refresh token from the database
        refresh_token = (
            RefreshToken.query.filter_by(token=refresh_token_str).first()
        )
        if refresh_token:
            db.session.delete(refresh_token)

        db.session.commit()

        # Remove cookies on the client side
        response = make_response(jsonify({'message': 'Logout successful'}))
        response.set_cookie('access_token',
                            '',
                            expires=0,
                            httponly=True,
                            secure=True,
                            samesite='Strict')
        response.set_cookie('refresh_token',
                            '',
                            expires=0,
                            httponly=True,
                            secure=True,
                            samesite='Strict')
        return response
