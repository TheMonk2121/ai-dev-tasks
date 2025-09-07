#!/usr/bin/env python3
"""Test database query for reader gold generation."""

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Get database connection from environment or default."""
    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    return psycopg2.connect(dsn, cursor_factory=RealDictCursor)


def test_query():
    """Test the database query."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT 
                    dc.id,
                    dc.content,
                    d.file_path,
                    d.filename,
                    LENGTH(dc.content) as content_length
                FROM document_chunks dc
                JOIN documents d ON dc.document_id = d.id
                WHERE dc.content IS NOT NULL 
                AND LENGTH(dc.content) > 200
                AND LENGTH(dc.content) < 2000
                AND (d.file_path LIKE '100_%' OR d.file_path LIKE '200_%' OR d.file_path LIKE '300_%' OR d.file_path LIKE '400_%' OR d.file_path LIKE '500_%')
                ORDER BY RANDOM()
                LIMIT 5
            """
            )

            rows = cur.fetchall()
            print(f"Found {len(rows)} rows")

            for i, row in enumerate(rows):
                print(f"\nRow {i+1}:")
                print(f"  ID: {row['id']}")
                print(f"  File: {row['filename']}")
                print(f"  Path: {row['file_path']}")
                print(f"  Content length: {row['content_length']}")
                print(f"  Content preview: {row['content'][:100]}...")


if __name__ == "__main__":
    test_query()
