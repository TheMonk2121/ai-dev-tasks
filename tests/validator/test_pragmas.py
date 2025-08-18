"""Test pragma expiration behavior"""

import os
import tempfile
from datetime import datetime, timedelta

import pytest

from scripts.doc_coherence_validator import file_allows


def test_expired_pragma_fails():
    """Test that expired pragmas trigger violations"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            f"""# Test File

<!-- validator:allow xref-missing; expires={yesterday}; reason=legacy doc -->

Some content with missing references.
"""
        )
        f.flush()

        # Should not allow xref-missing violations (expired)
        assert not file_allows(f.name, "xref-missing")

        os.unlink(f.name)


def test_valid_pragma_succeeds():
    """Test that valid pragmas suppress violations"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            f"""# Test File

<!-- validator:allow xref-missing; expires={tomorrow}; reason=legacy doc -->

Some content with missing references.
"""
        )
        f.flush()

        # Should allow xref-missing violations (not expired)
        assert file_allows(f.name, "xref-missing")

        os.unlink(f.name)


def test_pragma_without_expiry_succeeds():
    """Test that pragmas without expiry work"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            """# Test File

<!-- validator:allow xref-missing; reason=legacy doc -->

Some content with missing references.
"""
        )
        f.flush()

        # Should allow xref-missing violations (no expiry)
        assert file_allows(f.name, "xref-missing")

        os.unlink(f.name)


def test_pragma_with_invalid_expiry_fails():
    """Test that invalid expiry dates fail"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            """# Test File

<!-- validator:allow xref-missing; expires=invalid-date; reason=legacy doc -->

Some content with missing references.
"""
        )
        f.flush()

        # Should not allow xref-missing violations (invalid expiry)
        assert not file_allows(f.name, "xref-missing")

        os.unlink(f.name)


def test_pragma_with_timezone():
    """Test pragma with timezone handling"""
    tomorrow_utc = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT23:59:59Z")

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(
            f"""# Test File

<!-- validator:allow xref-missing; expires={tomorrow_utc}; reason=legacy doc -->

Some content with missing references.
"""
        )
        f.flush()

        # Should allow xref-missing violations (not expired)
        assert file_allows(f.name, "xref-missing")

        os.unlink(f.name)


@pytest.mark.governance
@pytest.mark.xref
def test_pragma_and_ledger_merge_behavior(tmp_path):
    """Test that pragma and ledger merge behavior works correctly."""
    import json
    import subprocess

    # Create test file with pragma
    f = tmp_path / "doc.md"
    f.write_text("# T\n<!-- validator:allow xref-missing; expires=2999-01-01; reason=test -->\n")

    # Create ledger with exception
    (tmp_path / "data").mkdir()
    ledger = {
        "exceptions": {
            "doc.md": [
                {"key": "xref-missing", "expires": "2999-01-01", "reason": "ok", "created": "2999-01-01T00:00:00Z"}
            ]
        },
        "metadata": {},
    }
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
