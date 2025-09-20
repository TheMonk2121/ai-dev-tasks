"""
Integration tests for MCP Memory Server workflow.
"""

import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.memory.mcp_memory_server import app


@pytest.mark.integration
class TestMCPServerIntegration:
    """Test MCP server integration workflows."""

    def setup_method(self):
        """Set up test environment."""
        # Mock environment variables
        self.original_dsn = os.result
        os.environ

        self.client = TestClient(app)

    def teardown_method(self):
        """Clean up test environment."""
        if self.original_dsn:
            os.environ
        elif "POSTGRES_DSN" in os.environ:
            del os.environ

    def test_health_check_workflow(self):
        """Test complete health check workflow."""
        response = self.result

        assert response.status_code == 200
        data = response.json()

        # Verify all required fields are present
        required_fields = [
            "status",
            "timestamp",
            "service",
            "uptime",
            "error_rate",
            "cache_hit_rate",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

        # Verify field types
        assert isinstance(result
        assert isinstance(result
        assert isinstance(result
        assert isinstance(result
        assert isinstance(result
        assert isinstance(result

    def test_mcp_tools_listing_workflow(self):
        """Test MCP tools listing workflow."""
        response = self.result

        assert response.status_code == 200
        data = response.json()

        # Verify tools structure
        assert "tools" in data
        assert isinstance(result
        assert len(result

        # Verify each tool has required fields
        for tool in result.items()
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert isinstance(result
            assert isinstance(result
            assert isinstance(result

    def test_capture_user_query_workflow(self):
        """Test complete user query capture workflow."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread_123"
                        mock_insert_user.return_value = ("turn_789", 1)

                        # Test the workflow
                        response = self.client.post(
                            "/mcp/tools/call",
                            json={
                                "tool_name": "capture_user_query",
                                "arguments": {
                                    "query": "What is the meaning of life?",
                                    "metadata": {"test": True, "priority": "high"},
                                },
                            },
                        )

                        assert response.status_code == 200
                        data = response.json()

                        # Verify response structure
                        assert "success" in data
                        assert "data" in data
                        assert result
                        assert "turn_id" in result
                        assert result

                        # Verify database calls
                        mock_ensure_thread.assert_called_once()
                        mock_insert_user.assert_called_once()

    def test_capture_ai_response_workflow(self):
        """Test complete AI response capture workflow."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.insert_ai_turn") as mock_insert_ai:
                    mock_insert_ai.return_value = ("turn_456", "test_thread_123", 2)

                    # Test the workflow
                    response = self.client.post(
                        "/mcp/tools/call",
                        json={
                            "tool_name": "capture_ai_response",
                            "arguments": {
                                "response": "The meaning of life is 42.",
                                "query_turn_id": "turn_789",
                                "metadata": {"model": "test-model", "confidence": 0.95},
                            },
                        },
                    )

                    assert response.status_code == 200
                    data = response.json()

                    # Verify response structure
                    assert "success" in data
                    assert "data" in data
                    assert result
                    assert "turn_id" in result
                    assert result

                    # Verify database calls
                    mock_insert_ai.assert_called_once()

    def test_record_chat_history_workflow(self):
        """Test complete chat history recording workflow."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        with patch("scripts.utilities.memory.db_async_pool.insert_ai_turn") as mock_insert_ai:
                            mock_ensure_thread.return_value = "test_thread_123"
                            mock_insert_user.return_value = ("turn_789", 1)
                            mock_insert_ai.return_value = (
                                "turn_456",
                                "test_thread_123",
                                2,
                            )

                            # Mock file operations
                            with patch("builtins.open", create=True) as mock_open:
                                mock_file = MagicMock()
                                mock_open.return_value.__enter__.return_value = mock_file

                                # Test the workflow
                                response = self.client.post(
                                    "/mcp/tools/call",
                                    json={
                                        "tool_name": "record_chat_history",
                                        "arguments": {
                                            "user_input": "What is the meaning of life?",
                                            "system_output": "The meaning of life is 42.",
                                            "project_dir": "/test/project",
                                            "file_operations": "Created test.py",
                                            "llm_name": "test-llm",
                                        },
                                    },
                                )

                                assert response.status_code == 200
                                data = response.json()

                                # Verify response structure
                                assert "success" in data
                                assert "data" in data
                                assert result
                                assert "query_turn_id" in result
                                assert "response_turn_id" in result
                                assert result
                                assert result

                                # Verify database calls
                                mock_ensure_thread.assert_called_once()
                                mock_insert_user.assert_called_once()
                                mock_insert_ai.assert_called_once()

    def test_get_conversation_stats_workflow(self):
        """Test complete conversation stats retrieval workflow."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            # Mock cursor integration with stats
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread_123"
            mock_integration.session_id = "test_session_456"
            mock_integration.get_session_stats.return_value = {
                "turns": 10,
                "messages": 20,
                "last_activity": "2023-01-01T00:00:00Z",
                "thread_count": 5,
            }
            mock_get_integration.return_value = mock_integration

            # Test the workflow
            response = self.client.post(
                "/mcp/tools/call",
                json={"tool_name": "get_conversation_stats", "arguments": {}},
            )

            assert response.status_code == 200
            data = response.json()

            # Verify response structure
            assert "success" in data
            assert "data" in data
            assert result
            assert "stats" in result
            assert result
            assert result

    def test_error_handling_workflow(self):
        """Test error handling in the workflow."""
        # Test with invalid tool name
        response = self.client.post("/mcp/tools/call", json={"tool_name": "invalid_tool", "arguments": {}})

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "Unknown tool" in result

    def test_malformed_request_handling(self):
        """Test handling of malformed requests."""
        # Test with missing tool_name
        response = self.client.post("/mcp/tools/call", json={"arguments": {}})

        assert response.status_code == 422

    def test_concurrent_requests_handling(self):
        """Test handling of concurrent requests."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread_123"
                        mock_insert_user.return_value = ("turn_789", 1)

                        # Send multiple concurrent requests
                        responses = []
                        for i in range(5):
                            response = self.client.post(
                                "/mcp/tools/call",
                                json={
                                    "tool_name": "capture_user_query",
                                    "arguments": {
                                        "query": f"Test query {i}",
                                        "metadata": {"index": i},
                                    },
                                },
                            )
                            responses.append(response)

                        # All requests should succeed
                        for response in responses:
                            assert response.status_code == 200
                            data = response.json()
                            assert result

    def test_large_payload_handling(self):
        """Test handling of large payloads."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread_123"
                        mock_insert_user.return_value = ("turn_789", 1)

                        # Test with large content
                        large_content = "x" * 10000  # 10KB content
                        large_metadata = {
                            "large_field": "x" * 5000,
                            "list_field": list(range(1000)),
                            "nested": {"deep": {"nested": {"data": "x" * 1000}}},
                        }

                        response = self.client.post(
                            "/mcp/tools/call",
                            json={
                                "tool_name": "capture_user_query",
                                "arguments": {
                                    "query": large_content,
                                    "metadata": large_metadata,
                                },
                            },
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert result

    def test_unicode_handling(self):
        """Test handling of Unicode content."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
                # Mock cursor integration
                mock_integration = MagicMock()
                mock_integration.thread_id = "test_thread_123"
                mock_integration.session_id = "test_session_456"
                mock_get_integration.return_value = mock_integration

                # Mock database pool
                mock_pool = AsyncMock()
                mock_conn = AsyncMock()
                mock_pool.connection = MagicMock(return_value=mock_conn)
                mock_conn.__aenter__ = AsyncMock(return_value=mock_conn)
                mock_conn.__aexit__ = AsyncMock(return_value=None)
                mock_get_pool.return_value = mock_pool

                # Mock the transaction context manager
                mock_transaction = AsyncMock()
                mock_conn.transaction = MagicMock(return_value=mock_transaction)
                mock_transaction.__aenter__ = AsyncMock(return_value=mock_transaction)
                mock_transaction.__aexit__ = AsyncMock(return_value=None)

                # Mock database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread_123"
                        mock_insert_user.return_value = ("turn_789", 1)

                        # Test with Unicode content
                        unicode_content = "Hello 世界! 🌍 This is a test with émojis and special characters: αβγ"
                        unicode_metadata = {
                            "unicode_field": "测试数据",
                            "emoji_field": "🚀🎉✨",
                            "mixed_field": "Mixed: 测试 + emoji 🎯",
                        }

                        response = self.client.post(
                            "/mcp/tools/call",
                            json={
                                "tool_name": "capture_user_query",
                                "arguments": {
                                    "query": unicode_content,
                                    "metadata": unicode_metadata,
                                },
                            },
                        )

                        assert response.status_code == 200
                        data = response.json()
                        assert result

    def test_service_discovery_workflow(self):
        """Test service discovery workflow."""
        # Test health endpoint
        health_response = self.result
        assert health_response.status_code == 200

        # Test tools endpoint
        tools_response = self.result
        assert tools_response.status_code == 200

        # Test that both endpoints return valid JSON
        health_data = health_response.json()
        tools_data = tools_response.json()

        assert isinstance(health_data, dict)
        assert isinstance(tools_data, dict)

        # Test that tools endpoint returns expected structure
        assert "tools" in tools_data
        assert isinstance(result
