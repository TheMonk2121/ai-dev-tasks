from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from psycopg import IsolationLevel

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

#!/usr/bin/env python3
"""
Apply database optimizations for trigram fallback performance.
Creates recommended indexes and sets optimal trigram threshold.
"""

# Add project root to path
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def get_db_connection():
    """Get database connection from environment or default."""
    dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
    try:
        conn = psycopg.connect(dsn)
        conn.set_isolation_level(IsolationLevel.AUTOCOMMIT)  # type: ignore
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def create_trigram_indexes(conn):
    """Create trigram indexes for better fallback performance."""
    print("🔧 Creating Trigram Indexes...")

    indexes = [
        {
            "name": "idx_dc_bm25_trgm",
            "sql": "CREATE INDEX IF NOT EXISTS idx_dc_bm25_trgm ON document_chunks USING gin (bm25_text gin_trgm_ops)",
            "description": "Trigram index for BM25 text fallback",
        },
        {
            "name": "idx_dc_file_path_trgm",
            "sql": "CREATE INDEX IF NOT EXISTS idx_dc_file_path_trgm ON document_chunks USING gin (file_path gin_trgm_ops)",
            "description": "Trigram index for file path fallback",
        },
    ]

    cursor = conn.cursor()

    for idx in indexes:
        try:
            print(f"   Creating {idx['name']}...")
            cursor.execute(idx["sql"])
            print(f"   ✅ {idx['description']}")
        except Exception as e:
            print(f"   ❌ Failed to create {idx['name']}: {e}")

    cursor.close()

def set_trigram_threshold(conn):
    """Set optimal trigram similarity threshold."""
    print("🔧 Setting Trigram Threshold...")

    cursor = conn.cursor()

    try:
        # Set threshold to 0.1 for better fallback matching
        cursor.execute("SELECT set_limit(0.1)")
        result = cursor.fetchone()[0]
        print(f"   ✅ Trigram similarity threshold set to: {result}")
    except Exception as e:
        print(f"   ⚠️  Could not set trigram threshold: {e}")
        print("   This may be normal for some PostgreSQL versions")

    cursor.close()

def verify_optimizations(conn):
    """Verify that optimizations were applied successfully."""
    print("🔍 Verifying Optimizations...")

    cursor = conn.cursor()

    # Check indexes
    try:
        cursor.execute(
            """
            SELECT indexname 
            FROM pg_indexes 
            WHERE indexname IN ('idx_dc_bm25_trgm', 'idx_dc_file_path_trgm')
            ORDER BY indexname
        """
        )
        indexes = [row[0] for row in cursor.fetchall()]

        if len(indexes) == 2:
            print("   ✅ Both trigram indexes created successfully")
        else:
            print(f"   ⚠️  Only {len(indexes)}/2 indexes found: {indexes}")
    except Exception as e:
        print(f"   ❌ Error verifying indexes: {e}")

    # Check threshold
    try:
        cursor.execute("SELECT current_setting('pg_trgm.similarity_threshold', true)")
        threshold = cursor.fetchone()[0]
        if threshold:
            print(f"   ✅ Trigram threshold: {threshold}")
        else:
            print("   ⚠️  Could not verify trigram threshold")
    except Exception as e:
        print(f"   ⚠️  Could not verify trigram threshold: {e}")

    cursor.close()

def main():
    """Main optimization function."""
    print("🚀 Database Optimization")
    print("=" * 50)

    # Get database connection
    conn = get_db_connection()
    if not conn:
        return 1

    try:
        # Apply optimizations
        create_trigram_indexes(conn)
        set_trigram_threshold(conn)
        verify_optimizations(conn)

        print("\n✅ Database optimization completed")
        print("\n💡 Next steps:")
        print("   1. Re-enable trigram fallback in gold profile:")
        print("      - Remove BM25_TRIGRAM_FALLBACK=0")
        print("      - Remove TITLE_TRIGRAM_FALLBACK=0")
        print("   2. Run evaluation to test improved performance")
        print("   3. Monitor logs for reduced trigram fallback warnings")

        return 0

    except Exception as e:
        print(f"❌ Error during optimization: {e}")
        return 1
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())