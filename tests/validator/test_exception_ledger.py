#!/usr/bin/env python3
"""
Tests for validator exception ledger (PR B)
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from scripts.xref_apply import XRefScanner


@pytest.mark.tier1
@pytest.mark.kind_unit
class TestExceptionLedger:
    """Test validator exception ledger functionality."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create 000_core directory
            core_dir = repo_path / "000_core"
            core_dir.mkdir()

            # Create test file
            (core_dir / "test_file.md").write_text("# Test File\n\nThis is a test.")

            yield repo_path

    @pytest.fixture
    def scanner(self, temp_repo):
        """Create XRef scanner instance."""
        return XRefScanner(temp_repo, "000_core")

    def test_load_exceptions(self, scanner, temp_repo):
        """Test loading exceptions from file."""
        # Create exception file
        exceptions_file = temp_repo / "exceptions.json"
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [{"key": "xref-missing", "expires": "2025-08-24", "reason": "Test exception"}]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is loaded
        assert "000_core/test_file.md" in scanner.exceptions
        assert len(scanner.exceptions["000_core/test_file.md"]) == 1
        assert scanner.exceptions["000_core/test_file.md"][0]["key"] == "xref-missing"

    def test_unexpired_exception_suppresses(self, scanner, temp_repo):
        """Test that unexpired exception suppresses validation."""
        # Create exception file with future expiry
        exceptions_file = temp_repo / "exceptions.json"
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [{"key": "xref-missing", "expires": future_date, "reason": "Future exception"}]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is active
        assert scanner.is_excepted("000_core/test_file.md", "xref-missing")

    def test_expired_exception_fails(self, scanner, temp_repo):
        """Test that expired exception fails validation."""
        # Create exception file with past expiry
        exceptions_file = temp_repo / "exceptions.json"
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [{"key": "xref-missing", "expires": past_date, "reason": "Expired exception"}]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is expired
        assert not scanner.is_excepted("000_core/test_file.md", "xref-missing")

    def test_multiple_exceptions(self, scanner, temp_repo):
        """Test multiple exceptions for same file."""
        # Create exception file with multiple exceptions
        exceptions_file = temp_repo / "exceptions.json"
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [
                    {"key": "xref-missing", "expires": future_date, "reason": "XRef exception"},
                    {"key": "multi-rep-missing", "expires": future_date, "reason": "Multi-rep exception"},
                ]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check both exceptions are active
        assert scanner.is_excepted("000_core/test_file.md", "xref-missing")
        assert scanner.is_excepted("000_core/test_file.md", "multi-rep-missing")

    def test_wrong_key_not_excepted(self, scanner, temp_repo):
        """Test that wrong key is not excepted."""
        # Create exception file
        exceptions_file = temp_repo / "exceptions.json"
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [{"key": "xref-missing", "expires": future_date, "reason": "XRef exception"}]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check wrong key is not excepted
        assert not scanner.is_excepted("000_core/test_file.md", "multi-rep-missing")

    def test_wrong_file_not_excepted(self, scanner, temp_repo):
        """Test that wrong file is not excepted."""
        # Create exception file
        exceptions_file = temp_repo / "exceptions.json"
        future_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [{"key": "xref-missing", "expires": future_date, "reason": "XRef exception"}]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check wrong file is not excepted
        assert not scanner.is_excepted("000_core/other_file.md", "xref-missing")

    def test_no_expiry_exception_active(self, scanner, temp_repo):
        """Test that exception without expiry is always active."""
        # Create exception file without expiry
        exceptions_file = temp_repo / "exceptions.json"
        exceptions_data = {
            "exceptions": {"000_core/test_file.md": [{"key": "xref-missing", "reason": "No expiry exception"}]}
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is active
        assert scanner.is_excepted("000_core/test_file.md", "xref-missing")

    def test_invalid_date_format(self, scanner, temp_repo):
        """Test handling of invalid date format."""
        # Create exception file with invalid date
        exceptions_file = temp_repo / "exceptions.json"
        exceptions_data = {
            "exceptions": {
                "000_core/test_file.md": [
                    {"key": "xref-missing", "expires": "invalid-date", "reason": "Invalid date exception"}
                ]
            }
        }
        exceptions_file.write_text(json.dumps(exceptions_data))

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is not active (invalid date)
        assert not scanner.is_excepted("000_core/test_file.md", "xref-missing")

    def test_missing_exceptions_file(self, scanner, temp_repo):
        """Test behavior when exceptions file doesn't exist."""
        # Don't create exceptions file
        scanner.load_exceptions(None)

        # Check no exceptions are loaded
        assert scanner.exceptions == {}

    def test_invalid_json_file(self, scanner, temp_repo):
        """Test handling of invalid JSON file."""
        # Create invalid JSON file
        exceptions_file = temp_repo / "exceptions.json"
        exceptions_file.write_text("invalid json content")

        # Load exceptions (should not crash)
        scanner.load_exceptions(exceptions_file)

        # Check no exceptions are loaded
        assert scanner.exceptions == {}


@pytest.mark.governance
@pytest.mark.xref
def test_ledger_key_synonyms_respected(tmp_path):
    """Test that ledger key synonyms are respected."""
    import json
    import subprocess

    # Create test document
    doc = tmp_path / "README.md"
    doc.write_text("# A\nUnlinked\n")

    # Create ledger with synonym key
    ledger = {
        "exceptions": {
            "README.md": [
                {"key": "multirep-xref", "expires": "2999-01-01", "reason": "ok", "created": "2999-01-01T00:00:00Z"}
            ]
        },
        "metadata": {"total_exceptions": 1},
    }

    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "validator_exceptions.json").write_text(json.dumps(ledger))

    # Run validator with exceptions
    res = subprocess.run(
        [
            "python3",
            "scripts/doc_coherence_validator.py",
            "--ci",
            "--json",
            "--root",
            str(tmp_path),
            "--exceptions",
            str(tmp_path / "data" / "validator_exceptions.json"),
        ],
        capture_output=True,
        text=True,
    )

    report = json.loads(res.stdout)
    assert len(report.get("impacted_files", {}).get("multirep", [])) == 0
