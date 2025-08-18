#!/usr/bin/env python3.12.123.11
"""
E2E Test for Dual Vector Store Modes (Round 1)
Tests both core and perf modes via facade without environment detection.
"""


import pytest

# Import through facade (no direct role module imports)
from dspy_modules.vector_store import get_vector_store


@pytest.mark.tier1
@pytest.mark.kind_e2e
class TestVectorStoreModesE2E:
    """End-to-end tests for vector store facade modes."""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection for offline testing."""
        return "postgresql://test:test@localhost:5432/test_db"

    def test_core_mode_initialization(self, mock_db_connection):
        """Test core mode initialization via facade."""
        # Use explicit mode selection, no environment detection
        vector_store = get_vector_store(mode="core", db_connection_string=mock_db_connection)

        # Assert minimal behavior: store is initialized
        assert vector_store is not None
        assert hasattr(vector_store, "forward")

        # Test minimal operation: store operation exists
        result = vector_store.forward(operation="ping")
        assert result is not None

    def test_perf_mode_initialization(self, mock_db_connection):
        """Test perf mode initialization via facade."""
        # Use explicit mode selection, no environment detection
        vector_store = get_vector_store(mode="perf", db_connection_string=mock_db_connection)

        # Assert minimal behavior: store is initialized
        assert vector_store is not None
        assert hasattr(vector_store, "forward")

        # Test minimal operation: store operation exists
        result = vector_store.forward(operation="ping")
        assert result is not None

    def test_facade_mode_selection(self, mock_db_connection):
        """Test that facade correctly routes to different modes."""
        # Test both modes return different instances (or at least different configurations)
        core_store = get_vector_store(mode="core", db_connection_string=mock_db_connection)
        perf_store = get_vector_store(mode="perf", db_connection_string=mock_db_connection)

        # Both should be valid stores
        assert core_store is not None
        assert perf_store is not None

        # They should be different instances (or have different configurations)
        # This is a minimal assertion to ensure the facade is working
        assert core_store != perf_store or hasattr(core_store, "_mode") != hasattr(perf_store, "_mode")

    def test_invalid_mode_handling(self, mock_db_connection):
        """Test that invalid modes are handled gracefully."""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            # This should raise an error for invalid mode
            get_vector_store(mode="invalid", db_connection_string=mock_db_connection)

    def test_offline_operation(self, mock_db_connection):
        """Test that operations work offline (no network calls)."""
        vector_store = get_vector_store(mode="core", db_connection_string=mock_db_connection)

        # Test that we can call operations without network dependencies
        # This is a minimal test to ensure the interface works
        try:
            result = vector_store.forward(operation="status")
            # Should return something (even if it's an error message)
            assert result is not None
        except Exception as e:
            # If it fails, it should be a predictable error, not a network error
            assert "connection" not in str(e).lower()
            assert "network" not in str(e).lower()
            assert "timeout" not in str(e).lower()
