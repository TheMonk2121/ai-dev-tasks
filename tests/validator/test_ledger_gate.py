"""Tests for validator ledger gate functionality."""

import datetime
import json
import subprocess
from pathlib import Path

import pytest


@pytest.mark.governance
def test_ledger_gate_blocks_new_entries_without_label(tmp_path):
    """Test that ledger gate blocks new entries without approval label."""

    script = Path(__file__).parent.parent.parent / "scripts" / "check_ledger_additions.py"

    # baseline has no exceptions
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"exceptions": {}}, indent=2))

    # current adds a new entry
    curr = tmp_path / "current.json"
    curr.write_text(
        json.dumps(
            {
                "exceptions": {
                    "OWNERS.md": [
                        {
                            "key": "xref-missing",
                            "expires": "2099-01-01",  # long expiry -> should be blocked without label
                            "reason": "test",
                            "created": "2099-01-01T00:00:00Z",
                        }
                    ]
                }
            },
            indent=2,
        )
    )

    # changed-files includes the ledger path so the gate runs
    res = subprocess.run(
        [
            "python3",
            str(script),
            "--base-json",
            str(base),
            "--current-json",
            str(curr),
            "--changed-files",
            str(curr),
        ],  # Use the actual current file path
        text=True,
        capture_output=True,
    )
    assert (
        res.returncode != 0
    ), f"Expected failure; got rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"


@pytest.mark.governance
def test_ledger_gate_allows_short_expiry_with_label(tmp_path):
    """Test that ledger gate allows approved entries with ≤7d expiry."""

    script = Path(__file__).parent.parent.parent / "scripts" / "check_ledger_additions.py"

    base = tmp_path / "base.json"
    base.write_text(json.dumps({"exceptions": {}}, indent=2))

    # expiry within 7 days
    expires = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
    curr = tmp_path / "current.json"
    curr.write_text(
        json.dumps(
            {
                "exceptions": {
                    "OWNERS.md": [
                        {
                            "key": "xref-missing",
                            "expires": expires,
                            "reason": "test",
                            "created": datetime.datetime.utcnow().isoformat() + "Z",
                        }
                    ]
                }
            },
            indent=2,
        )
    )

    res = subprocess.run(
        [
            "python3",
            str(script),
            "--base-json",
            str(base),
            "--current-json",
            str(curr),
            "--changed-files",
            str(curr),  # Use the actual current file path
            "--labels",
            "exception-approved",
        ],  # simulate approved label
        text=True,
        capture_output=True,
    )
    assert res.returncode == 0, f"Expected pass; got rc={res.returncode}\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
