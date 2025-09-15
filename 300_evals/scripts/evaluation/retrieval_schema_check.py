from __future__ import annotations
import os
import sys
from utils.db_pool import get_conn  # type: ignore[import-untyped]
#!/usr/bin/env python3
"""
Idempotent retrieval schema tuning (indexes + extension).

Creates minimal indexes for fast hybrid retrieval:
- vector: ivfflat index on document_chunks.embedding (cosine)
- GIN: index on document_chunks.content_tsv
- Composite: document_chunks(document_id, chunk_index)
- Filename: documents(filename)

Usage:
  export DATABASE_URL=postgresql://user@host:5432/db
  python scripts/retrieval_schema_check.py
"""

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DSRC = os.path.join(ROOT, "dspy-rag-system", "src")
if DSRC not in sys.path:
    sys.path.insert(0, DSRC)

def main() -> None:
    # Use writer role to allow DDL
    with get_conn(role="writer") as conn:
        with conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

            # document_chunks.content_tsv (GIN)
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dc_content_tsv
                ON document_chunks USING GIN (content_tsv);
                """
            )

            # document_chunks(document_id, chunk_index)
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_dc_docid_chunk
                ON document_chunks(document_id, chunk_index);
                """
            )

            # ivfflat on embedding (cosine); adjust lists via env if needed
            lists = int(os.getenv("IVFFLAT_LISTS", "100"))
            cur.execute(
                f"""
                CREATE INDEX IF NOT EXISTS idx_dc_embedding_ivfflat
                ON document_chunks USING ivfflat (embedding vector_cosine_ops)
                WITH (lists={lists});
                """
            )

            # documents(filename) for quick filename filters
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_documents_filename
                ON documents(filename);
                """
            )

        conn.commit()
    print("[OK] Retrieval schema verified (indexes ensured).")

if __name__ == "__main__":
    main()
