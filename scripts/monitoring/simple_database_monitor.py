from __future__ import annotations

import json
import os
import time
from datetime import datetime
from typing import Any, Optional, Union

import psycopg2
from psycopg2.extras import RealDictCursor

#!/usr/bin/env python3
"""
Simple Database Monitor - Basic performance monitoring for the consolidated ai_agency database
"""

class SimpleDatabaseMonitor:
    """Simple database performance monitoring."""

    def __init__(self, dsn: str):
        self.dsn = dsn

    def get_basic_stats(self) -> dict[str, Any]:
        """Get basic database statistics."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Database size
                    cur.execute("SELECT pg_size_pretty(pg_database_size(current_database())) as db_size")
                    db_size = cur.fetchone()["db_size"]

                    # Table counts
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            relname as table_name,
                            n_live_tup as row_count,
                            pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as table_size
                        FROM pg_stat_user_tables 
                        ORDER BY n_live_tup DESC
                    """
                    )
                    table_stats = cur.fetchall()

                    # Connection count
                    cur.execute(
                        """
                        SELECT count(*) as connection_count
                        FROM pg_stat_activity 
                        WHERE datname = current_database()
                    """
                    )
                    conn_count = cur.fetchone()["connection_count"]

                    return {
                        "database_size": db_size,
                        "connection_count": conn_count,
                        "tables": [dict(row) for row in table_stats],
                    }
        except Exception as e:
            return {"error": f"Basic stats error: {e}"}

    def test_query_performance(self) -> dict[str, Any]:
        """Test query performance with simple queries."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    results = {}

                    # Test 1: Simple count
                    start_time = time.time()
                    cur.execute("SELECT COUNT(*) FROM conversation_context")
                    count = cur.fetchone()[0]
                    results["simple_count"] = {"result": count, "time_ms": round((time.time() - start_time) * 1000, 2)}

                    # Test 2: Group by query
                    start_time = time.time()
                    cur.execute(
                        """
                        SELECT context_type, COUNT(*) as count 
                        FROM conversation_context 
                        GROUP BY context_type 
                        ORDER BY count DESC
                    """
                    )
                    group_result = cur.fetchall()
                    results["group_by"] = {
                        "result": [dict(row) for row in group_result],
                        "time_ms": round((time.time() - start_time) * 1000, 2),
                    }

                    # Test 3: JSONB query
                    start_time = time.time()
                    cur.execute(
                        """
                        SELECT COUNT(*) 
                        FROM conversation_context 
                        WHERE entities ? 'python'
                    """
                    )
                    jsonb_count = cur.fetchone()[0]
                    results["jsonb_query"] = {
                        "result": jsonb_count,
                        "time_ms": round((time.time() - start_time) * 1000, 2),
                    }

                    # Test 4: Join query
                    start_time = time.time()
                    cur.execute(
                        """
                        SELECT 
                            cs.session_id,
                            COUNT(cc.context_id) as context_count
                        FROM conversation_sessions cs
                        LEFT JOIN conversation_context cc ON cs.session_id = cc.session_id
                        GROUP BY cs.session_id
                        ORDER BY context_count DESC
                        LIMIT 10
                    """
                    )
                    join_result = cur.fetchall()
                    results["join_query"] = {
                        "result": [dict(row) for row in join_result],
                        "time_ms": round((time.time() - start_time) * 1000, 2),
                    }

                    return results
        except Exception as e:
            return {"error": f"Query performance error: {e}"}

    def check_indexes(self) -> dict[str, Any]:
        """Check index usage and performance."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Get all indexes
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                        FROM pg_stat_user_indexes 
                        ORDER BY pg_relation_size(indexrelid) DESC
                    """
                    )
                    all_indexes = cur.fetchall()

                    # Get unused indexes
                    cur.execute(
                        """
                        SELECT 
                            schemaname,
                            tablename,
                            indexname,
                            pg_size_pretty(pg_relation_size(indexrelid)) as index_size
                        FROM pg_stat_user_indexes 
                        WHERE idx_scan = 0
                        ORDER BY pg_relation_size(indexrelid) DESC
                    """
                    )
                    unused_indexes = cur.fetchall()

                    return {
                        "all_indexes": [dict(row) for row in all_indexes],
                        "unused_indexes": [dict(row) for row in unused_indexes],
                        "total_indexes": len(all_indexes),
                        "unused_count": len(unused_indexes),
                    }
        except Exception as e:
            return {"error": f"Index check error: {e}"}

    def check_data_quality(self) -> dict[str, Any]:
        """Check data quality and integrity."""
        try:
            with psycopg2.connect(self.dsn) as conn:
                with conn.cursor() as cur:
                    results = {}

                    # Check for NULL values in critical columns
                    cur.execute(
                        """
                        SELECT 
                            COUNT(*) as total_records,
                            COUNT(session_id) as non_null_session_id,
                            COUNT(context_type) as non_null_context_type,
                            COUNT(entities) as non_null_entities
                        FROM conversation_context
                    """
                    )
                    null_check = cur.fetchone()
                    results["null_checks"] = {
                        "total_records": null_check[0],
                        "non_null_session_id": null_check[1],
                        "non_null_context_type": null_check[2],
                        "non_null_entities": null_check[3],
                    }

                    # Check data distribution
                    cur.execute(
                        """
                        SELECT 
                            context_type,
                            COUNT(*) as count,
                            MIN(created_at) as earliest,
                            MAX(created_at) as latest
                        FROM conversation_context
                        GROUP BY context_type
                        ORDER BY count DESC
                    """
                    )
                    distribution = cur.fetchall()
                    results["data_distribution"] = [dict(row) for row in distribution]

                    # Check JSONB data quality
                    cur.execute(
                        """
                        SELECT 
                            COUNT(*) as total_entities,
                            COUNT(*) FILTER (WHERE jsonb_typeof(entities) = 'array') as array_entities,
                            COUNT(*) FILTER (WHERE jsonb_array_length(entities) > 0) as non_empty_entities
                        FROM conversation_context
                        WHERE entities IS NOT NULL
                    """
                    )
                    jsonb_check = cur.fetchone()
                    results["jsonb_quality"] = {
                        "total_entities": jsonb_check[0],
                        "array_entities": jsonb_check[1],
                        "non_empty_entities": jsonb_check[2],
                    }

                    return results
        except Exception as e:
            return {"error": f"Data quality check error: {e}"}

    def generate_report(self) -> dict[str, Any]:
        """Generate comprehensive performance report."""
        print("🔍 Generating Simple Database Performance Report...")
        print("=" * 60)

        report = {
            "timestamp": datetime.now().isoformat(),
            "basic_stats": self.get_basic_stats(),
            "query_performance": self.test_query_performance(),
            "index_analysis": self.check_indexes(),
            "data_quality": self.check_data_quality(),
        }

        return report

    def print_summary(self, report: dict[str, Any]):
        """Print a human-readable summary."""
        print("\n📊 DATABASE PERFORMANCE SUMMARY")
        print("=" * 60)

        # Basic stats
        if "basic_stats" in report and "error" not in report["basic_stats"]:
            stats = report["basic_stats"]
            print(f"💾 Database Size: {stats['database_size']}")
            print(f"🔗 Active Connections: {stats['connection_count']}")

            if "tables" in stats:
                total_rows = sum(table["row_count"] for table in stats["tables"])
                print(f"📋 Total Records: {total_rows:,}")

                # Show top tables
                print("📈 Top Tables by Row Count:")
                for table in stats["tables"][:5]:
                    print(f"   - {table['table_name']}: {table['row_count']:,} rows ({table['table_size']})")

        # Query performance
        if "query_performance" in report and "error" not in report["query_performance"]:
            perf = report["query_performance"]
            print("\n⚡ Query Performance:")
            for test_name, result in perf.items():
                if "time_ms" in result:
                    print(f"   - {test_name}: {result['time_ms']}ms")

        # Index analysis
        if "index_analysis" in report and "error" not in report["index_analysis"]:
            idx = report["index_analysis"]
            print("\n📊 Index Analysis:")
            print(f"   - Total Indexes: {idx['total_indexes']}")
            print(f"   - Unused Indexes: {idx['unused_count']}")
            if idx["unused_count"] > 0:
                print("   ⚠️  Consider removing unused indexes for better performance")
            else:
                print("   ✅ All indexes are being used")

        # Data quality
        if "data_quality" in report and "error" not in report["data_quality"]:
            quality = report["data_quality"]
            if "null_checks" in quality:
                nulls = quality["null_checks"]
                print("\n🔍 Data Quality:")
                print(f"   - Total Records: {nulls['total_records']:,}")
                print(f"   - Complete Records: {nulls['non_null_session_id']:,}")

                if nulls["total_records"] > 0:
                    completeness = (nulls["non_null_session_id"] / nulls["total_records"]) * 100
                    print(f"   - Data Completeness: {completeness:.1f}%")

        # Performance recommendations
        print("\n💡 Performance Recommendations:")
        if "query_performance" in report and "error" not in report["query_performance"]:
            perf = report["query_performance"]
            slow_queries = [name for name, result in perf.items() if "time_ms" in result and result["time_ms"] > 100]
            if slow_queries:
                print(f"   - Consider optimizing: {', '.join(slow_queries)}")
            else:
                print("   - All queries are performing well (< 100ms)")

        if "index_analysis" in report and "error" not in report["index_analysis"]:
            idx = report["index_analysis"]
            if idx["unused_count"] > 0:
                print("   - Remove unused indexes to reduce storage overhead")

    def save_report(self, report: dict[str, Any], filename: str = None):
        """Save report to JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"metrics/simple_db_performance_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            print(f"📁 Report saved to: {filename}")
        except Exception as e:
            print(f"❌ Error saving report: {e}")

def main():
    """Main monitoring function."""
    print("🔍 Simple Database Performance Monitor")
    print("=" * 60)

    # Get database DSN
    dsn = "postgresql://danieljacobs@localhost:5432/ai_agency"
    print(f"📡 Monitoring database: {dsn}")

    # Create monitor
    monitor = SimpleDatabaseMonitor(dsn)

    # Generate report
    report = monitor.generate_report()

    # Print summary
    monitor.print_summary(report)

    # Save detailed report
    monitor.save_report(report)

    print("\n🎉 Performance monitoring complete!")

if __name__ == "__main__":
    main()
