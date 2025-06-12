"""
models.__init__.py
------------------
This module initializes the SQLAlchemy database instance for the application.
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
