"""Tests for anchor drift check functionality."""

import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
def test_anchor_drift_detects_removed_heading(tmp_path):
    """Test that anchor drift detects removed heading."""

    # Create test files with link
    a = tmp_path / "a.md"
    a.write_text("# A\n## Section\n")

    b = tmp_path / "b.md"
    b.write_text("# B\nSee [link](./a.md#section)\n")

    # Remove anchor
    a.write_text("# A\n")

    # Run anchor drift check
    validator_script = Path(__file__).parent.parent.parent / "scripts" / "anchor_drift_check.py"
    rc = subprocess.run(["python3", str(validator_script), "--root", str(tmp_path)], capture_output=True).returncode

    assert rc != 0
