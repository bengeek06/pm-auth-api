# PM Auth API

[![Tests](https://github.com/bengeek06/pm-auth-api/actions/workflows/python-app.yml/badge.svg)](https://github.com/bengeek06/pm-auth-api/actions)
[![License: AGPL v3 / Commercial](https://img.shields.io/badge/license-AGPLv3%20%2F%20Commercial-blue)](LICENCE.md)
[![OpenAPI Spec](https://img.shields.io/badge/OpenAPI-3.0-blue.svg)](openapi.yml)
![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)
![Flask](https://img.shields.io/badge/flask-%3E=2.0-green.svg)
![Coverage](https://img.shields.io/badge/coverage-pytest-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)


---

## Overview

**PM Auth API** is a RESTful authentication service for user login, logout, token verification, refresh, and configuration/version endpoints.  
It uses JWT for access tokens and supports secure cookie-based authentication.

---

## Project Structure

```
.
├── app
│   ├── config.py
│   ├── __init__.py
│   ├── logger.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── refresh_token.py
│   │   └── token_blacklist.py
│   ├── resources
│   │   ├── config.py
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── logout.py
│   │   ├── refresh.py
│   │   ├── verify.py
│   │   └── version.py
│   ├── routes.py
│   └── utils.py
├── CODE_OF_CONDUCT.md
├── COMMERCIAL-LICENCE.txt
├── Dockerfile
├── env.example
├── instance/
├── LICENCE.md
├── migrations/
├── openapi.yml
├── pytest.ini
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── run.py
├── tests/
├── wait-for-it.sh
└── wsgi.py
```

---

## Environments

The application supports multiple environments, each with its own configuration:

- **Development**: For local development. Debug mode enabled.
- **Testing**: For running automated tests. Uses a separate test database.
- **Staging**: For pre-production validation. Debug mode enabled, but production-like settings.
- **Production**: For live deployments. Debug mode disabled, secure settings.

Set the environment with the `FLASK_ENV` environment variable (`development`, `testing`, `staging`, `production`).  
Database URL and secrets are configured via environment variables (see `env.example`).

---

## Features

- User authentication with JWT access and refresh tokens
- Token revocation (blacklist)
- Token refresh endpoint
- Configuration and version endpoints
- Secure HttpOnly cookies for tokens
- OpenAPI 3.0 documentation

---

## Quickstart

### Requirements

- Python 3.11+
- pip

### Installation

```bash
git clone https://github.com/bengeek06/pm-auth-api.git
cd pm-auth-api
pip install -r requirements.txt
```

### Environment

Copy and edit the example environment file:

```bash
cp env.example .env
```

Set at least:

- `FLASK_ENV=development`
- `DATABASE_URL=sqlite:///pm-auth.db`
- `SECRET_KEY=your_secret`
- `JWT_SECRET=your_jwt_secret`

### Running

```bash
flask run
```

Or with Gunicorn:

```bash
gunicorn wsgi:app
```

---

## API Documentation

The OpenAPI specification is available in [openapi.yml](openapi.yml).  
You can visualize it with [Swagger Editor](https://editor.swagger.io/) or [Redoc](https://redocly.github.io/redoc/).

---

## Endpoints

| Method | Path      | Description                    |
|--------|-----------|--------------------------------|
| POST   | /login    | User login, returns tokens     |
| POST   | /logout   | User logout, revokes tokens    |
| POST   | /refresh  | Refresh access token           |
| GET    | /verify   | Verify access token            |
| GET    | /config   | Get app configuration          |
| GET    | /version  | Get API version                |

---

## Running Tests

```bash
pytest
```

---

## License

This project is dual-licensed:

- **Community version**: [GNU AGPLv3](https://www.gnu.org/licenses/agpl-3.0.html)
- **Commercial license**: See [LICENCE.md](LICENCE.md) and [COMMERCIAL-LICENCE.txt](COMMERCIAL-LICENCE.txt)

For commercial use or support, contact: **bengeek06@gmail.com**

---

## Contributing

See [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for guidelines.

---
