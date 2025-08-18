"""Tests for validator ratchet gate functionality."""

import json
import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
def test_ratchet_blocks_changed_file_regressions(tmp_path, monkeypatch):
    """Test that ratchet blocks changed file regressions."""

    # Create baseline with no violations
    baseline = {"categories": {"readme": {"violations": 0}, "multirep": {"violations": 0}}}
    (tmp_path / "baseline.json").write_text(json.dumps(baseline))

    # Create current report with regression
    current = {
        "categories": {"readme": {"violations": 1}, "multirep": {"violations": 0}},
        "impacted_files": {"readme": ["docs/README.md"]},
    }
    (tmp_path / "validator_report.json").write_text(json.dumps(current))

    # Set environment for changed files
    env = os.environ.copy()
    env["CHANGED_FILES_ONLY"] = "1"
    env["CHANGED_FILES"] = "docs/README.md"

    # Run ratchet check
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "validator_ratchet.py"
    rc = subprocess.run(
        [
            "python3",
            str(validator_script),
            "--report",
            str(tmp_path / "validator_report.json"),
            "--changed-files",
            "docs/README.md",
        ],
        cwd=tmp_path,
        env=env,
    ).returncode

    assert rc != 0


@pytest.mark.governance
def test_ratchet_ignores_unchanged_file_regressions(tmp_path, monkeypatch):
    """Test that ratchet ignores violations in unchanged files."""

    # Create baseline with no violations
    baseline = {"categories": {"readme": {"violations": 0}, "multirep": {"violations": 0}}}
    (tmp_path / "baseline.json").write_text(json.dumps(baseline))

    # Create current report with regression in unchanged file
    current = {
        "categories": {"readme": {"violations": 1}, "multirep": {"violations": 0}},
        "impacted_files": {"readme": ["unchanged/README.md"]},
    }
    (tmp_path / "validator_report.json").write_text(json.dumps(current))

    # Set environment for changed files (different file)
    env = os.environ.copy()
    env["CHANGED_FILES_ONLY"] = "1"
    env["CHANGED_FILES"] = "docs/README.md"

    # Run ratchet check - should pass since violation is in unchanged file
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "validator_ratchet.py"
    rc = subprocess.run(
        [
            "python3",
            str(validator_script),
            "--report",
            str(tmp_path / "validator_report.json"),
            "--changed-files",
            "docs/README.md",
        ],
        cwd=tmp_path,
        env=env,
    ).returncode

    assert rc == 0
