#!/usr/bin/env python3
"""
Capture Hypothesis findings and promote them to fast regression tests.
"""

import json
import pathlib
import subprocess
import sys
from datetime import datetime


def capture_hypothesis_findings():
    """Capture current Hypothesis findings and save them to edge_cases.jsonl."""
    edge_cases_file = pathlib.Path(__file__).parent.parent / "tests" / "data" / "edge_cases.jsonl"

    # Ensure the directory exists
    edge_cases_file.parent.mkdir(parents=True, exist_ok=True)

    # Run property tests and capture failures
    try:
        result = subprocess.run(
            [
                "uv",
                "run",
                "python",
                "-m",
                "pytest",
                "tests/property/",
                "-m",
                "prop",
                "--tb=short",
                "--maxfail=10",
                "-q",
            ],
            capture_output=True,
            text=True,
            cwd=pathlib.Path(__file__).parent.parent,
        )

        # Parse the output for failing examples
        findings = []

        if result.returncode != 0:
            # Extract failing examples from the output
            lines = result.stdout.split("\n")
            current_test = None
            current_example = None

            for line in lines:
                if "Falsifying example:" in line:
                    # Extract test name and example
                    parts = line.split("Falsifying example:")
                    if len(parts) > 1:
                        test_part = parts[0].strip()
                        example_part = parts[1].strip()

                        # Extract test name
                        if "::" in test_part:
                            test_name = test_part.split("::")[-1].strip()
                        else:
                            test_name = "unknown"

                        # Extract example parameters
                        if "(" in example_part and ")" in example_part:
                            # Simple extraction - look for string literals
                            if "'" in example_part:
                                start = example_part.find("'")
                                end = example_part.rfind("'")
                                if start != -1 and end != -1 and end > start:
                                    example_value = example_part[start + 1 : end]

                                    finding = {
                                        "raw": example_value,
                                        "expected": "normalized_value",  # Will be filled in later
                                        "test": test_name,
                                        "timestamp": datetime.now().isoformat(),
                                        "type": "unicode_case_issue",
                                    }
                                    findings.append(finding)

        # Add the specific ß case we found
        findings.append(
            {
                "raw": "ß",
                "expected": "ss",  # Should normalize to consistent value
                "test": "test_normalize_case_invariant",
                "timestamp": datetime.now().isoformat(),
                "type": "unicode_case_issue",
            }
        )

        # Append findings to edge_cases.jsonl
        with open(edge_cases_file, "a") as f:
            for finding in findings:
                f.write(json.dumps(finding) + "\n")

        print(f"✅ Captured {len(findings)} Hypothesis findings to {edge_cases_file}")
        return findings

    except Exception as e:
        print(f"❌ Error capturing findings: {e}")
        return []


if __name__ == "__main__":
    findings = capture_hypothesis_findings()
    print(f"Found {len(findings)} edge cases")
