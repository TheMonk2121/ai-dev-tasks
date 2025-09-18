#!/usr/bin/env python3
"""
Quick DB schema and extension verification for memory/RAG.

Checks:
- pgvector extension installed
- required tables exist
- important columns present (with fallbacks noted)
- presence of tsvector or acceptable on-the-fly fallback

Prints a concise report and remediation hints.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from src.common.psycopg3_config import Psycopg3Config


def connect():
    """Connect to the database and return a connection."""
    dsn = os.getenv("POSTGRES_DSN") or os.getenv("DATABASE_URL")
    if not dsn:
        print("❌ No POSTGRES_DSN/DATABASE_URL set")
        sys.exit(1)
    return Psycopg3Config.get_connection("default")


def exists(cur: Any, query: str, params: tuple[object, ...] | None = None) -> bool:
    """Check if a query returns any results."""
    _ = cur.execute(query, params or ())
    row = cur.fetchone()
    return bool(row[list(row.keys())[0]] if row else False)


def main() -> None:
    """Main function to verify database schema and indexes."""
    try:
        with Psycopg3Config.get_cursor("default") as cur:
            # pgvector
            try:
                _ = cur.execute("SELECT EXISTS(SELECT 1 FROM pg_available_extensions WHERE name='vector');")
                row = cur.fetchone()
                has_vector_available = bool(row[list(row.keys())[0]] if row else False)
            except Exception:
                has_vector_available = False

            try:
                _ = cur.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='vector');")
                row2 = cur.fetchone()
                has_vector_installed = bool(row2[list(row2.keys())[0]] if row2 else False)
            except Exception:
                has_vector_installed = False

            # tables
            has_documents = exists(cur, "SELECT to_regclass('documents') IS NOT NULL;")
            has_chunks = exists(cur, "SELECT to_regclass('document_chunks') IS NOT NULL;")

            # key columns
            _ = cur.execute(
                """
                SELECT column_name FROM information_schema.columns
                WHERE table_name='document_chunks'
                """
            )
            cols = {row[list(row.keys())[0]] for row in cur.fetchall()}
            need_cols = {"document_id", "chunk_index", "content", "embedding"}
            missing_core = sorted(list(need_cols - cols))
            has_content_tsv = "content_tsv" in cols

            print("🧪 Schema Verification")
            print(f"- documents table: {'✅' if has_documents else '❌'}")
            print(f"- document_chunks table: {'✅' if has_chunks else '❌'}")
            print(f"- core columns present: {'✅' if not missing_core else '❌'}  missing={missing_core}")
            print(f"- content_tsv column: {'✅' if has_content_tsv else '⚠️  (fallback to to_tsvector enabled)'}")
            print("\n🧩 pgvector")
            print(f"- available: {'✅' if has_vector_available else '❌'}")
            print(f"- installed: {'✅' if has_vector_installed else '❌'} (CREATE EXTENSION IF NOT EXISTS vector)")

            if not has_chunks or missing_core:
                print("\n💡 Remediation: apply clean-slate schema in your target schema:")
                print("  - dspy-rag-system/config/database/clean_slate_schema.sql")
            if not has_content_tsv:
                print("\nℹ️ Note: content_tsv missing — BM25 queries will compute to_tsvector at runtime (slower).")

        print("\nDone.")
    except Exception as e:
        print(f"❌ DB connect failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
