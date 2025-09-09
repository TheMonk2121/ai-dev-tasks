#!/usr/bin/env python3
"""
Run the quick migration to add content_tsv and its GIN index on legacy document_chunks.

Uses POSTGRES_DSN or DATABASE_URL.
"""

import os
import sys

import psycopg2


def main():
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ Set POSTGRES_DSN or DATABASE_URL")
        sys.exit(1)
    sql_path = os.path.join(os.path.dirname(__file__), "migrations", "add_content_tsv.sql")
    try:
        with open(sql_path, encoding="utf-8") as f:
            sql = f.read()
    except Exception as e:
        print(f"❌ Could not read SQL file: {e}")
        sys.exit(1)

    try:
        conn = psycopg2.connect(dsn)
        with conn:
            with conn.cursor() as cur:
                cur.execute(sql)
        print("✅ content_tsv migration completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
