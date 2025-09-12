#!/usr/bin/env python3
"""
Test Suite for Dependency Monitor - Automated Dependency Analysis

Tests the dependency monitoring system including:
- Dependency tree generation
- Circular dependency detection
- Import conflict analysis
- Change detection
- File output and logging
"""

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.dependency_monitor import DependencyMonitor


class TestDependencyMonitor:
    """Test cases for DependencyMonitor class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def monitor(self, temp_dir):
        """Create DependencyMonitor instance for testing."""
        return DependencyMonitor(dry_run=True, output_dir=temp_dir)

    def test_monitor_initialization(self, monitor, temp_dir):
        """Test DependencyMonitor initialization."""
        assert monitor.dry_run is True
        assert monitor.output_dir == Path(temp_dir)
        assert monitor.output_dir.exists()

    def test_log_function(self, monitor, temp_dir):
        """Test logging functionality."""
        monitor.log("Test message", "INFO")

        log_file = Path(temp_dir) / "dependency_changes.log"
        assert log_file.exists()

        with open(log_file) as f:
            content = f.read()
            assert "Test message" in content
            assert "[INFO]" in content

    def test_load_previous_state_nonexistent(self, monitor):
        """Test loading previous state when file doesn't exist."""
        state = monitor._load_previous_state()
        assert state == {}

    def test_load_previous_state_existing(self, monitor, temp_dir):
        """Test loading previous state from existing file."""
        # Create a mock previous state file
        state_data = {"test": "data", "timestamp": "2024-01-01T00:00:00"}
        state_file = Path(temp_dir) / "dependency_graph.json"

        with open(state_file, "w") as f:
            json.dump(state_data, f)

        # Update monitor's file path
        monitor.dependency_file = state_file
        state = monitor._load_previous_state()

        assert state == {"dependency_tree": state_data}

    @patch("subprocess.run")
    def test_generate_dependency_tree_success(self, mock_run, monitor):
        """Test successful dependency tree generation."""
        # Mock pipdeptree output
        mock_output = json.dumps([{"package": {"key": "test-package", "installed_version": "1.0.0"}}])

        mock_run.return_value = MagicMock(stdout=mock_output, returncode=0)

        result = monitor.generate_dependency_tree()

        assert result is not None
        assert result["tool"] == "pipdeptree"
        assert result["total_packages"] == 1
        assert "timestamp" in result
        assert "hash" in result

    @patch("subprocess.run")
    def test_generate_dependency_tree_failure(self, mock_run, monitor):
        """Test dependency tree generation failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "pipdeptree")

        result = monitor.generate_dependency_tree()

        assert result is None

    @patch("subprocess.run")
    def test_check_circular_dependencies_no_cycles(self, mock_run, monitor):
        """Test circular dependency check with no cycles."""
        # Need to enable force mode for circular dependency checks
        monitor.force = True
        mock_run.return_value = MagicMock(stdout="No circular dependencies found", stderr="", returncode=0)

        result = monitor.check_circular_dependencies()

        assert result is not None
        assert result["tool"] == "pycycle"
        assert result["has_circular_dependencies"] is False
        assert result["exit_code"] == 0

    @patch("subprocess.run")
    def test_check_circular_dependencies_with_cycles(self, mock_run, monitor):
        """Test circular dependency check with cycles detected."""
        # Need to enable force mode for circular dependency checks
        monitor.force = True
        mock_run.return_value = MagicMock(stdout="Circular dependency detected: A -> B -> A", stderr="", returncode=1)

        result = monitor.check_circular_dependencies()

        assert result is not None
        assert result["tool"] == "pycycle"
        assert result["has_circular_dependencies"] is True
        assert result["exit_code"] == 1

    @patch("subprocess.run")
    def test_analyze_import_conflicts_success(self, mock_run, monitor):
        """Test successful import conflict analysis."""
        mock_conflicts = {"conflicts": [], "status": "success"}
        mock_run.return_value = MagicMock(stdout=json.dumps(mock_conflicts), returncode=0)

        result = monitor.analyze_import_conflicts()

        assert result is not None
        assert result["tool"] == "conflict_audit.py"
        assert result["exit_code"] == 0
        assert result["conflicts"] == mock_conflicts

    def test_detect_changes_new_state(self, monitor):
        """Test change detection with new state."""
        previous_state = {}
        current_state = {"dependency_tree": {"new": "data"}}

        changes = monitor.detect_changes(current_state, previous_state)

        assert changes["changes_detected"] is True
        assert changes["details"]["dependency_tree"] == "new"

    def test_detect_changes_modified_state(self, monitor):
        """Test change detection with modified state."""
        previous_state = {"dependency_tree": {"old": "data"}}
        current_state = {"dependency_tree": {"new": "data"}}

        changes = monitor.detect_changes(current_state, previous_state)

        assert changes["changes_detected"] is True
        assert changes["details"]["dependency_tree"] == "modified"

    def test_detect_changes_no_changes(self, monitor):
        """Test change detection with no changes."""
        state = {"dependency_tree": {"same": "data"}}

        changes = monitor.detect_changes(state, state)

        assert changes["changes_detected"] is False
        assert changes["details"] == {}

    def test_generate_summary(self, monitor):
        """Test summary generation."""
        analysis_result = {
            "dependency_tree": {"total_packages": 150},
            "circular_dependencies": {"has_circular_dependencies": False},
            "import_conflicts": {"exit_code": 0},
            "changes": {"changes_detected": False},
        }

        summary = monitor.generate_summary(analysis_result)

        assert "DEPENDENCY ANALYSIS SUMMARY" in summary
        assert "📦 Dependencies: 150 packages" in summary
        assert "✅ Circular dependencies: None detected" in summary
        assert "✅ Import conflicts: Analysis completed" in summary
        assert "🔄 Changes detected: No" in summary

    def test_save_state_dry_run(self, monitor, temp_dir):
        """Test state saving in dry-run mode."""
        state = {"test": "data"}
        filename = Path(temp_dir) / "test.json"

        monitor._save_state(state, filename)

        # In dry-run mode, file should not be created
        assert not filename.exists()

    def test_save_state_normal(self, temp_dir):
        """Test state saving in normal mode."""
        monitor = DependencyMonitor(dry_run=False, output_dir=temp_dir)
        state = {"test": "data"}
        filename = Path(temp_dir) / "test.json"

        monitor._save_state(state, filename)

        # File should be created
        assert filename.exists()

        with open(filename) as f:
            saved_state = json.load(f)
            assert saved_state == state


class TestDependencyMonitorIntegration:
    """Integration tests for DependencyMonitor."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for integration testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @patch("subprocess.run")
    def test_full_analysis_workflow(self, mock_run, temp_dir):
        """Test complete analysis workflow."""
        # Mock all subprocess calls
        mock_run.side_effect = [
            # pipdeptree
            MagicMock(stdout=json.dumps([{"package": {"key": "test", "version": "1.0"}}]), returncode=0),
            # conflict_audit
            MagicMock(stdout=json.dumps({"conflicts": [], "status": "success"}), returncode=0),
        ]

        monitor = DependencyMonitor(dry_run=False, force=False, output_dir=temp_dir)
        result = monitor.run_analysis()

        # Check that all components were executed
        assert result["dependency_tree"] is not None
        assert result["circular_dependencies"] is None  # Skipped when force=False
        assert result["import_conflicts"] is not None
        assert "changes" in result

        # Check that files were created
        assert (Path(temp_dir) / "dependency_graph.json").exists()
        assert not (Path(temp_dir) / "circular_dependencies.json").exists()  # Not created when skipped
        assert (Path(temp_dir) / "import_conflicts.json").exists()
        assert (Path(temp_dir) / "dependency_changes.log").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
