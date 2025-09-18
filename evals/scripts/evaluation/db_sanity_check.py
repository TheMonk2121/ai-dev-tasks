#!/usr/bin/env python3
"""
Database sanity check script to verify PostgreSQL extensions and indexes
for optimal BM25 and trigram fallback performance.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from psycopg import Connection
from psycopg.rows import DictRow, dict_row

from src.common.psycopg3_config import get_db_connection


def check_extensions(conn: Connection[DictRow]) -> None:
    """Check if required extensions are installed."""
    print("\n🔍 Checking PostgreSQL Extensions...")

    required_extensions = {
        "pg_trgm": "Trigram similarity for BM25 fallback",
        "vector": "Vector similarity for embeddings",
    }

    with conn.cursor(row_factory=dict_row) as cursor:
        for ext_name, description in required_extensions.items():
            try:
                _ = cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = %s)", (ext_name,))
                result = cursor.fetchone()
                exists = result["exists"] if result else False

                if exists:
                    print(f"✅ {ext_name}: {description}")
                else:
                    print(f"❌ {ext_name}: {description} - NOT INSTALLED")
                    print(f"   Install with: CREATE EXTENSION IF NOT EXISTS {ext_name};")
            except Exception as e:
                print(f"⚠️  {ext_name}: Error checking - {e}")


def check_indexes(conn: Connection[DictRow]) -> None:
    """Check if recommended indexes exist."""
    print("\n🔍 Checking Recommended Indexes...")

    recommended_indexes = [
        {
            "name": "idx_dc_bm25_trgm",
            "table": "document_chunks",
            "columns": "bm25_text",
            "type": "gin",
            "ops": "gin_trgm_ops",
            "description": "Trigram index for BM25 text fallback",
        },
        {
            "name": "idx_dc_file_path_trgm",
            "table": "document_chunks",
            "columns": "file_path",
            "type": "gin",
            "ops": "gin_trgm_ops",
            "description": "Trigram index for file path fallback",
        },
    ]

    with conn.cursor(row_factory=dict_row) as cursor:
        for idx in recommended_indexes:
            try:
                _ = cursor.execute(
                    """
                    SELECT EXISTS(
                        SELECT 1 FROM pg_indexes 
                        WHERE indexname = %s
                    )
                    """,
                    (idx["name"],),
                )
                result = cursor.fetchone()
                exists = result["exists"] if result else False

                if exists:
                    print(f"✅ {idx['name']}: {idx['description']}")
                else:
                    print(f"❌ {idx['name']}: {idx['description']} - NOT FOUND")
                    print(
                        f"   Create with: CREATE INDEX IF NOT EXISTS {idx['name']} ON {idx['table']} USING {idx['type']} ({idx['columns']} {idx['ops']});"
                    )
            except Exception as e:
                print(f"⚠️  {idx['name']}: Error checking - {e}")


def check_trigram_settings(conn: Connection[DictRow]) -> None:
    """Check trigram similarity settings."""
    print("\n🔍 Checking Trigram Settings...")

    with conn.cursor(row_factory=dict_row) as cursor:
        try:
            # Try different ways to get trigram threshold depending on PostgreSQL version
            try:
                _ = cursor.execute("SHOW pg_trgm.similarity_threshold")
                result = cursor.fetchone()
                threshold = result["pg_trgm.similarity_threshold"] if result else "0.3"
            except Exception:
                # Fallback for newer PostgreSQL versions
                _ = cursor.execute("SELECT current_setting('pg_trgm.similarity_threshold', true)")
                result = cursor.fetchone()
                threshold = result["current_setting"] if result else "0.3"

            print(f"📊 Current trigram similarity threshold: {threshold}")

            if float(threshold) > 0.1:
                print("💡 Consider lowering threshold for better fallback matching:")
                print("   SELECT set_limit(0.1);")
            else:
                print("✅ Threshold is appropriately low for fallback matching")

        except Exception as e:
            print(f"⚠️  Error checking trigram settings: {e}")
            print("   This is normal for some PostgreSQL versions")


def check_table_stats(conn: Connection[DictRow]) -> None:
    """Check basic table statistics."""
    print("\n🔍 Checking Table Statistics...")

    with conn.cursor(row_factory=dict_row) as cursor:
        try:
            _ = cursor.execute(
                """
                SELECT 
                    schemaname,
                    relname as table_name,
                    n_tup_ins as inserts,
                    n_tup_upd as updates,
                    n_tup_del as deletes,
                    n_live_tup as live_rows,
                    n_dead_tup as dead_rows
                FROM pg_stat_user_tables 
                WHERE relname IN ('document_chunks', 'documents')
                ORDER BY relname
                """
            )

            results = cursor.fetchall()

            if results:
                print("📊 Table Statistics:")
                for row in results:
                    schema = row["schemaname"]
                    table = row["table_name"]
                    inserts = row["inserts"]
                    updates = row["updates"]
                    deletes = row["deletes"]
                    live = row["live_rows"]
                    dead = row["dead_rows"]
                    print(f"   {schema}.{table}: {live:,} live rows, {dead:,} dead rows")
                    print(f"      Operations: {inserts:,} inserts, {updates:,} updates, {deletes:,} deletes")
            else:
                print("⚠️  No statistics found for document tables")

        except Exception as e:
            print(f"⚠️  Error checking table statistics: {e}")
            print("   This may be normal if tables don't exist yet")


def main():
    """Main sanity check function."""
    print("🔧 Database Sanity Check")
    print("=" * 50)

    # Get database connection
    try:
        conn = get_db_connection()
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return 1

    try:
        # Run all checks
        check_extensions(conn)
        check_indexes(conn)
        check_trigram_settings(conn)
        check_table_stats(conn)

        print("\n✅ Database sanity check completed")
        print("\n💡 Recommendations:")
        print("   1. Install missing extensions if needed")
        print("   2. Create recommended indexes for better performance")
        print("   3. Consider lowering trigram threshold if fallback is too strict")
        print("   4. Run VACUUM ANALYZE if table statistics seem stale")

        return 0

    except Exception as e:
        print(f"❌ Error during sanity check: {e}")
        return 1
    finally:
        # Ensure connection is properly closed
        if conn:
            conn.close()


if __name__ == "__main__":
    sys.exit(main())
