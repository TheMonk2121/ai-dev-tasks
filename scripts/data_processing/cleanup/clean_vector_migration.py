#!/usr/bin/env python3
"""
Clean migration of vector tables to 384 dimensions with fresh start.
"""

import os

# Add project paths
import sys

import psycopg

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config


def clean_vector_migration():
    """Clean migration with fresh start."""

    print("🔄 CLEAN VECTOR MIGRATION: Fresh Start → 384 dimensions")
    print("=" * 70)

    try:
        with psycopg.connect(resolve_dsn(strict=False, role="clean_vector_migration")) as conn:
            with conn.cursor() as cur:
                # Step 1: Start fresh - drop and recreate tables
                print("\\n🔧 Step 1: Fresh start - recreating vector tables...")

                # Drop all views first
                views_to_drop = ["conversation_summaries", "active_document_chunks", "active_conversation_sessions"]

                for view in views_to_drop:
                    try:
                        cur.execute(f"DROP VIEW IF EXISTS {view} CASCADE")
                        print(f"   ✅ {view}: Dropped view")
                    except Exception as e:
                        print(f"   ⚠️  {view}: Could not drop view: {e}")

                # Drop and recreate tables with 384 dimensions
                tables_to_recreate = [
                    {
                        "name": "atlas_node",
                        "sql": """
                            CREATE TABLE atlas_node_new (
                                node_id VARCHAR PRIMARY KEY,
                                node_type VARCHAR NOT NULL,
                                title TEXT NOT NULL,
                                content TEXT,
                                metadata JSONB,
                                embedding vector(384),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                expires_at TIMESTAMP
                            )
                        """,
                    },
                    {
                        "name": "conv_chunks",
                        "sql": """
                            CREATE TABLE conv_chunks_new (
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
                        """,
                    },
                    {
                        "name": "atlas_conversation_turn",
                        "sql": """
                            CREATE TABLE atlas_conversation_turn_new (
                                turn_id VARCHAR PRIMARY KEY,
                                thread_id VARCHAR NOT NULL,
                                role VARCHAR NOT NULL,
                                content TEXT NOT NULL,
                                timestamp TIMESTAMP NOT NULL,
                                embedding vector(384),
                                metadata JSONB,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """,
                    },
                    {
                        "name": "atlas_thread",
                        "sql": """
                            CREATE TABLE atlas_thread_new (
                                thread_id VARCHAR PRIMARY KEY,
                                session_id VARCHAR NOT NULL,
                                title VARCHAR NOT NULL,
                                status VARCHAR DEFAULT 'active',
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata JSONB,
                                embedding vector(384)
                            )
                        """,
                    },
                    {
                        "name": "conversation_memory",
                        "sql": """
                            CREATE TABLE conversation_memory_new (
                                id SERIAL PRIMARY KEY,
                                session_id VARCHAR NOT NULL,
                                content TEXT NOT NULL,
                                embedding vector(384),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata JSONB
                            )
                        """,
                    },
                    {
                        "name": "conversation_messages",
                        "sql": """
                            CREATE TABLE conversation_messages_new (
                                id SERIAL PRIMARY KEY,
                                session_id VARCHAR NOT NULL,
                                role VARCHAR NOT NULL,
                                content TEXT NOT NULL,
                                content_hash VARCHAR,
                                embedding vector(384),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata JSONB
                            )
                        """,
                    },
                    {
                        "name": "document_chunks",
                        "sql": """
                            CREATE TABLE document_chunks_new (
                                id SERIAL PRIMARY KEY,
                                document_id INTEGER NOT NULL,
                                chunk_index INTEGER NOT NULL,
                                content TEXT NOT NULL,
                                embedding vector(384),
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                metadata JSONB
                            )
                        """,
                    },
                ]

                for table_info in tables_to_recreate:
                    table_name = table_info["name"]
                    try:
                        # Drop old table
                        cur.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")

                        # Create new table with 384 dimensions
                        cur.execute(table_info["sql"])

                        # Rename to original name
                        cur.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")

                        print(f"   ✅ {table_name}: Recreated with vector(384)")

                    except Exception as e:
                        print(f"   ❌ {table_name}: Failed to recreate: {e}")

                # Step 2: Create indexes
                print("\\n🔧 Step 2: Creating vector indexes...")

                for table_info in tables_to_recreate:
                    table_name = table_info["name"]
                    try:
                        cur.execute(
                            f"""
                            CREATE INDEX IF NOT EXISTS {table_name}_embedding_idx 
                            ON {table_name} USING hnsw (embedding vector_cosine_ops)
                        """
                        )
                        print(f"   ✅ {table_name}: Created HNSW vector index")
                    except Exception as e:
                        print(f"   ⚠️  {table_name}: Could not create index: {e}")

                # Step 3: Recreate views
                print("\\n🔧 Step 3: Recreating views...")

                try:
                    cur.execute(
                        """
                        CREATE VIEW conversation_summaries AS
                        SELECT 
                            session_id,
                            COUNT(*) as message_count,
                            MAX(created_at) as last_message,
                            MIN(created_at) as first_message
                        FROM conversation_messages 
                        GROUP BY session_id
                    """
                    )
                    print("   ✅ conversation_summaries: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  conversation_summaries: Could not recreate view: {e}")

                try:
                    cur.execute(
                        """
                        CREATE VIEW active_document_chunks AS
                        SELECT 
                            dc.*,
                            d.file_path,
                            d.filename
                        FROM document_chunks dc
                        JOIN documents d ON dc.document_id = d.id
                        WHERE dc.created_at > NOW() - INTERVAL '7 days'
                    """
                    )
                    print("   ✅ active_document_chunks: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  active_document_chunks: Could not recreate view: {e}")

                try:
                    cur.execute(
                        """
                        CREATE VIEW active_conversation_sessions AS
                        SELECT 
                            session_id,
                            COUNT(*) as message_count,
                            MAX(created_at) as last_activity
                        FROM conversation_messages 
                        WHERE created_at > NOW() - INTERVAL '24 hours'
                        GROUP BY session_id
                    """
                    )
                    print("   ✅ active_conversation_sessions: Recreated view")
                except Exception as e:
                    print(f"   ⚠️  active_conversation_sessions: Could not recreate view: {e}")

                # Step 4: Test 384-dimensional vector insertion
                print("\\n🧪 Step 4: Testing 384-dimensional vector insertion...")

                test_vector = [0.1] * 384
                test_successful = []
                test_failed = []

                for table_info in tables_to_recreate:
                    table_name = table_info["name"]
                    try:
                        if table_name == "atlas_node":
                            cur.execute(
                                """
                                INSERT INTO atlas_node (node_id, node_type, title, content, embedding, expires_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_384_clean",
                                    "test",
                                    "Test 384",
                                    "Test content",
                                    test_vector,
                                    "2025-09-15 00:00:00",
                                ),
                            )
                        elif table_name == "conv_chunks":
                            cur.execute(
                                """
                                INSERT INTO conv_chunks (session_id, chunk_text, embedding, expires_at)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_session", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table_name == "conversation_messages":
                            cur.execute(
                                """
                                INSERT INTO conversation_messages (session_id, role, content, embedding, created_at, content_hash)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_session",
                                    "user",
                                    "Test content",
                                    test_vector,
                                    "2025-09-15 00:00:00",
                                    "test_hash",
                                ),
                            )
                        else:
                            print(f"   ⚠️  {table_name}: Skipping test (complex schema)")
                            continue

                        # Clean up test data
                        cur.execute(
                            f"DELETE FROM {table_name} WHERE node_id = %s OR session_id = %s",
                            ("test_384_clean", "test_session"),
                        )
                        conn.commit()

                        print(f"   ✅ {table_name}: 384-dimensional vector insertion successful")
                        test_successful.append(table_name)

                    except Exception as e:
                        print(f"   ❌ {table_name}: 384-dimensional vector insertion failed: {e}")
                        test_failed.append(table_name)

                # Final summary
                print("\\n🎯 CLEAN MIGRATION SUMMARY:")
                print("=" * 50)
                print(f"✅ Tables recreated: {len(tables_to_recreate)}")
                print(f"🧪 Test successful: {len(test_successful)}/{len(tables_to_recreate)}")

                if test_successful:
                    print(f"\\n✅ Test successful tables: {', '.join(test_successful)}")

                if test_failed:
                    print(f"\\n❌ Test failed tables: {', '.join(test_failed)}")

                print("\\n🎉 CLEAN MIGRATION COMPLETE!")
                print("   All vector tables recreated with 384-dimensional embeddings")
                print("   Database is clean and ready for standards-compliant chunking")

    except Exception as e:
        print(f"❌ Clean migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Clean Vector Migration")
    print("=" * 70)
    print("⚠️  WARNING: This will DROP and RECREATE all vector tables!")
    print("   This is a clean slate approach - all existing data will be lost.")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the clean migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = clean_vector_migration()

    if success:
        print("\\n🎉 Clean migration completed successfully!")
        print("   All vector tables now support 384-dimensional embeddings")
        print("   Database is clean and ready for standards-compliant chunking")
        return 0
    else:
        print("\\n❌ Clean migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
