#!/usr/bin/env python3
"""
Regression tests for property-based test findings.
Loads edge cases discovered by Hypothesis and runs them as fast param tests.
"""

import json
import pathlib
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import your actual functions here
# from src.dspy_modules.enhanced_rag_system import normalize_query


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
    for line in edge_cases_file.read_text().strip().splitlines():
        if line.strip():
            try:
                cases.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    return cases


# Load edge cases for parametrized testing
edge_cases = load_edge_cases()

# Filter cases by test type for better organization
normalize_cases = [c for c in edge_cases if c.get("test", "").startswith("test_normalize")]
vector_cases = [c for c in edge_cases if c.get("test", "").startswith("test_vector")]
sql_cases = [c for c in edge_cases if c.get("test", "").startswith("test_sql")]


class TestPropertyRegressions:
    """Fast regression tests for property-based findings."""

    @pytest.mark.parametrize("case", normalize_cases)
    def test_normalize_regressions(self, case: dict) -> None:
        """Test normalization regressions found by Hypothesis."""
        raw = case["raw"]
        expected = case["expected"]
        test_name = case.get("test", "unknown")

        result = normalize_query(raw)
        assert result == expected, f"Regression in {test_name}: '{raw}' -> '{result}', expected '{expected}'"

    @pytest.mark.parametrize("case", vector_cases)
    def test_vector_regressions(self, case: dict) -> None:
        """Test vector operation regressions found by Hypothesis."""
        # TODO: Implement when we have actual vector functions
        pytest.skip("Vector regression tests not yet implemented")

    @pytest.mark.parametrize("case", sql_cases)
    def test_sql_regressions(self, case: dict) -> None:
        """Test SQL operation regressions found by Hypothesis."""
        # TODO: Implement when we have actual SQL functions
        pytest.skip("SQL regression tests not yet implemented")


if __name__ == "__main__":
    pytest.main([__file__])
