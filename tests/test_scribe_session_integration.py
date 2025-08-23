#!/usr/bin/env python3
"""
Integration tests for Scribe Session Integration.

Tests the comprehensive integration between Scribe system and session registry:
- Scribe start/stop integration
- Session registration and cleanup
- Context tagging during Scribe sessions
- Memory rehydration integration
- End-to-end workflow validation
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Import the session registry system
from scripts.session_registry import SessionRegistry


class TestScribeSessionIntegration:
    """Integration tests for Scribe session management."""

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
    def mock_single_doorway(self):
        """Mock single_doorway.py for testing."""
        # Note: SessionRegistry is imported inside single_doorway functions, not at module level
        yield MagicMock()

    def test_scribe_start_registers_session(self, registry):
        """Test that Scribe start automatically registers a session."""
        # Simulate Scribe start
        backlog_id = "B-1000"
        pid = 12345
        worklog_path = "artifacts/worklogs/B-1000.md"

        # This would normally be called by single_doorway.py
        registry.register_session(
            backlog_id=backlog_id,
            pid=pid,
            worklog_path=worklog_path,
            session_type="brainstorming",
            priority="medium",
        )

        # Verify session was registered
        assert backlog_id in registry.sessions
        session = registry.sessions[backlog_id]
        assert session.pid == pid
        assert session.worklog_path == worklog_path
        assert session.status == "active"

    def test_scribe_stop_updates_session_status(self, registry):
        """Test that Scribe stop updates session status to completed."""
        # Register a session (simulating Scribe start)
        backlog_id = "B-1000"
        registry.register_session(
            backlog_id=backlog_id,
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
        )

        # Simulate Scribe stop
        registry.update_session_status(backlog_id, "completed")

        # Verify session status was updated
        session = registry.sessions[backlog_id]
        assert session.status == "completed"
        assert session.last_activity is not None

    def test_session_context_tagging_during_scribe(self, registry):
        """Test context tagging during Scribe sessions."""
        # Register a session
        backlog_id = "B-1000"
        registry.register_session(
            backlog_id=backlog_id,
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
        )

        # Add context tags during session
        context_tags = ["role-validation", "context-preservation", "dspy-integration"]
        registry.add_context_tags(backlog_id, context_tags)

        # Verify tags were added
        session = registry.sessions[backlog_id]
        assert all(tag in session.context.tags for tag in context_tags)

        # Remove some tags
        tags_to_remove = ["role-validation"]
        registry.remove_context_tags(backlog_id, tags_to_remove)

        # Verify tags were removed
        assert "role-validation" not in session.context.tags
        assert "context-preservation" in session.context.tags

    def test_multiple_scribe_sessions_management(self, registry):
        """Test management of multiple concurrent Scribe sessions."""
        # Register multiple sessions
        sessions_data = [
            {"backlog_id": "B-1000", "pid": 12345, "tags": ["implementation"]},
            {"backlog_id": "B-1001", "pid": 12346, "tags": ["brainstorming"]},
            {"backlog_id": "B-1002", "pid": 12347, "tags": ["debugging"]},
        ]

        for session_data in sessions_data:
            registry.register_session(
                backlog_id=session_data["backlog_id"],
                pid=session_data["pid"],
                worklog_path=f"artifacts/worklogs/{session_data['backlog_id']}.md",
                tags=session_data["tags"],
            )

        # Verify all sessions are active
        active_sessions = registry.get_active_sessions()
        assert len(active_sessions) == 3

        # Complete one session
        registry.update_session_status("B-1000", "completed")
        active_sessions = registry.get_active_sessions()
        assert len(active_sessions) == 2

        # Get sessions by context
        implementation_sessions = registry.get_sessions_by_context(["implementation"])
        assert len(implementation_sessions) == 1
        assert implementation_sessions[0].backlog_id == "B-1000"

    def test_scribe_session_cleanup(self, registry):
        """Test cleanup of completed Scribe sessions."""
        # Register and complete multiple sessions
        for i in range(3):
            backlog_id = f"B-{1000 + i}"
            registry.register_session(
                backlog_id=backlog_id,
                pid=12345 + i,
                worklog_path=f"artifacts/worklogs/{backlog_id}.md",
            )
            registry.update_session_status(backlog_id, "completed")

        # Mock old timestamps for cleanup
        for backlog_id in ["B-1000", "B-1001", "B-1002"]:
            old_session = registry.sessions[backlog_id]
            old_session.start_time = "2025-08-14T00:00:00Z"  # 7+ days old

        # Run cleanup
        registry.cleanup_completed_sessions()

        # All old sessions should be removed
        assert len(registry.sessions) == 0

    def test_scribe_session_process_validation(self, registry):
        """Test process validation for Scribe sessions."""
        # Register a session
        backlog_id = "B-1000"
        registry.register_session(
            backlog_id=backlog_id,
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
        )

        # Mock process not running
        with patch("psutil.Process") as mock_process:
            mock_process.return_value.is_running.return_value = False

            # Run validation
            registry.validate_processes()

            # Session should be marked as orphaned
            session = registry.sessions[backlog_id]
            assert session.status == "orphaned"

    def test_scribe_session_persistence(self, temp_registry_path):
        """Test persistence of Scribe session data."""
        # Create registry and add session
        registry = SessionRegistry(registry_path=temp_registry_path)
        registry.register_session(
            backlog_id="B-1000",
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
            tags=["scribe-session", "implementation"],
        )

        # Add context tags
        registry.add_context_tags("B-1000", ["role-validation"])

        # Create new registry instance (should load existing data)
        new_registry = SessionRegistry(registry_path=temp_registry_path)

        # Verify data was persisted
        assert "B-1000" in new_registry.sessions
        session = new_registry.sessions["B-1000"]
        assert session.backlog_id == "B-1000"
        assert session.pid == 12345
        assert "scribe-session" in session.context.tags
        assert "role-validation" in session.context.tags

    def test_scribe_session_error_handling(self, registry):
        """Test error handling in Scribe session management."""
        # Test operations on non-existent session
        registry.update_session_status("NON-EXISTENT", "completed")
        registry.add_context_tags("NON-EXISTENT", ["test-tag"])
        registry.remove_context_tags("NON-EXISTENT", ["test-tag"])

        # Should not raise exceptions, just log warnings
        assert len(registry.sessions) == 0

    def test_scribe_session_cli_integration(self, registry):
        """Test CLI integration for Scribe session management."""
        # Test session listing
        registry.register_session(
            backlog_id="B-1000",
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
            tags=["cli-test"],
        )

        # Verify session appears in registry
        active_sessions = registry.get_active_sessions()
        assert len(active_sessions) == 1
        assert active_sessions[0].backlog_id == "B-1000"

        # Test session info retrieval
        session_info = registry.get_session_info("B-1000")
        assert session_info is not None
        assert session_info.backlog_id == "B-1000"
        assert "cli-test" in session_info.context.tags

    def test_scribe_session_memory_integration(self, temp_registry_path):
        """Test integration with memory rehydration system."""
        from scripts.session_context_integration import SessionContextIntegrator

        # Create registry with session data
        registry = SessionRegistry(registry_path=temp_registry_path)
        registry.register_session(
            backlog_id="B-1000",
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
            tags=["memory-integration", "scribe-session"],
        )

        # Test memory integration
        integrator = SessionContextIntegrator(registry_path=temp_registry_path)
        context = integrator.get_active_sessions_context()

        assert context["session_count"] == 1
        assert len(context["active_sessions"]) == 1
        assert context["active_sessions"][0]["backlog_id"] == "B-1000"

        # Test session summary
        summary = integrator.get_session_summary()
        assert "B-1000" in summary
        assert "memory-integration" in summary

    def test_scribe_session_end_to_end_workflow(self, temp_registry_path):
        """Test complete end-to-end Scribe session workflow."""
        # 1. Start Scribe session
        registry = SessionRegistry(registry_path=temp_registry_path)
        registry.register_session(
            backlog_id="B-1000",
            pid=12345,
            worklog_path="artifacts/worklogs/B-1000.md",
            session_type="implementation",
            priority="high",
            tags=["e2e-test"],
        )

        # 2. Add context during session
        registry.add_context_tags("B-1000", ["role-validation", "context-preservation"])

        # 3. Verify session is active
        active_sessions = registry.get_active_sessions()
        assert len(active_sessions) == 1
        session = active_sessions[0]
        assert session.status == "active"
        assert "e2e-test" in session.context.tags
        assert "role-validation" in session.context.tags

        # 4. Complete session
        registry.update_session_status("B-1000", "completed")

        # 5. Verify session is completed
        session = registry.get_session_info("B-1000")
        assert session.status == "completed"
        assert session.last_activity is not None

        # 6. Test memory integration
        from scripts.session_context_integration import SessionContextIntegrator

        integrator = SessionContextIntegrator(registry_path=temp_registry_path)
        context = integrator.get_active_sessions_context()
        assert context["session_count"] == 0  # No active sessions after completion

        # 7. Test cleanup
        session.start_time = "2025-08-14T00:00:00Z"  # Old timestamp
        registry.cleanup_completed_sessions()
        assert "B-1000" not in registry.sessions

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
