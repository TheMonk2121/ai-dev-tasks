#!/usr/bin/env python3
"""
Bullet‑proof database connection pool implementation with per‑role GUCs.

Adds:
- Safe, global `ThreadedConnectionPool` with connection health check.
- Per‑role/session GUCs applied on checkout (timeouts, work_mem, search_path,
  plan_cache_mode) to support plan/cache separation and predictable behavior.
- TCP keepalive and connect/statement timeouts to avoid "flaky" hangs.
"""

import contextlib
import logging
import os

from psycopg2.pool import ThreadedConnectionPool

try:
    # Optional typing only
    from typing import Dict, Optional
except Exception:  # pragma: no cover
    Dict = dict  # type: ignore
    Optional = object  # type: ignore

log = logging.getLogger("db_pool")

_POOL = None

# Default environment-driven settings (can be overridden per process)
_DEFAULTS = {
    "DB_APP_NAME": os.getenv("DB_APP_NAME", "ai-agency"),
    "DB_CONNECT_TIMEOUT": int(os.getenv("DB_CONNECT_TIMEOUT", "5")),  # seconds
    "DB_STATEMENT_TIMEOUT_MS": int(os.getenv("DB_STATEMENT_TIMEOUT_MS", "30000")),
    "DB_IDLE_IN_TX_TIMEOUT_MS": int(os.getenv("DB_IDLE_IN_TX_TIMEOUT_MS", "10000")),
    # TCP keepalive parameters (Linux/macOS compatible)
    "DB_KEEPALIVES": int(os.getenv("DB_KEEPALIVES", "1")),
    "DB_KEEPALIVES_IDLE": int(os.getenv("DB_KEEPALIVES_IDLE", "30")),
    "DB_KEEPALIVES_INTERVAL": int(os.getenv("DB_KEEPALIVES_INTERVAL", "10")),
    "DB_KEEPALIVES_COUNT": int(os.getenv("DB_KEEPALIVES_COUNT", "3")),
}

# Role -> GUC profile (tune as needed)
_ROLE_GUCS = {
    # Retrieval-heavy: larger work_mem for CTE / ranking; prefer custom plans
    "retrieval": {
        "work_mem": os.getenv("DB_GUC_WORK_MEM_RETRIEVAL", "128MB"),
        "plan_cache_mode": os.getenv("DB_GUC_PLAN_CACHE_MODE_RETRIEVAL", "force_custom_plan"),
        # Example: restrict schema if desired
        # "search_path": os.getenv("DB_GUC_SEARCH_PATH_RETRIEVAL", "public"),
    },
    # Writers/background tasks: conservative memory
    "writer": {
        "work_mem": os.getenv("DB_GUC_WORK_MEM_WRITER", "32MB"),
        "plan_cache_mode": os.getenv("DB_GUC_PLAN_CACHE_MODE_WRITER", "auto"),
    },
    # Evaluation/analytics
    "eval": {
        "work_mem": os.getenv("DB_GUC_WORK_MEM_EVAL", "64MB"),
        "plan_cache_mode": os.getenv("DB_GUC_PLAN_CACHE_MODE_EVAL", "auto"),
    },
}


def init_pool(minconn=1, maxconn=10) -> None:
    """Initialize the database connection pool."""
    global _POOL
    if _POOL:
        return
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL not set")
    # Build connection kwargs for keepalives/timeouts and observability
    conn_kwargs = {
        "dsn": url,
        "application_name": _DEFAULTS["DB_APP_NAME"],
        "connect_timeout": _DEFAULTS["DB_CONNECT_TIMEOUT"],
        "keepalives": _DEFAULTS["DB_KEEPALIVES"],
        "keepalives_idle": _DEFAULTS["DB_KEEPALIVES_IDLE"],
        "keepalives_interval": _DEFAULTS["DB_KEEPALIVES_INTERVAL"],
        "keepalives_count": _DEFAULTS["DB_KEEPALIVES_COUNT"],
    }
    _POOL = ThreadedConnectionPool(minconn, maxconn, **conn_kwargs)
    log.info("DB pool ready: %s-%s", minconn, maxconn)


def close_pool() -> None:
    """Close the database connection pool."""
    global _POOL
    if _POOL:
        _POOL.closeall()
        _POOL = None


def _apply_session_gucs(conn, *, role: Optional[str] = None, extra_gucs: Optional[Dict[str, str]] = None) -> None:
    """Apply per-session and per-role GUCs on a live connection.

    This is called on every checkout to ensure predictability even after
    server-side resets. Ignores unsupported GUCs safely.
    """
    gucs: Dict[str, str] = {}
    # Timeouts apply to all roles
    gucs["statement_timeout"] = str(_DEFAULTS["DB_STATEMENT_TIMEOUT_MS"])  # ms
    gucs["idle_in_transaction_session_timeout"] = str(_DEFAULTS["DB_IDLE_IN_TX_TIMEOUT_MS"])  # ms
    # Include role in application_name for observability
    if role:
        gucs["application_name"] = f"{_DEFAULTS['DB_APP_NAME']}:{role}"

    # Merge role profile
    if role and role in _ROLE_GUCS:
        gucs.update({k: str(v) for k, v in _ROLE_GUCS[role].items()})

    # Merge explicit overrides last
    if extra_gucs:
        gucs.update({k: str(v) for k, v in extra_gucs.items()})

    # Apply
    with conn.cursor() as cur:
        for k, v in gucs.items():
            try:
                cur.execute(f"SET {k} = %s;", (v,))
            except Exception:
                # Non-fatal: ignore unknown or unsupported GUCs
                log.debug("Ignoring unsupported GUC %s=%s", k, v)


@contextlib.contextmanager
def get_conn(*, role: Optional[str] = None, extra_gucs: Optional[Dict[str, str]] = None):
    """Yield a dedicated psycopg2 connection from the pool.
    Applies per-role GUCs and timeouts on checkout.
    """
    if _POOL is None:
        init_pool()
    conn = None
    try:
        conn = _POOL.getconn()
        # quick health check — fast and safe
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
        # apply session-level configuration
        try:
            _apply_session_gucs(conn, role=role, extra_gucs=extra_gucs)
        except Exception:
            log.exception("Failed applying session GUCs (role=%s)", role)
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
