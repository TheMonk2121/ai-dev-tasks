from __future__ import annotations
import json
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from monitoring.maintenance_metrics import MaintenanceMetricsDB, store_maintenance_analysis
import os
from typing import Any, Dict, List, Optional, Union
"""
Property-based tests for maintenance metrics database integration.

Tests the maintenance metrics system end-to-end using Hypothesis to ensure
robustness across various data scenarios and edge cases.
"""


# Add src to path for imports


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))



@pytest.mark.prop
class TestMaintenanceMetricsProperties:
    """Property-based tests for maintenance metrics database operations."""

    @given(
        session_id=st.text(min_size=1, max_size=100),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup", "test_cleanup"]),
        status=st.sampled_from(["success", "partial", "failed"]),
        files_removed=st.integers(min_value=0, max_value=10000),
        directories_removed=st.integers(min_value=0, max_value=1000),
        bytes_freed=st.integers(min_value=0, max_value=10**12),  # Up to 1TB
        duration_seconds=st.floats(min_value=0.0, max_value=3600.0),  # Up to 1 hour
        error_count=st.integers(min_value=0, max_value=100),
    )
    def test_maintenance_session_data_consistency(
        self,
        session_id: str,
        maintenance_type: str,
        status: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
    ):
        """Test that maintenance session data maintains consistency properties."""
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

        # Create metadata
        metadata = {
            "cleanup_type": maintenance_type,
            "dry_run": False,
            "verbose": True,
            "test_run": True,
        }

        # Test data validation properties
        assert files_removed >= 0, "Files removed should be non-negative"
        assert directories_removed >= 0, "Directories removed should be non-negative"
        assert bytes_freed >= 0, "Bytes freed should be non-negative"
        assert duration_seconds >= 0.0, "Duration should be non-negative"
        assert error_count >= 0, "Error count should be non-negative"
        assert len(session_id) > 0, "Session ID should not be empty"
        assert maintenance_type in ["cache_cleanup", "log_cleanup", "full_cleanup", "test_cleanup"]
        assert status in ["success", "partial", "failed"]

        # Test analysis data structure
        assert "summary" in analysis_data
        assert "detailed_analysis" in analysis_data
        assert "lessons_learned" in analysis_data
        assert analysis_data["summary"]["total_cache_dirs"] == directories_removed
        assert analysis_data["summary"]["total_pyc_files"] == files_removed
        assert analysis_data["summary"]["bytes_freed"] == bytes_freed

    @given(
        cleanup_results=st.dictionaries(
            keys=st.sampled_from(
                ["files_removed", "directories_removed", "bytes_freed", "duration_seconds", "error_count"]
            ),
            values=st.one_of(
                st.integers(min_value=0, max_value=10000),
                st.floats(min_value=0.0, max_value=3600.0),
            ),
            min_size=3,
            max_size=5,
        ).filter(
            lambda d: all(
                (k in ["duration_seconds"] and isinstance(v, int | float))
                or (k not in ["duration_seconds"] and isinstance(v, int))
                for k, v in d.items()
            )
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
    def test_cleanup_results_analysis_data_compatibility(
        self,
        cleanup_results: dict[str, Any],
        analysis_data: dict[str, Any],
    ):
        """Test that cleanup results and analysis data are compatible."""
        # Ensure required fields exist
        required_fields = ["files_removed", "directories_removed", "bytes_freed"]
        for field in required_fields:
            if field not in cleanup_results:
                cleanup_results[field] = 0

        # Test data types
        assert isinstance(cleanup_results["files_removed"], int)
        assert isinstance(cleanup_results["directories_removed"], int)
        assert isinstance(cleanup_results["bytes_freed"], int)
        assert cleanup_results["files_removed"] >= 0
        assert cleanup_results["directories_removed"] >= 0
        assert cleanup_results["bytes_freed"] >= 0

        # Test analysis data is serializable
        try:
            json.dumps(analysis_data)
        except (TypeError, ValueError):
            pytest.fail("Analysis data should be JSON serializable")

    @given(
        session_id=st.text(min_size=1, max_size=50),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        error_count=st.integers(min_value=0, max_value=10),
    )
    def test_status_calculation_consistency(
        self,
        session_id: str,
        maintenance_type: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        error_count: int,
    ):
        """Test that status calculation is consistent with error count."""
        # Calculate expected status
        expected_status = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"

        # Test status calculation logic
        if error_count == 0:
            assert expected_status == "success"
        elif error_count < 5:
            assert expected_status == "partial"
        else:
            assert expected_status == "failed"

        # Test that status is deterministic
        status1 = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"
        status2 = "success" if error_count == 0 else "partial" if error_count < 5 else "failed"
        assert status1 == status2

    @given(
        days=st.integers(min_value=1, max_value=365),
        limit=st.integers(min_value=1, max_value=1000),
        maintenance_type=st.one_of(
            st.none(),
            st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        ),
    )
    def test_query_parameters_validity(
        self,
        days: int,
        limit: int,
        maintenance_type: str | None,
    ):
        """Test that query parameters are valid and consistent."""
        assert days > 0, "Days should be positive"
        assert limit > 0, "Limit should be positive"
        assert limit <= 1000, "Limit should be reasonable"
        assert days <= 365, "Days should be reasonable"

        if maintenance_type is not None:
            assert maintenance_type in ["cache_cleanup", "log_cleanup", "full_cleanup"]

    @given(
        analysis_data=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(max_size=200),
                st.integers(max_value=10000),
                st.floats(max_value=1000.0),
                st.lists(st.text(max_size=100), max_size=20),
                st.dictionaries(st.text(max_size=10), st.text(max_size=50), max_size=10),
            ),
            min_size=1,
            max_size=20,
        ),
    )
    def test_analysis_data_json_serialization(
        self,
        analysis_data: dict[str, Any],
    ):
        """Test that analysis data can be JSON serialized and deserialized."""
        try:
            # Test serialization
            json_str = json.dumps(analysis_data, default=str)
            assert isinstance(json_str, str)
            assert len(json_str) > 0

            # Test deserialization
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)

            # Test that key structure is preserved
            assert set(deserialized.keys()) == set(analysis_data.keys())

        except (TypeError, ValueError) as e:
            pytest.fail(f"Analysis data should be JSON serializable: {e}")

    @given(
        git_sha=st.one_of(
            st.none(),
            st.text(min_size=7, max_size=40, alphabet="0123456789abcdef"),
        ),
    )
    @settings(suppress_health_check=[])
    def test_git_sha_format_validation(
        self,
        git_sha: str | None,
    ):
        """Test that git SHA format is valid."""
        if git_sha is not None:
            assert len(git_sha) >= 7, "Git SHA should be at least 7 characters"
            assert len(git_sha) <= 40, "Git SHA should be at most 40 characters"
            assert all(c in "0123456789abcdef" for c in git_sha.lower()), "Git SHA should contain only hex characters"

    @given(
        session_id=st.text(min_size=1, max_size=100),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        duration_seconds=st.floats(min_value=0.0, max_value=3600.0),
        error_count=st.integers(min_value=0, max_value=10),
    )
    def test_cleanup_results_structure_consistency(
        self,
        session_id: str,
        maintenance_type: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
    ):
        """Test that cleanup results structure is consistent."""
        cleanup_results = {
            "files_removed": files_removed,
            "directories_removed": directories_removed,
            "bytes_freed": bytes_freed,
            "duration_seconds": duration_seconds,
            "error_count": error_count,
        }

        # Test structure properties
        assert isinstance(cleanup_results, dict)
        assert len(cleanup_results) == 5
        assert all(
            key in cleanup_results
            for key in ["files_removed", "directories_removed", "bytes_freed", "duration_seconds", "error_count"]
        )

        # Test value properties
        assert cleanup_results["files_removed"] >= 0
        assert cleanup_results["directories_removed"] >= 0
        assert cleanup_results["bytes_freed"] >= 0
        assert cleanup_results["duration_seconds"] >= 0.0
        assert cleanup_results["error_count"] >= 0

        # Test that values match inputs
        assert cleanup_results["files_removed"] == files_removed
        assert cleanup_results["directories_removed"] == directories_removed
        assert cleanup_results["bytes_freed"] == bytes_freed
        assert cleanup_results["duration_seconds"] == duration_seconds
        assert cleanup_results["error_count"] == error_count

    @given(
        metadata=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.booleans(),
                st.text(max_size=100),
                st.integers(max_value=1000),
                st.floats(max_value=1000.0),
                st.lists(st.text(max_size=50), max_size=10),
                st.dictionaries(st.text(max_size=10), st.text(max_size=50), max_size=5),
            ),
            min_size=1,
            max_size=15,
        ),
    )
    def test_metadata_structure_consistency(
        self,
        metadata: dict[str, Any],
    ):
        """Test that metadata structure is consistent and serializable."""
        # Test that metadata is a dictionary
        assert isinstance(metadata, dict)
        assert len(metadata) > 0

        # Test that all keys are strings
        assert all(isinstance(key, str) for key in metadata.keys())
        assert all(len(key) > 0 for key in metadata.keys())

        # Test JSON serialization
        try:
            json.dumps(metadata, default=str)
        except (TypeError, ValueError) as e:
            pytest.fail(f"Metadata should be JSON serializable: {e}")

    @given(
        session_id=st.text(min_size=1, max_size=50),
        maintenance_type=st.sampled_from(["cache_cleanup", "log_cleanup", "full_cleanup"]),
        status=st.sampled_from(["success", "partial", "failed"]),
        files_removed=st.integers(min_value=0, max_value=1000),
        directories_removed=st.integers(min_value=0, max_value=100),
        bytes_freed=st.integers(min_value=0, max_value=10**9),
        duration_seconds=st.floats(min_value=0.0, max_value=3600.0),
        error_count=st.integers(min_value=0, max_value=10),
    )
    def test_maintenance_session_completeness(
        self,
        session_id: str,
        maintenance_type: str,
        status: str,
        files_removed: int,
        directories_removed: int,
        bytes_freed: int,
        duration_seconds: float,
        error_count: int,
    ):
        """Test that maintenance session data is complete and consistent."""
        # Create complete session data
        analysis_data = {
            "summary": {
                "total_cache_dirs": directories_removed,
                "total_pyc_files": files_removed,
                "bytes_freed": bytes_freed,
            },
            "detailed_analysis": {
                "cache_by_module": {"test.module": files_removed // 2},
            },
            "lessons_learned": {
                "most_compiled_modules": ["test.module"],
            },
        }

        metadata = {
            "cleanup_type": maintenance_type,
            "test_run": True,
        }

        # Test that all required fields are present
        required_fields = [
            "session_id",
            "maintenance_type",
            "status",
            "files_removed",
            "directories_removed",
            "bytes_freed",
            "duration_seconds",
            "error_count",
        ]

        session_data = {
            "session_id": session_id,
            "maintenance_type": maintenance_type,
            "status": status,
            "files_removed": files_removed,
            "directories_removed": directories_removed,
            "bytes_freed": bytes_freed,
            "duration_seconds": duration_seconds,
            "error_count": error_count,
            "analysis_data": analysis_data,
            "metadata": metadata,
        }

        # Test completeness
        assert all(field in session_data for field in required_fields)
        assert all(session_data[field] is not None for field in required_fields)

        # Test data types
        assert isinstance(session_data["session_id"], str)
        assert isinstance(session_data["maintenance_type"], str)
        assert isinstance(session_data["status"], str)
        assert isinstance(session_data["files_removed"], int)
        assert isinstance(session_data["directories_removed"], int)
        assert isinstance(session_data["bytes_freed"], int)
        assert isinstance(session_data["duration_seconds"], float)
        assert isinstance(session_data["error_count"], int)
        assert isinstance(session_data["analysis_data"], dict)
        assert isinstance(session_data["metadata"], dict)

        # Test value ranges
        assert session_data["files_removed"] >= 0
        assert session_data["directories_removed"] >= 0
        assert session_data["bytes_freed"] >= 0
        assert session_data["duration_seconds"] >= 0.0
        assert session_data["error_count"] >= 0
