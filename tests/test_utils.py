"""
test_utils.py
-------------
This module contains tests for the check_credentials utility function.
It covers all supported environments and error cases, including development,
test, production, and various failure scenarios for the user service.
"""
import requests
from app.utils import check_credentials


def test_check_credentials_dev(monkeypatch):
    """
    Test check_credentials in development environment.

    Ensures that any credentials return a stub user in development.
    """
    monkeypatch.setenv('FLASK_ENV', 'development')
    user = check_credentials('foo@bar.com', 'pass')
    assert user['id'] == 1
    assert user['email'] == 'foo@bar.com'
    assert user['username'] == 'testuser'
    assert user['is_admin'] is True


def test_check_credentials_test(monkeypatch):
    """
    Test check_credentials in test environment.

    Ensures that any credentials return a stub user in test.
    """
    monkeypatch.setenv('FLASK_ENV', 'test')
    user = check_credentials('foo@bar.com', 'pass')
    assert user['id'] == 1
    assert user['email'] == 'foo@bar.com'


def test_check_credentials_unsupported_env(monkeypatch):
    """
    Test check_credentials with an unsupported environment.

    Ensures that credentials return None if FLASK_ENV is not supported.
    """
    monkeypatch.setenv('FLASK_ENV', 'foo')
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_missing_user_service_url(monkeypatch):
    """
    Test check_credentials in production with missing USER_SERVICE_URL.

    Ensures that credentials return None if USER_SERVICE_URL is not set.
    """
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.delenv('USER_SERVICE_URL', raising=False)
    monkeypatch.setenv('INTERNAL_AUTH_TOKEN', 'secret')
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_missing_internal_auth_token(monkeypatch):
    """
    Test check_credentials in production with missing INTERNAL_AUTH_TOKEN.

    Ensures that credentials return None if INTERNAL_AUTH_TOKEN is not set.
    """
    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('USER_SERVICE_URL', 'http://fake')
    monkeypatch.delenv('INTERNAL_AUTH_TOKEN', raising=False)
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_invalid_response(monkeypatch):
    """
    Test check_credentials in production with an invalid user service response.

    Ensures that credentials return None if the user service returns a non-200
    status.
    """
    class FakeResp:
        status_code = 400
        text = 'fail'
        def json(self): return {}

    def fake_post(*a, **k): return FakeResp()

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('USER_SERVICE_URL', 'http://fake')
    monkeypatch.setenv('INTERNAL_AUTH_TOKEN', 'secret')
    monkeypatch.setattr(requests, 'post', fake_post)
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_invalid_user(monkeypatch):
    """
    Test check_credentials in production with invalid user credentials.

    Ensures that credentials return None if the user service returns valid=False.
    """
    class FakeResp:
        status_code = 200
        text = 'ok'
        def json(self): return {'valid': False}

    def fake_post(*a, **k): return FakeResp()

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('USER_SERVICE_URL', 'http://fake')
    monkeypatch.setenv('INTERNAL_AUTH_TOKEN', 'secret')
    monkeypatch.setattr(requests, 'post', fake_post)
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_missing_user_id(monkeypatch):
    """
    Test check_credentials in production with missing user_id in response.

    Ensures that credentials return None if the user service does not return a user_id.
    """
    class FakeResp:
        status_code = 200
        text = 'ok'
        def json(self): return {'valid': True}

    def fake_post(*a, **k): return FakeResp()

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('USER_SERVICE_URL', 'http://fake')
    monkeypatch.setenv('INTERNAL_AUTH_TOKEN', 'secret')
    monkeypatch.setattr(requests, 'post', fake_post)
    user = check_credentials('foo@bar.com', 'pass')
    assert user is None


def test_check_credentials_prod_success(monkeypatch):
    """
    Test check_credentials in production with a valid user service response.

    Ensures that credentials return the correct user dictionary if the user is valid.
    """
    class FakeResp:
        status_code = 200
        text = 'ok'
        def json(self):
            return {
                'valid': True,
                'user_id': 42,
                'username': 'bob',
                'company_id': 7,
                'is_admin': True
            }


    def fake_post(*a, **k): return FakeResp()

    monkeypatch.setenv('FLASK_ENV', 'production')
    monkeypatch.setenv('USER_SERVICE_URL', 'http://fake')
    monkeypatch.setenv('INTERNAL_AUTH_TOKEN', 'secret')
    monkeypatch.setattr(requests, 'post', fake_post)
    user = check_credentials('foo@bar.com', 'pass')
    assert user['user_id'] == 42
    assert user['username'] == 'bob'
    assert user['company_id'] == 7
    assert user['is_admin'] is True
