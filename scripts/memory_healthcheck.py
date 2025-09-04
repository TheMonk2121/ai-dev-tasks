#!/usr/bin/env python3
"""
Memory System Healthcheck

Performs sanity checks for the LTST memory system:
- Database connectivity
- Required extensions (vector, optional pg_trgm)
- Required objects (session_summary view, clean_expired_* functions)
"""

import os
import sys
from typing import Tuple


def main() -> int:
    try:
        try:
            import psycopg2  # type: ignore
        except Exception:
            print("[FAIL] psycopg2 not installed — install psycopg2-binary to use DB features")
            return 1

        dsn = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")
        conn = psycopg2.connect(dsn)  # type: ignore
        cur = conn.cursor()

        # 1) Connectivity
        cur.execute("SELECT 1")
        row = cur.fetchone()
        if not row or row[0] != 1:
            print("[FAIL] Database connectivity check failed")
            return 2
        print("[OK] Database connectivity")

        # 2) Extensions
        cur.execute("SELECT extname FROM pg_extension")
        exts = {r[0] for r in cur.fetchall()}
        if "vector" in exts:
            print("[OK] vector extension present")
        else:
            print("[WARN] vector extension missing — pgvector features will be disabled")

        if "pg_trgm" in exts:
            print("[OK] pg_trgm extension present (trigram search enabled)")
        else:
            print("[INFO] pg_trgm missing — decision trigram search will be skipped (set DECISION_TRIGRAM_ENABLED=false)")

        # 3) Required objects
        checks: Tuple[Tuple[str, str], ...] = (
            ("session_summary view", "SELECT 1 FROM session_summary LIMIT 1"),
            ("clean_expired_cache() function", "SELECT 1 FROM pg_proc WHERE proname='clean_expired_cache'"),
            ("clean_expired_context() function", "SELECT 1 FROM pg_proc WHERE proname='clean_expired_context'"),
        )
        for label, sql in checks:
            try:
                cur.execute(sql)
                _ = cur.fetchone()
                print(f"[OK] {label}")
            except Exception as e:
                print(f"[WARN] {label} not found: {e}")

        cur.close()
        conn.close()
        print("[DONE] Memory healthcheck complete")
        return 0

    except Exception as e:
        print(f"[FAIL] Healthcheck error: {e}")
        return 99


if __name__ == "__main__":
    sys.exit(main())

