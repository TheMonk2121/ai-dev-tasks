from __future__ import annotations
import math
import os
import sys
import time
import psycopg2
from psycopg2.extras import execute_values
from sentence_transformers import SentenceTransformer
#!/usr/bin/env python3

DSN = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
MODEL_NAME = os.getenv("EMBED_MODEL", "BAAI/bge-small-en-v1.5")  # 384-dim, fast, great for code+docs
BATCH = int(os.getenv("EMBED_BATCH", "64"))

def ensure_schema(cur, dim):
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='document_chunks' AND column_name='embedding'
            ) THEN
                EXECUTE 'ALTER TABLE document_chunks ADD COLUMN embedding vector(%s);'::text
                USING %s;
            END IF;
        END$$;
    """,
        (dim, dim),
    )
    # Index tuned light; bump lists if corpus grows
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_chunks_embedding
        ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 200);
    """
    )

def fetch_missing(cur, limit=5000):
    cur.execute(
        """
        SELECT id, COALESCE(embedding_text, content) AS txt
        FROM document_chunks
        WHERE embedding IS NULL
          AND length(COALESCE(embedding_text, content)) > 0
        LIMIT %s;
    """,
        (limit,),
    )
    return cur.fetchall()

def main():
    m = SentenceTransformer(MODEL_NAME)
    dim = m.get_sentence_embedding_dimension()
    with psycopg2.connect(DSN) as conn, conn.cursor() as cur:
        ensure_schema(cur, dim)
        conn.commit()

        total = 0
        t0 = time.time()
        while True:
            rows = fetch_missing(cur)
            if not rows:
                break
            texts = [r[1] for r in rows]
            embs = m.encode(texts, batch_size=BATCH, normalize_embeddings=True)
            # Upsert embeddings
            for r, emb in zip(rows, embs):
                cur.execute("UPDATE document_chunks SET embedding = %s::vector WHERE id = %s", (emb.tolist(), r[0]))
            conn.commit()
            total += len(rows)
            # Low, polite pacing
            time.sleep(0.2)
        # ANALYZE for planner quality
        cur.execute("ANALYZE document_chunks;")
        conn.commit()
    dt = time.time() - t0
    print(f"Backfilled {total} chunks in {dt:.1f}s")

if __name__ == "__main__":
    main()