"""
Tests for abp_validation.py

Tests the ABP (Agent Behavior Protocol) validation functionality
that validates evaluation results against established protocols.
"""

#!/usr/bin/env python3

import json
import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import Mock, mock_open, patch

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.utilities.abp_validation import _fresh, _load, main


class TestABPValidationFunctions:
    """Test cases for ABP validation functions."""

    @patch("scripts.utilities.abp_validation.os.path.getmtime")
    @patch("scripts.utilities.abp_validation.time.time")
    def test_fresh_file_recent(self, mock_time, mock_getmtime: Any):
        """Test _fresh returns True for recent file."""
        mock_time.return_value = 1000000  # Current time
        mock_getmtime.return_value = 999000  # File modified 1000 seconds ago (fresh)

        result = _fresh("test.json", 2)  # 2 days max age

        assert result is True

    @patch("scripts.utilities.abp_validation.os.path.getmtime")
    @patch("scripts.utilities.abp_validation.time.time")
    def test_fresh_file_old(self, mock_time, mock_getmtime: Any):
        """Test _fresh returns False for old file."""
        mock_time.return_value = 1000000  # Current time
        mock_getmtime.return_value = 900000  # File modified 100000 seconds ago (old)

        result = _fresh("test.json", 1)  # 1 day max age

        assert result is False

    @patch("scripts.utilities.abp_validation.os.path.getmtime")
    def test_fresh_file_not_found(self, mock_getmtime: Any):
        """Test _fresh handles file not found."""
        mock_getmtime.side_effect = FileNotFoundError("File not found")

        result = _fresh("nonexistent.json", 1)

        assert result is False

    def test_load_success(self: Any):
        """Test _load loads JSON successfully."""
        mock_data = {"test": "data"}

        with patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = _load("test.json")

            assert result == mock_data

    def test_load_file_not_found(self: Any):
        """Test _load handles file not found."""
        with patch("builtins.open", side_effect=FileNotFoundError):
            result = _load("nonexistent.json")

            assert result is None

    def test_load_invalid_json(self: Any):
        """Test _load handles invalid JSON."""
        with patch("builtins.open", mock_open(read_data="invalid json")):
            result = _load("invalid.json")

            assert result is None

    @patch("scripts.utilities.abp_validation._fresh")
    @patch("scripts.utilities.abp_validation._load")
    @patch("scripts.utilities.abp_validation.os.path.exists")
    def test_main_success(self, mock_exists, mock_load, mock_fresh: Any):
        """Test main function runs successfully."""
        mock_exists.return_value = True
        mock_fresh.return_value = True
        mock_load.return_value = {"test": "data"}

        with patch("sys.argv", ["abp_validation.py", "--profile", "gold"]):
            from scripts.utilities.abp_validation import main

            result = main()

            assert result == 0

    @patch("scripts.utilities.abp_validation._fresh")
    @patch("scripts.utilities.abp_validation._load")
    @patch("scripts.utilities.abp_validation.os.path.exists")
    def test_main_missing_manifest(self, mock_exists, mock_load, mock_fresh: Any):
        """Test main function handles missing manifest."""
        mock_exists.return_value = False

        with patch("sys.argv", ["abp_validation.py", "--profile", "gold"]):
            from scripts.utilities.abp_validation import main

            result = main()

            assert result == 1

    @patch("scripts.utilities.abp_validation._fresh")
    @patch("scripts.utilities.abp_validation._load")
    @patch("scripts.utilities.abp_validation.os.path.exists")
    def test_main_stale_manifest(self, mock_exists, mock_load, mock_fresh: Any):
        """Test main function handles stale manifest."""
        mock_exists.return_value = True
        mock_fresh.return_value = False

        with patch("sys.argv", ["abp_validation.py", "--profile", "gold", "--strict"]):
            from scripts.utilities.abp_validation import main

            result = main()

            assert result == 1

    @patch("scripts.utilities.abp_validation._fresh")
    @patch("scripts.utilities.abp_validation._load")
    @patch("scripts.utilities.abp_validation.os.path.exists")
    def test_main_ci_mode(self, mock_exists, mock_load, mock_fresh: Any):
        """Test main function in CI mode."""
        mock_exists.return_value = True
        mock_fresh.return_value = False
        mock_load.return_value = {"test": "data"}

        with patch("sys.argv", ["abp_validation.py", "--profile", "gold", "--ci-mode"]):
            with patch("builtins.print") as mock_print:
                from scripts.utilities.abp_validation import main

                result = main()

                assert result == 0
                mock_print.assert_called()

    @patch("sys.argv", ["abp_validation.py", "--help"])
    def test_main_help(self: Any):
        """Test main function shows help."""
        with patch("scripts.utilities.abp_validation.argparse.ArgumentParser.print_help"):
            with patch("scripts.utilities.abp_validation.sys.exit") as mock_exit:
                from scripts.utilities.abp_validation import main

                main()

                mock_exit.assert_called_once_with(0)


if __name__ == "__main__":
    pytest.main([__file__])
