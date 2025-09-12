from __future__ import annotations
import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import Any, Optional
    import psycopg2
    from psycopg2.extras import RealDictCursor
        import subprocess
import sys
from typing import Any, Dict, List, Optional, Union
"""
Maintenance Metrics Database Integration

Stores maintenance analysis data in PostgreSQL following the same pattern
as evaluation_metrics table. Integrates with existing monitoring system.
"""


try:

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class MaintenanceMetricsDB:
    """Database integration for maintenance metrics following evaluation_metrics pattern."""

    def __init__(self, database_url: str | None = None):
        """Initialize with database connection."""
        self.database_url = database_url or os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("Database URL required (POSTGRES_DSN or DATABASE_URL)")

        # Determine database type
        self.is_sqlite = (
            self.database_url == ":memory:"
            or self.database_url.startswith("sqlite://")
            or self.database_url.endswith(".db")
            or "/tmp/" in self.database_url
        )
        self.is_postgres = not self.is_sqlite and PSYCOPG2_AVAILABLE

    def store_maintenance_session(
        self,
        session_id: str,
        maintenance_type: str,
        status: str,
        files_removed: int = 0,
        directories_removed: int = 0,
        bytes_freed: int = 0,
        duration_seconds: float = 0.0,
        error_count: int = 0,
        analysis_data: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        git_sha: str | None = None,
    ) -> bool:
        """
        Store maintenance session data following evaluation_metrics pattern.

        Args:
            session_id: Unique session identifier
            maintenance_type: Type of maintenance ('cache_cleanup', 'log_cleanup', 'full_cleanup')
            status: Session status ('success', 'partial', 'failed')
            files_removed: Number of files removed
            directories_removed: Number of directories removed
            bytes_freed: Bytes freed during cleanup
            duration_seconds: Duration of maintenance session
            error_count: Number of errors encountered
            analysis_data: Detailed analysis and lessons learned (JSONB)
            metadata: Additional context (JSONB)
            git_sha: Git commit SHA

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.is_sqlite:
                return self._store_sqlite(
                    session_id,
                    maintenance_type,
                    status,
                    files_removed,
                    directories_removed,
                    bytes_freed,
                    duration_seconds,
                    error_count,
                    analysis_data,
                    metadata,
                    git_sha,
                )
            elif self.is_postgres:
                return self._store_postgres(
                    session_id,
                    maintenance_type,
                    status,
                    files_removed,
                    directories_removed,
                    bytes_freed,
                    duration_seconds,
                    error_count,
                    analysis_data,
                    metadata,
                    git_sha,
                )
            else:
                print("No supported database driver available")
                return False

        except Exception as e:
            print(f"Error storing maintenance metrics: {e}")
            return False

    def get_maintenance_history(
        self, maintenance_type: str | None = None, days: int = 30, limit: int = 100
    ) -> list[dict[str, Any]]:
        """
        Get maintenance history following evaluation_metrics query pattern.

        Args:
            maintenance_type: Filter by maintenance type
            days: Number of days to look back
            limit: Maximum number of records to return

        Returns:
            List of maintenance records
        """
        try:
            if self.is_sqlite:
                return self._get_history_sqlite(maintenance_type, days, limit)
            elif self.is_postgres:
                return self._get_history_postgres(maintenance_type, days, limit)
            else:
                print("No supported database driver available")
                return []

        except Exception as e:
            print(f"Error retrieving maintenance history: {e}")
            return []

    def _get_history_sqlite(self, maintenance_type: str | None, days: int, limit: int) -> list[dict[str, Any]]:
        """Get maintenance history from SQLite database."""
        if self.database_url is None:
            raise ValueError("Database URL is None")
        with sqlite3.connect(self.database_url) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Ensure table exists
            self._ensure_sqlite_table_exists(cur)

            query = f"""
            SELECT ts, session_id, maintenance_type, status, files_removed,
                   directories_removed, bytes_freed, duration_seconds, error_count,
                   analysis_data, metadata, git_sha
            FROM maintenance_metrics
            WHERE ts >= datetime('now', '-{days} days')
            """
            params = []

            if maintenance_type:
                query += " AND maintenance_type = ?"
                params.append(maintenance_type)

            query += " ORDER BY ts DESC LIMIT ?"
            params.append(limit)

            cur.execute(query, params)
            rows = [dict(row) for row in cur.fetchall()]

            # Parse JSON fields
            for row in rows:
                if row.get("analysis_data"):
                    try:
                        row["analysis_data"] = json.loads(row["analysis_data"])
                    except (json.JSONDecodeError, TypeError):
                        row["analysis_data"] = None
                if row.get("metadata"):
                    try:
                        row["metadata"] = json.loads(row["metadata"])
                    except (json.JSONDecodeError, TypeError):
                        row["metadata"] = None

            return rows

    def _get_history_postgres(self, maintenance_type: str | None, days: int, limit: int) -> list[dict[str, Any]]:
        """Get maintenance history from PostgreSQL database."""
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                SELECT ts, session_id, maintenance_type, status, files_removed,
                       directories_removed, bytes_freed, duration_seconds, error_count,
                       analysis_data, metadata, git_sha
                FROM maintenance_metrics
                WHERE ts >= now() - interval '%s days'
                """
                params: list[Any] = [days]

                if maintenance_type:
                    query += " AND maintenance_type = %s"
                    params.append(maintenance_type)

                query += " ORDER BY ts DESC LIMIT %s"
                params.append(limit)

                cur.execute(query, params)
                return [dict(row) for row in cur.fetchall()]

    def _store_sqlite(
        self,
        session_id: str,
        maintenance_type: str,
        status: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
        analysis_data: dict[str, Any] | None,
        metadata: dict[str, Any] | None,
        git_sha: str | None,
    ) -> bool:
        """Store maintenance session in SQLite database."""
        if self.database_url is None:
            raise ValueError("Database URL is None")
        with sqlite3.connect(self.database_url) as conn:
            cur = conn.cursor()
            # Create table if it doesn't exist
            self._ensure_sqlite_table_exists(cur)

            # Insert maintenance metrics
            cur.execute(
                """
                INSERT INTO maintenance_metrics
                (ts, session_id, maintenance_type, status, files_removed, 
                 directories_removed, bytes_freed, duration_seconds, error_count,
                 analysis_data, metadata, git_sha)
                VALUES
                (datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    maintenance_type,
                    status,
                    files_removed,
                    directories_removed,
                    bytes_freed,
                    duration_seconds,
                    error_count,
                    json.dumps(analysis_data) if analysis_data else None,
                    json.dumps(metadata) if metadata else None,
                    git_sha,
                ),
            )
            conn.commit()
            return True

    def _store_postgres(
        self,
        session_id: str,
        maintenance_type: str,
        status: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
        analysis_data: dict[str, Any] | None,
        metadata: dict[str, Any] | None,
        git_sha: str | None,
    ) -> bool:
        """Store maintenance session in PostgreSQL database."""
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor() as cur:
                # Create table if it doesn't exist
                self._ensure_table_exists(cur)

                # Insert maintenance metrics
                cur.execute(
                    """
                    INSERT INTO maintenance_metrics
                    (ts, session_id, maintenance_type, status, files_removed, 
                     directories_removed, bytes_freed, duration_seconds, error_count,
                     analysis_data, metadata, git_sha)
                    VALUES
                    (now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        session_id,
                        maintenance_type,
                        status,
                        files_removed,
                        directories_removed,
                        bytes_freed,
                        duration_seconds,
                        error_count,
                        json.dumps(analysis_data) if analysis_data else None,
                        json.dumps(metadata) if metadata else None,
                        git_sha,
                    ),
                )
                conn.commit()
                return True

    def get_maintenance_summary(self, days: int = 30) -> dict[str, Any]:
        """
        Get maintenance summary statistics.

        Args:
            days: Number of days to analyze

        Returns:
            Summary statistics
        """
        try:
            if self.is_sqlite:
                return self._get_summary_sqlite(days)
            elif self.is_postgres:
                return self._get_summary_postgres(days)
            else:
                print("No supported database driver available")
                return {}

        except Exception as e:
            print(f"Error retrieving maintenance summary: {e}")
            return {}

    def _get_summary_sqlite(self, days: int) -> dict[str, Any]:
        """Get maintenance summary from SQLite database."""
        if self.database_url is None:
            raise ValueError("Database URL is None")
        with sqlite3.connect(self.database_url) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()

            # Ensure table exists
            self._ensure_sqlite_table_exists(cur)

            cur.execute(
                f"""
                SELECT 
                    maintenance_type,
                    COUNT(*) as total_sessions,
                    AVG(files_removed) as avg_files_removed,
                    AVG(directories_removed) as avg_directories_removed,
                    AVG(bytes_freed) as avg_bytes_freed,
                    AVG(duration_seconds) as avg_duration_seconds,
                    AVG(error_count) as avg_error_count,
                    SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_sessions
                FROM maintenance_metrics
                WHERE ts >= datetime('now', '-{days} days')
                GROUP BY maintenance_type
                ORDER BY total_sessions DESC
                """
            )

            results = [dict(row) for row in cur.fetchall()]

            # Calculate overall statistics
            total_sessions = sum(r["total_sessions"] for r in results)
            total_successful = sum(r["successful_sessions"] for r in results)
            success_rate = (total_successful / total_sessions * 100) if total_sessions > 0 else 0

            return {
                "period_days": days,
                "total_sessions": total_sessions,
                "success_rate": round(success_rate, 2),
                "by_type": results,
                "timestamp": datetime.now().isoformat(),
            }

    def _get_summary_postgres(self, days: int) -> dict[str, Any]:
        """Get maintenance summary from PostgreSQL database."""
        with psycopg2.connect(self.database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT 
                        maintenance_type,
                        COUNT(*) as total_sessions,
                        AVG(files_removed) as avg_files_removed,
                        AVG(directories_removed) as avg_directories_removed,
                        AVG(bytes_freed) as avg_bytes_freed,
                        AVG(duration_seconds) as avg_duration_seconds,
                        AVG(error_count) as avg_error_count,
                        SUM(CASE WHEN status = 'success' THEN 1 ELSE 0 END) as successful_sessions
                    FROM maintenance_metrics
                    WHERE ts >= now() - interval '%s days'
                    GROUP BY maintenance_type
                    ORDER BY total_sessions DESC
                    """,
                    [days],
                )

                results = [dict(row) for row in cur.fetchall()]

                # Calculate overall statistics
                total_sessions = sum(r["total_sessions"] for r in results)
                total_successful = sum(r["successful_sessions"] for r in results)
                success_rate = (total_successful / total_sessions * 100) if total_sessions > 0 else 0

                return {
                    "period_days": days,
                    "total_sessions": total_sessions,
                    "success_rate": round(success_rate, 2),
                    "by_type": results,
                    "timestamp": datetime.now().isoformat(),
                }

    def _ensure_sqlite_table_exists(self, cur) -> None:
        """Ensure maintenance_metrics table exists in SQLite with proper structure."""
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenance_metrics (
                ts TEXT NOT NULL DEFAULT (datetime('now')),
                session_id TEXT NOT NULL,
                maintenance_type TEXT NOT NULL,
                status TEXT NOT NULL,
                files_removed INTEGER DEFAULT 0,
                directories_removed INTEGER DEFAULT 0,
                bytes_freed INTEGER DEFAULT 0,
                duration_seconds REAL,
                error_count INTEGER DEFAULT 0,
                analysis_data TEXT,
                metadata TEXT,
                git_sha TEXT,
                PRIMARY KEY (ts, session_id)
            )
            """
        )

        # Create indexes
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_type_ts 
            ON maintenance_metrics (maintenance_type, ts)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_session_id 
            ON maintenance_metrics (session_id)
            """
        )

    def _ensure_table_exists(self, cur) -> None:
        """Ensure maintenance_metrics table exists with proper structure."""
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS maintenance_metrics (
                ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                session_id UUID NOT NULL,
                maintenance_type VARCHAR(100) NOT NULL,
                status VARCHAR(50) NOT NULL,
                files_removed INTEGER DEFAULT 0,
                directories_removed INTEGER DEFAULT 0,
                bytes_freed BIGINT DEFAULT 0,
                duration_seconds REAL,
                error_count INTEGER DEFAULT 0,
                analysis_data JSONB,
                metadata JSONB,
                git_sha VARCHAR(40),
                PRIMARY KEY (ts, session_id)
            )
            """
        )

        # Create indexes
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_type_ts 
            ON maintenance_metrics (maintenance_type, ts)
            """
        )

        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_session_id 
            ON maintenance_metrics (session_id)
            """
        )

        # Try to create hypertable if TimescaleDB is available
        try:
            cur.execute(
                """
                SELECT create_hypertable('maintenance_metrics', 'ts', if_not_exists => true)
                """
            )
        except Exception:
            # TimescaleDB not available, that's fine
            pass


def get_git_sha() -> str | None:
    """Get current git SHA for tracking."""
    try:

        result = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()[:40]  # First 40 characters
    except Exception:
        return None


def store_maintenance_analysis(
    session_id: str,
    maintenance_type: str,
    cleanup_results: dict[str, Any],
    analysis_data: dict[str, Any],
    metadata: dict[str, Any] | None = None,
    database_url: str | None = None,
) -> bool:
    """
    Convenience function to store maintenance analysis data.

    Args:
        session_id: Unique session identifier
        maintenance_type: Type of maintenance performed
        cleanup_results: Results from maintenance_cleanup.py
        analysis_data: Detailed analysis from cache analysis
        metadata: Additional metadata
        database_url: Optional database URL override

    Returns:
        bool: True if successful
    """
    db = MaintenanceMetricsDB(database_url=database_url)

    # Extract metrics from cleanup results
    files_removed = cleanup_results.get("files_removed", 0)
    directories_removed = cleanup_results.get("directories_removed", 0)
    bytes_freed = cleanup_results.get("bytes_freed", 0)
    duration_seconds = cleanup_results.get("duration_seconds", 0.0)
    error_count = cleanup_results.get("error_count", 0)
    status = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"

    return db.store_maintenance_session(
        session_id=session_id,
        maintenance_type=maintenance_type,
        status=status,
        files_removed=files_removed,
        directories_removed=directories_removed,
        bytes_freed=bytes_freed,
        duration_seconds=duration_seconds,
        error_count=error_count,
        analysis_data=analysis_data,
        metadata=metadata,
        git_sha=get_git_sha(),
    )
