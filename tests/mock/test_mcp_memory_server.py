"""
Unit tests for MCP Memory Server components.
"""

import sys
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.memory.mcp_memory_server import (
    HealthResponse,
    MemoryQuery,
    MemoryResponse,
    app,
    capture_ai_response,
    capture_user_query,
    get_conversation_stats,
    record_chat_history,
)


@pytest.mark.unit
class TestMCPServerModels:
    """Test MCP server data models."""

    def test_memory_query_validation(self) -> None:
        """Test MemoryQuery model validation."""
        # Valid query
        query = MemoryQuery(
            query="test query",
            role="planner",
            max_tokens=1000,
            systems=["ltst", "cursor"],
        )
        assert query.query == "test query"
        assert query.role == "planner"
        assert query.max_tokens == 1000
        assert query.systems == ["ltst", "cursor"]

    def test_memory_query_invalid_role(self) -> None:
        """Test MemoryQuery with invalid role."""
        with pytest.raises(ValueError, match="Role must be one of"):
            _ = MemoryQuery(query="test", role="invalid_role")

    def test_memory_query_invalid_system(self) -> None:
        """Test MemoryQuery with invalid system."""
        with pytest.raises(ValueError, match="Invalid system"):
            _ = MemoryQuery(query="test", systems=["invalid_system"])

    def test_memory_query_empty_query(self) -> None:
        """Test MemoryQuery with empty query."""
        with pytest.raises(Exception):  # Pydantic validation error
            _ = MemoryQuery(query="")

    def test_memory_response_creation(self) -> None:
        """Test MemoryResponse model creation."""
        response = MemoryResponse(success=True, data={"test": "data"}, error=None)
        assert response.success is True
        assert response.data == {"test": "data"}
        assert response.error is None

    def test_health_response_creation(self) -> None:
        """Test HealthResponse model creation."""
        response = HealthResponse(
            status="healthy",
            timestamp=1234567890.0,
            service="test-service",
            uptime="1 day, 2:30:45",
            error_rate=0.1,
            cache_hit_rate=0.8,
        )
        assert response.status == "healthy"
        assert response.timestamp == 1234567890.0
        assert response.service == "test-service"


@pytest.mark.unit
class TestMCPServerEndpoints:
    """Test MCP server HTTP endpoints."""

    def __init__(self) -> None:
        """Initialize test class."""
        self.client: TestClient[Any] = TestClient(app)

    def setup_method(self) -> None:
        """Set up test client."""
        self.client = TestClient(app)

    def test_health_endpoint(self) -> None:
        """Test health check endpoint."""
        response = self.client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
        assert "uptime" in data
        assert "error_rate" in data
        assert "cache_hit_rate" in data

    def test_mcp_tools_endpoint(self) -> None:
        """Test MCP tools listing endpoint."""
        response = self.client.get("/mcp/tools")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
        assert len(data["tools"]) > 0

    def test_mcp_tool_call_invalid_tool(self) -> None:
        """Test MCP tool call with invalid tool name."""
        response = self.client.post("/mcp/tools/call", json={"tool_name": "invalid_tool", "arguments": {}})
        # The server returns 200 but with an error in the response
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

    def test_mcp_tool_call_capture_user_query(self) -> None:
        """Test capture_user_query tool call."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread"
            mock_integration.session_id = "test_session"
            mock_get_integration.return_value = mock_integration

            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
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

                # Mock the database functions
                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread"
                        mock_insert_user.return_value = ("turn_123", 1)

                        response = self.client.post(
                            "/mcp/tools/call",
                            json={
                                "tool_name": "capture_user_query",
                                "arguments": {
                                    "query": "test query",
                                    "metadata": {"test": True},
                                },
                            },
                        )
                        assert response.status_code == 200
                        data = response.json()
                        assert data["success"] is True
                        assert "turn_id" in data["data"]


@pytest.mark.unit
class TestMCPServerFunctions:
    """Test MCP server core functions."""

    @pytest.mark.asyncio
    async def test_capture_user_query_success(self) -> None:
        """Test successful user query capture."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread"
            mock_integration.session_id = "test_session"
            mock_get_integration.return_value = mock_integration

            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
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

                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        mock_ensure_thread.return_value = "test_thread"
                        mock_insert_user.return_value = ("turn_123", 1)

                        result = await capture_user_query({"query": "test query", "metadata": {"test": True}})

                        assert isinstance(result, MemoryResponse)
                        assert result.success is True
                        assert "turn_id" in result.data

    @pytest.mark.asyncio
    async def test_capture_user_query_no_integration(self) -> None:
        """Test user query capture when integration is not available."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_get_integration.return_value = None

            result = await capture_user_query({"query": "test query", "metadata": {"test": True}})

            assert isinstance(result, MemoryResponse)
            assert result.success is False
            assert result.error is not None
            assert "Cursor integration not available" in result.error

    @pytest.mark.asyncio
    async def test_capture_ai_response_success(self) -> None:
        """Test successful AI response capture."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread"
            mock_integration.session_id = "test_session"
            mock_get_integration.return_value = mock_integration

            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
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

                with patch("scripts.utilities.memory.db_async_pool.insert_ai_turn") as mock_insert_ai:
                    mock_insert_ai.return_value = ("turn_456", "test_thread", 2)

                    result = await capture_ai_response(
                        {
                            "response": "test response",
                            "query_turn_id": "turn_123",
                            "metadata": {"test": True},
                        }
                    )

                    assert isinstance(result, MemoryResponse)
                    assert result.success is True
                    assert "turn_id" in result.data

    @pytest.mark.asyncio
    async def test_get_conversation_stats_success(self) -> None:
        """Test successful conversation stats retrieval."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread"
            mock_integration.session_id = "test_session"
            mock_integration.get_session_stats.return_value = {
                "turns": 5,
                "messages": 10,
            }
            mock_get_integration.return_value = mock_integration

            result = await get_conversation_stats({})

            assert isinstance(result, MemoryResponse)
            assert result.success is True
            assert "stats" in result.data
            assert result.data["stats"] is not None

    @pytest.mark.asyncio
    async def test_record_chat_history_success(self) -> None:
        """Test successful chat history recording."""
        with patch("scripts.utilities.memory.mcp_memory_server.get_cursor_integration") as mock_get_integration:
            mock_integration = MagicMock()
            mock_integration.thread_id = "test_thread"
            mock_integration.session_id = "test_session"
            mock_get_integration.return_value = mock_integration

            with patch("scripts.utilities.memory.db_async_pool.get_pool") as mock_get_pool:
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

                with patch("scripts.utilities.memory.db_async_pool.ensure_thread_exists") as mock_ensure_thread:
                    with patch("scripts.utilities.memory.db_async_pool.insert_user_turn") as mock_insert_user:
                        with patch("scripts.utilities.memory.db_async_pool.insert_ai_turn") as mock_insert_ai:
                            mock_ensure_thread.return_value = "test_thread"
                            mock_insert_user.return_value = ("turn_123", 1)
                            mock_insert_ai.return_value = ("turn_456", "test_thread", 2)

                            with patch("builtins.open", create=True) as mock_open:
                                mock_file = MagicMock()
                                mock_open.return_value.__enter__.return_value = mock_file

                                result = await record_chat_history(
                                    {
                                        "user_input": "test input",
                                        "system_output": "test output",
                                        "project_dir": "/test/project",
                                        "file_operations": "test operations",
                                        "llm_name": "test-llm",
                                    }
                                )

                                assert isinstance(result, MemoryResponse)
                                assert result.success is True
                                assert "query_turn_id" in result.data
                                assert "response_turn_id" in result.data
