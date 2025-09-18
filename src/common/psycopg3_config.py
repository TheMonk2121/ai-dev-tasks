"""
Centralized psycopg3 configuration for AI Dev Tasks project.
Provides standardized connection patterns and fixes type issues.
"""

from contextlib import contextmanager
from typing import Any, cast

import psycopg
from psycopg.rows import DictRow, dict_row

from src.common.db_dsn import resolve_dsn


class Psycopg3Config:
    """Centralized psycopg3 configuration and connection management."""

    # Standard connection parameters optimized for AI Dev Tasks
    DEFAULT_CONNECTION_PARAMS: dict[str, Any] = {
        "application_name": "ai-dev-tasks",
        "connect_timeout": 10,
        "command_timeout": 300,  # 5 minutes for complex vector queries
        "options": [
            "-c default_transaction_isolation=read_committed",
            "-c work_mem=256MB",  # Increased for vector operations
            "-c maintenance_work_mem=1GB",  # For vector index maintenance
            "-c effective_cache_size=32GB",  # Utilize 128GB RAM
            "-c shared_buffers=8GB",  # Increased buffer pool
            "-c random_page_cost=1.1",  # SSD optimization
            "-c effective_io_concurrency=200",  # SSD parallel I/O
        ],
    }

    # Vector-specific optimizations
    VECTOR_OPTIMIZATIONS: dict[str, str] = {
        "vector.hnsw_ef_search": "100",  # Higher precision for vector search
        "vector.hnsw_ef_construction": "200",  # Better index quality
        "vector.hnsw_m": "16",  # Optimal for 384-dim vectors
    }

    @classmethod
    def get_connection_params(cls, role: str = "default", **overrides: Any) -> dict[str, Any]:
        """Get connection parameters with role-specific optimizations."""
        params = cls.DEFAULT_CONNECTION_PARAMS.copy()
        # Add vector optimizations for vector-heavy roles
        if role in ["ltst", "retrieval", "vector"]:
            vector_options = [f"-c {k}={v}" for k, v in cls.VECTOR_OPTIMIZATIONS.items()]
            params["options"].extend(vector_options)

        # Apply overrides
        params.update(overrides)
        return params

    @classmethod
    def create_connection(cls, role: str = "default", **overrides: Any) -> psycopg.Connection[DictRow]:
        """
        Create a psycopg3 connection with proper typing and configuration.

        This method fixes the type issues by using cursor-level row factory
        instead of connection-level, which avoids psycopg3's strict typing.
        """
        dsn = resolve_dsn(role=role)
        params = cls.get_connection_params(role, **overrides)

        # Create connection without row_factory to avoid type issues
        conn = psycopg.connect(dsn, **params)
        return cast(psycopg.Connection[DictRow], conn)

    @classmethod
    @contextmanager
    def get_connection(cls, role: str = "default", **overrides: Any):
        """
        Context manager for database connections with automatic cleanup.

        Usage:
            with Psycopg3Config.get_connection("ltst") as conn:
                with conn.cursor(row_factory=dict_row) as cur:
                    cur.execute("SELECT * FROM table")
                    results = cur.fetchall()
        """
        conn = cls.create_connection(role, **overrides)
        try:
            yield conn
        finally:
            conn.close()

    @classmethod
    @contextmanager
    def get_cursor(cls, role: str = "default", **overrides: Any):
        """
        Context manager for database cursors with dict_row factory.

        Usage:
            with Psycopg3Config.get_cursor("ltst") as cur:
                cur.execute("SELECT * FROM table")
                results = cur.fetchall()  # Returns list[dict[str, Any]]
        """
        with cls.get_connection(role, **overrides) as conn:
            with conn.cursor(row_factory=dict_row) as cur:
                yield cur


# Convenience functions for common patterns
def get_db_connection(role: str = "default") -> psycopg.Connection[DictRow]:
    """Get a database connection with proper configuration."""
    return Psycopg3Config.create_connection(role)


def get_db_cursor(role: str = "default"):
    """Get a database cursor with dict_row factory."""
    return Psycopg3Config.get_cursor(role)


# Legacy compatibility functions
def connect(role: str = "default"):
    """Legacy compatibility function - use get_db_connection instead."""
    return get_db_connection(role)


# Migration helper functions
def migrate_connection_pattern(old_connection_code: str) -> str:
    """
    Migrate old connection patterns to new standardized patterns.

    This helps convert existing code to use the new configuration.
    """
    # Pattern 1: Direct psycopg.connect with row_factory
    if "psycopg.connect" in old_connection_code and "row_factory=dict_row" in old_connection_code:
        return old_connection_code.replace(
            "psycopg.connect(dsn, row_factory=dict_row)", "Psycopg3Config.create_connection(role)"
        )

    # Pattern 2: Connection with type ignore
    if "type: ignore" in old_connection_code and "row_factory" in old_connection_code:
        return old_connection_code.replace(
            "conn = psycopg.connect(dsn, row_factory=dict_row)  # type: ignore[arg-type]",
            "conn = Psycopg3Config.create_connection(role)",
        )

    return old_connection_code


# Performance monitoring
class ConnectionMonitor:
    """Monitor database connection performance and health."""

    def __init__(self) -> None:
        self.connection_count: int = 0
        self.slow_queries: list[tuple[str, float]] = []

    def log_connection(self, role: str, duration: float) -> None:
        """Log connection metrics."""
        self.connection_count += 1
        if duration > 1.0:  # Log slow connections
            self.slow_queries.append((role, duration))

    def get_stats(self) -> dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": self.connection_count,
            "slow_queries": len(self.slow_queries),
            "slow_query_details": self.slow_queries[-10:],  # Last 10 slow queries
        }


# Global monitor instance
connection_monitor = ConnectionMonitor()
