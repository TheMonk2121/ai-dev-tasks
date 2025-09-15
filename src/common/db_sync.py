import psycopg2
from psycopg2.extras import RealDictCursor

from .db_dsn import resolve_dsn


def connect(role: str = "default"):
    """
    Create a psycopg2 database connection with resolved DSN.

    Args:
        role: Application role for connection tagging

    Returns:
        psycopg2 database connection
    """
    return psycopg2.connect(resolve_dsn(role=role), cursor_factory=RealDictCursor)
