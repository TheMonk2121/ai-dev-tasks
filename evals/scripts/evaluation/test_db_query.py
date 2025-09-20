from __future__ import annotations
from typing import Any
# Add project paths
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.common.psycopg3_config import Psycopg3Config
import os
#!/usr/bin/env python3
"""Test database query for reader gold generation."""

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
                # Type cast to help the type checker understand this is a dict-like object
                row_dict: dict[str, Any] = row  # type: ignore
                print(f"\nRow {i+1}:")
                print(f"  ID: {result
                print(f"  File: {result
                print(f"  Path: {result
                print(f"  Content length: {result
                print(f"  Content preview: {result

if __name__ == "__main__":
    test_query()
