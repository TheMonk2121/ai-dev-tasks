from __future__ import annotations
import psycopg2
from psycopg2.extras import RealDictCursor
import os
#!/usr/bin/env python3
"""Test pg_stat_statements queries"""

def test_queries():
    try:
        with psycopg2.connect("postgresql://danieljacobs@localhost:5432/ai_agency") as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Test slow queries
                cur.execute(
                    """

                    SELECT 
                        query,
                        calls,
                        total_exec_time as total_time,
                        mean_exec_time as mean_time,
                        max_exec_time as max_time,
                        rows
                    FROM pg_stat_statements 
                    ORDER BY total_exec_time DESC 
                    LIMIT 10
                """
                )
                slow_queries = cur.fetchall()
                print(f"Slow queries: {len(slow_queries)} rows")

                # Test frequent queries
                cur.execute(
                    """
                    SELECT 
                        query,
                        calls,
                        total_exec_time as total_time,
                        mean_exec_time as mean_time
                    FROM pg_stat_statements 
                    ORDER BY calls DESC 
                    LIMIT 10
                """
                )
                frequent_queries = cur.fetchall()
                print(f"Frequent queries: {len(frequent_queries)} rows")

                return {
                    "slow_queries": [dict(row) for row in slow_queries],
                    "frequent_queries": [dict(row) for row in frequent_queries],
                }
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = test_queries()
    print(f"Result: {result}")
