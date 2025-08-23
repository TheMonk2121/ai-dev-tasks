#!/usr/bin/env python3
"""
Setup AI Models (Cursor-native safe checks)

Performs non-interactive, local-first environment validation for model-related
runtime. Avoids heavyweight downloads; focuses on quick health checks.

Checks:
- Python version
- Presence of key Python packages (import detection only)
- PostgreSQL DSN presence and optional connectivity test
- pgvector extension presence (optional when DB check enabled)

Usage:
  python3 scripts/setup_ai_models.py                 # run all default checks
  python3 scripts/setup_ai_models.py --check-db      # also attempt DB connection
  python3 scripts/setup_ai_models.py --dsn postgresql://user:pass@localhost:5432/db

Exit codes: 0 on success, 1 if any check fails
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys
from typing import List, Tuple

REQUIRED_IMPORTS: List[str] = [
    # Light-weight/importable modules only; avoid heavy initializations
    "dspy",                  # core DSPy interface
    "flask",                 # dashboard
    "psycopg2",              # Postgres client
]

OPTIONAL_IMPORTS: List[str] = [
    # Optional but commonly used
    "sentence_transformers", # embeddings
    "torch",                 # model runtime (optional)
    "transformers",          # tokenizer/LLM utils (optional)
]

def _check_python_version(min_major: int = 3, min_minor: int = 10) -> Tuple[bool, str]:
    ver = sys.version_info
    ok = (ver.major, ver.minor) >= (min_major, min_minor)
    return ok, f"Python {ver.major}.{ver.minor} detected (require >= {min_major}.{min_minor})"

def _check_imports(module_names: List[str]) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    for name in module_names:
        if importlib.util.find_spec(name) is None:
            missing.append(name)
    return len(missing) == 0, missing

def _check_db_connection(dsn: str, check_pgvector: bool = True) -> Tuple[bool, str]:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(dsn)
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT 1")
                _ = cur.fetchone()
                if check_pgvector:
                    cur.execute("SELECT 1 FROM pg_extension WHERE extname='vector'")
                    has_vector = cur.fetchone() is not None
                    if not has_vector:
                        return False, "pgvector extension not found (CREATE EXTENSION vector)"
        finally:
            conn.close()
        return True, "Database connectivity OK"
    except Exception as e:
        return False, f"Database check failed: {e}"

def main() -> int:
    parser = argparse.ArgumentParser(description="Setup validator for Cursor-native AI models")
    parser.add_argument("--dsn", default=os.getenv("POSTGRES_DSN", ""), help="PostgreSQL DSN for optional checks")
    parser.add_argument("--check-db", action="store_true", help="Attempt DB connection and pgvector check")
    args = parser.parse_args()

    overall_ok = True

    ok, msg = _check_python_version()
    print(f"[python] {msg}")
    overall_ok &= ok

    ok_req, missing_req = _check_imports(REQUIRED_IMPORTS)
    if ok_req:
        print("[imports] Required packages available")
    else:
        print(f"[imports] Missing required packages: {', '.join(missing_req)}")
    overall_ok &= ok_req

    ok_opt, missing_opt = _check_imports(OPTIONAL_IMPORTS)
    if ok_opt:
        print("[imports] Optional packages available")
    else:
        # optional → informational only
        print(f"[imports] Optional packages missing (informational): {', '.join(missing_opt)}")

    dsn = args.dsn
    if args.check_db:
        if not dsn:
            print("[db] No DSN provided (use --dsn or POSTGRES_DSN) → skipping DB check")
        else:
            ok_db, db_msg = _check_db_connection(dsn)
            print(f"[db] {db_msg}")
            overall_ok &= ok_db
    else:
        # Provide guidance without failing
        if dsn:
            print("[db] DSN detected; run with --check-db to validate connectivity and pgvector")
        else:
            print("[db] No DSN detected; set POSTGRES_DSN or pass --dsn to enable DB checks")

    if overall_ok:
        print("✔ Environment checks passed")
        return 0
    else:
        print("✖ Environment checks failed; see messages above")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())

