#!/usr/bin/env python3
"""Validate evaluation targets against database."""

from __future__ import annotations

import json
import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from psycopg.rows import dict_row

from src.common.psycopg3_config import Psycopg3Config


def main() -> Any:
    # Load unified gold cases (v1)
    try:
        from src.utils.gold_loader import load_gold_cases
    except Exception as e:
        print(f"Failed to import gold loader: {e}", file=sys.stderr)
        sys.exit(2)

    gold_path: str = os.getenv("GOLD_FILE", "evals/gold/v1/gold_cases.jsonl")
    cases = load_gold_cases(gold_path)

    config = Psycopg3Config()
    with config.get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
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
