#!/usr/bin/env python3
import os, sys, json
import psycopg2
from psycopg2.extras import RealDictCursor


def main():
    gold = json.load(open("evals/gold_cases.json"))
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    with psycopg2.connect(dsn, cursor_factory=RealDictCursor) as conn, conn.cursor() as cur:
        missing = []
        for case in gold:
            for expect in case.get("expects", []):
                fp = expect.get("file_path") or ""
                if not fp:
                    continue
                cur.execute(
                    "SELECT 1 FROM documents WHERE (file_path || '/' || filename) ILIKE %s LIMIT 1;",
                    (f"%{fp.split('/')[-1]}%",),
                )
                if cur.fetchone() is None:
                    missing.append(fp)
        if missing:
            print("MISSING_IN_DB", json.dumps(sorted(set(missing)), indent=2))
            sys.exit(2)
        print("OK")


if __name__ == "__main__":
    main()
