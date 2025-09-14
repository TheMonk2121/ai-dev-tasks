#!/usr/bin/env python3
"""
Setup Missing Database Tables

Creates the missing conv_chunks table and other required tables
for the evaluation system.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def setup_missing_tables():
    """Create missing database tables."""

    print("🔧 Setting up missing database tables...")
    print("=" * 50)

    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        # Connect to database
        dsn = os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")
        conn = psycopg2.connect(dsn)
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Create conv_chunks table (48-hour hot memory pool)
        print("📝 Creating conv_chunks table...")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conv_chunks (
                id BIGSERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding vector(384) NOT NULL,
                entities TEXT[] DEFAULT ARRAY[]::TEXT[],
                salience_score REAL DEFAULT 0.0,
                source_turn_id BIGINT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                is_pinned BOOLEAN DEFAULT FALSE,
                chunk_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', chunk_text)) STORED
            );
        """
        )

        # Create index on embedding for similarity search
        print("🔍 Creating embedding index...")
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS conv_chunks_embedding_idx 
            ON conv_chunks USING hnsw (embedding vector_cosine_ops);
        """
        )

        # Create index on created_at for time-based queries
        print("⏰ Creating timestamp index...")
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS conv_chunks_created_at_idx 
            ON conv_chunks (created_at);
        """
        )

        # Create index on session_id for session-based queries
        print("🔗 Creating session index...")
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS conv_chunks_session_id_idx 
            ON conv_chunks (session_id);
        """
        )

        # Create index on tsvector for text search
        print("📝 Creating text search index...")
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS conv_chunks_tsv_idx 
            ON conv_chunks USING gin (chunk_tsv);
        """
        )

        # Try to create hypertable (if TimescaleDB is available)
        print("📊 Attempting to create hypertable...")
        try:
            cur.execute("SELECT create_hypertable('conv_chunks', 'created_at', if_not_exists => true);")
            print("   ✅ Hypertable created successfully")

            # Add retention policy
            cur.execute("SELECT add_retention_policy('conv_chunks', INTERVAL '48 hours');")
            print("   ✅ 48-hour retention policy added")
        except Exception as e:
            print(f"   ⚠️ Hypertable creation skipped: {e}")
            print("   ℹ️ Table created as regular PostgreSQL table")

        # Commit changes
        conn.commit()
        print("✅ All tables created successfully")

        # Verify table creation
        cur.execute(
            """
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'conv_chunks' 
            ORDER BY ordinal_position
        """
        )

        columns = cur.fetchall()
        print(f"\n📋 conv_chunks table structure:")
        for col in columns:
            print(f"   • {col['column_name']}: {col['data_type']}")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False


def main():
    """Main function."""
    success = setup_missing_tables()

    if success:
        print("\n✅ Database setup completed successfully!")
        print("   Ready to proceed with data ingestion.")
    else:
        print("\n❌ Database setup failed!")
        print("   Please check the error messages above.")

    return success


if __name__ == "__main__":
    main()
