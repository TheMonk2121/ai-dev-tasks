"""
Test suite for LTST Memory System database schema.

This module tests the database schema, functions, triggers, and views
for the LTST Memory System implementation.
"""

import hashlib

import psycopg2
import pytest


class TestLTSTMemorySchema:
    """Test class for LTST Memory System database schema."""

    @pytest.fixture(autouse=True)
    def setup_database(self, db_connection):
        """Setup database connection for tests."""
        self.conn = db_connection
        self.cursor = self.conn.cursor()

        # Load schema
        with open("config/database/ltst_memory_schema.sql", "r") as f:
            schema_sql = f.read()

        # Execute schema creation
        self.cursor.execute(schema_sql)
        self.conn.commit()

    def test_conversation_sessions_table(self):
        """Test conversation_sessions table creation and constraints."""
        # Test table exists
        self.cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'conversation_sessions'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "conversation_sessions table should exist"

        # Test primary key constraint
        self.cursor.execute(
            """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'conversation_sessions'
            AND constraint_type = 'PRIMARY KEY'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "conversation_sessions should have primary key"

        # Test required columns
        self.cursor.execute(
            """
            SELECT column_name, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'conversation_sessions'
        """
        )
        columns = {row[0]: row[1] for row in self.cursor.fetchall()}

        assert "session_id" in columns, "session_id column should exist"
        assert columns["session_id"] == "NO", "session_id should be NOT NULL"
        assert "user_id" in columns, "user_id column should exist"
        assert columns["user_id"] == "NO", "user_id should be NOT NULL"

    def test_conversation_messages_table(self):
        """Test conversation_messages table creation and constraints."""
        # Test table exists
        self.cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'conversation_messages'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "conversation_messages table should exist"

        # Test foreign key constraint
        self.cursor.execute(
            """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'conversation_messages'
            AND constraint_type = 'FOREIGN KEY'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "conversation_messages should have foreign key"

        # Test vector column
        self.cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name = 'conversation_messages'
            AND column_name = 'embedding'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "embedding column should exist"
        assert "vector" in result[1].lower(), "embedding should be vector type"

    def test_user_preferences_table(self):
        """Test user_preferences table creation and constraints."""
        # Test table exists
        self.cursor.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_name = 'user_preferences'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "user_preferences table should exist"

        # Test unique constraint
        self.cursor.execute(
            """
            SELECT constraint_name
            FROM information_schema.table_constraints
            WHERE table_name = 'user_preferences'
            AND constraint_type = 'UNIQUE'
        """
        )
        result = self.cursor.fetchone()
        assert result is not None, "user_preferences should have unique constraint"

    def test_indexes_creation(self):
        """Test that all required indexes are created."""
        expected_indexes = [
            "idx_conversation_sessions_user_id",
            "idx_conversation_sessions_last_activity",
            "idx_conversation_sessions_relevance_score",
            "idx_conversation_messages_session_id",
            "idx_conversation_messages_embedding",
            "idx_conversation_messages_message_index",
            "idx_user_preferences_user_id",
            "idx_user_preferences_key",
            "idx_memory_retrieval_cache_session_id",
            "idx_memory_retrieval_cache_expires_at",
        ]

        for index_name in expected_indexes:
            self.cursor.execute(
                """
                SELECT indexname
                FROM pg_indexes
                WHERE indexname = %s
            """,
                (index_name,),
            )
            result = self.cursor.fetchone()
            assert result is not None, f"Index {index_name} should exist"

    def test_triggers_creation(self):
        """Test that all required triggers are created."""
        expected_triggers = [
            "update_session_length_trigger",
            "update_conversation_sessions_updated_at",
            "update_conversation_context_updated_at",
            "update_user_preferences_updated_at",
        ]

        for trigger_name in expected_triggers:
            self.cursor.execute(
                """
                SELECT trigger_name
                FROM information_schema.triggers
                WHERE trigger_name = %s
            """,
                (trigger_name,),
            )
            result = self.cursor.fetchone()
            assert result is not None, f"Trigger {trigger_name} should exist"

    def test_functions_creation(self):
        """Test that all required functions are created."""
        expected_functions = ["update_session_length", "clean_expired_cache", "clean_expired_context"]

        for function_name in expected_functions:
            self.cursor.execute(
                """
                SELECT routine_name
                FROM information_schema.routines
                WHERE routine_name = %s
            """,
                (function_name,),
            )
            result = self.cursor.fetchone()
            assert result is not None, f"Function {function_name} should exist"

    def test_views_creation(self):
        """Test that all required views are created."""
        expected_views = ["session_summary", "user_preference_summary"]

        for view_name in expected_views:
            self.cursor.execute(
                """
                SELECT table_name
                FROM information_schema.views
                WHERE table_name = %s
            """,
                (view_name,),
            )
            result = self.cursor.fetchone()
            assert result is not None, f"View {view_name} should exist"

    def test_session_length_trigger(self):
        """Test that session length is updated when messages are added."""
        # Create a test session
        session_id = "test_session_001"
        user_id = "test_user"

        self.cursor.execute(
            """
            INSERT INTO conversation_sessions (session_id, user_id, session_name)
            VALUES (%s, %s, %s)
        """,
            (session_id, user_id, "Test Session"),
        )

        # Add a message
        content = "Test message content"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        self.cursor.execute(
            """
            INSERT INTO conversation_messages
            (session_id, role, content, content_hash, message_index)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (session_id, "human", content, content_hash, 1),
        )

        # Check that session length was updated
        self.cursor.execute(
            """
            SELECT session_length FROM conversation_sessions
            WHERE session_id = %s
        """,
            (session_id,),
        )
        result = self.cursor.fetchone()
        assert result[0] == 1, "Session length should be updated to 1"

    def test_default_system_preferences(self):
        """Test that default system preferences are inserted."""
        self.cursor.execute(
            """
            SELECT preference_key, preference_value
            FROM user_preferences
            WHERE user_id = 'system'
        """
        )
        preferences = {row[0]: row[1] for row in self.cursor.fetchall()}

        expected_preferences = {
            "memory_retention_days": "30",
            "max_context_length": "10000",
            "relevance_threshold": "0.7",
            "cache_ttl_hours": "1",
        }

        for key, value in expected_preferences.items():
            assert key in preferences, f"System preference {key} should exist"
            assert preferences[key] == value, f"System preference {key} should have value {value}"

    def test_session_summary_view(self):
        """Test session_summary view functionality."""
        # Create test data
        session_id = "test_session_002"
        user_id = "test_user"

        self.cursor.execute(
            """
            INSERT INTO conversation_sessions (session_id, user_id, session_name)
            VALUES (%s, %s, %s)
        """,
            (session_id, user_id, "Test Session 2"),
        )

        # Add test messages
        for i in range(3):
            content = f"Test message {i}"
            content_hash = hashlib.sha256(content.encode()).hexdigest()

            self.cursor.execute(
                """
                INSERT INTO conversation_messages
                (session_id, role, content, content_hash, message_index, relevance_score)
                VALUES (%s, %s, %s, %s, %s, %s)
            """,
                (session_id, "human", content, content_hash, i + 1, 0.8),
            )

        # Test view query
        self.cursor.execute(
            """
            SELECT session_id, message_count, avg_message_relevance
            FROM session_summary
            WHERE session_id = %s
        """,
            (session_id,),
        )
        result = self.cursor.fetchone()

        assert result is not None, "Session should appear in summary view"
        assert result[1] == 3, "Message count should be 3"
        assert abs(result[2] - 0.8) < 0.01, "Average relevance should be approximately 0.8"

    def test_user_preference_summary_view(self):
        """Test user_preference_summary view functionality."""
        # Create test preferences
        user_id = "test_user"
        preferences = [
            ("coding_style", "functional", "coding"),
            ("communication_style", "concise", "communication"),
            ("project_focus", "performance", "project"),
        ]

        for key, value, pref_type in preferences:
            self.cursor.execute(
                """
                INSERT INTO user_preferences
                (user_id, preference_key, preference_value, preference_type, confidence_score)
                VALUES (%s, %s, %s, %s, %s)
            """,
                (user_id, key, value, pref_type, 0.9),
            )

        # Test view query
        self.cursor.execute(
            """
            SELECT preference_type, preference_count, avg_confidence
            FROM user_preference_summary
            WHERE user_id = %s
        """,
            (user_id,),
        )
        results = self.cursor.fetchall()

        assert len(results) == 3, "Should have 3 preference types"

        # Check coding preferences
        coding_prefs = [r for r in results if r[0] == "coding"]
        assert len(coding_prefs) == 1, "Should have 1 coding preference"
        assert coding_prefs[0][1] == 1, "Should have 1 coding preference count"

    def test_cleanup_functions(self):
        """Test cleanup functions for expired data."""
        # Test clean_expired_cache function
        self.cursor.execute("SELECT clean_expired_cache()")
        # Should not raise an exception

        # Test clean_expired_context function
        self.cursor.execute("SELECT clean_expired_context()")
        # Should not raise an exception

    def test_vector_operations(self):
        """Test vector operations with embeddings."""
        # Create test session and message with embedding
        session_id = "test_session_003"
        user_id = "test_user"

        self.cursor.execute(
            """
            INSERT INTO conversation_sessions (session_id, user_id, session_name)
            VALUES (%s, %s, %s)
        """,
            (session_id, user_id, "Test Session 3"),
        )

        # Create a test embedding (384-dimensional vector)
        test_embedding = [0.1] * 384

        content = "Test message with embedding"
        content_hash = hashlib.sha256(content.encode()).hexdigest()

        self.cursor.execute(
            """
            INSERT INTO conversation_messages
            (session_id, role, content, content_hash, message_index, embedding)
            VALUES (%s, %s, %s, %s, %s, %s)
        """,
            (session_id, "human", content, content_hash, 1, test_embedding),
        )

        # Test vector similarity search
        self.cursor.execute(
            """
            SELECT message_id, content,
                   1 - (embedding <=> %s) as similarity
            FROM conversation_messages
            WHERE session_id = %s
            ORDER BY embedding <=> %s
            LIMIT 1
        """,
            (test_embedding, session_id, test_embedding),
        )

        result = self.cursor.fetchone()
        assert result is not None, "Vector search should return results"
        assert result[2] > 0.99, "Similarity should be very high for identical embedding"

    def test_performance_metrics(self):
        """Test memory performance metrics table."""
        # Insert test performance metric
        session_id = "test_session_004"

        self.cursor.execute(
            """
            INSERT INTO memory_performance_metrics
            (operation_type, session_id, execution_time_ms, result_count, cache_hit)
            VALUES (%s, %s, %s, %s, %s)
        """,
            ("retrieval", session_id, 150, 5, False),
        )

        # Verify insertion
        self.cursor.execute(
            """
            SELECT operation_type, execution_time_ms, result_count, cache_hit
            FROM memory_performance_metrics
            WHERE session_id = %s
        """,
            (session_id,),
        )

        result = self.cursor.fetchone()
        assert result is not None, "Performance metric should be inserted"
        assert result[0] == "retrieval", "Operation type should match"
        assert result[1] == 150, "Execution time should match"
        assert result[2] == 5, "Result count should match"
        assert not result[3], "Cache hit should match"

    def test_session_relationships(self):
        """Test session relationships table."""
        # Create test sessions
        session1 = "test_session_005"
        session2 = "test_session_006"
        user_id = "test_user"

        for session_id in [session1, session2]:
            self.cursor.execute(
                """
                INSERT INTO conversation_sessions (session_id, user_id, session_name)
                VALUES (%s, %s, %s)
            """,
                (session_id, user_id, f"Test Session {session_id}"),
            )

        # Create relationship
        self.cursor.execute(
            """
            INSERT INTO session_relationships
            (source_session_id, target_session_id, relationship_type, similarity_score)
            VALUES (%s, %s, %s, %s)
        """,
            (session1, session2, "related", 0.85),
        )

        # Verify relationship
        self.cursor.execute(
            """
            SELECT relationship_type, similarity_score
            FROM session_relationships
            WHERE source_session_id = %s AND target_session_id = %s
        """,
            (session1, session2),
        )

        result = self.cursor.fetchone()
        assert result is not None, "Session relationship should be created"
        assert result[0] == "related", "Relationship type should match"
        assert result[1] == 0.85, "Similarity score should match"

    def test_data_integrity_constraints(self):
        """Test data integrity constraints."""
        # Test foreign key constraint
        with pytest.raises(psycopg2.IntegrityError):
            self.cursor.execute(
                """
                INSERT INTO conversation_messages
                (session_id, role, content, content_hash, message_index)
                VALUES (%s, %s, %s, %s, %s)
            """,
                ("non_existent_session", "human", "test", "hash", 1),
            )

        # Test unique constraint on user preferences
        user_id = "test_user"
        preference_key = "test_preference"

        # Insert first preference
        self.cursor.execute(
            """
            INSERT INTO user_preferences
            (user_id, preference_key, preference_value)
            VALUES (%s, %s, %s)
        """,
            (user_id, preference_key, "value1"),
        )

        # Try to insert duplicate
        with pytest.raises(psycopg2.IntegrityError):
            self.cursor.execute(
                """
                INSERT INTO user_preferences
                (user_id, preference_key, preference_value)
                VALUES (%s, %s, %s)
            """,
                (user_id, preference_key, "value2"),
            )

    def tearDown(self):
        """Clean up test data."""
        if hasattr(self, "cursor") and self.cursor:
            self.cursor.close()
        if hasattr(self, "conn") and self.conn:
            self.conn.close()


if __name__ == "__main__":
    pytest.main([__file__])
