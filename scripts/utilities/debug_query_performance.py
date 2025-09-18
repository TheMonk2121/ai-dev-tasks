from __future__ import annotations

import os
import sys
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""Debug query performance issues"""

def debug_query_performance() -> Any:
    try:
        with Psycopg3Config.get_cursor("default") as cur:
                # Check if pg_stat_statements is available
                print("1. Checking pg_stat_statements availability...")
                _ = cur.execute(
                    """

                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'pg_stat_statements'
                    )
                """
                )
                result: Any = cur.fetchone()
                print(f"   Query result: {result}")
                has_pg_stat_statements = result["exists"] if result else False
                print(f"   pg_stat_statements available: {has_pg_stat_statements}")

                if not has_pg_stat_statements:
                    return {"message": "pg_stat_statements extension not available"}

                # Test slow queries
                print("2. Testing slow queries...")
                _ = cur.execute(
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
                slow_queries: Any = cur.fetchall()
                print(f"   Slow queries: {len(slow_queries)} rows")

                # Test frequent queries
                print("3. Testing frequent queries...")
                _ = cur.execute(
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
                frequent_queries: Any = cur.fetchall()
                print(f"   Frequent queries: {len(frequent_queries)} rows")

                return {
                    "slow_queries": [dict(row) for row in slow_queries],
                    "frequent_queries": [dict(row) for row in frequent_queries],
                }
    except Exception as e:
        print(f"Exception type: {type(e)}")
        print(f"Exception value: {repr(e)}")
        print(f"Exception str: {str(e)}")
        return {"error": f"Query performance error: {e}"}

if __name__ == "__main__":
    result = debug_query_performance()
    print(f"Final result: {result}")
