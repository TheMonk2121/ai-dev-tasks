from __future__ import annotations
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
from src.common.db_dsn import resolve_dsn
#!/usr/bin/env python3
"""
Database Schema Setup for Evaluation System
Creates all required tables, indexes, and extensions for the evaluation system.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_extensions(cur):
    """Create required PostgreSQL extensions."""
    print("🔧 Creating PostgreSQL extensions...")

    extensions = [
        "vector",  # For vector similarity search
        "pg_trgm",  # For trigram text search
        "timescaledb",  # For time-series data (optional)
    ]

    for ext in extensions:
        try:
            cur.execute(f"CREATE EXTENSION IF NOT EXISTS {ext}")
            print(f"   ✅ {ext} extension created/enabled")
        except Exception as e:
            print(f"   ⚠️  {ext} extension: {e}")
            # Ensure connection is usable after extension failure
            try:
                cur.connection.rollback()
            except Exception:
                pass

def create_documents_table(cur):
    """Create documents table for storing document metadata."""
    print("📄 Creating documents table...")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            file_path VARCHAR(500) UNIQUE NOT NULL,
            file_name VARCHAR(255) NOT NULL,
            content_type VARCHAR(100) DEFAULT 'text',
            content_sha VARCHAR(64),
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Create indexes
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_file_path 
        ON documents (file_path)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_documents_content_type 
        ON documents (content_type)
    """
    )

    print("   ✅ documents table created with indexes")

def create_document_chunks_table(cur):
    """Create document_chunks table for storing chunks with embeddings."""
    print("📝 Creating document_chunks table...")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS document_chunks (
            id SERIAL PRIMARY KEY,
            document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,
            content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
            embedding vector(384),  -- Cursor AI embedding dimension
            metadata JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(document_id, chunk_index)
        )
    """
    )

    # Create indexes for performance
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
        ON document_chunks (document_id)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_chunks_content_tsv 
        ON document_chunks USING GIN (content_tsv)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding 
        ON document_chunks USING ivfflat (embedding vector_cosine_ops) 
        WITH (lists = 200)
    """
    )

    print("   ✅ document_chunks table created with indexes")

def create_evaluation_metrics_table(cur):
    """Create evaluation_metrics table for storing evaluation results."""
    print("📊 Creating evaluation_metrics table...")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluation_metrics (
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            run_id UUID NOT NULL,
            profile VARCHAR(100) NOT NULL,
            pass_id VARCHAR(100) NOT NULL,
            f1 DOUBLE PRECISION,
            precision DOUBLE PRECISION,
            recall DOUBLE PRECISION,
            faithfulness DOUBLE PRECISION,
            artifact_path TEXT,
            git_sha VARCHAR(40),
            tags TEXT[] DEFAULT '{}',
            PRIMARY KEY (ts, run_id)
        )
    """
    )

    # Create hypertable if TimescaleDB is available
    try:
        cur.execute(
            """
            SELECT create_hypertable('evaluation_metrics', 'ts', if_not_exists => true)
        """
        )
        print("   ✅ evaluation_metrics hypertable created")
    except Exception as e:
        print(f"   ⚠️  TimescaleDB hypertable: {e}")

    # Create indexes
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_profile 
        ON evaluation_metrics (profile, ts)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_evaluation_metrics_run_id 
        ON evaluation_metrics (run_id)
    """
    )

    print("   ✅ evaluation_metrics table created with indexes")

def create_maintenance_metrics_table(cur):
    """Create maintenance_metrics table for storing maintenance analysis data."""
    print("🧹 Creating maintenance_metrics table...")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS maintenance_metrics (
            ts TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            session_id UUID NOT NULL,
            maintenance_type VARCHAR(100) NOT NULL,
            status VARCHAR(50) NOT NULL,
            files_removed INTEGER DEFAULT 0,
            directories_removed INTEGER DEFAULT 0,
            bytes_freed BIGINT DEFAULT 0,
            duration_seconds REAL,
            error_count INTEGER DEFAULT 0,
            analysis_data JSONB,
            metadata JSONB,
            git_sha VARCHAR(40),
            PRIMARY KEY (ts, session_id)
        )
        """
    )

    # Create indexes
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_type_ts 
        ON maintenance_metrics (maintenance_type, ts)
        """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_maintenance_metrics_session_id 
        ON maintenance_metrics (session_id)
        """
    )

    # Try to create hypertable if TimescaleDB is available
    try:
        cur.execute(
            """
            SELECT create_hypertable('maintenance_metrics', 'ts', if_not_exists => true)
            """
        )
        print("   ✅ maintenance_metrics hypertable created")
    except Exception as e:
        print(f"   ⚠️  TimescaleDB hypertable: {e}")

    print("   ✅ maintenance_metrics table created with indexes")

def create_conversation_tables(cur):
    """Create conversation-related tables for memory system."""
    print("💬 Creating conversation tables...")

    # Conversation sessions
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_sessions (
            session_id VARCHAR(255) PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'
        )
    """
    )

    # Conversation context
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_context (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) REFERENCES conversation_sessions(session_id) ON DELETE CASCADE,
            context_type VARCHAR(100) NOT NULL,
            context_key VARCHAR(255) NOT NULL,
            context_value TEXT NOT NULL,
            relevance_score DOUBLE PRECISION DEFAULT 0.0,
            context_hash VARCHAR(64),
            metadata JSONB DEFAULT '{}',
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(session_id, context_type, context_key)
        )
    """
    )

    # Create indexes
    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversation_context_session_id 
        ON conversation_context (session_id)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversation_context_type 
        ON conversation_context (context_type)
    """
    )

    print("   ✅ conversation tables created with indexes")

def create_memory_system_tables(cur):
    """Create memory system tables for advanced memory management."""
    print("🧠 Creating memory system tables...")

    # Conversational chunks
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
        )
    """
    )

    # Make conv_chunks a hypertable if TimescaleDB is available (for 48h hot-pool retention)
    try:
        cur.execute(
            """
            SELECT create_hypertable('conv_chunks', 'created_at', if_not_exists => true)
            """
        )
        # Apply a default 48-hour retention policy for the hot pool
        # Note: This is a coarse policy and does not consider is_pinned. Pinning logic,
        # if required, should be handled by application-level promotion before expiry.
        cur.execute(
            """
            SELECT add_retention_policy('conv_chunks', INTERVAL '48 hours')
            """
        )
        print("   ✅ conv_chunks hypertable with 48h retention policy")
    except Exception as e:
        print(f"   ⚠️  TimescaleDB conv_chunks retention: {e}")

    # Rolling summaries
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS rolling_summaries (
            session_id VARCHAR(255) PRIMARY KEY,
            goals TEXT[] DEFAULT ARRAY[]::TEXT[],
            decisions TEXT[] DEFAULT ARRAY[]::TEXT[],
            open_questions TEXT[] DEFAULT ARRAY[]::TEXT[],
            next_actions TEXT[] DEFAULT ARRAY[]::TEXT[],
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            turn_count INTEGER DEFAULT 0
        )
    """
    )

    # Entity facts
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS entity_facts (
            id BIGSERIAL PRIMARY KEY,
            entity VARCHAR(255) NOT NULL,
            fact_key VARCHAR(255) NOT NULL,
            fact_value TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            status VARCHAR(20) DEFAULT 'active',
            version INTEGER DEFAULT 1,
            source_turn_id BIGINT,
            last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(entity, fact_key, version)
        )
    """
    )

    # Episodes
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS episodes (
            id BIGSERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            episode_type VARCHAR(50) NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            entities TEXT[] DEFAULT ARRAY[]::TEXT[],
            salience_score REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """
    )

    # Prune log
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS conv_prune_log (
            id BIGSERIAL PRIMARY KEY,
            pruned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            chunk_id BIGINT NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            reason TEXT NOT NULL,
            salience_score REAL,
            created_at TIMESTAMP,
            last_accessed TIMESTAMP,
            access_count BIGINT
        )
    """
    )

    # Create indexes for memory system
    # ANN index for long-term store is HNSW; for the hot pool, exact scan is acceptable.
    # Keep HNSW here to preserve existing behavior; consider gating by env if needed.
    try:
        cur.execute(
            """
            CREATE INDEX IF NOT EXISTS conv_chunks_embedding_idx 
            ON conv_chunks USING hnsw (embedding vector_cosine_ops)
        """
        )
    except Exception as e:
        print(f"   ⚠️  conv_chunks HNSW index: {e}")

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS conv_chunks_tsv_idx 
        ON conv_chunks USING GIN (chunk_tsv)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS conv_chunks_session_idx 
        ON conv_chunks (session_id, created_at)
    """
    )

    cur.execute(
        """
        CREATE INDEX IF NOT EXISTS entity_facts_active_idx 
        ON entity_facts (entity, fact_key) WHERE status = 'active'
    """
    )

    print("   ✅ memory system tables created with indexes")

def verify_schema(cur):
    """Verify that all required tables and indexes exist."""
    print("🔍 Verifying database schema...")

    required_tables = [
        "documents",
        "document_chunks",
        "evaluation_metrics",
        "maintenance_metrics",
        "conversation_sessions",
        "conversation_context",
        "conv_chunks",
        "rolling_summaries",
        "entity_facts",
        "episodes",
        "conv_prune_log",
    ]

    missing_tables = []
    for table in required_tables:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """,
            (table,),
        )
        if not cur.fetchone()[0]:
            missing_tables.append(table)

    if missing_tables:
        print(f"   ❌ Missing tables: {', '.join(missing_tables)}")
        return False

    print("   ✅ All required tables exist")

    # Check for vector extension
    cur.execute(
        """
        SELECT EXISTS (
            SELECT FROM pg_extension WHERE extname = 'vector'
        )
    """
    )
    if not cur.fetchone()[0]:
        print("   ⚠️  Vector extension not found")
        return False

    print("   ✅ Vector extension is available")
    return True

def main():
    """Main function to set up the database schema."""
    print("🚀 Setting up database schema for evaluation system...")
    print("=" * 60)

    # Get database connection
    dsn = resolve_dsn(strict=True)
    if not dsn:
        print("❌ No database DSN configured")
        print("   Set POSTGRES_DSN or DATABASE_URL environment variable")
        return 1

    print(f"📡 Connecting to database: {dsn[:30]}...")

    try:
        with psycopg2.connect(dsn) as conn:
            # Avoid transaction aborts if optional extensions fail
            conn.autocommit = True
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Create extensions
                create_extensions(cur)

                # Create tables
                create_documents_table(cur)
                create_document_chunks_table(cur)
                create_evaluation_metrics_table(cur)
                create_maintenance_metrics_table(cur)
                create_conversation_tables(cur)
                create_memory_system_tables(cur)

                # Commit all changes
                conn.commit()

                # Verify schema
                if verify_schema(cur):
                    print("\n✅ Database schema setup completed successfully!")
                    print("🎉 All tables, indexes, and extensions are ready")
                    return 0
                else:
                    print("\n❌ Schema verification failed")
                    return 1

    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())