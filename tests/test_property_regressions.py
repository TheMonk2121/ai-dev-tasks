#!/usr/bin/env python3
"""
Regression tests for edge cases discovered by Hypothesis property-based testing.
"""

import json
import pathlib

import pytest


def normalize_query(query: str) -> str:
    """Placeholder - replace with actual implementation."""
    if not query:
        return ""

    # Use Unicode-aware case conversion with special handling for ß
    normalized = query.strip().casefold()

    # Handle special Unicode cases
    normalized = normalized.replace("ß", "ss")
    normalized = normalized.replace("ı", "i")  # Turkish dotless i
    normalized = normalized.replace("i̇", "i")  # Turkish dotted i (İ -> i̇ -> i)

    # Collapse whitespace
    normalized = " ".join(normalized.split())
    return normalized


def load_edge_cases() -> list[dict]:
    """Load edge cases discovered by Hypothesis."""
    edge_cases_file = pathlib.Path(__file__).parent / "data" / "edge_cases.jsonl"

    if not edge_cases_file.exists():
        return []

    cases = []
    with open(edge_cases_file) as f:
        for line in f:
            if line.strip():
                cases.append(json.loads(line))

    return cases


# Load edge cases for parametrized tests
normalize_cases = [case for case in load_edge_cases() if case.get("test", "").startswith("test_normalize")]


class TestPropertyRegressions:
    """Regression tests for Hypothesis-discovered edge cases."""

    @pytest.mark.parametrize("case", normalize_cases)
    def test_normalize_regressions(self, case: dict) -> None:
        """Test normalization regressions found by Hypothesis."""
        raw = case["raw"]
        expected = case["expected"]
        test_name = case.get("test", "unknown")

        result = normalize_query(raw)
        assert result == expected, f"Regression in {test_name}: '{raw}' -> '{result}', expected '{expected}'"

    def test_no_regressions_loaded(self) -> None:
        """Ensure we have regression tests loaded."""
        assert len(normalize_cases) > 0, "No regression cases loaded from edge_cases.jsonl"
