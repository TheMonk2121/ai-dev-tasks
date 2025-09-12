from __future__ import annotations
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
#!/usr/bin/env python3
"""
Database sanity check script to verify PostgreSQL extensions and indexes
for optimal BM25 and trigram fallback performance.
"""

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    try:
        conn = psycopg2.connect(dsn)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def check_extensions(conn):
    """Check if required extensions are installed."""
    print("\n🔍 Checking PostgreSQL Extensions...")

    required_extensions = {
        "pg_trgm": "Trigram similarity for BM25 fallback",
        "vector": "Vector similarity for embeddings",
    }

    cursor = conn.cursor()

    for ext_name, description in required_extensions.items():
        try:
            cursor.execute("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname = %s)", (ext_name,))
            exists = cursor.fetchone()[0]

            if exists:
                print(f"✅ {ext_name}: {description}")
            else:
                print(f"❌ {ext_name}: {description} - NOT INSTALLED")
                print(f"   Install with: CREATE EXTENSION IF NOT EXISTS {ext_name};")
        except Exception as e:
            print(f"⚠️  {ext_name}: Error checking - {e}")

    cursor.close()

def check_indexes(conn):
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

    cursor = conn.cursor()

    for idx in recommended_indexes:
        try:
            cursor.execute(
                """
                SELECT EXISTS(
                    SELECT 1 FROM pg_indexes 
                    WHERE indexname = %s
                )
            """,
                (idx["name"],),
            )
            exists = cursor.fetchone()[0]

            if exists:
                print(f"✅ {idx['name']}: {idx['description']}")
            else:
                print(f"❌ {idx['name']}: {idx['description']} - NOT CREATED")
                print(
                    f"   Create with: CREATE INDEX IF NOT EXISTS {idx['name']} ON {idx['table']} USING {idx['type']} ({idx['columns']} {idx['ops']});"
                )
        except Exception as e:
            print(f"⚠️  {idx['name']}: Error checking - {e}")

    cursor.close()

def check_trigram_settings(conn):
    """Check trigram similarity settings."""
    print("\n🔍 Checking Trigram Settings...")

    cursor = conn.cursor()

    try:
        # Try different ways to get trigram threshold depending on PostgreSQL version
        try:
            cursor.execute("SHOW pg_trgm.similarity_threshold")
            threshold = cursor.fetchone()[0]
        except Exception:
            # Fallback for newer PostgreSQL versions
            cursor.execute("SELECT current_setting('pg_trgm.similarity_threshold', true)")
            threshold = cursor.fetchone()[0]

        print(f"📊 Current trigram similarity threshold: {threshold}")

        if float(threshold) > 0.1:
            print("💡 Consider lowering threshold for better fallback matching:")
            print("   SELECT set_limit(0.1);")
        else:
            print("✅ Threshold is appropriately low for fallback matching")

    except Exception as e:
        print(f"⚠️  Error checking trigram settings: {e}")
        print("   This is normal for some PostgreSQL versions")

    cursor.close()

def check_table_stats(conn):
    """Check basic table statistics."""
    print("\n🔍 Checking Table Statistics...")

    cursor = conn.cursor()

    try:
        cursor.execute(
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
                schema, table, inserts, updates, deletes, live, dead = row
                print(f"   {schema}.{table}: {live:,} live rows, {dead:,} dead rows")
                print(f"      Operations: {inserts:,} inserts, {updates:,} updates, {deletes:,} deletes")
        else:
            print("⚠️  No statistics found for document tables")

    except Exception as e:
        print(f"⚠️  Error checking table statistics: {e}")
        print("   This may be normal if tables don't exist yet")

    cursor.close()

def main():
    """Main sanity check function."""
    print("🔧 Database Sanity Check")
    print("=" * 50)

    # Get database connection
    conn = get_db_connection()
    if not conn:
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
        conn.close()

if __name__ == "__main__":
    sys.exit(main())