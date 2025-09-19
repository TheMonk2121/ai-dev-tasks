"""
Database connection utilities using psycopg3.

This module provides database connection functionality using the project's
standardized psycopg3 configuration.
"""

from .psycopg3_config import connect as _psycopg3_connect


def connect(role: str | None = None):
    """
    Create a psycopg3 database connection with resolved DSN.

    Args:
        role: Application role for connection tagging

    Returns:
        psycopg3 database connection
    """
    return _psycopg3_connect(role or "default")
