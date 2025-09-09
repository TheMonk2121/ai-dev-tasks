#!/usr/bin/env python3
"""
Backfill file_path on document_chunks and add slug/identifier columns and indexes.
Safe to run multiple times.
"""

import os
import sys
from pathlib import Path


def main() -> int:
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    try:
        import psycopg2  # type: ignore
    except Exception as e:
        print(f"❌ psycopg2 not available: {e}")
        return 1

    try:
        conn = psycopg2.connect(dsn)
        conn.autocommit = True
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return 1

    try:
        with conn.cursor() as cur:
            # 1) Backfill file_path from documents
            cur.execute(
                """
                UPDATE document_chunks c
                SET file_path = d.file_path
                FROM documents d
                WHERE c.document_id = d.id
                  AND (c.file_path IS NULL OR c.file_path = '')
                """
            )

            # 2) Add generated columns: filename, normalized_slug
            cur.execute(
                """
                DO $$
                BEGIN
                  IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'document_chunks' AND column_name = 'filename'
                  ) THEN
                    ALTER TABLE document_chunks
                    ADD COLUMN filename TEXT
                    GENERATED ALWAYS AS (
                      split_part(file_path, '/', array_length(string_to_array(file_path, '/'), 1))
                    ) STORED;
                  END IF;
                END $$;
                """
            )

            cur.execute(
                """
                DO $$
                BEGIN
                  IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'document_chunks' AND column_name = 'normalized_slug'
                  ) THEN
                    ALTER TABLE document_chunks
                    ADD COLUMN normalized_slug TEXT
                    GENERATED ALWAYS AS (
                      lower(replace(coalesce(filename,''), '.md',''))
                    ) STORED;
                  END IF;
                END $$;
                """
            )

            # 3) Optional identifier tsvector and indexes
            cur.execute(
                """
                DO $$
                BEGIN
                  IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'document_chunks' AND column_name = 'ident_tsv'
                  ) THEN
                    ALTER TABLE document_chunks
                    ADD COLUMN ident_tsv tsvector
                    GENERATED ALWAYS AS (
                      to_tsvector('simple', coalesce(filename,'') || ' ' || replace(coalesce(file_path,''), '/',' '))
                    ) STORED;
                  END IF;
                END $$;
                """
            )

            # Indexes
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_chunks_slug ON document_chunks (normalized_slug);
                CREATE INDEX IF NOT EXISTS idx_chunks_ident_tsv ON document_chunks USING GIN (ident_tsv);
                ANALYZE document_chunks;
                """
            )

        print("✅ DB slug support ensured")
        return 0
    except Exception as e:
        print(f"❌ Error applying DB slug patch: {e}")
        return 1
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
