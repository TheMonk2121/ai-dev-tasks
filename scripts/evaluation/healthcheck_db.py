from __future__ import annotations
import sys
from pathlib import Path
import psycopg2
from common.db_dsn import resolve_dsn
import os
#!/usr/bin/env python3
"""Database healthcheck script for B-1070 validation."""

# Add src to path for resolver import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
        result = cur.fetchone()
        if result:
            print("server_version:", result[0])
        else:
            print("server_version: unknown")

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
        result = cur.fetchone()
        if result:
            ver = result[0]
        else:
            ver = "0"
        print("pgvector:", ver)
        if tuple(map(int, ver.split(".")[:2])) < (0, 8):
            print("ERROR: pgvector < 0.8.0; iterative_scan not available", file=sys.stderr)
            sys.exit(2)

        # Optional capability checks (don't fail)
        cur.execute("SHOW default_toast_compression;")
        result = cur.fetchone()
        if result:
            print("default_toast_compression:", result[0])
        else:
            print("default_toast_compression: unknown")

        cur.execute("SHOW wal_compression;")
        result = cur.fetchone()
        if result:
            print("wal_compression:", result[0])
        else:
            print("wal_compression: unknown")

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
            result = cur.fetchone()
            if result:
                print(f"{key}:", result[0])
            else:
                print(f"{key}: unknown")

        cur.close()
        conn.close()
        print("OK")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
