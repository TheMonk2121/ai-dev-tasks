#!/usr/bin/env python3
"""
Read-only database readiness checker.

Verifies:
- Can resolve and connect to DB via `DATABASE_URL` (or `POSTGRES_DSN` fallback)
- Required extensions exist and pgvector version is adequate (>= 0.8)
- Presence of critical tables from the LTST + legacy memory schemas

Exits non-zero on failure; prints a concise summary for CI/PR gates.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterable

import psycopg2

# Add src to path for resolver import
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from common.db_dsn import resolve_dsn  # noqa: E402

CRITICAL_TABLES: tuple[str, ...] = (
    # LTST schema core
    "conversation_sessions",
    "conversation_messages",
    "conversation_context",
    "user_preferences",
    "memory_retrieval_cache",
    # Relationships and metrics
    "session_relationships",
    "memory_performance_metrics",
    # Backward-compatibility (existing prod tables expected to remain)
    "documents",
    "document_chunks",
    "conversation_memory",
)


def check_extensions(cur) -> tuple[bool, list[str]]:
    cur.execute(
        """
        SELECT extname, extversion
        FROM pg_extension
        WHERE extname IN ('vector','pg_stat_statements')
        ORDER BY extname;
        """
    )
    rows = cur.fetchall()
    found = {row[0]: row[1] for row in rows}
    missing = [e for e in ("vector", "pg_stat_statements") if e not in found]

    # vector version check >= 0.8
    ok = True
    msgs = []
    if missing:
        ok = False
        msgs.append(f"Missing extensions: {', '.join(missing)}")
    vec_ver = found.get("vector")
    if vec_ver:
        try:
            major_minor = tuple(int(x) for x in vec_ver.split(".")[:2])
            if major_minor < (0, 8):
                ok = False
                msgs.append(f"pgvector too old: {vec_ver} (< 0.8)")
        except Exception:
            # Non-fatal, but warn
            msgs.append(f"Unable to parse pgvector version: {vec_ver}")
    return ok, msgs


def table_exists(cur, table: str) -> bool:
    cur.execute(
        """
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = 'public' AND table_name = %s
        );
        """,
        (table,),
    )
    return bool(cur.fetchone()[0])


def check_tables(cur, tables: Iterable[str]) -> tuple[bool, list[str]]:
    missing: list[str] = []
    for t in tables:
        try:
            if not table_exists(cur, t):
                missing.append(t)
        except Exception as e:
            missing.append(f"{t} (error: {e})")
    return (len(missing) == 0), missing


def main() -> int:
    try:
        dsn = resolve_dsn(strict=True)
    except Exception as e:
        print(f"ERROR: DSN resolution failed: {e}", file=sys.stderr)
        return 1

    try:
        conn = psycopg2.connect(dsn)
    except Exception as e:
        print(f"ERROR: DB connection failed: {e}", file=sys.stderr)
        return 1

    try:
        cur = conn.cursor()

        # Basic server info
        cur.execute("SHOW server_version;")
        server_version = cur.fetchone()[0]

        # Extensions
        ext_ok, ext_msgs = check_extensions(cur)

        # Critical tables
        tables_ok, missing_tables = check_tables(cur, CRITICAL_TABLES)

        # Summary output
        status = "OK" if (ext_ok and tables_ok) else "FAIL"
        print("db_server_version:", server_version)
        print("extensions_ok:", ext_ok)
        if ext_msgs:
            print("extensions_notes:", "; ".join(ext_msgs))
        print("critical_tables_ok:", tables_ok)
        if not tables_ok:
            print("missing_tables:", ", ".join(missing_tables))
        print("READINESS:", status)

        return 0 if (ext_ok and tables_ok) else 2
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())

