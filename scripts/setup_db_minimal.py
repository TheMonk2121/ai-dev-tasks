#!/usr/bin/env python3
"""
Minimal DB setup runner (safe/idempotent).

Performs the single highest-impact optimization plus core table setup:
- Ensures retrieval indexes (pgvector ivfflat + GIN + composites)
- Ensures decisions/supersedence tables, indexes, FKs
- Ensures performance helper function exists and pre-creates future partitions

Usage:
  export DATABASE_URL=postgresql://user@host:5432/db
  python scripts/setup_db_minimal.py
"""

from __future__ import annotations

import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DSRC = os.path.join(ROOT, "src")
if DSRC not in sys.path:
    sys.path.insert(0, DSRC)

from utils.db_pool import get_conn  # type: ignore
from utils.decision_extractor import create_decisions_table  # type: ignore
from utils.supersedence_retrieval import create_supersedence_tables  # type: ignore


def ensure_retrieval_schema() -> None:
    # Reuse the dedicated script logic inline to avoid import coupling
    with get_conn(role="writer") as conn:
        with conn.cursor() as cur:
            cur.execute('CREATE EXTENSION IF NOT EXISTS "vector";')
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dc_content_tsv
                ON document_chunks USING GIN (content_tsv);
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dc_docid_chunk
                ON document_chunks(document_id, chunk_index);
                """
            )
            lists = int(os.getenv("IVFFLAT_LISTS", "100"))
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_dc_embedding_ivfflat
                ON document_chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists={lists});
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_filename
                ON documents(filename);
                """
            )
        conn.commit()


def ensure_performance_helpers() -> None:
    with get_conn(role="writer") as conn:
        with conn.cursor() as cur:
            # Call helper to create next 7 days of partitions if the function exists
            cur.execute("SELECT 1 FROM pg_proc WHERE proname='ensure_future_performance_partitions';")
            if cur.fetchone():
                cur.execute("SELECT ensure_future_performance_partitions(7);")
        conn.commit()


def main() -> None:
    dsn = os.getenv("DATABASE_URL", "")
    # High-impact retrieval indexes
    ensure_retrieval_schema()
    # Core decision/supersedence setup
    create_decisions_table(dsn)
    create_supersedence_tables(dsn)
    # Performance partitions helper
    ensure_performance_helpers()
    print("[OK] Minimal DB setup completed.")


if __name__ == "__main__":
    main()
