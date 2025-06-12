"""
login.py
--------
This module provides the LoginResource for handling user authentication and
token issuance.
"""
import os
from datetime import datetime, timedelta, timezone
import secrets
import uuid
from flask import request, make_response, jsonify
from flask_restful import Resource
import jwt

from app.utils import check_credentials
from app.logger import logger
from app.models.refresh_token import RefreshToken
from app.models import db


class LoginResource(Resource):
    """
    Resource for handling user login and issuing JWT access and refresh tokens.

    POST /login:
        - Validates user credentials.
        - Issues JWT access and refresh tokens.
        - Sets tokens as HttpOnly cookies in the response.
    """
    def post(self):
        """
        Handle user login.

        Expects JSON body with 'email' and 'password'.
        If credentials are valid, generates and returns JWT access and refresh
        tokens as cookies.
        Returns 401 if credentials are invalid or missing.
        """
        logger.info("Login attempt started")
        data = request.get_json()
        if not data or 'email' not in data or 'password' not in data:
            logger.error("Invalid login request: Missing email or password")
            return {'message': 'Invalid email or password'}, 401

        email = data['email']
        password = data['password']
        user = check_credentials(email, password)
        if not user:
            logger.error("Login failed for email: %s", email)
            return {'message': 'Invalid email or password'}, 401

        logger.info("Login successful for user: %s", user['email'])

        # Génération des tokens
        access_token_exp = datetime.now(timezone.utc) + timedelta(minutes=15)
        refresh_token_exp = datetime.now(timezone.utc) + timedelta(days=7)
        jti = str(uuid.uuid4())
        access_token = jwt.encode(
            {
                'sub': user['id'],
                'email': user['email'],
                'company_id': user.get('company_id'),
                'exp': access_token_exp,
                'jti': jti
            },
            os.environ['JWT_SECRET'],
            algorithm='HS256'
        )

        refresh_token_str = secrets.token_urlsafe(64)
        refresh_token = RefreshToken(
            token=refresh_token_str,
            user_id=user['id'],
            company_id=user.get('company_id'),
            expires_at=refresh_token_exp
        )
        db.session.add(refresh_token)
        db.session.commit()

        # Création de la réponse avec cookies httpOnly
        response = make_response(jsonify({'message': 'Login successful'}))
        response.set_cookie(
            'access_token',
            access_token,
            httponly=True,
            secure=True,
            samesite='Strict',
            expires=access_token_exp
        )
        response.set_cookie(
            'refresh_token',
            refresh_token_str,
            httponly=True,
            secure=True,
            samesite='Strict',
            expires=refresh_token_exp
        )
        return response
