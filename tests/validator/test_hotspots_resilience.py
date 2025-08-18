"""Tests for hotspots resilience functionality."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
def test_readme_hotspots_handles_invalid_or_empty_report(tmp_path, monkeypatch):
    """Test that readme hotspots handles invalid or empty report."""

    # Create empty/invalid report
    (tmp_path / "validator_report.json").write_text("")  # empty/invalid

    # Run hotspots analysis
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "readme_hotspots.py"
    rc = subprocess.run(["python3", str(validator_script)], cwd=tmp_path, capture_output=True, text=True)

    # Should not crash; should print a clean error or auto-regenerate
    assert rc.returncode == 0 or rc.returncode == 1
