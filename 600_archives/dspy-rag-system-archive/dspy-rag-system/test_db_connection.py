#!/usr/bin/env python3
"""
Minimal database connection test to isolate the KeyError: 0 issue.
"""

import os

import psycopg2
from dotenv import load_dotenv

load_dotenv()


def test_direct_connection():
    """Test direct psycopg2 connection without the pool."""
    print("Testing direct psycopg2 connection...")

    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            result = cur.fetchone()
            if result and result[0]:
                print(f"✅ Direct connection successful: {result[0][:50]}...")
            else:
                print("✅ Direct connection successful (no version info)")

        conn.close()
        return True
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        return False


def test_simple_insert():
    """Test a simple insert operation."""
    print("\nTesting simple insert...")

    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        with conn.cursor() as cur:
            # Insert a test document
            cur.execute(
                """
                INSERT INTO documents (filename, file_path, file_type, file_size, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """,
                ("test.md", "/test/path", "markdown", 1000, "completed"),
            )

            result = cur.fetchone()
            if result and result[0]:
                doc_id = result[0]
                print(f"✅ Insert successful, document ID: {doc_id}")
            else:
                print("❌ Insert failed: no document ID returned")
                return False

            # Insert a test chunk
            cur.execute(
                """
                INSERT INTO document_chunks (content, document_id, chunk_index)
                VALUES (%s, %s, %s)
                RETURNING id
            """,
                ("Test content", str(doc_id), 0),
            )

            result = cur.fetchone()
            if result and result[0]:
                chunk_id = result[0]
                print(f"✅ Chunk insert successful, chunk ID: {chunk_id}")
            else:
                print("❌ Chunk insert failed: no chunk ID returned")
                return False

            conn.commit()

        conn.close()
        return True
    except Exception as e:
        print(f"❌ Insert failed: {e}")
        return False


if __name__ == "__main__":
    print("=== Database Connection Test ===")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'NOT SET')}")

    if test_direct_connection():
        test_simple_insert()
    else:
        print("Cannot proceed with insert test due to connection failure.")
