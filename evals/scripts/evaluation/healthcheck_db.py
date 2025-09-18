#!/usr/bin/env python3
"""Database healthcheck script for B-1070 validation."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config


def main():
    """Run database healthcheck and exit with appropriate code."""

    try:
        # Resolve DSN
        _ = resolve_dsn(strict=True)

        # Connect and validate
        with Psycopg3Config.get_cursor("default") as cur:
            # Basic facts
            _ = cur.execute("SHOW server_version;")
            result = cur.fetchone()
            if result:
                print("server_version:", result.get("server_version", ""))
            else:
                print("server_version: unknown")

            # Check required extensions
            _ = cur.execute(
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
            _ = cur.execute("SELECT extversion FROM pg_extension WHERE extname='vector';")
            result = cur.fetchone()
            if result:
                ver = result.get("extversion", "")
            else:
                ver = "0"
            print("pgvector:", ver)
            if tuple(map(int, ver.split(".")[:2])) < (0, 8):
                print("ERROR: pgvector < 0.8.0; iterative_scan not available", file=sys.stderr)
                sys.exit(2)

            # Optional capability checks (don't fail)
            _ = cur.execute("SHOW default_toast_compression;")
            result = cur.fetchone()
            if result:
                print("default_toast_compression:", result.get("default_toast_compression", ""))
            else:
                print("default_toast_compression: unknown")

            _ = cur.execute("SHOW wal_compression;")
            result = cur.fetchone()
            if result:
                print("wal_compression:", result.get("wal_compression", ""))
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
                _ = cur.execute(f"SHOW {key};")
                result = cur.fetchone()
                if result:
                    print(f"{key}:", result.get(key, ""))
                else:
                    print(f"{key}: unknown")

        print("OK")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
