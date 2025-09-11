#!/usr/bin/env python3
"""
Database Performance Monitor - Comprehensive monitoring for the consolidated ai_agency database
"""

import json
import time
from datetime import datetime
from typing import Any, Dict, List

import psycopg2
from psycopg2.extras import RealDictCursor


class DatabasePerformanceMonitor:
    """Monitor database performance metrics and health."""

    def __init__(self, dsn: str):
        self.dsn = dsn
        self.metrics = {}

    def get_connection_stats(self) -> dict[str, Any]:
        """Get connection and activity statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Connection stats
                    cur.execute(
                        """
                        SELECT 
                            count(*) as total_connections,
                            count(*) FILTER (WHERE state = 'active') as active_connections,
                            count(*) FILTER (WHERE state = 'idle') as idle_connections
                        FROM pg_stat_activity 
                        WHERE datname = current_database()
                    """
                    )
                    conn_stats = cur.fetchone()

                    # Database size
                    cur.execute(
                        """
                        SELECT pg_size_pretty(pg_database_size(current_database())) as db_size,
                               pg_database_size(current_database()) as db_size_bytes
                    """
                    )
                    size_stats = cur.fetchone()

                    return {"connections": dict(conn_stats), "database_size": dict(size_stats)}
        except Exception as e:
            return {"error": f"Connection stats error: {e}"}

    def get_table_stats(self) -> dict[str, Any]:
        """Get table statistics and sizes."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Table sizes and row counts
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            relname as tablename,
                            n_tup_ins as inserts,
                            n_tup_upd as updates,
                            n_tup_del as deletes,
                            n_live_tup as live_tuples,
                            n_dead_tup as dead_tuples,
                            last_vacuum,
                            last_autovacuum,
                            last_analyze,
                            last_autoanalyze
                        FROM pg_stat_user_tables 
                        ORDER BY n_live_tup DESC
                    """
                    )
                    table_stats = cur.fetchall()

                    # Table sizes
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            tablename,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
                        FROM pg_tables 
                        WHERE schemaname = 'public'
                        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
                    """
                    )
                    size_stats = cur.fetchall()

                    return {
                        "table_activity": [dict(row) for row in table_stats],
                        "table_sizes": [dict(row) for row in size_stats],
                    }
        except Exception as e:
            return {"error": f"Table stats error: {e}"}

    def get_index_stats(self) -> dict[str, Any]:
        """Get index usage and performance statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Index usage stats
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            relname as tablename,
                            indexrelname as indexname,
                            idx_tup_read,
                            idx_tup_fetch,
                            idx_scan,
                            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                        FROM pg_stat_user_indexes 
                        ORDER BY idx_scan DESC
                    """
                    )
                    index_stats = cur.fetchall()

                    # Unused indexes
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            relname as tablename,
                            indexrelname as indexname,
                            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                        FROM pg_stat_user_indexes 
                        WHERE idx_scan = 0
                        ORDER BY pg_relation_size(indexrelid) DESC
                    """
                    )
                    unused_indexes = cur.fetchall()

                    return {
                        "index_usage": [dict(row) for row in index_stats],
                        "unused_indexes": [dict(row) for row in unused_indexes],
                    }
        except Exception as e:
            return {"error": f"Index stats error: {e}"}

    def get_query_performance(self) -> dict[str, Any]:
        """Get query performance statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Check if pg_stat_statements is available
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'pg_stat_statements'
                        )
                    """
                    )
                    has_pg_stat_statements = cur.fetchone()["exists"]

                    if not has_pg_stat_statements:
                        return {"message": "pg_stat_statements extension not available"}

                    # Slow queries
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

                    # Query frequency
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

                    return {
                        "slow_queries": [dict(row) for row in slow_queries],
                        "frequent_queries": [dict(row) for row in frequent_queries],
                    }
        except Exception as e:
            return {"error": f"Query performance error: {e}"}

    def get_memory_stats(self) -> dict[str, Any]:
        """Get memory and cache statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Buffer cache stats
                    cur.execute(
                        """
                        SELECT 
                            'shared_buffers' as cache_type,
                            setting as size,
                            unit
                        FROM pg_settings 
                        WHERE name = 'shared_buffers'
                        
                        UNION ALL
                        
                        SELECT 
                            'effective_cache_size' as cache_type,
                            setting as size,
                            unit
                        FROM pg_settings 
                        WHERE name = 'effective_cache_size'
                    """
                    )
                    cache_stats = cur.fetchall()

                    # Cache hit ratios
                    cur.execute(
                        """
                        SELECT 
                            'buffer_hit_ratio' as metric,
                            round(
                                (blks_hit::numeric / (blks_hit + blks_read)) * 100, 2
                            ) as percentage
                        FROM pg_stat_database 
                        WHERE datname = current_database()
                    """
                    )
                    hit_ratio = cur.fetchone()

                    return {
                        "cache_settings": [dict(row) for row in cache_stats],
                        "hit_ratios": dict(hit_ratio) if hit_ratio else {},
                    }
        except Exception as e:
            return {"error": f"Memory stats error: {e}"}

    def get_locks_and_waits(self) -> dict[str, Any]:
        """Get lock and wait statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Current locks
                    cur.execute(
                        """
                        SELECT 
                            mode,
                            count(*) as lock_count
                        FROM pg_locks 
                        WHERE database = (SELECT oid FROM pg_database WHERE datname = current_database())
                        GROUP BY mode
                        ORDER BY lock_count DESC
                    """
                    )
                    lock_stats = cur.fetchall()

                    # Long running queries
                    cur.execute(
                        """
                        SELECT 
                            pid,
                            now() - pg_stat_activity.query_start AS duration,
                            query,
                            state
                        FROM pg_stat_activity 
                        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
                        AND state != 'idle'
                        ORDER BY duration DESC
                    """
                    )
                    long_queries = cur.fetchall()

                    return {
                        "locks": [dict(row) for row in lock_stats],
                        "long_running_queries": [dict(row) for row in long_queries],
                    }
        except Exception as e:
            return {"error": f"Locks and waits error: {e}"}

    def run_performance_test(self) -> dict[str, Any]:
        """Run a simple performance test."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    # Test query performance
                    start_time = time.time()

                    # Test 1: Simple count query
                    cur.execute("SELECT COUNT(*) FROM conversation_context")
                    count_result = cur.fetchone()[0]
                    count_time = time.time() - start_time

                    # Test 2: Complex query with joins
                    start_time = time.time()
                    cur.execute(
                        """
                        SELECT 
                            cc.context_type,
                            COUNT(*) as record_count,
                            AVG(cc.relevance_score) as avg_relevance
                        FROM conversation_context cc
                        LEFT JOIN conversation_sessions cs ON cc.session_id = cs.session_id
                        GROUP BY cc.context_type
                        ORDER BY record_count DESC
                    """
                    )
                    complex_result = cur.fetchall()
                    complex_time = time.time() - start_time

                    # Test 3: JSONB query performance
                    start_time = time.time()
                    cur.execute(
                        """
                        SELECT COUNT(*) 
                        FROM conversation_context 
                        WHERE entities ? 'python'
                    """
                    )
                    jsonb_result = cur.fetchone()[0]
                    jsonb_time = time.time() - start_time

                    return {
                        "simple_count": {"result": count_result, "time_ms": round(count_time * 1000, 2)},
                        "complex_join": {
                            "result": [dict(row) for row in complex_result],
                            "time_ms": round(complex_time * 1000, 2),
                        },
                        "jsonb_query": {"result": jsonb_result, "time_ms": round(jsonb_time * 1000, 2)},
                    }
        except Exception as e:
            return {"error": f"Performance test error: {e}"}

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        print("🔍 Generating Database Performance Report...")
        print("=" * 60)

        report = {
            "timestamp": datetime.now().isoformat(),
            "connection_stats": self.get_connection_stats(),
            "table_stats": self.get_table_stats(),
            "index_stats": self.get_index_stats(),
            "query_performance": self.get_query_performance(),
            "memory_stats": self.get_memory_stats(),
            "locks_and_waits": self.get_locks_and_waits(),
            "performance_test": self.run_performance_test(),
        }

        return report

    def print_summary(self, report: dict[str, Any]):
        """Print a human-readable summary."""
        print("\n📊 DATABASE PERFORMANCE SUMMARY")
        print("=" * 60)

        # Connection summary
        if "connection_stats" in report and "error" not in report["connection_stats"]:
            conn = report["connection_stats"]["connections"]
            size = report["connection_stats"]["database_size"]
            print(f"🔗 Connections: {conn['active_connections']} active, {conn['idle_connections']} idle")
            print(f"💾 Database Size: {size['db_size']}")

        # Table summary
        if "table_stats" in report and "error" not in report["table_stats"]:
            tables = report["table_stats"]["table_activity"]
            total_tuples = sum(row["live_tuples"] for row in tables)
            print(f"📋 Total Records: {total_tuples:,}")

            # Top tables by size
            sizes = report["table_stats"]["table_sizes"]
            if sizes:
                print(f"📈 Largest Table: {sizes[0]['tablename']} ({sizes[0]['size']})")

        # Performance test results
        if "performance_test" in report and "error" not in report["performance_test"]:
            perf = report["performance_test"]
            print("⚡ Query Performance:")
            print(f"   - Simple Count: {perf['simple_count']['time_ms']}ms")
            print(f"   - Complex Join: {perf['complex_join']['time_ms']}ms")
            print(f"   - JSONB Query: {perf['jsonb_query']['time_ms']}ms")

        # Index summary
        if "index_stats" in report and "error" not in report["index_stats"]:
            unused = report["index_stats"]["unused_indexes"]
            if unused:
                print(f"⚠️  Unused Indexes: {len(unused)} (consider removing)")
            else:
                print("✅ All indexes are being used")

        # Memory summary
        if "memory_stats" in report and "error" not in report["memory_stats"]:
            hit_ratio = report["memory_stats"]["hit_ratios"]
            if hit_ratio and "percentage" in hit_ratio:
                ratio = hit_ratio["percentage"]
                if ratio > 95:
                    print(f"✅ Cache Hit Ratio: {ratio}% (excellent)")
                elif ratio > 90:
                    print(f"⚠️  Cache Hit Ratio: {ratio}% (good)")
                else:
                    print(f"❌ Cache Hit Ratio: {ratio}% (needs improvement)")

    def save_report(self, report: dict[str, Any], filename: str = None):
        """Save report to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics/database_performance_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📁 Report saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")


def main():
    """Main monitoring function."""
    print("🔍 Database Performance Monitor")
    print("=" * 60)

    # Get database DSN
    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    print(f"📡 Monitoring database: {dsn}")

    # Create monitor
    monitor = DatabasePerformanceMonitor(dsn)

    # Generate report
    report = monitor.generate_report()

    # Print summary
    monitor.print_summary(report)

    # Save detailed report
    monitor.save_report(report)

    print("\n🎉 Performance monitoring complete!")


if __name__ == "__main__":
    main()
