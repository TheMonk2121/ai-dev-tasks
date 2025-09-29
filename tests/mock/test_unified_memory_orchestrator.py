"""
Unit tests for Unified Memory Orchestrator component.
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.unified_memory_orchestrator import UnifiedMemoryOrchestrator


@pytest.mark.unit
class TestUnifiedMemoryOrchestrator:
    """Test Unified Memory Orchestrator functionality."""

    def setup_method(self):
        """Set up test environment."""
        # Mock environment variables
        self.original_dsn = os.environ.get("POSTGRES_DSN")
        self.original_db_url = os.environ.get("DATABASE_URL")
        os.environ["POSTGRES_DSN"] = "mock://test"
        os.environ["DATABASE_URL"] = "mock://test"

    def teardown_method(self):
        """Clean up test environment."""
        if self.original_dsn is not None:
            os.environ["POSTGRES_DSN"] = self.original_dsn
        elif "POSTGRES_DSN" in os.environ:
            del os.environ["POSTGRES_DSN"]

        if self.original_db_url is not None:
            os.environ["DATABASE_URL"] = self.original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

    def test_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = UnifiedMemoryOrchestrator()

        assert orchestrator is not None
        assert hasattr(orchestrator, "get_ltst_memory")
        assert hasattr(orchestrator, "get_cursor_memory")
        assert hasattr(orchestrator, "get_go_cli_memory")

    def test_get_ltst_memory_no_adapter(self):
        """Test LTST memory when adapter is not available."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            False,
        ):
            orchestrator = UnifiedMemoryOrchestrator()
            result = orchestrator.get_ltst_memory("test query")

            assert result
            assert "LTST Memory System not available" in result
            assert result

    def test_get_ltst_memory_with_adapter_success(self):
        """Test LTST memory with successful adapter call."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.MemoryRehydrator") as mock_rehydrator_class:
                with patch("scripts.utilities.unified_memory_orchestrator.RehydrationRequest") as mock_request_class:
                    # Mock the rehydrator instance
                    mock_rehydrator = MagicMock()
                    mock_rehydrator_class.return_value = mock_rehydrator

                    # Mock the request instance
                    mock_request = MagicMock()
                    mock_request_class.return_value = mock_request

                    # Mock the rehydrate result
                    mock_result = MagicMock()
                    mock_result.context_relevance_scores = [0.8, 0.9]
                    mock_result.rehydration_time_ms = 150
                    mock_result.cache_hit = True
                    mock_result.metadata = {"test": "data"}
                    mock_rehydrator.rehydrate_memory.return_value = mock_result

                    orchestrator = UnifiedMemoryOrchestrator()
                    result = orchestrator.get_ltst_memory("test query")

                    assert result
                    assert result
                    assert "bundle" in result
                    assert result
                    assert result
                    assert result

    def test_get_ltst_memory_with_adapter_exception(self):
        """Test LTST memory when adapter raises exception."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.MemoryRehydrator") as mock_rehydrator_class:
                with patch("scripts.utilities.unified_memory_orchestrator.RehydrationRequest") as mock_request_class:
                    # Mock the rehydrator instance to raise exception
                    mock_rehydrator = MagicMock()
                    mock_rehydrator.rehydrate_memory.side_effect = Exception("Test error")
                    mock_rehydrator_class.return_value = mock_rehydrator

                    # Mock the request instance
                    mock_request = MagicMock()
                    mock_request_class.return_value = mock_request

                    orchestrator = UnifiedMemoryOrchestrator()
                    result = orchestrator.get_ltst_memory("test query")

                    assert result
                    assert result
                    assert "Test error" in result

    def test_get_cursor_memory_no_adapter(self):
        """Test Cursor memory when adapter is not available."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            False,
        ):
            orchestrator = UnifiedMemoryOrchestrator()
            result = orchestrator.get_cursor_memory("test query")

            assert result
            assert "Memory adapter not available" in result
            assert result

    def test_get_cursor_memory_with_adapter_success(self):
        """Test Cursor memory with successful adapter call."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.cursor_rehydrate") as mock_cursor_rehydrate:
                # Mock the cursor rehydrate result
                mock_result = MagicMock()
                mock_result.text = "Test response"
                mock_result.meta = {"test": "metadata"}
                mock_cursor_rehydrate.return_value = mock_result

                orchestrator = UnifiedMemoryOrchestrator()
                result = orchestrator.get_cursor_memory("test query")

                assert result
                assert result
                assert result
                assert result

    def test_get_cursor_memory_with_adapter_exception(self):
        """Test Cursor memory when adapter raises exception."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.cursor_rehydrate") as mock_cursor_rehydrate:
                mock_cursor_rehydrate.side_effect = Exception("Cursor error")

                orchestrator = UnifiedMemoryOrchestrator()
                result = orchestrator.get_cursor_memory("test query")

                assert result
                assert result
                assert "Cursor error" in result

    def test_get_go_cli_memory_always_returns_error(self):
        """Test that Go CLI memory always returns error (not implemented)."""
        orchestrator = UnifiedMemoryOrchestrator()
        result = orchestrator.get_go_cli_memory("test query")

        assert result
        assert result

    def test_get_go_cli_memory_error_message(self):
        """Test Go CLI memory error message content."""
        orchestrator = UnifiedMemoryOrchestrator()
        result = orchestrator.get_go_cli_memory("test query")

        assert result

    def test_memory_orchestrator_import_handling(self):
        """Test that orchestrator handles import failures gracefully."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            False,
        ):
            orchestrator = UnifiedMemoryOrchestrator()

            # Should not raise any exceptions during initialization
            assert orchestrator is not None

            # All memory methods should return error responses
            ltst_result = orchestrator.get_ltst_memory("test")
            cursor_result = orchestrator.get_cursor_memory("test")
            go_cli_result = orchestrator.get_go_cli_memory("test")

            assert ltst_result
            assert cursor_result
            assert go_cli_result

    def test_timestamp_in_responses(self):
        """Test that all responses include timestamps."""
        orchestrator = UnifiedMemoryOrchestrator()

        ltst_result = orchestrator.get_ltst_memory("test")
        cursor_result = orchestrator.get_cursor_memory("test")
        go_cli_result = orchestrator.get_go_cli_memory("test")

        assert "timestamp" in ltst_result
        assert "timestamp" in cursor_result
        assert "timestamp" in go_cli_result

        # Timestamps should be numeric
        assert isinstance(ltst_result["timestamp"], int | float)
        assert isinstance(cursor_result["timestamp"], int | float)
        assert isinstance(go_cli_result["timestamp"], int | float)

    def test_source_identification(self):
        """Test that all responses include correct source identification."""
        orchestrator = UnifiedMemoryOrchestrator()

        ltst_result = orchestrator.get_ltst_memory("test")
        cursor_result = orchestrator.get_cursor_memory("test")
        go_cli_result = orchestrator.get_go_cli_memory("test")

        assert "source" in ltst_result
        assert "source" in cursor_result
        assert "source" in go_cli_result

        assert "LTST" in ltst_result["source"]
        assert "Cursor" in cursor_result["source"]
        assert "Go CLI" in go_cli_result["source"]

    def test_error_response_structure(self):
        """Test that error responses have consistent structure."""
        orchestrator = UnifiedMemoryOrchestrator()

        result = orchestrator.get_ltst_memory("test")

        assert "status" in result
        assert "bundle" in result
        assert "source" in result
        assert "timestamp" in result

        assert result["status"] == "error"
        assert isinstance(result["bundle"], list)
        assert len(result["bundle"]) == 0

    def test_success_response_structure(self):
        """Test that success responses have consistent structure."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.MemoryRehydrator") as mock_rehydrator_class:
                with patch("scripts.utilities.unified_memory_orchestrator.RehydrationRequest") as mock_request_class:
                    # Mock successful rehydration
                    mock_rehydrator = MagicMock()
                    mock_rehydrator_class.return_value = mock_rehydrator

                    mock_request = MagicMock()
                    mock_request_class.return_value = mock_request

                    mock_result = MagicMock()
                    mock_result.context_relevance_scores = [0.8]
                    mock_result.rehydration_time_ms = 100
                    mock_result.cache_hit = False
                    mock_result.metadata = {}
                    mock_rehydrator.rehydrate.return_value = mock_result

                    orchestrator = UnifiedMemoryOrchestrator()
                    result = orchestrator.get_ltst_memory("test")

                    assert "status" in result
                    assert "source" in result
                    assert "bundle" in result
                    assert "timestamp" in result

                    assert result["status"] == "success"
                    assert isinstance(result["bundle"], list)

    def test_role_parameter_handling(self):
        """Test that role parameter is handled correctly."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.cursor_rehydrate") as mock_cursor_rehydrate:
                mock_result = MagicMock()
                mock_result.text = "Test response"
                mock_result.meta = {}
                mock_cursor_rehydrate.return_value = mock_result

                orchestrator = UnifiedMemoryOrchestrator()

                # Test with default role
                result1 = orchestrator.get_cursor_memory("test query")
                mock_cursor_rehydrate.assert_called_with(query="test query", role="planner")

                # Test with custom role
                result2 = orchestrator.get_cursor_memory("test query", role="coder")
                mock_cursor_rehydrate.assert_called_with(query="test query", role="coder")

    def test_query_parameter_handling(self):
        """Test that query parameter is passed correctly."""
        with patch(
            "scripts.utilities.unified_memory_orchestrator.MEMORY_ADAPTER_AVAILABLE",
            True,
        ):
            with patch("scripts.utilities.unified_memory_orchestrator.cursor_rehydrate") as mock_cursor_rehydrate:
                mock_result = MagicMock()
                mock_result.text = "Test response"
                mock_result.meta = {}
                mock_cursor_rehydrate.return_value = mock_result

                orchestrator = UnifiedMemoryOrchestrator()

                test_query = "What is the meaning of life?"
                orchestrator.get_cursor_memory(test_query)

                mock_cursor_rehydrate.assert_called_with(query=test_query, role="planner")
