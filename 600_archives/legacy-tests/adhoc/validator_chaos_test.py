#!/usr/bin/env python3.11
"""
Validator Chaos Test

Tests validator chaos scenarios and rollback mechanisms to ensure they work as designed.
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timezone, UTC
from typing import Dict, Tuple


def create_synthetic_violations() -> dict:
    """Create synthetic violations for testing."""
    return {
        "categories": {
            "archive": {"violations": 1, "fail": True},
            "shadow_fork": {"violations": 1, "fail": True},
            "readme": {"violations": 1, "fail": True},
            "multirep": {"violations": 1, "fail": True},
        },
        "impacted_files": {
            "archive": ["test_archive_violation.md"],
            "shadow_fork": ["test_shadow_violation.py"],
            "readme": ["test_readme_violation.md"],
            "multirep": ["test_multirep_violation.md"],
        },
        "schema_version": "1.1.0",
        "generated_at": datetime.now(UTC).isoformat() + "Z",
    }


def test_ratchet_scenario() -> tuple[bool, str]:
    """Test ratchet scenario with synthetic violations."""
    print("🧪 Testing Ratchet Scenario...")

    # Create synthetic report with violations
    synthetic_report = create_synthetic_violations()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(synthetic_report, f)
        report_path = f.name

    try:
        # Test ratchet with synthetic violations
        import subprocess

        result = subprocess.run(
            ["python3", "scripts/validator_ratchet.py", "--report", report_path], capture_output=True, text=True
        )

        # Ratchet should fail with violations
        if result.returncode != 0:
            print("✅ Ratchet correctly failed with violations")
            return True, "Ratchet correctly blocked violations"
        else:
            print("❌ Ratchet should have failed with violations")
            return False, "Ratchet did not block violations"

    except Exception as e:
        return False, f"Ratchet test failed: {e}"
    finally:
        os.unlink(report_path)


def test_fail_mode_scenario() -> tuple[bool, str]:
    """Test FAIL mode scenario with synthetic violations."""
    print("🧪 Testing FAIL Mode Scenario...")

    # Create synthetic report with violations in FAIL mode
    synthetic_report = create_synthetic_violations()

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(synthetic_report, f)
        report_path = f.name

    try:
        # Test FAIL mode gate
        import subprocess

        result = subprocess.run(
            [
                "python3",
                "-c",
                f"""
import json, sys
r = json.load(open('{report_path}'))
fail = 0
for cat, info in r.get("categories", {{}}).items():
    v = info.get("violations", 0)
    if info.get("fail") and v > 0:
        print(f"FAIL: {{cat}} has {{v}} violations in FAIL mode")
        fail = 2
sys.exit(fail)
            """,
            ],
            capture_output=True,
            text=True,
        )

        # FAIL mode gate should fail with violations
        if result.returncode != 0:
            print("✅ FAIL mode gate correctly failed with violations")
            return True, "FAIL mode gate correctly blocked violations"
        else:
            print("❌ FAIL mode gate should have failed with violations")
            return False, "FAIL mode gate did not block violations"

    except Exception as e:
        return False, f"FAIL mode test failed: {e}"
    finally:
        os.unlink(report_path)


def test_rollback_scenario() -> tuple[bool, str]:
    """Test rollback scenario with >5% false positives."""
    print("🧪 Testing Rollback Scenario...")

    # Create synthetic report with high violation count (>5% threshold)
    synthetic_report = {
        "categories": {
            "archive": {"violations": 50, "fail": True},  # High count
            "shadow_fork": {"violations": 0, "fail": True},
            "readme": {"violations": 0, "fail": True},
            "multirep": {"violations": 0, "fail": True},
        },
        "impacted_files": {
            "archive": [f"test_archive_{i}.md" for i in range(50)],
            "shadow_fork": [],
            "readme": [],
            "multirep": [],
        },
        "schema_version": "1.1.0",
        "generated_at": datetime.now(UTC).isoformat() + "Z",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(synthetic_report, f)
        report_path = f.name

    try:
        # Test flip manager with high violation count
        import subprocess

        result = subprocess.run(
            ["python3", "scripts/validator_flip_manager.py", report_path, "--dry-run"], capture_output=True, text=True
        )

        # Should detect high violation count and suggest rollback
        if "rollback" in result.stdout.lower() or "high" in result.stdout.lower():
            print("✅ Rollback scenario correctly detected")
            return True, "Rollback scenario correctly detected"
        else:
            print("❌ Rollback scenario not detected")
            return False, "Rollback scenario not detected"

    except Exception as e:
        return False, f"Rollback test failed: {e}"
    finally:
        os.unlink(report_path)


def test_schema_guard() -> tuple[bool, str]:
    """Test schema guard with invalid schema version."""
    print("🧪 Testing Schema Guard...")

    # Create synthetic report with wrong schema version
    synthetic_report = {
        "categories": {
            "archive": {"violations": 0, "fail": True},
            "shadow_fork": {"violations": 0, "fail": True},
            "readme": {"violations": 0, "fail": True},
            "multirep": {"violations": 0, "fail": True},
        },
        "impacted_files": {"archive": [], "shadow_fork": [], "readme": [], "multirep": []},
        "schema_version": "2.0.0",  # Wrong version
        "generated_at": datetime.now(UTC).isoformat() + "Z",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(synthetic_report, f)
        report_path = f.name

    try:
        # Test schema guard
        import subprocess

        result = subprocess.run(
            ["python3", "scripts/validator_schema_guard.py", "--report", report_path], capture_output=True, text=True
        )

        # Schema guard should fail with wrong version
        if result.returncode != 0:
            print("✅ Schema guard correctly failed with wrong version")
            return True, "Schema guard correctly blocked wrong version"
        else:
            print("❌ Schema guard should have failed with wrong version")
            return False, "Schema guard did not block wrong version"

    except Exception as e:
        return False, f"Schema guard test failed: {e}"
    finally:
        os.unlink(report_path)


def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Test validator chaos scenarios")
    parser.add_argument("--confirm", action="store_true", help="Actually make changes (default: dry-run)")
    parser.add_argument(
        "--scenario",
        choices=["all", "ratchet", "fail", "rollback", "schema"],
        default="all",
        help="Test scenario to run",
    )

    args = parser.parse_args()

    print("🎭 Validator Chaos Test")
    print(f"Mode: {'DRY-RUN' if not args.confirm else 'LIVE'}")
    print(f"Scenario: {args.scenario}")
    print()

    results = []

    # Run selected scenarios
    if args.scenario in ["all", "ratchet"]:
        success, message = test_ratchet_scenario()
        results.append(("Ratchet", success, message))

    if args.scenario in ["all", "fail"]:
        success, message = test_fail_mode_scenario()
        results.append(("FAIL Mode", success, message))

    if args.scenario in ["all", "rollback"]:
        success, message = test_rollback_scenario()
        results.append(("Rollback", success, message))

    if args.scenario in ["all", "schema"]:
        success, message = test_schema_guard()
        results.append(("Schema Guard", success, message))

    # Print results
    print("\n📊 Test Results")
    print("| Scenario | Status | Message |")
    print("|----------|--------|---------|")

    all_passed = True
    for scenario, success, message in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"| {scenario} | {status} | {message} |")
        if not success:
            all_passed = False

    print()
    if all_passed:
        print("🎉 All chaos tests passed!")
        return 0
    else:
        print("💥 Some chaos tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
