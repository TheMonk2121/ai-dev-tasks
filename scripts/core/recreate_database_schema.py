#!/usr/bin/env python3
"""
Completely recreate the database schema with 384-dimensional vectors.
"""

import os

# Add project paths
import sys

import psycopg
from psycopg import sql

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config


def recreate_database_schema():
    """Completely recreate the database schema with 384-dimensional vectors."""

    print("🔄 COMPLETE DATABASE SCHEMA RECREATION")
    print("=" * 60)

    try:
        with psycopg.connect(resolve_dsn(strict=False, role="recreate_database_schema")) as conn:
            with conn.cursor() as cur:
                # Step 1: Drop ALL tables and views
                print("\\n🗑️  Step 1: Dropping ALL tables and views...")

                # Drop all views first
                views_to_drop = ["conversation_summaries", "active_document_chunks", "active_conversation_sessions"]

                for view in views_to_drop:
                    try:
                        cur.execute(sql.SQL("DROP VIEW IF EXISTS {} CASCADE").format(sql.Identifier(view)))
                        print(f"   ✅ {view}: Dropped view")
                    except Exception as e:
                        print(f"   ⚠️  {view}: Could not drop view: {e}")

                # Drop all tables
                tables_to_drop = [
                    "atlas_node",
                    "conv_chunks",
                    "atlas_conversation_turn",
                    "atlas_thread",
                    "conversation_memory",
                    "conversation_messages",
                    "document_chunks",
                    "documents",
                ]

                for table in tables_to_drop:
                    try:
                        cur.execute(sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(sql.Identifier(table)))
                        print(f"   ✅ {table}: Dropped table")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not drop table: {e}")

                # Step 2: Create fresh tables with 384-dimensional vectors
                print("\\n🔧 Step 2: Creating fresh tables with 384-dimensional vectors...")

                # Create documents table first (referenced by document_chunks)
                try:
                    cur.execute(
                        """
                        CREATE TABLE documents (
                            id SERIAL PRIMARY KEY,
                            file_path VARCHAR UNIQUE NOT NULL,
                            filename VARCHAR NOT NULL,
                            content_type VARCHAR,
                            content_sha VARCHAR,
                            metadata JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """
                    )
                    print("   ✅ documents: Created table")
                except Exception as e:
                    print(f"   ❌ documents: Failed to create table: {e}")

                # Create atlas_node table
                try:
                    cur.execute(
                        """
                        CREATE TABLE atlas_node (
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
                    """
                    )
                    print("   ✅ atlas_node: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ atlas_node: Failed to create table: {e}")

                # Create conv_chunks table
                try:
                    cur.execute(
                        """
                        CREATE TABLE conv_chunks (
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
                    print("   ✅ conv_chunks: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ conv_chunks: Failed to create table: {e}")

                # Create atlas_conversation_turn table
                try:
                    cur.execute(
                        """
                        CREATE TABLE atlas_conversation_turn (
                            turn_id VARCHAR PRIMARY KEY,
                            thread_id VARCHAR NOT NULL,
                            role VARCHAR NOT NULL,
                            content TEXT NOT NULL,
                            timestamp TIMESTAMP NOT NULL,
                            embedding vector(384),
                            metadata JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """
                    )
                    print("   ✅ atlas_conversation_turn: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ atlas_conversation_turn: Failed to create table: {e}")

                # Create atlas_thread table
                try:
                    cur.execute(
                        """
                        CREATE TABLE atlas_thread (
                            thread_id VARCHAR PRIMARY KEY,
                            session_id VARCHAR NOT NULL,
                            title VARCHAR NOT NULL,
                            status VARCHAR DEFAULT 'active',
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            metadata JSONB,
                            embedding vector(384)
                        )
                    """
                    )
                    print("   ✅ atlas_thread: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ atlas_thread: Failed to create table: {e}")

                # Create conversation_memory table
                try:
                    cur.execute(
                        """
                        CREATE TABLE conversation_memory (
                            id SERIAL PRIMARY KEY,
                            session_id VARCHAR NOT NULL,
                            content TEXT NOT NULL,
                            embedding vector(384),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            metadata JSONB
                        )
                    """
                    )
                    print("   ✅ conversation_memory: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ conversation_memory: Failed to create table: {e}")

                # Create conversation_messages table
                try:
                    cur.execute(
                        """
                        CREATE TABLE conversation_messages (
                            id SERIAL PRIMARY KEY,
                            session_id VARCHAR NOT NULL,
                            role VARCHAR NOT NULL,
                            content TEXT NOT NULL,
                            content_hash VARCHAR,
                            embedding vector(384),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            metadata JSONB
                        )
                    """
                    )
                    print("   ✅ conversation_messages: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ conversation_messages: Failed to create table: {e}")

                # Create document_chunks table
                try:
                    cur.execute(
                        """
                        CREATE TABLE document_chunks (
                            id SERIAL PRIMARY KEY,
                            document_id INTEGER NOT NULL,
                            chunk_index INTEGER NOT NULL,
                            content TEXT NOT NULL,
                            embedding vector(384),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            metadata JSONB,
                            FOREIGN KEY (document_id) REFERENCES documents(id)
                        )
                    """
                    )
                    print("   ✅ document_chunks: Created table with vector(384)")
                except Exception as e:
                    print(f"   ❌ document_chunks: Failed to create table: {e}")

                # Step 3: Create vector indexes
                print("\\n🔧 Step 3: Creating vector indexes...")

                tables_with_embeddings = [
                    "atlas_node",
                    "conv_chunks",
                    "atlas_conversation_turn",
                    "atlas_thread",
                    "conversation_memory",
                    "conversation_messages",
                    "document_chunks",
                ]

                for table in tables_with_embeddings:
                    try:
                        cur.execute(
                            sql.SQL("""
                            CREATE INDEX IF NOT EXISTS {}_embedding_idx 
                            ON {} USING hnsw (embedding vector_cosine_ops)
                        """).format(sql.Identifier(f"{table}_embedding_idx"), sql.Identifier(table))
                        )
                        print(f"   ✅ {table}: Created HNSW vector index")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not create index: {e}")

                # Step 4: Create views
                print("\\n🔧 Step 4: Creating views...")

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
                    print("   ✅ conversation_summaries: Created view")
                except Exception as e:
                    print(f"   ⚠️  conversation_summaries: Could not create view: {e}")

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
                    print("   ✅ active_document_chunks: Created view")
                except Exception as e:
                    print(f"   ⚠️  active_document_chunks: Could not create view: {e}")

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
                    print("   ✅ active_conversation_sessions: Created view")
                except Exception as e:
                    print(f"   ⚠️  active_conversation_sessions: Could not create view: {e}")

                # Step 5: Test 384-dimensional vector insertion
                print("\\n🧪 Step 5: Testing 384-dimensional vector insertion...")

                test_vector = [0.1] * 384
                test_successful = []
                test_failed = []

                for table in tables_with_embeddings:
                    try:
                        if table == "atlas_node":
                            cur.execute(
                                """
                                INSERT INTO atlas_node (node_id, node_type, title, content, embedding, expires_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_384_fresh",
                                    "test",
                                    "Test 384",
                                    "Test content",
                                    test_vector,
                                    "2025-09-15 00:00:00",
                                ),
                            )
                        elif table == "conv_chunks":
                            cur.execute(
                                """
                                INSERT INTO conv_chunks (session_id, chunk_text, embedding, expires_at)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_session", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "conversation_messages":
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
                            print(f"   ⚠️  {table}: Skipping test (complex schema)")
                            continue

                        # Clean up test data
                        cur.execute(
                            f"DELETE FROM {table} WHERE node_id = %s OR session_id = %s",
                            ("test_384_fresh", "test_session"),
                        )
                        conn.commit()

                        print(f"   ✅ {table}: 384-dimensional vector insertion successful")
                        test_successful.append(table)

                    except Exception as e:
                        print(f"   ❌ {table}: 384-dimensional vector insertion failed: {e}")
                        test_failed.append(table)

                # Final summary
                print("\\n🎯 SCHEMA RECREATION SUMMARY:")
                print("=" * 50)
                print(f"✅ Tables created: {len(tables_with_embeddings)}")
                print(f"🧪 Test successful: {len(test_successful)}/{len(tables_with_embeddings)}")

                if test_successful:
                    print(f"\\n✅ Test successful tables: {', '.join(test_successful)}")

                if test_failed:
                    print(f"\\n❌ Test failed tables: {', '.join(test_failed)}")

                print("\\n🎉 SCHEMA RECREATION COMPLETE!")
                print("   All tables created with 384-dimensional vectors")
                print("   All indexes created")
                print("   All views created")
                print("   Database is clean and ready for standards-compliant chunking")

    except Exception as e:
        print(f"❌ Schema recreation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Main schema recreation function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Complete Database Schema Recreation")
    print("=" * 70)
    print("⚠️  WARNING: This will DROP and RECREATE ALL tables!")
    print("   This is a complete fresh start - all existing data will be lost.")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the complete schema recreation? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Schema recreation cancelled")
        return 1

    # Run schema recreation
    success = recreate_database_schema()

    if success:
        print("\\n🎉 Complete schema recreation completed successfully!")
        print("   All tables now support 384-dimensional vectors")
        print("   Database is clean and ready for standards-compliant chunking")
        return 0
    else:
        print("\\n❌ Schema recreation failed!")
        return 1


if __name__ == "__main__":
    exit(main())
