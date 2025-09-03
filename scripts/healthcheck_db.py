#!/usr/bin/env python3
"""Database healthcheck script for B-1070 validation."""

import sys
from pathlib import Path

import psycopg2

# Add src to path for resolver import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from common.db_dsn import resolve_dsn


def main():
    """Run database healthcheck and exit with appropriate code."""
    try:
        # Resolve DSN
        dsn = resolve_dsn(strict=True)
        if not dsn:
            print("ERROR: No DSN resolved", file=sys.stderr)
            sys.exit(1)

        # Connect and validate
        conn = psycopg2.connect(dsn)
        cur = conn.cursor()

        # Basic facts
        cur.execute("SHOW server_version;")
        print("server_version:", cur.fetchone()[0])

        # Check required extensions
        cur.execute(
            """
            SELECT extname, extversion
            FROM pg_extension
            WHERE extname IN ('vector','pg_stat_statements')
            ORDER BY extname;
        """
        )
        extensions = cur.fetchall()
        print("extensions:", extensions)

        # pgvector version check (0.8.0+ required for iterative_scan)
        cur.execute("SELECT extversion FROM pg_extension WHERE extname='vector';")
        ver = (cur.fetchone() or ["0"])[0]
        print("pgvector:", ver)
        if tuple(map(int, ver.split(".")[:2])) < (0, 8):
            print("ERROR: pgvector < 0.8.0; iterative_scan not available", file=sys.stderr)
            sys.exit(2)

        # Optional capability checks (don't fail)
        cur.execute("SHOW default_toast_compression;")
        print("default_toast_compression:", cur.fetchone()[0])

        cur.execute("SHOW wal_compression;")
        print("wal_compression:", cur.fetchone()[0])

        # Key settings of interest
        for key in (
            "shared_buffers",
            "effective_cache_size",
            "work_mem",
            "maintenance_work_mem",
            "jit",
            "track_io_timing",
        ):
            cur.execute(f"SHOW {key};")
            print(f"{key}:", cur.fetchone()[0])

        cur.close()
        conn.close()
        print("OK")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
