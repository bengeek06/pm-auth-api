"""
test_login.py
-------------
This module contains tests for the /login endpoint to ensure user
authentication, token issuance, and error handling work as expected.
"""


def test_login_success(client, monkeypatch):
    """
    Test successful login with valid credentials.

    Ensures that a valid login returns a 200 status, a success message,
    and sets both access and refresh token cookies.
    """
    user = {'id': 1, 'email': 'test@example.com', 'company_id': 42}

    def fake_check_credentials(email, password):
        return user

    monkeypatch.setattr(
        'app.resources.login.check_credentials',
        fake_check_credentials
        )

    response = client.post(
        '/login',
        json={'email': 'test@example.com', 'password': 'password123'}
        )
    assert response.status_code == 200
    assert response.json['message'] == 'Login successful'
    cookies = response.headers.getlist('Set-Cookie')
    assert any('access_token=' in c for c in cookies)
    assert any('refresh_token=' in c for c in cookies)



def test_login_invalid_credentials(client, monkeypatch):
    """
    Test login with invalid credentials.

    Ensures that an invalid login returns a 401 status and an appropriate
    error message.
    """
    def fake_check_credentials(email, password):
        return None

    monkeypatch.setattr(
        'app.resources.login.check_credentials',
        fake_check_credentials
        )
    response = client.post(
        '/login',
        json={'email': 'wrong@example.com', 'password': 'badpass'}
        )
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'


def test_login_missing_fields(client):
    """
    Test login with missing fields in the request body.

    Ensures that missing email or password returns a 401 status and an error
    message.
    """
    response = client.post('/login', json={'email': 'test@example.com'})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'

    response = client.post('/login', json={'password': 'password123'})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'

    response = client.post('/login', json={})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid email or password'
