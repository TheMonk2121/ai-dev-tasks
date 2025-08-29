#!/usr/bin/env python3
"""
Bullet-proof database connection pool implementation.
Fixes the KeyError: 0 and threading issues in the original DatabaseResilienceManager.
"""

import contextlib
import logging
import os

from psycopg2.pool import ThreadedConnectionPool

log = logging.getLogger("db_pool")

_POOL = None


def init_pool(minconn=1, maxconn=10) -> None:
    """Initialize the database connection pool."""
    global _POOL
    if _POOL:
        return
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    _POOL = ThreadedConnectionPool(minconn, maxconn, dsn=url)
    log.info("DB pool ready: %s-%s", minconn, maxconn)


def close_pool() -> None:
    """Close the database connection pool."""
    global _POOL
    if _POOL:
        _POOL.closeall()
        _POOL = None


@contextlib.contextmanager
def get_conn():
    """Yield a dedicated psycopg2 connection from the pool.
    Always returns a REAL connection (not a contextmanager).
    """
    if _POOL is None:
        init_pool()
    conn = None
    try:
        conn = _POOL.getconn()
        # quick health check — fast and safe
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        yield conn
        # caller commits; if they forget, we can force it:
        # conn.commit()
    except Exception:
        if conn:
            conn.rollback()
        log.exception("DB get_conn() failure")
        raise
    finally:
        if conn:
            _POOL.putconn(conn)


def execute_query(query: str, params=None):
    """Execute a query and return results."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                return cur.fetchall()
            else:
                conn.commit()
                return cur.rowcount


def execute_transaction(queries):
    """Execute multiple queries in a transaction."""
    with get_conn() as conn:
        with conn.cursor() as cur:
            results = []
            for query, params in queries:
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    results.extend(cur.fetchall())
                else:
                    results.append(cur.rowcount)
            conn.commit()
            return results
