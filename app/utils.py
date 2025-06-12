"""
utils.py
--------
This module provides utility functions for authentication, including credential
checking
against a user service or a local stub for development and testing
environments.
"""
import os
import dotenv
import requests
from app.logger import logger


def check_credentials(email, password):
    """
    Check user credentials against the user service or a local stub.

    In development or test environments, returns a stub user.
    In production or staging, verifies credentials by calling the user
    service API.
    Returns user information if credentials are valid, otherwise returns None.

    Args:
        email (str): The user's email address.
        password (str): The user's password.

    Returns:
        dict or None: User information dictionary if valid, otherwise None.
    """
    env = os.getenv('FLASK_ENV')
    if env in ['development', 'test']:
        # Stub: accept any credentials in dev/test
        return {
            'id': 1,
            'username': 'testuser',
            'is_admin': True,
            'email': email,
            'hashed_password': 'fakehash'
        }
    if env in ['production', 'staging']:
        dotenv.load_dotenv(f'.env.{env}')
        user_service_url = os.getenv('USER_SERVICE_URL')
        if not user_service_url:
            logger.error(
                "USER_SERVICE_URL is not set in environment variables.")
            return None
        internal_secret = os.getenv('INTERNAL_AUTH_TOKEN')
        if not internal_secret:
            logger.error(
                "INTERNAL_AUTH_TOKEN is not set in environment variables.")
            return None

        try:
            payload = {'email': email, 'password': password}
            logger.debug(
                "Verifying password for user %s at %s/users/verify_password",
                email, user_service_url
                )

            # Call the user service to verify the password
            requests_headers = {'X-Internal-Token': internal_secret}
            resp = requests.post(
                f"{user_service_url}/users/verify_password",
                json=payload,
                headers=requests_headers,
                timeout=2
                )
            if resp.status_code != 200:
                logger.error(
                    "Failed to fetch user: %s - %s",
                    resp.status_code,
                    resp.text
                    )
                return None
            logger.debug("Response status code: %s", resp.status_code)
            logger.debug("Response text: %s", resp.text)

            user = resp.json()
            logger.debug("User data: %s", user)
            if user.get('valid') is not True:
                logger.error("Invalid user credentials.")
                return None

            # If the user is valid, fetch the full user data
            user_id = user.get('user_id')
            if not user_id:
                logger.error("User ID not found in user data.")
                return None

            return {
                'user_id': user_id,
                'username': user.get('username'),
                'company_id': user.get('company_id'),
                'is_admin': user.get('is_admin', False)
            }

        except requests.Timeout:
            logger.error("User service request timed out.")
            return None
        except requests.ConnectionError:
            logger.error("User service connection error.")
            return None
        except requests.RequestException as e:
            logger.error("User service request exception: %s", e)
            return None
        except ValueError as e:
            logger.error("Error decoding JSON response: %s", e)
            return None

    else:
        logger.error("Unsupported environment: %s", env)
        return None
