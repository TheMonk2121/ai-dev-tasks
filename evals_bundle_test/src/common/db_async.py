import asyncpg

from .db_dsn import resolve_dsn


async def aconnect(role: str = "default") -> asyncpg.Connection:
    """
    Create an asyncpg database connection with resolved DSN.

    Args:
        role: Application role for connection tagging

    Returns:
        asyncpg database connection
    """
    return await asyncpg.connect(dsn=resolve_dsn(role=role))
