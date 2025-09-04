#!/usr/bin/env python3


import psycopg2


def test_connection_resilience():
    print("✅ Testing connection resilience...")

    # Test valid connection
    try:
        conn = psycopg2.connect("postgresql://danieljacobs@localhost:5432/dspy_rag")
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"  Connection test: SUCCESS ({result[0]})")
        conn.close()
    except Exception as e:
        print(f"  Connection test: FAILED ({e})")

    # Test invalid connection
    print("✅ Testing invalid connection handling...")
    try:
        conn = psycopg2.connect("postgresql://invalid@localhost:5432/invalid")
    except Exception as e:
        print(f"  Invalid connection: Properly handled ({type(e).__name__})")


def test_database_health():
    print("✅ Testing database health...")
    try:
        conn = psycopg2.connect("postgresql://danieljacobs@localhost:5432/dspy_rag")
        cursor = conn.cursor()

        # Test basic operations
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM document_chunks")
        chunk_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM conversation_memory")
        memory_count = cursor.fetchone()[0]

        print(f"  Documents: {doc_count}")
        print(f"  Chunks: {chunk_count}")
        print(f"  Memory entries: {memory_count}")

        conn.close()
        return True
    except Exception as e:
        print(f"  Health check failed: {e}")
        return False


if __name__ == "__main__":
    test_connection_resilience()
    test_database_health()
