"""
Unit tests for Cursor Working Integration component.
"""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.utilities.cursor_working_integration import CursorWorkingIntegration


@pytest.mark.unit
class TestCursorWorkingIntegration:
    """Test Cursor Working Integration functionality."""
    
    original_dsn: str | None = None
    original_db_url: str | None = None
    original_allow_remote: str | None = None

    def setup_method(self):
        """Set up test environment."""
        # Mock the database DSN to avoid real database connections
        self.original_dsn = os.environ.get("POSTGRES_DSN")
        self.original_db_url = os.environ.get("DATABASE_URL")
        self.original_allow_remote = os.environ.get("ALLOW_REMOTE_DSN")
        os.environ["POSTGRES_DSN"] = "mock://test"
        os.environ["DATABASE_URL"] = "mock://test"
        os.environ["ALLOW_REMOTE_DSN"] = "1"

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

        if self.original_allow_remote is not None:
            os.environ["ALLOW_REMOTE_DSN"] = self.original_allow_remote
        elif "ALLOW_REMOTE_DSN" in os.environ:
            del os.environ["ALLOW_REMOTE_DSN"]

    def test_initialization_mock_mode(self):
        """Test initialization in mock mode."""
        integration = CursorWorkingIntegration()

        # The DSN gets canonicalized by resolve_dsn(), so check that it starts with mock://test
        assert integration.dsn.startswith("mock://test")
        assert integration.is_mock is True
        assert integration.session_id.startswith("cursor_session_")
        assert integration.thread_id.startswith("thread_")
        assert integration.message_index == 0
        assert integration.embedding_dim == 384

    def test_initialization_with_custom_dsn(self):
        """Test initialization with custom DSN."""
        integration = CursorWorkingIntegration(dsn="mock://custom")

        assert integration.dsn == "mock://custom"
        assert integration.is_mock is True

    def test_initialization_with_resolve_dsn(self):
        """Test initialization using resolve_dsn."""
        # This test should use the environment variable set in setup_method
        integration = CursorWorkingIntegration()

        assert integration.dsn.startswith("mock://test")
        assert integration.is_mock is True

    def test_session_id_format(self):
        """Test that session ID follows expected format."""
        integration = CursorWorkingIntegration()

        assert integration.session_id.startswith("cursor_session_")
        # Should be followed by a timestamp
        timestamp_part = integration.session_id.replace("cursor_session_", "")
        assert timestamp_part.isdigit()
        assert len(timestamp_part) >= 10  # Unix timestamp length

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_thread_id_format(self, _mock_resolve_dsn: Any):
        """Test that thread ID follows expected format."""
        integration = CursorWorkingIntegration()

        assert integration.thread_id.startswith("thread_")
        # Should be followed by 8 hex characters
        hex_part = integration.thread_id.replace("thread_", "")
        assert len(hex_part) == 8
        assert all(c in "0123456789abcdef" for c in hex_part)

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_embedder_initialization(self, _mock_resolve_dsn: Any):
        """Test that the sentence transformer is properly initialized."""
        integration = CursorWorkingIntegration()

        assert integration.embedder is not None
        assert hasattr(integration.embedder, "encode")
        assert callable(integration.embedder.encode)

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_message_index_initialization(self, _mock_resolve_dsn: Any):
        """Test that message index starts at 0."""
        integration = CursorWorkingIntegration()

        assert integration.message_index == 0

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_embedding_dimension(self, _mock_resolve_dsn: Any):
        """Test that embedding dimension is correct for the model."""
        integration = CursorWorkingIntegration()

        assert integration.embedding_dim == 384  # all-MiniLM-L6-v2 dimension

    @patch("scripts.utilities.cursor_working_integration.psycopg.connect")
    def test_database_initialization_real_mode(self, mock_connect: Any):
        """Test database initialization in real mode."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        integration = CursorWorkingIntegration(dsn="postgresql://test:test@localhost/test")

        # Should not raise any exceptions
        assert integration.dsn == "postgresql://test:test@localhost/test"
        assert integration.is_mock is False

    def test_mock_mode_database_initialization(self):
        """Test database initialization in mock mode."""
        integration = CursorWorkingIntegration()

        # In mock mode, should not attempt real database operations
        assert integration.is_mock is True
        # No exceptions should be raised

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_multiple_instances_unique_ids(self, _mock_resolve_dsn: Any):
        """Test that multiple instances have unique session and thread IDs."""
        integration1 = CursorWorkingIntegration()
        integration2 = CursorWorkingIntegration()

        assert integration1.session_id != integration2.session_id
        assert integration1.thread_id != integration2.thread_id

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_thread_id_uniqueness(self, _mock_resolve_dsn: Any):
        """Test that thread IDs are unique across multiple instances."""
        integrations = [CursorWorkingIntegration() for _ in range(10)]
        thread_ids = [integration.thread_id for integration in integrations]

        # All thread IDs should be unique
        assert len(set(thread_ids)) == len(thread_ids)

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_session_id_uniqueness(self, _mock_resolve_dsn: Any):
        """Test that session IDs are unique across multiple instances."""
        integrations = [CursorWorkingIntegration() for _ in range(10)]
        session_ids = [integration.session_id for integration in integrations]

        # All session IDs should be unique
        assert len(set(session_ids)) == len(session_ids)

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_embedder_consistency(self, _mock_resolve_dsn: Any):
        """Test that the same embedder model is used across instances."""
        integration1 = CursorWorkingIntegration()
        integration2 = CursorWorkingIntegration()

        # Both should use the same model
        assert isinstance(integration1.embedder, type(integration2.embedder))
        assert integration1.embedding_dim == integration2.embedding_dim

    def test_embedding_encoding(self):
        """Test that the embedder can encode text."""
        integration = CursorWorkingIntegration()

        # Test encoding a simple text
        test_text = "This is a test sentence."
        embedding = integration.embedder.encode(test_text)

        assert embedding is not None
        assert len(embedding) == integration.embedding_dim
        # The embedding is a numpy array with float32 elements
        import numpy as np

        assert all(isinstance(x, float | int | np.floating | np.integer) for x in embedding)

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_embedding_consistency(self, _mock_resolve_dsn: Any):
        """Test that the same text produces the same embedding."""
        integration = CursorWorkingIntegration()

        test_text = "Consistent test sentence."
        embedding1 = integration.embedder.encode(test_text)
        embedding2 = integration.embedder.encode(test_text)

        # Embeddings should be identical
        assert (embedding1 == embedding2).all()

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_embedding_different_texts(self, _mock_resolve_dsn: Any):
        """Test that different texts produce different embeddings."""
        integration = CursorWorkingIntegration()

        text1 = "First test sentence."
        text2 = "Second test sentence."

        embedding1 = integration.embedder.encode(text1)
        embedding2 = integration.embedder.encode(text2)

        # Embeddings should be different
        assert not (embedding1 == embedding2).all()

    def test_environment_variable_handling(self):
        """Test handling of environment variables."""
        # Test with POSTGRES_DSN set to a specific mock DSN
        os.environ["POSTGRES_DSN"] = "mock://env_test"
        os.environ["DATABASE_URL"] = "mock://env_test"

        integration = CursorWorkingIntegration()

        assert integration.dsn.startswith("mock://env_test")
        assert integration.is_mock is True

    @patch("scripts.utilities.cursor_working_integration.resolve_dsn")
    def test_mock_dsn_detection(self, _mock_resolve_dsn: Any):
        """Test that mock DSNs are properly detected."""
        test_cases = [
            "mock://test",
            "mock://",
            "mock://anything",
        ]

        for dsn in test_cases:
            integration = CursorWorkingIntegration(dsn=dsn)
            assert integration.is_mock is True, f"DSN {dsn} should be detected as mock"

    @patch("scripts.utilities.cursor_working_integration.psycopg.connect")
    def test_real_dsn_detection(self, mock_connect: Any):
        """Test that real DSNs are properly detected."""
        # Mock the database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn

        test_cases = [
            "postgresql://user:pass@localhost/db",
            "postgres://user:pass@localhost/db",
            "postgresql://localhost/db",
        ]

        for dsn in test_cases:
            integration = CursorWorkingIntegration(dsn=dsn)
            assert integration.dsn == dsn
            assert integration.is_mock is False, f"DSN {dsn} should be detected as real"
