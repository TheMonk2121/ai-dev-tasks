from __future__ import annotations
import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from scripts.session_registry import SessionRegistry
        from scripts.session_context_integration import SessionContextIntegrator
        from scripts.session_context_integration import integrate_with_memory_rehydrator
import sys
#!/usr/bin/env python3
"""
Test suite for Session Registry System.

Tests the comprehensive session registry implementation including:
- Session registration and management
- Context tagging and metadata
- Integration with Scribe system
- Memory rehydration integration
- Error handling and validation
"""

# Import the session registry system

class TestSessionRegistry:
    """Test suite for SessionRegistry class."""

    @pytest.fixture
    def temp_registry_path(self):
        """Create a temporary registry file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(
                '{"sessions": {}, "last_updated": "2025-08-21T00:00:00Z", "total_sessions": 0, "active_sessions": 0}'
            )
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def registry(self, temp_registry_path):
        """Create a SessionRegistry instance for testing."""
        return SessionRegistry(registry_path=temp_registry_path)

    @pytest.fixture
    def sample_session_data(self):
        """Sample session data for testing."""
        return {
            "backlog_id": "B-999",
            "pid": 12345,
            "worklog_path": "artifacts/worklogs/B-999.md",
            "session_type": "implementation",
            "priority": "high",
            "tags": ["role-validation", "context-preservation", "dspy-integration"],
        }

    def test_registry_initialization(self, registry):
        """Test SessionRegistry initialization."""
        assert registry is not None
        assert isinstance(registry.sessions, dict)
        assert len(registry.sessions) == 0

    def test_register_session(self, registry, sample_session_data):
        """Test session registration."""
        # Register a new session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
            session_type=sample_session_data["session_type"],
            priority=sample_session_data["priority"],
            tags=sample_session_data["tags"],
        )

        # Verify session was registered
        assert sample_session_data["backlog_id"] in registry.sessions
        session = registry.sessions[sample_session_data["backlog_id"]]

        assert session.backlog_id == sample_session_data["backlog_id"]
        assert session.pid == sample_session_data["pid"]
        assert session.worklog_path == sample_session_data["worklog_path"]
        assert session.status == "active"
        assert session.context.session_type == sample_session_data["session_type"]
        assert session.context.priority == sample_session_data["priority"]
        assert set(sample_session_data["tags"]).issubset(session.context.tags)

    def test_update_session_status(self, registry, sample_session_data):
        """Test session status updates."""
        # Register a session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
        )

        # Update status to completed
        registry.update_session_status(sample_session_data["backlog_id"], "completed")

        session = registry.sessions[sample_session_data["backlog_id"]]
        assert session.status == "completed"
        assert session.last_activity is not None

    def test_add_context_tags(self, registry, sample_session_data):
        """Test adding context tags to a session."""
        # Register a session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
        )

        # Add new tags
        new_tags = ["new-tag", "another-tag"]
        registry.add_context_tags(sample_session_data["backlog_id"], new_tags)

        session = registry.sessions[sample_session_data["backlog_id"]]
        assert all(tag in session.context.tags for tag in new_tags)

    def test_remove_context_tags(self, registry, sample_session_data):
        """Test removing context tags from a session."""
        # Register a session with tags
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
            tags=sample_session_data["tags"],
        )

        # Remove some tags
        tags_to_remove = ["role-validation"]
        registry.remove_context_tags(sample_session_data["backlog_id"], tags_to_remove)

        session = registry.sessions[sample_session_data["backlog_id"]]
        assert "role-validation" not in session.context.tags
        assert "context-preservation" in session.context.tags  # Should remain

    def test_get_active_sessions(self, registry, sample_session_data):
        """Test retrieving active sessions."""
        # Register multiple sessions with different statuses
        registry.register_session(backlog_id="B-999", pid=12345, worklog_path="artifacts/worklogs/B-999.md")

        registry.register_session(backlog_id="B-1000", pid=12346, worklog_path="artifacts/worklogs/B-1000.md")

        # Update one to completed
        registry.update_session_status("B-999", "completed")

        # Get active sessions
        active_sessions = registry.get_active_sessions()
        assert len(active_sessions) == 1
        assert active_sessions[0].backlog_id == "B-1000"

    def test_get_sessions_by_context(self, registry, sample_session_data):
        """Test retrieving sessions by context tags."""
        # Register sessions with different tags
        registry.register_session(
            backlog_id="B-999",
            pid=12345,
            worklog_path="artifacts/worklogs/B-999.md",
            tags=["role-validation", "context-preservation"],
        )

        registry.register_session(
            backlog_id="B-1000",
            pid=12346,
            worklog_path="artifacts/worklogs/B-1000.md",
            tags=["dspy-integration", "testing"],
        )

        # Get sessions by context
        matching_sessions = registry.get_sessions_by_context(["role-validation"])
        assert len(matching_sessions) == 1
        assert matching_sessions[0].backlog_id == "B-999"

        # Test multiple tag matching
        matching_sessions = registry.get_sessions_by_context(["dspy-integration", "testing"])
        assert len(matching_sessions) == 1
        assert matching_sessions[0].backlog_id == "B-1000"

    def test_get_session_info(self, registry, sample_session_data):
        """Test retrieving detailed session information."""
        # Register a session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
        )

        # Get session info
        session_info = registry.get_session_info(sample_session_data["backlog_id"])
        assert session_info is not None
        assert session_info.backlog_id == sample_session_data["backlog_id"]
        assert session_info.pid == sample_session_data["pid"]

        # Test non-existent session
        session_info = registry.get_session_info("NON-EXISTENT")
        assert session_info is None

    def test_cleanup_completed_sessions(self, registry, sample_session_data):
        """Test cleanup of old completed sessions."""
        # Register a session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
        )

        # Complete the session
        registry.update_session_status(sample_session_data["backlog_id"], "completed")

        # Mock old timestamp for cleanup by directly setting the start_time
        old_session = registry.sessions[sample_session_data["backlog_id"]]
        old_session.start_time = "2025-08-14T00:00:00Z"  # 7+ days old

        # Run cleanup
        registry.cleanup_completed_sessions()

        # Session should be removed
        assert sample_session_data["backlog_id"] not in registry.sessions

    @patch("psutil.Process")
    def test_validate_processes(self, mock_process, registry, sample_session_data):
        """Test process validation."""
        # Register a session
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
        )

        # Mock process not running
        mock_process.return_value.is_running.return_value = False

        # Run validation
        registry.validate_processes()

        # Session should be marked as orphaned
        session = registry.sessions[sample_session_data["backlog_id"]]
        assert session.status == "orphaned"

    def test_save_and_load_registry(self, temp_registry_path):
        """Test registry persistence."""
        # Create registry and add session
        registry = SessionRegistry(registry_path=temp_registry_path)
        registry.register_session(
            backlog_id="B-999", pid=12345, worklog_path="artifacts/worklogs/B-999.md", tags=["test-tag"]
        )

        # Create new registry instance (should load existing data)
        new_registry = SessionRegistry(registry_path=temp_registry_path)

        # Verify data was persisted
        assert "B-999" in new_registry.sessions
        session = new_registry.sessions["B-999"]
        assert session.backlog_id == "B-999"
        assert session.pid == 12345
        assert "test-tag" in session.context.tags

    def test_error_handling_invalid_backlog_id(self, registry):
        """Test error handling for invalid operations."""
        # Try to update non-existent session
        registry.update_session_status("NON-EXISTENT", "completed")
        # Should not raise exception, just log warning

        # Try to add tags to non-existent session
        registry.add_context_tags("NON-EXISTENT", ["test-tag"])
        # Should not raise exception, just log warning

    def test_session_context_serialization(self, registry, sample_session_data):
        """Test session context serialization for JSON storage."""
        # Register session with complex context
        registry.register_session(
            backlog_id=sample_session_data["backlog_id"],
            pid=sample_session_data["pid"],
            worklog_path=sample_session_data["worklog_path"],
            session_type=sample_session_data["session_type"],
            priority=sample_session_data["priority"],
            tags=sample_session_data["tags"],
        )

        # Save registry (this tests serialization)
        registry.save_registry()

        # Load registry (this tests deserialization)
        new_registry = SessionRegistry(registry_path=registry.registry_path)

        # Verify context was properly serialized/deserialized
        session = new_registry.sessions[sample_session_data["backlog_id"]]
        assert session.context.session_type == sample_session_data["session_type"]
        assert session.context.priority == sample_session_data["priority"]
        assert set(sample_session_data["tags"]).issubset(session.context.tags)

class TestSessionContextIntegrator:
    """Test suite for session context integration with memory rehydration."""

    @pytest.fixture
    def temp_registry_path(self):
        """Create a temporary registry file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            # Create sample registry data
            sample_data = {
                "last_updated": "2025-08-21T00:00:00Z",
                "total_sessions": 2,
                "active_sessions": 1,
                "sessions": {
                    "B-999": {
                        "backlog_id": "B-999",
                        "pid": 12345,
                        "start_time": "2025-08-21T00:00:00Z",
                        "worklog_path": "artifacts/worklogs/B-999.md",
                        "status": "active",
                        "context": {
                            "tags": ["role-validation", "context-preservation"],
                            "session_type": "implementation",
                            "priority": "high",
                            "description": None,
                            "related_sessions": None,
                        },
                        "last_activity": None,
                        "idle_timeout": 1800,
                    },
                    "B-1000": {
                        "backlog_id": "B-1000",
                        "pid": 12346,
                        "start_time": "2025-08-21T00:00:00Z",
                        "worklog_path": "artifacts/worklogs/B-1000.md",
                        "status": "completed",
                        "context": {
                            "tags": ["dspy-integration"],
                            "session_type": "brainstorming",
                            "priority": "medium",
                            "description": None,
                            "related_sessions": None,
                        },
                        "last_activity": "2025-08-21T01:00:00Z",
                        "idle_timeout": 1800,
                    },
                },
            }
            f.write(json.dumps(sample_data))
            temp_path = f.name

        yield temp_path

        # Cleanup
        Path(temp_path).unlink(missing_ok=True)

    @pytest.fixture
    def integrator(self, temp_registry_path):
        """Create a SessionContextIntegrator instance for testing."""

        return SessionContextIntegrator(registry_path=temp_registry_path)

    def test_get_active_sessions_context(self, integrator):
        """Test retrieving active sessions context."""
        context = integrator.get_active_sessions_context()

        assert context["session_count"] == 1
        assert len(context["active_sessions"]) == 1
        assert context["active_sessions"][0]["backlog_id"] == "B-999"
        # Note: The integrator doesn't include status in the active sessions context
        # as it only returns active sessions by definition

    def test_get_sessions_by_context(self, integrator):
        """Test retrieving sessions by context tags."""
        # Test single tag
        context = integrator.get_sessions_by_context(["role-validation"])
        assert context["count"] == 1
        assert context["matching_sessions"][0]["backlog_id"] == "B-999"

        # Test multiple tags
        context = integrator.get_sessions_by_context(["dspy-integration"])
        assert context["count"] == 1
        assert context["matching_sessions"][0]["backlog_id"] == "B-1000"

        # Test non-matching tags
        context = integrator.get_sessions_by_context(["non-existent-tag"])
        assert context["count"] == 0

    def test_get_session_summary(self, integrator):
        """Test generating human-readable session summary."""
        summary = integrator.get_session_summary()

        assert "Active Scribe Sessions (1)" in summary
        assert "B-999" in summary
        assert "role-validation" in summary
        assert "context-preservation" in summary

    def test_enhance_memory_context(self, integrator):
        """Test enhancing memory context with session data."""
        base_context = {"existing": "data"}
        enhanced_context = integrator.enhance_memory_context(base_context)

        assert enhanced_context["existing"] == "data"
        assert "scribe_sessions" in enhanced_context
        assert "session_summary" in enhanced_context
        assert enhanced_context["scribe_sessions"]["session_count"] == 1

    def test_integrate_with_memory_rehydrator(self, temp_registry_path):
        """Test integration with memory rehydrator."""

        # Mock the integrator to use our test registry
        with patch("scripts.session_context_integration.SessionContextIntegrator") as mock_integrator_class:
            mock_integrator = MagicMock()
            mock_integrator_class.return_value = mock_integrator

            # Mock the integration data
            mock_integrator.get_active_sessions_context.return_value = {"active_sessions": [], "session_count": 0}
            mock_integrator.get_session_summary.return_value = "No active sessions"

            # Test integration
            integration_data = integrate_with_memory_rehydrator()

            assert "session_registry" in integration_data
            assert "session_summary" in integration_data
            assert "integration_timestamp" in integration_data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
