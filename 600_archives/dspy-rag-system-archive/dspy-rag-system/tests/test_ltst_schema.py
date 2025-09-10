"""
LTST Memory System Schema Validation Tests

This module tests the database schema for the LTST Memory System,
ensuring all tables, indexes, and functions are properly created.
"""

import os
import sys
import unittest

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from utils.database_resilience import DatabaseResilienceManager


class TestLTSTSchema(unittest.TestCase):
    """Test cases for LTST Memory System database schema."""

    def setUp(self):
        """Set up test environment."""
        self.db_manager = DatabaseResilienceManager(os.getenv("DATABASE_URL", "postgresql://localhost/dspy_rag"))

    def test_conversation_sessions_table_exists(self):
        """Test that conversation_sessions table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'conversation_sessions'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "conversation_sessions table should exist")

    def test_conversation_messages_table_exists(self):
        """Test that conversation_messages table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'conversation_messages'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "conversation_messages table should exist")

    def test_conversation_context_table_exists(self):
        """Test that conversation_context table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'conversation_context'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "conversation_context table should exist")

    def test_user_preferences_table_exists(self):
        """Test that user_preferences table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'user_preferences'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "user_preferences table should exist")

    def test_session_relationships_table_exists(self):
        """Test that session_relationships table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'session_relationships'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "session_relationships table should exist")

    def test_session_summary_table_exists(self):
        """Test that session_summary table exists."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = 'session_summary'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "session_summary table should exist")

    def test_conversation_sessions_columns(self):
        """Test that conversation_sessions has all required columns."""
        expected_columns = {
            "session_id",
            "user_id",
            "session_name",
            "session_type",
            "status",
            "metadata",
            "context_summary",
            "relevance_score",
            "created_at",
            "last_activity",
        }

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'conversation_sessions'
                """
                )
                actual_columns = {row[0] for row in cursor.fetchall()}

                missing_columns = expected_columns - actual_columns
                self.assertEqual(missing_columns, set(), f"Missing columns in conversation_sessions: {missing_columns}")

    def test_conversation_messages_columns(self):
        """Test that conversation_messages has all required columns."""
        expected_columns = {
            "id",
            "session_id",
            "message_type",
            "role",
            "content",
            "content_hash",
            "context_hash",
            "timestamp",
            "message_index",
            "metadata",
            "embedding",
            "relevance_score",
            "is_context_message",
            "parent_message_id",
        }

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'conversation_messages'
                """
                )
                actual_columns = {row[0] for row in cursor.fetchall()}

                missing_columns = expected_columns - actual_columns
                self.assertEqual(missing_columns, set(), f"Missing columns in conversation_messages: {missing_columns}")

    def test_required_indexes_exist(self):
        """Test that all required indexes exist."""
        required_indexes = [
            "idx_conversation_sessions_user_id",
            "idx_conversation_sessions_last_activity",
            "idx_conversation_sessions_status",
            "idx_conversation_messages_session_id",
            "idx_conversation_messages_timestamp",
            "idx_conversation_messages_role",
            "idx_conversation_messages_content_hash",
            "idx_conversation_messages_embedding",
            "idx_conversation_context_session_id",
            "idx_conversation_context_type",
            "idx_conversation_context_expires",
            "idx_user_preferences_user_id",
            "idx_user_preferences_key",
            "idx_session_relationships_source",
            "idx_session_relationships_target",
            "idx_session_relationships_type",
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for index_name in required_indexes:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM pg_indexes
                            WHERE indexname = %s
                        );
                    """,
                        (index_name,),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"Index {index_name} should exist")

    def test_foreign_key_constraints(self):
        """Test that foreign key constraints are properly set up."""
        expected_fks = [
            ("conversation_messages", "session_id", "conversation_sessions", "session_id"),
            ("conversation_context", "session_id", "conversation_sessions", "session_id"),
            ("session_relationships", "source_session_id", "conversation_sessions", "session_id"),
            ("session_relationships", "target_session_id", "conversation_sessions", "session_id"),
            ("session_summary", "session_id", "conversation_sessions", "session_id"),
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for table, column, ref_table, ref_column in expected_fks:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.table_constraints tc
                            JOIN information_schema.key_column_usage kcu
                                ON tc.constraint_name = kcu.constraint_name
                            JOIN information_schema.constraint_column_usage ccu
                                ON ccu.constraint_name = tc.constraint_name
                            WHERE tc.constraint_type = 'FOREIGN KEY'
                            AND tc.table_name = %s
                            AND kcu.column_name = %s
                            AND ccu.table_name = %s
                            AND ccu.column_name = %s
                        );
                    """,
                        (table, column, ref_table, ref_column),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(
                        exists, f"Foreign key constraint missing: {table}.{column} -> {ref_table}.{ref_column}"
                    )

    def test_helper_functions_exist(self):
        """Test that helper functions exist."""
        required_functions = [
            "update_session_activity",
            "clean_expired_context",
            "update_session_summary",
            "trigger_update_session_activity",
            "trigger_update_session_summary",
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for func_name in required_functions:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM pg_proc p
                            JOIN pg_namespace n ON p.pronamespace = n.oid
                            WHERE n.nspname = 'public'
                            AND p.proname = %s
                        );
                    """,
                        (func_name,),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"Function {func_name} should exist")

    def test_triggers_exist(self):
        """Test that triggers exist."""
        required_triggers = ["trigger_conversation_messages_activity", "trigger_conversation_messages_summary"]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for trigger_name in required_triggers:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM pg_trigger t
                            JOIN pg_class c ON t.tgrelid = c.oid
                            WHERE t.tgname = %s
                        );
                    """,
                        (trigger_name,),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"Trigger {trigger_name} should exist")

    def test_pgvector_extension_enabled(self):
        """Test that pgvector extension is enabled."""
        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM pg_extension
                        WHERE extname = 'vector'
                    );
                """
                )
                exists = cursor.fetchone()[0]
                self.assertTrue(exists, "pgvector extension should be enabled")

    def test_vector_columns_exist(self):
        """Test that vector columns exist in relevant tables."""
        vector_columns = [("conversation_messages", "embedding"), ("conversation_memory", "embedding")]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for table, column in vector_columns:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = %s
                            AND column_name = %s
                            AND data_type = 'USER-DEFINED'
                        );
                    """,
                        (table, column),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"Vector column {table}.{column} should exist")

    def test_jsonb_columns_exist(self):
        """Test that JSONB columns exist for metadata storage."""
        jsonb_columns = [
            ("conversation_sessions", "metadata"),
            ("conversation_messages", "metadata"),
            ("conversation_context", "metadata"),
            ("user_preferences", "metadata"),
            ("session_relationships", "metadata"),
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for table, column in jsonb_columns:
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.columns
                            WHERE table_name = %s
                            AND column_name = %s
                            AND data_type = 'jsonb'
                        );
                    """,
                        (table, column),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"JSONB column {table}.{column} should exist")

    def test_unique_constraints(self):
        """Test that unique constraints are properly set up."""
        unique_constraints = [
            ("conversation_sessions", "session_id"),
            ("conversation_messages", ["session_id", "message_index"]),
            ("conversation_context", ["session_id", "context_type", "context_key"]),
            ("user_preferences", ["user_id", "preference_key"]),
            ("session_relationships", ["source_session_id", "target_session_id", "relationship_type"]),
            ("session_summary", "session_id"),
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for table, columns in unique_constraints:
                    if isinstance(columns, str):
                        columns = [columns]

                    column_list = ", ".join(columns)
                    cursor.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.table_constraints tc
                            JOIN information_schema.key_column_usage kcu
                                ON tc.constraint_name = kcu.constraint_name
                            WHERE tc.constraint_type = 'UNIQUE'
                            AND tc.table_name = %s
                            AND kcu.column_name = ANY(%s)
                        );
                    """,
                        (table, columns),
                    )
                    exists = cursor.fetchone()[0]
                    self.assertTrue(exists, f"Unique constraint missing: {table}.{column_list}")

    def test_default_values(self):
        """Test that default values are properly set."""
        default_values = [
            ("conversation_sessions", "session_type", "'conversation'"),
            ("conversation_sessions", "status", "'active'"),
            ("conversation_messages", "message_type", "'message'"),
            ("conversation_messages", "is_context_message", "false"),
            ("conversation_sessions", "relevance_score", "0.0"),
            ("conversation_messages", "relevance_score", "0.0"),
            ("conversation_context", "relevance_score", "0.0"),
        ]

        with self.db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                for table, column, expected_default in default_values:
                    cursor.execute(
                        """
                        SELECT column_default
                        FROM information_schema.columns
                        WHERE table_name = %s
                        AND column_name = %s
                    """,
                        (table, column),
                    )
                    result = cursor.fetchone()
                    if result and result[0]:
                        actual_default = result[0]
                        self.assertIn(
                            expected_default,
                            actual_default,
                            f"Default value for {table}.{column} should be {expected_default}",
                        )

    def tearDown(self):
        """Clean up test environment."""
        if hasattr(self, "db_manager"):
            self.db_manager.shutdown()


if __name__ == "__main__":
    unittest.main()
