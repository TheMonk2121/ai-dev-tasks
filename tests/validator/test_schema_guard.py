"""Tests for validator schema guard functionality."""

import json
import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
def test_schema_guard_honors_pinned_version(tmp_path, monkeypatch):
    """Test that schema guard honors pinned version."""

    # Simulate current report with schema 1.1.0
    (tmp_path / "validator_report.json").write_text(json.dumps({"schema_version": "1.1.0"}))

    # Run schema guard
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "validator_schema_guard.py"
    ok = subprocess.run(["python3", str(validator_script)], cwd=tmp_path).returncode
    assert ok == 0
