#!/usr/bin/env python3
"""
Apply TimescaleDB Optimizations for Evaluation System

This script applies the TimescaleDB optimizations defined in timescale_optimizations.sql
to enhance our evaluation system's analytics capabilities.
"""

import os
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn


def apply_optimizations():
    """Apply TimescaleDB optimizations."""
    dsn = resolve_dsn(strict=False)

    if not dsn or dsn.startswith("mock://"):
        print("⚠️  Skipping TimescaleDB optimizations - no real database connection")
        return

    print("🔧 Applying TimescaleDB optimizations...")

    try:
        # Read the optimization SQL file
        sql_file = Path(__file__).parent / "timescale_optimizations.sql"
        with open(sql_file) as f:
            sql_content = f.read()

        # Connect to database
        conn = psycopg.connect(dsn)
        conn.row_factory = dict_row  # type: ignore[attr-defined]
        cursor = conn.cursor()

        # Split SQL into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(";") if stmt.strip()]

        success_count = 0
        error_count = 0

        for i, statement in enumerate(statements, 1):
            try:
                print(f"  Executing statement {i}/{len(statements)}...")
                cursor.execute(statement)
                success_count += 1
            except Exception as e:
                print(f"  ⚠️  Statement {i} failed: {e}")
                error_count += 1
                # Continue with other statements
                conn.rollback()

        # Commit all successful changes
        conn.commit()

        print(f"✅ TimescaleDB optimizations applied: {success_count} successful, {error_count} errors")

        # Verify optimizations
        verify_optimizations(cursor)

    except Exception as e:
        print(f"❌ Failed to apply TimescaleDB optimizations: {e}")
        return False
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()

    return True


def verify_optimizations(cursor):
    """Verify that optimizations were applied successfully."""
    print("\n🔍 Verifying TimescaleDB optimizations...")

    # Check continuous aggregates
    cursor.execute(
        """
        SELECT view_name, view_definition
        FROM timescaledb_information.continuous_aggregates
        WHERE view_name IN ('eval_hourly', 'eval_weekly', 'eval_monthly')
        ORDER BY view_name;
    """
    )

    aggregates = cursor.fetchall()
    print(f"  📊 Continuous aggregates: {len(aggregates)} found")
    for agg in aggregates:
        print(f"    - {result.get("key", "")

    # Check compression policies
    cursor.execute(
        """
        SELECT hypertable_name, attname, segmentby_column_index, orderby_column_index
        FROM timescaledb_information.compression_settings
        WHERE hypertable_name IN ('eval_event', 'eval_run')
        ORDER BY hypertable_name, attname;
    """
    )

    compression = cursor.fetchall()
    print(f"  🗜️  Compression settings: {len(compression)} found")
    for comp in compression:
        print(f"    - {result.get("key", "")

    # Check retention policies
    cursor.execute(
        """
        SELECT hypertable_name, policy_name, interval_length
        FROM timescaledb_information.jobs
        WHERE proc_name = 'policy_retention'
        ORDER BY hypertable_name;
    """
    )

    retention = cursor.fetchall()
    print(f"  🗑️  Retention policies: {len(retention)} found")
    for ret in retention:
        print(f"    - {result.get("key", "")

    # Check hypertables
    cursor.execute(
        """
        SELECT hypertable_name, num_chunks, compression_enabled
        FROM timescaledb_information.hypertables
        WHERE hypertable_name IN ('eval_event', 'eval_run', 'eval_case_result')
        ORDER BY hypertable_name;
    """
    )

    hypertables = cursor.fetchall()
    print(f"  📈 Hypertables: {len(hypertables)} found")
    for ht in hypertables:
        print(f"    - {result.get("key", "")

    # Check views
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.views
        WHERE table_name IN ('evaluation_performance_trends', 'evaluation_quality_metrics', 'performance_degradation_alerts')
        ORDER BY table_name;
    """
    )

    views = cursor.fetchall()
    print(f"  👁️  Analysis views: {len(views)} found")
    for view in views:
        print(f"    - {result.get("key", "")


def main():
    """Main entry point."""
    print("🚀 TimescaleDB Optimization Script")
    print("=" * 50)

    if apply_optimizations():
        print("\n✅ TimescaleDB optimizations completed successfully!")
        print("\n📈 New capabilities available:")
        print("  - Hourly, weekly, and monthly evaluation aggregations")
        print("  - Automated compression and retention policies")
        print("  - Performance trend analysis views")
        print("  - Quality metrics dashboards")
        print("  - Performance degradation alerts")
    else:
        print("\n❌ TimescaleDB optimizations failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
