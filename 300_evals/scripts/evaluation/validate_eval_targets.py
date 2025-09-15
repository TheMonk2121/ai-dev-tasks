#!/usr/bin/env python3
import json
import os
import sys

import psycopg2
from psycopg2.extras import RealDictCursor

def main():
    # Load unified gold cases (v1)
    try:
        from src.utils.gold_loader import load_gold_cases
    except Exception as e:
        print(f"Failed to import gold loader: {e}", file=sys.stderr)
        sys.exit(2)

    gold_path = os.getenv("GOLD_FILE", "evals/gold/v1/gold_cases.jsonl")
    cases = load_gold_cases(gold_path)
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn, conn.cursor() as cur:
        missing = []
        for case in cases:
            for fp in list(case.expected_files or []):
                # Match by basename containment
                base = os.path.basename(fp)
                cur.execute(
                    "SELECT 1 FROM documents WHERE (file_path || '/' || filename) ILIKE %s LIMIT 1;",
                    (f"%{base}%",),
                )
                if cur.fetchone() is None:
                    missing.append(fp)
        if missing:
            print("MISSING_IN_DB", json.dumps(sorted(set(missing)), indent=2))
            sys.exit(2)
        print("OK")

if __name__ == "__main__":
    main()
