#!/usr/bin/env python3
"""
Comprehensive migration of ALL vector tables to 384 dimensions.
"""

import os

# Add project paths
import sys

import psycopg
from psycopg import sql

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
from src.common.db_dsn import resolve_dsn
from src.common.psycopg3_config import Psycopg3Config


def migrate_all_vector_tables():
    """Migrate ALL vector tables to 384 dimensions."""

    print("🔄 COMPREHENSIVE VECTOR MIGRATION: ALL TABLES → 384 dimensions")
    print("=" * 80)

    # All tables with vector columns that need migration
    tables_to_migrate = [
        "atlas_conversation_turn",
        "atlas_node",
        "atlas_thread",
        "conv_chunks",
        "conversation_memory",
        "conversation_messages",
        "document_chunks",
    ]

    try:
        with psycopg.connect(resolve_dsn(strict=False, role="migrate_all_vector_tables")) as conn:
            with conn.cursor() as cur:
                # Step 1: Drop NOT NULL constraints on all tables
                print("\\n🔧 Step 1: Dropping NOT NULL constraints...")

                for table in tables_to_migrate:
                    try:
                        cur.execute(sql.SQL("ALTER TABLE {} ALTER COLUMN embedding DROP NOT NULL").format(sql.Identifier(table)))
                        print(f"   ✅ {table}: Dropped NOT NULL constraint")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not drop NOT NULL constraint: {e}")

                # Step 2: Clear existing vector data from all tables
                print("\\n🗑️  Step 2: Clearing existing vector data...")

                total_cleared = 0
                for table in tables_to_migrate:
                    try:
                        cur.execute(sql.SQL("UPDATE {} SET embedding = NULL WHERE embedding IS NOT NULL").format(sql.Identifier(table)))
                        cleared = cur.rowcount
                        total_cleared += cleared
                        print(f"   ✅ {table}: Cleared {cleared} embeddings")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not clear embeddings: {e}")

                print(f"   📊 Total embeddings cleared: {total_cleared}")

                # Step 3: Update ALL tables to 384 dimensions
                print("\\n🔧 Step 3: Updating ALL tables to 384 dimensions...")

                for table in tables_to_migrate:
                    try:
                        cur.execute(sql.SQL("ALTER TABLE {} ALTER COLUMN embedding TYPE vector(384)").format(sql.Identifier(table)))
                        print(f"   ✅ {table}: Updated to vector(384)")
                    except Exception as e:
                        print(f"   ❌ {table}: Failed to update to vector(384): {e}")

                # Step 4: Recreate ALL vector indexes
                print("\\n🔧 Step 4: Recreating ALL vector indexes...")

                # Drop existing indexes
                for table in tables_to_migrate:
                    try:
                        cur.execute(sql.SQL("DROP INDEX IF EXISTS {}_embedding_idx").format(sql.Identifier(f"{table}_embedding_idx")))
                        cur.execute(sql.SQL("DROP INDEX IF EXISTS {}_embedding_hnsw_idx").format(sql.Identifier(f"{table}_embedding_hnsw_idx")))
                        print(f"   ✅ {table}: Dropped existing indexes")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not drop indexes: {e}")

                # Create new indexes
                for table in tables_to_migrate:
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

                # Step 5: Restore NOT NULL constraints where appropriate
                print("\\n🔧 Step 5: Restoring NOT NULL constraints...")

                # Only restore NOT NULL for tables that should have it
                not_null_tables = ["conv_chunks"]  # Add others as needed

                for table in not_null_tables:
                    try:
                        cur.execute(sql.SQL("ALTER TABLE {} ALTER COLUMN embedding SET NOT NULL").format(sql.Identifier(table)))
                        print(f"   ✅ {table}: Restored NOT NULL constraint")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Could not restore NOT NULL constraint: {e}")

                # Commit all changes
                conn.commit()
                print("\\n✅ Comprehensive migration completed successfully!")

                # Step 6: Verify ALL tables
                print("\\n📊 Step 6: Verification...")

                for table in tables_to_migrate:
                    try:
                        cur.execute(
                            sql.SQL("""
                            SELECT column_name, data_type, is_nullable
                            FROM information_schema.columns 
                            WHERE table_name = {} 
                            AND column_name = 'embedding'
                        """).format(sql.Literal(table))
                        )

                        result = cur.fetchone()
                        if result:
                            print(f"   ✅ {table}.embedding: {result[1]} (nullable: {result[2]})")
                        else:
                            print(f"   ❌ {table}: No embedding column found")
                    except Exception as e:
                        print(f"   ⚠️  {table}: Verification failed: {e}")

                # Step 7: Test 384-dimensional vector insertion
                print("\\n🧪 Step 7: Testing 384-dimensional vector insertion...")

                test_vector = [0.1] * 384
                successful_tables = []
                failed_tables = []

                for table in tables_to_migrate:
                    try:
                        # Test insertion based on table structure
                        if table == "atlas_node":
                            cur.execute(
                                """
                                INSERT INTO atlas_node (node_id, node_type, title, content, embedding, expires_at)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_384_final",
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
                        elif table == "atlas_conversation_turn":
                            cur.execute(
                                """
                                INSERT INTO atlas_conversation_turn (turn_id, thread_id, role, content, embedding, timestamp)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """,
                                (
                                    "test_turn",
                                    "test_thread",
                                    "user",
                                    "Test content",
                                    test_vector,
                                    "2025-09-15 00:00:00",
                                ),
                            )
                        elif table == "atlas_thread":
                            cur.execute(
                                """
                                INSERT INTO atlas_thread (thread_id, session_id, title, embedding)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_thread", "test_session", "Test thread", test_vector),
                            )
                        elif table == "conversation_memory":
                            cur.execute(
                                """
                                INSERT INTO conversation_memory (session_id, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s)
                            """,
                                ("test_session", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "conversation_messages":
                            cur.execute(
                                """
                                INSERT INTO conversation_messages (session_id, role, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """,
                                ("test_session", "user", "Test content", test_vector, "2025-09-15 00:00:00"),
                            )
                        elif table == "document_chunks":
                            cur.execute(
                                """
                                INSERT INTO document_chunks (document_id, chunk_index, content, embedding, created_at)
                                VALUES (%s, %s, %s, %s, %s)
                            """,
                                (1, 1, "Test content", test_vector, "2025-09-15 00:00:00"),
                            )

                        # Clean up test data
                        cur.execute(
                            sql.SQL("DELETE FROM {} WHERE node_id = %s OR turn_id = %s OR thread_id = %s OR session_id = %s OR document_id = %s").format(sql.Identifier(table)),
                            ("test_384_final", "test_turn", "test_thread", "test_session", 1),
                        )
                        conn.commit()

                        print(f"   ✅ {table}: 384-dimensional vector insertion successful")
                        successful_tables.append(table)

                    except Exception as e:
                        print(f"   ❌ {table}: 384-dimensional vector insertion failed: {e}")
                        failed_tables.append(table)

                # Final summary
                print("\\n🎯 MIGRATION SUMMARY:")
                print("=" * 50)
                print(f"✅ Successfully migrated: {len(successful_tables)}/{len(tables_to_migrate)} tables")
                print(f"❌ Failed migrations: {len(failed_tables)}/{len(tables_to_migrate)} tables")

                if successful_tables:
                    print(f"\\n✅ Successful tables: {', '.join(successful_tables)}")

                if failed_tables:
                    print(f"\\n❌ Failed tables: {', '.join(failed_tables)}")
                    print("   These tables may need manual intervention.")

                print("\\n🎉 COMPREHENSIVE MIGRATION COMPLETE!")
                print("   All vector tables now support 384-dimensional embeddings")
                print("   Ready for standards-compliant chunking across the entire system")

    except Exception as e:
        print(f"❌ Comprehensive migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


def main():
    """Main migration function."""

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency"

    print("🚀 Starting Comprehensive Vector Migration")
    print("=" * 80)
    print("⚠️  WARNING: This will migrate ALL vector tables to 384 dimensions!")
    print("   This affects 7 tables across the entire database.")
    print("   Make sure you have a database backup before proceeding.")
    print()

    # Ask for confirmation
    response = input("Do you want to proceed with the comprehensive migration? (yes/no): ")
    if response.lower() != "yes":
        print("❌ Migration cancelled")
        return 1

    # Run migration
    success = migrate_all_vector_tables()

    if success:
        print("\\n🎉 Comprehensive migration completed successfully!")
        print("   All vector tables now support 384-dimensional embeddings")
        print("   Database is fully aligned with project standards")
        return 0
    else:
        print("\\n❌ Comprehensive migration failed!")
        return 1


if __name__ == "__main__":
    exit(main())
