#!/usr/bin/env python3
"""
Test script to validate the new database pool implementation.
"""

import json
import sys
import threading

from dotenv import load_dotenv

# Add src to path
sys.path.append("src")

from utils.db_pool import execute_query, get_conn, init_pool

load_dotenv()


def smoke_test():
    """Smoke test the pool (5s)"""
    print("=== Smoke Test ===")
    try:
        init_pool()
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                result = cur.fetchone()
                if result and result[0]:
                    print(f"✅ Pool smoke test passed: {result[0][:50]}...")
                    return True
                else:
                    print("❌ Pool smoke test failed: no version info")
                    return False
    except Exception as e:
        print(f"❌ Pool smoke test failed: {e}")
        return False


def single_thread_write():
    """Single-thread write test (10s)"""
    print("\n=== Single Thread Write Test ===")
    try:
        # Insert one document
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO documents (filename, file_path, file_type, file_size, status)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """,
                    ("test_doc.md", "/test/path", "markdown", 1000, "completed"),
                )

                result = cur.fetchone()
                if result and result[0]:
                    doc_id = result[0]
                    print(f"✅ Document inserted, ID: {doc_id}")

                    # Insert 3 chunks
                    for i in range(3):
                        cur.execute(
                            """
                            INSERT INTO document_chunks (content, document_id, chunk_index, metadata)
                            VALUES (%s, %s, %s, %s)
                        """,
                            (f"Test chunk {i+1}", str(doc_id), i, json.dumps({"test": True})),
                        )

                    conn.commit()
                    print("✅ 3 chunks inserted and committed")
                    return True
                else:
                    print("❌ Document insert failed: no ID returned")
                    return False
    except Exception as e:
        print(f"❌ Single thread write failed: {e}")
        return False


def multi_thread_write():
    """Multi-thread write test (15s)"""
    print("\n=== Multi Thread Write Test ===")

    def write_doc(thread_id):
        """Write a document from a thread."""
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO documents (filename, file_path, file_type, file_size, status)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """,
                        (f"thread_{thread_id}.md", f"/thread/{thread_id}", "markdown", 1000, "completed"),
                    )

                    result = cur.fetchone()
                    if result and result[0]:
                        doc_id = result[0]

                        # Insert a chunk
                        cur.execute(
                            """
                            INSERT INTO document_chunks (content, document_id, chunk_index, metadata)
                            VALUES (%s, %s, %s, %s)
                        """,
                            (f"Thread {thread_id} chunk", str(doc_id), 0, json.dumps({"thread_id": thread_id})),
                        )

                        conn.commit()
                        print(f"✅ Thread {thread_id}: Document {doc_id} inserted")
                        return True
                    else:
                        print(f"❌ Thread {thread_id}: Document insert failed")
                        return False
        except Exception as e:
            print(f"❌ Thread {thread_id} failed: {e}")
            return False

    # Start 3 threads
    threads = []
    results = []

    for i in range(3):
        thread = threading.Thread(target=lambda tid=i: results.append(write_doc(tid)))
        threads.append(thread)
        thread.start()

    # Wait for all threads
    for thread in threads:
        thread.join()

    success_count = sum(results)
    print(f"✅ Multi-thread test: {success_count}/3 threads succeeded")
    return success_count == 3


def check_counts():
    """Check database counts"""
    print("\n=== Database Counts ===")
    try:
        doc_count = execute_query("SELECT COUNT(*) FROM documents")
        chunk_count = execute_query("SELECT COUNT(*) FROM document_chunks")

        if doc_count and chunk_count:
            print(f"✅ Documents: {doc_count[0][0]}")
            print(f"✅ Chunks: {chunk_count[0][0]}")
            return doc_count[0][0] > 0 and chunk_count[0][0] > 0
        else:
            print("❌ Could not get counts")
            return False
    except Exception as e:
        print(f"❌ Count check failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=== Database Pool Validation Tests ===")

    tests = [
        ("Smoke Test", smoke_test),
        ("Single Thread Write", single_thread_write),
        ("Multi Thread Write", multi_thread_write),
        ("Count Check", check_counts),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    print("\n=== Test Results ===")
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    all_passed = all(result for _, result in results)
    print(f"\nOverall: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")


if __name__ == "__main__":
    main()
