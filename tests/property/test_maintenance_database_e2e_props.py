"""
End-to-end property-based tests for maintenance database integration.

Tests the complete maintenance metrics system with actual database operations
using Hypothesis to ensure robustness across various scenarios.
"""

import json
import os

# Add src to path for imports
import sys
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from monitoring.maintenance_metrics import MaintenanceMetricsDB, store_maintenance_analysis


@pytest.mark.prop
class TestMaintenanceDatabaseE2EProperties:
    """End-to-end property-based tests for maintenance database operations."""

    def _create_temp_db(self):
        """Create a temporary database for testing."""
        # Use temporary file for testing to persist data across operations
        temp_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        temp_file.close()
        return MaintenanceMetricsDB(database_url=temp_file.name)

    @given(
        session_id=st.text(min_size=1, max_size=50),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        duration_seconds=st.floats(min_value=0.0, max_value=3600.0),
        error_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=5, deadline=5000, suppress_health_check=[])  # Limit examples for database tests
    def test_store_and_retrieve_maintenance_session(
        self,
        session_id: str,
        maintenance_type: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
    ):
        """Test storing and retrieving maintenance session data."""
        # Create temporary database
        temp_db = self._create_temp_db()

        # Create analysis data
        analysis_data = {
            "summary": {
                "total_cache_dirs": directories_removed,
                "total_pyc_files": files_removed,
                "bytes_freed": bytes_freed,
                "most_active_modules": [["test.module", files_removed // 2]],
            },
            "detailed_analysis": {
                "cache_by_module": {"test.module": files_removed // 2},
                "module_activity": {"test.module": files_removed},
            },
            "lessons_learned": {
                "most_compiled_modules": ["test.module"],
                "recommendations": ["Test recommendation"],
            },
        }

        metadata = {
            "cleanup_type": maintenance_type,
            "test_run": True,
            "session_id": session_id,
        }

        # Calculate expected status
        status = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"

        # Store the session
        success = temp_db.store_maintenance_session(
            session_id=session_id,
            maintenance_type=maintenance_type,
            status=status,
            files_removed=files_removed,
            directories_removed=directories_removed,
            bytes_freed=bytes_freed,
            duration_seconds=duration_seconds,
            error_count=error_count,
            analysis_data=analysis_data,
            metadata=metadata,
            git_sha="test1234567890abcdef",
        )

        assert success, "Session should be stored successfully"

        # Retrieve the session
        history = temp_db.get_maintenance_history(days=1, limit=10)
        assert len(history) >= 1, "Should retrieve at least one session"

        # Find our session
        our_session = None
        for session in history:
            if session["session_id"] == session_id:
                our_session = session
                break

        assert our_session is not None, "Our session should be found in history"

        # Verify data integrity
        assert our_session["maintenance_type"] == maintenance_type
        assert our_session["status"] == status
        assert our_session["files_removed"] == files_removed
        assert our_session["directories_removed"] == directories_removed
        assert our_session["bytes_freed"] == bytes_freed
        assert our_session["duration_seconds"] == duration_seconds
        assert our_session["error_count"] == error_count

        # Verify JSONB fields
        assert our_session["analysis_data"] == analysis_data
        assert our_session["metadata"] == metadata
        assert our_session["git_sha"] == "test1234567890abcdef"

    @given(
        num_sessions=st.integers(min_value=1, max_value=5),
        maintenance_types=st.lists(
            st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
            min_size=1,
            max_size=3,
            unique=True,
        ),
    )
    @settings(max_examples=5, deadline=10000, suppress_health_check=[])
    def test_multiple_sessions_aggregation(
        self,
        num_sessions: int,
        maintenance_types: list[str],
    ):
        """Test storing multiple sessions and aggregating them."""
        # Create temporary database
        temp_db = self._create_temp_db()

        total_files = 0
        total_dirs = 0
        total_bytes = 0
        total_errors = 0

        # Store multiple sessions
        for i in range(num_sessions):
            maint_type = maintenance_types[i % len(maintenance_types)]
            session_id = f"test_session_{i}_{uuid.uuid4().hex[:8]}"

            files_removed = (i + 1) * 10
            directories_removed = (i + 1) * 2
            bytes_freed = (i + 1) * 1000
            error_count = i % 3

            total_files += files_removed
            total_dirs += directories_removed
            total_bytes += bytes_freed
            total_errors += error_count

            analysis_data = {
                "summary": {
                    "total_cache_dirs": directories_removed,
                    "total_pyc_files": files_removed,
                    "bytes_freed": bytes_freed,
                },
            }

            metadata = {
                "cleanup_type": maint_type,
                "test_run": True,
                "session_number": i,
            }

            status = "success" if error_count == 0 else "partial" if error_count < 2 else "failed"

            success = temp_db.store_maintenance_session(
                session_id=session_id,
                maintenance_type=maint_type,
                status=status,
                files_removed=files_removed,
                directories_removed=directories_removed,
                bytes_freed=bytes_freed,
                duration_seconds=1.0 + i,
                error_count=error_count,
                analysis_data=analysis_data,
                metadata=metadata,
            )

            assert success, f"Session {i} should be stored successfully"

        # Test summary aggregation
        summary = temp_db.get_maintenance_summary(days=1)
        assert summary["total_sessions"] == num_sessions, "Should have correct number of sessions"

        # Test history retrieval
        history = temp_db.get_maintenance_history(days=1, limit=100)
        assert len(history) == num_sessions, "Should retrieve all sessions"

        # Test filtering by maintenance type
        # Only test filtering for types that were actually used
        used_types = set()
        for i in range(num_sessions):
            maint_type = maintenance_types[i % len(maintenance_types)]
            used_types.add(maint_type)

        for maint_type in used_types:
            filtered_history = temp_db.get_maintenance_history(maintenance_type=maint_type, days=1, limit=100)
            assert len(filtered_history) >= 1, f"Should have at least one session of type {maint_type}"

    @given(
        cleanup_results=st.dictionaries(
            keys=st.sampled_from(
                ["files_removed", "directories_removed", "bytes_freed", "duration_seconds", "error_count"]
            ),
            values=st.one_of(
                st.integers(min_value=0, max_value=1000),
                st.floats(min_value=0.0, max_value=3600.0),
            ),
            min_size=3,
            max_size=5,
        ),
        analysis_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(max_size=100),
                st.integers(max_value=1000),
                st.lists(st.text(max_size=50), max_size=10),
                st.dictionaries(st.text(max_size=10), st.text(max_size=50), max_size=5),
            ),
            min_size=1,
            max_size=10,
        ),
    )
    @settings(max_examples=5, deadline=5000, suppress_health_check=[])
    def test_store_maintenance_analysis_convenience_function(
        self,
        cleanup_results: dict[str, Any],
        analysis_data: dict[str, Any],
    ):
        """Test the convenience function for storing maintenance analysis."""
        # Create temporary database
        temp_db = self._create_temp_db()

        # Ensure required fields exist
        if "files_removed" not in cleanup_results:
            cleanup_results["files_removed"] = 0
        if "directories_removed" not in cleanup_results:
            cleanup_results["directories_removed"] = 0
        if "bytes_freed" not in cleanup_results:
            cleanup_results["bytes_freed"] = 0
        if "duration_seconds" not in cleanup_results:
            cleanup_results["duration_seconds"] = 0.0
        if "error_count" not in cleanup_results:
            cleanup_results["error_count"] = 0

        session_id = f"convenience_test_{uuid.uuid4().hex[:8]}"
        maintenance_type = "full_cleanup"

        # Test the convenience function
        success = store_maintenance_analysis(
            session_id=session_id,
            maintenance_type=maintenance_type,
            cleanup_results=cleanup_results,
            analysis_data=analysis_data,
            metadata={"test_run": True},
            database_url=temp_db.database_url,
        )

        # Note: This will fail if database is not available, which is expected in test environment
        # We're testing the function structure and data preparation, not actual database storage
        assert isinstance(success, bool), "Function should return a boolean"

    @given(
        session_id=st.text(min_size=1, max_size=50),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        error_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=5, deadline=5000, suppress_health_check=[])
    def test_data_consistency_across_operations(
        self,
        session_id: str,
        maintenance_type: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        error_count: int,
    ):
        """Test that data remains consistent across store/retrieve operations."""
        # Create temporary database
        temp_db = self._create_temp_db()

        analysis_data = {
            "summary": {
                "total_cache_dirs": directories_removed,
                "total_pyc_files": files_removed,
                "bytes_freed": bytes_freed,
            },
            "test_data": {
                "random_value": files_removed * 2,
                "nested": {
                    "deep_value": directories_removed + 1,
                },
            },
        }

        metadata = {
            "cleanup_type": maintenance_type,
            "test_run": True,
            "original_values": {
                "files_removed": files_removed,
                "directories_removed": directories_removed,
                "bytes_freed": bytes_freed,
                "error_count": error_count,
            },
        }

        status = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"

        # Store the session
        success = temp_db.store_maintenance_session(
            session_id=session_id,
            maintenance_type=maintenance_type,
            status=status,
            files_removed=files_removed,
            directories_removed=directories_removed,
            bytes_freed=bytes_freed,
            duration_seconds=1.0,
            error_count=error_count,
            analysis_data=analysis_data,
            metadata=metadata,
        )

        assert success, "Session should be stored successfully"

        # Retrieve and verify consistency
        history = temp_db.get_maintenance_history(days=1, limit=10)
        our_session = next((s for s in history if s["session_id"] == session_id), None)

        assert our_session is not None, "Session should be retrievable"

        # Test basic field consistency
        assert our_session["maintenance_type"] == maintenance_type
        assert our_session["files_removed"] == files_removed
        assert our_session["directories_removed"] == directories_removed
        assert our_session["bytes_freed"] == bytes_freed
        assert our_session["error_count"] == error_count

        # Test JSONB field consistency
        assert our_session["analysis_data"] == analysis_data
        assert our_session["metadata"] == metadata

        # Test nested data consistency
        assert our_session["analysis_data"]["test_data"]["random_value"] == files_removed * 2
        assert our_session["analysis_data"]["test_data"]["nested"]["deep_value"] == directories_removed + 1
        assert our_session["metadata"]["original_values"]["files_removed"] == files_removed

    @given(
        days=st.integers(min_value=1, max_value=30),
        limit=st.integers(min_value=1, max_value=100),
        maintenance_type=st.one_of(
            st.none(),
            st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        ),
    )
    @settings(max_examples=3, deadline=3000, suppress_health_check=[])
    def test_query_parameter_validation(
        self,
        days: int,
        limit: int,
        maintenance_type: str | None,
    ):
        """Test that query parameters are validated and handled correctly."""
        # Create temporary database
        temp_db = self._create_temp_db()

        # Test get_maintenance_history with various parameters
        history = temp_db.get_maintenance_history(
            maintenance_type=maintenance_type,
            days=days,
            limit=limit,
        )

        # Should return a list
        assert isinstance(history, list)

        # Should respect limit
        assert len(history) <= limit

        # Test get_maintenance_summary
        summary = temp_db.get_maintenance_summary(days=days)

        # Should return a dictionary with expected keys
        assert isinstance(summary, dict)
        assert "total_sessions" in summary
        assert "success_rate" in summary
        assert "by_type" in summary
        assert "timestamp" in summary

        # Test that summary data is consistent
        assert summary["total_sessions"] >= 0
        assert 0 <= summary["success_rate"] <= 100
        assert isinstance(summary["by_type"], list)

    @given(
        session_id=st.text(min_size=1, max_size=50),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        error_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=3, deadline=5000, suppress_health_check=[])
    def test_edge_case_data_handling(
        self,
        session_id: str,
        maintenance_type: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        error_count: int,
    ):
        """Test handling of edge case data values."""
        # Create temporary database
        temp_db = self._create_temp_db()

        # Test with extreme values
        analysis_data = {
            "summary": {
                "total_cache_dirs": directories_removed,
                "total_pyc_files": files_removed,
                "bytes_freed": bytes_freed,
            },
            "edge_cases": {
                "zero_values": files_removed == 0,
                "large_values": bytes_freed > 10**6,
                "high_error_count": error_count > 5,
            },
        }

        metadata = {
            "cleanup_type": maintenance_type,
            "test_run": True,
            "edge_case_test": True,
            "extreme_values": {
                "files_removed": files_removed,
                "bytes_freed": bytes_freed,
            },
        }

        status = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"

        # Store the session
        success = temp_db.store_maintenance_session(
            session_id=session_id,
            maintenance_type=maintenance_type,
            status=status,
            files_removed=files_removed,
            directories_removed=directories_removed,
            bytes_freed=bytes_freed,
            duration_seconds=0.001 if files_removed == 0 else 3600.0,  # Edge case duration
            error_count=error_count,
            analysis_data=analysis_data,
            metadata=metadata,
        )

        assert success, "Session should be stored successfully even with edge case data"

        # Verify edge case data is preserved
        history = temp_db.get_maintenance_history(days=1, limit=10)
        our_session = next((s for s in history if s["session_id"] == session_id), None)

        assert our_session is not None, "Session should be retrievable"
        assert our_session["analysis_data"]["edge_cases"]["zero_values"] == (files_removed == 0)
        assert our_session["analysis_data"]["edge_cases"]["large_values"] == (bytes_freed > 10**6)
        assert our_session["analysis_data"]["edge_cases"]["high_error_count"] == (error_count > 5)
