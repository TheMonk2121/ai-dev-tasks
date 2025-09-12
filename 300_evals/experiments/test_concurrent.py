#!/usr/bin/env python3

import threading
import time

import psycopg2

def test_query():
    try:
        conn = psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency")
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM documents")
        result = cursor.fetchone()[0]
        conn.close()
        return f"Thread {threading.current_thread().name}: {result}"
    except Exception as e:
        return f"Thread {threading.current_thread().name}: ERROR {e}"

def test_concurrent_operations():
    print("✅ Testing concurrent operations...")
    results = []

    # Create 5 concurrent threads
    threads = [threading.Thread(target=lambda: results.append(test_query())) for _ in range(5)]

    start = time.time()
    [t.start() for t in threads]
    [t.join() for t in threads]
    end = time.time()

    print(f"Concurrent operations completed in {end-start:.3f}s:")
    [print(f"  {r}") for r in results]

if __name__ == "__main__":
    test_concurrent_operations()
