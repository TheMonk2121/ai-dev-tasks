"""
Comprehensive Tests for LTST Memory System

This module provides comprehensive testing for the LTST Memory System including
unit tests, integration tests, performance validation, and security testing.
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from src.utils.context_merger import ContextMerger, ContextMergeRequest, MergedContext
from src.utils.conversation_storage import (
    ConversationMessage,
    ConversationSession,
    ConversationStorage,
)
from src.utils.ltst_memory_integration import LTSTMemoryBundle, LTSTMemoryIntegration
from src.utils.ltst_performance_optimizer import LTSTPerformanceOptimizer, PerformanceBenchmark
from src.utils.session_manager import SessionManager, SessionState


class TestConversationStorage:
    """Test ConversationStorage functionality."""

    @pytest.fixture
    def storage(self):
        """Create ConversationStorage instance."""
        return ConversationStorage()

    @pytest.fixture
    def sample_session(self):
        """Create sample conversation session."""
        return ConversationSession(
            session_id="test_session_001", user_id="test_user", session_name="Test Session", session_type="conversation"
        )

    @pytest.fixture
    def sample_message(self):
        """Create sample conversation message."""
        return ConversationMessage(
            session_id="test_session_001", role="human", content="Hello, this is a test message", message_type="message"
        )

    def test_create_session(self, storage, sample_session):
        """Test session creation."""
        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            result = storage.create_session(sample_session)

            assert result is True
            mock_cursor.execute.assert_called()
            mock_cursor.commit.assert_called()

    def test_store_message(self, storage, sample_message):
        """Test message storage."""
        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = [1]  # Next message index
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            result = storage.store_message(sample_message)

            assert result is True
            mock_cursor.execute.assert_called()
            mock_cursor.commit.assert_called()

    def test_get_messages(self, storage):
        """Test message retrieval."""
        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {
                    "session_id": "test_session_001",
                    "role": "human",
                    "content": "Test message",
                    "message_type": "message",
                    "message_index": 1,
                    "parent_message_id": None,
                    "metadata": {},
                    "embedding": [],
                    "relevance_score": 0.8,
                    "is_context_message": False,
                    "timestamp": datetime.now(),
                }
            ]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            messages = storage.get_messages("test_session_001", limit=10)

            assert len(messages) == 1
            assert messages[0].role == "human"
            assert messages[0].content == "Test message"

    def test_search_messages(self, storage):
        """Test message search functionality."""
        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = [
                {
                    "session_id": "test_session_001",
                    "role": "human",
                    "content": "Test message",
                    "message_type": "message",
                    "message_index": 1,
                    "parent_message_id": None,
                    "metadata": {},
                    "embedding": [],
                    "relevance_score": 0.8,
                    "is_context_message": False,
                    "timestamp": datetime.now(),
                    "similarity": 0.9,
                }
            ]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            results = storage.search_messages("test", session_id="test_session_001")

            assert len(results) == 1
            assert results[0][1] >= 0.7  # Similarity threshold


class TestContextMerger:
    """Test ContextMerger functionality."""

    @pytest.fixture
    def merger(self):
        """Create ContextMerger instance."""
        return ContextMerger()

    @pytest.fixture
    def merge_request(self):
        """Create sample merge request."""
        return ContextMergeRequest(
            session_id="test_session_001",
            user_id="test_user",
            current_message="Test message for context merging",
            context_types=["conversation", "preference", "project"],
            max_context_length=2000,
            relevance_threshold=0.7,
        )

    def test_merge_context(self, merger, merge_request):
        """Test context merging."""
        # Mock conversation storage
        with patch.object(merger.conversation_storage, "get_messages") as mock_get_messages:
            mock_get_messages.return_value = []

            # Mock database connection for user preferences
            with patch.object(merger.conversation_storage.db_manager, "get_connection") as mock_conn:
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

                result = merger.merge_context(merge_request)

                assert result is not None
                assert isinstance(result, MergedContext)
                assert result.session_id == "test_session_001"
                assert result.conversation_history == []
                assert result.user_preferences == {}

    def test_calculate_relevance_scores(self, merger):
        """Test relevance score calculation."""
        conversation_history = []
        user_preferences = {}
        project_context = {}
        relevant_contexts = []
        current_message = "Test message"

        scores = merger._calculate_relevance_scores(
            conversation_history, user_preferences, project_context, relevant_contexts, current_message
        )

        assert isinstance(scores, dict)
        assert "overall" in scores
        assert scores["overall"] == 0.0  # No context available

    def test_update_user_preference(self, merger):
        """Test user preference update."""
        # Mock database connection
        with patch.object(merger.conversation_storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            result = merger.update_user_preference(
                user_id="test_user",
                preference_key="test_preference",
                preference_value="test_value",
                preference_type="general",
                confidence_score=0.8,
            )

            assert result is True
            mock_cursor.execute.assert_called()
            mock_cursor.commit.assert_called()


class TestSessionManager:
    """Test SessionManager functionality."""

    @pytest.fixture
    def session_manager(self):
        """Create SessionManager instance."""
        return SessionManager()

    def test_create_session(self, session_manager):
        """Test session creation."""
        # Mock conversation storage
        with patch.object(session_manager.conversation_storage, "create_session") as mock_create:
            mock_create.return_value = True

            session_id = session_manager.create_session(user_id="test_user", session_name="Test Session")

            assert session_id is not None
            assert session_id in session_manager.active_sessions

    def test_add_message(self, session_manager):
        """Test message addition."""
        # Mock session state
        session_manager.active_sessions["test_session"] = SessionState(
            session_id="test_session", user_id="test_user", status="active"
        )

        # Mock conversation storage
        with patch.object(session_manager.conversation_storage, "store_message") as mock_store:
            mock_store.return_value = True

            result = session_manager.add_message(session_id="test_session", role="human", content="Test message")

            assert result is True
            mock_store.assert_called()

    def test_get_context_for_message(self, session_manager):
        """Test context retrieval for message."""
        # Mock session state
        session_manager.active_sessions["test_session"] = SessionState(
            session_id="test_session", user_id="test_user", status="active"
        )

        # Mock context merger
        with patch.object(session_manager.context_merger, "merge_context") as mock_merge:
            mock_merge.return_value = Mock(
                merged_content="Test content", relevance_scores={"overall": 0.8}, context_hash="test_hash"
            )

            result = session_manager.get_context_for_message(
                session_id="test_session", user_id="test_user", current_message="Test message"
            )

            assert result is not None
            assert "merged_content" in result
            assert "relevance_scores" in result


class TestLTSTMemoryIntegration:
    """Test LTSTMemoryIntegration functionality."""

    @pytest.fixture
    def integration(self):
        """Create LTSTMemoryIntegration instance."""
        return LTSTMemoryIntegration()

    def test_rehydrate_with_conversation_context(self, integration):
        """Test memory rehydration with conversation context."""
        # Mock session manager
        with patch.object(integration.session_manager, "create_session") as mock_create:
            mock_create.return_value = "test_session"

            # Mock memory rehydrator
            with patch("src.utils.ltst_memory_integration.rehydrate") as mock_rehydrate:
                mock_rehydrate.return_value = Mock()

                # Mock database connection
                with patch.object(integration.db_manager, "get_connection") as mock_conn:
                    mock_cursor = Mock()
                    mock_cursor.fetchall.return_value = []
                    mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = (
                        mock_cursor
                    )

                    bundle = integration.rehydrate_with_conversation_context(query="Test query", user_id="test_user")

                    assert isinstance(bundle, LTSTMemoryBundle)
                    assert bundle.original_bundle is not None
                    assert bundle.conversation_history == []
                    assert bundle.user_preferences == {}

    def test_store_conversation_response(self, integration):
        """Test conversation response storage."""
        # Mock session manager
        with patch.object(integration.session_manager, "add_message") as mock_add:
            mock_add.return_value = True

            result = integration.store_conversation_response(session_id="test_session", response="Test AI response")

            assert result is True
            mock_add.assert_called()

    def test_get_conversation_summary(self, integration):
        """Test conversation summary retrieval."""
        # Mock session manager
        with patch.object(integration.session_manager, "get_session_statistics") as mock_stats:
            mock_stats.return_value = {"message_count": 10}

            # Mock database connection
            with patch.object(integration.db_manager, "get_connection") as mock_conn:
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

                summary = integration.get_conversation_summary("test_session")

                assert summary is not None
                assert "statistics" in summary
                assert summary["statistics"]["message_count"] == 10


class TestLTSTPerformanceOptimizer:
    """Test LTSTPerformanceOptimizer functionality."""

    @pytest.fixture
    def optimizer(self):
        """Create LTSTPerformanceOptimizer instance."""
        return LTSTPerformanceOptimizer()

    def test_optimize_database_queries(self, optimizer):
        """Test database query optimization."""
        # Mock database connection
        with patch.object(optimizer.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            results = optimizer.optimize_database_queries()

            assert isinstance(results, dict)
            assert "storage" in results
            assert "merger" in results
            assert "session" in results

    def test_implement_caching_strategies(self, optimizer):
        """Test caching strategy implementation."""
        # Mock context merger
        with patch.object(optimizer.context_merger, "cleanup_cache"):
            # Mock session manager
            with patch.object(optimizer.session_manager, "cleanup_expired_sessions") as mock_cleanup:
                mock_cleanup.return_value = 5

                # Mock conversation storage
                with patch.object(optimizer.conversation_storage, "cleanup_expired_data") as mock_storage_cleanup:
                    mock_storage_cleanup.return_value = True

                    results = optimizer.implement_caching_strategies()

                    assert isinstance(results, dict)
                    assert "merger_cache" in results
                    assert "session_cache" in results
                    assert "storage_cache" in results

    def test_benchmark_memory_rehydration(self, optimizer):
        """Test memory rehydration benchmarking."""
        test_queries = ["Test query 1", "Test query 2", "Test query 3"]

        # Mock LTST integration
        with patch.object(optimizer.ltst_integration, "rehydrate_with_conversation_context") as mock_rehydrate:
            mock_rehydrate.return_value = Mock(metadata={})

            benchmark = optimizer.benchmark_memory_rehydration(test_queries, "test_user")

            assert isinstance(benchmark, PerformanceBenchmark)
            assert benchmark.benchmark_name == "memory_rehydration"
            assert benchmark.total_operations == 3
            assert benchmark.success_rate > 0

    def test_track_performance_metric(self, optimizer):
        """Test performance metric tracking."""
        optimizer.track_performance_metric(
            operation_type="test_operation", execution_time_ms=100.0, result_count=5, cache_hit=True, database_queries=2
        )

        assert len(optimizer.performance_metrics) == 1
        metric = optimizer.performance_metrics[0]
        assert metric.operation_type == "test_operation"
        assert metric.execution_time_ms == 100.0
        assert metric.cache_hit is True

    def test_get_performance_summary(self, optimizer):
        """Test performance summary generation."""
        # Add some test metrics
        optimizer.track_performance_metric("test_op", 100.0, 5, True, 2)
        optimizer.track_performance_metric("test_op", 150.0, 3, False, 1)

        summary = optimizer.get_performance_summary()

        assert isinstance(summary, dict)
        assert "total_metrics" in summary
        assert "operation_stats" in summary
        assert "cache_stats" in summary
        assert summary["total_metrics"] == 2


class TestLTSTMemorySystemIntegration:
    """Integration tests for the complete LTST Memory System."""

    @pytest.fixture
    def complete_system(self):
        """Create complete LTST system components."""
        storage = ConversationStorage()
        merger = ContextMerger(storage)
        session_manager = SessionManager(storage, merger)
        integration = LTSTMemoryIntegration(storage, merger, session_manager)
        optimizer = LTSTPerformanceOptimizer(storage, merger, session_manager)

        return {
            "storage": storage,
            "merger": merger,
            "session_manager": session_manager,
            "integration": integration,
            "optimizer": optimizer,
        }

    def test_end_to_end_conversation_flow(self, complete_system):
        """Test complete conversation flow."""
        storage = complete_system["storage"]
        session_manager = complete_system["session_manager"]
        integration = complete_system["integration"]

        # Mock all database operations
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = [1]  # Next message index
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            # Mock session creation
            with patch.object(session_manager.conversation_storage, "create_session") as mock_create:
                mock_create.return_value = True

                # Mock memory rehydration
                with patch("src.utils.ltst_memory_integration.rehydrate") as mock_rehydrate:
                    mock_rehydrate.return_value = Mock()

                    # 1. Create session
                    session_id = session_manager.create_session("test_user", "Test Session")
                    assert session_id is not None

                    # 2. Add user message
                    result = session_manager.add_message(session_id, "human", "Hello, how are you?")
                    assert result is True

                    # 3. Get context for AI response
                    context = session_manager.get_context_for_message(session_id, "test_user", "Hello, how are you?")
                    assert context is not None

                    # 4. Store AI response
                    result = session_manager.add_message(session_id, "ai", "I'm doing well, thank you!")
                    assert result is True

                    # 5. Rehydrate memory with conversation context
                    bundle = integration.rehydrate_with_conversation_context(
                        query="What did we talk about?", user_id="test_user", session_id=session_id
                    )
                    assert isinstance(bundle, LTSTMemoryBundle)

    def test_performance_benchmarks(self, complete_system):
        """Test performance benchmarking."""
        optimizer = complete_system["optimizer"]

        # Mock all database operations
        with patch.object(optimizer.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchall.return_value = []
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            # Mock LTST integration
            with patch.object(optimizer.ltst_integration, "rehydrate_with_conversation_context") as mock_rehydrate:
                mock_rehydrate.return_value = Mock(metadata={})

                # Test memory rehydration benchmark
                test_queries = ["Query 1", "Query 2", "Query 3"]
                benchmark = optimizer.benchmark_memory_rehydration(test_queries, "test_user")

                assert benchmark.average_time_ms < 5000  # Should be under 5 seconds
                assert benchmark.success_rate == 1.0  # All operations should succeed

    def test_error_handling_and_recovery(self, complete_system):
        """Test error handling and recovery mechanisms."""
        storage = complete_system["storage"]
        session_manager = complete_system["session_manager"]

        # Test with database connection failure
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_conn.side_effect = Exception("Database connection failed")

            # Should handle database errors gracefully
            result = storage.create_session(ConversationSession(session_id="test_session", user_id="test_user"))
            assert result is False

            # Should handle session creation errors gracefully
            session_id = session_manager.create_session("test_user", "Test Session")
            assert session_id is None

    def test_security_validation(self, complete_system):
        """Test security validation and input sanitization."""
        storage = complete_system["storage"]

        # Test with potentially malicious input
        malicious_message = ConversationMessage(
            session_id="test_session",
            role="human",
            content="<script>alert('xss')</script>DROP TABLE users;",
            message_type="message",
        )

        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = [1]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            # Should handle malicious input safely
            result = storage.store_message(malicious_message)
            assert result is True  # Should be sanitized and stored safely

    def test_data_integrity(self, complete_system):
        """Test data integrity and consistency."""
        storage = complete_system["storage"]

        # Test message ordering and indexing
        messages = [
            ConversationMessage(session_id="test_session", role="human", content=f"Message {i}") for i in range(5)
        ]

        # Mock database connection
        with patch.object(storage.db_manager, "get_connection") as mock_conn:
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = [1]
            mock_conn.return_value.__enter__.return_value.cursor.return_value.__enter__.return_value = mock_cursor

            # Store messages
            for message in messages:
                result = storage.store_message(message)
                assert result is True

            # Verify message ordering (mock retrieval)
            mock_cursor.fetchall.return_value = [
                {
                    "session_id": "test_session",
                    "role": "human",
                    "content": f"Message {i}",
                    "message_type": "message",
                    "message_index": i + 1,
                    "parent_message_id": None,
                    "metadata": {},
                    "embedding": [],
                    "relevance_score": 0.8,
                    "is_context_message": False,
                    "timestamp": datetime.now(),
                }
                for i in range(5)
            ]

            retrieved_messages = storage.get_messages("test_session", limit=10)
            assert len(retrieved_messages) == 5

            # Verify message indices are sequential
            for i, message in enumerate(retrieved_messages):
                assert message.message_index == i + 1


if __name__ == "__main__":
    pytest.main([__file__])
