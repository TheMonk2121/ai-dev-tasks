#!/usr/bin/env python3
"""
Property-based tests for SQL query building functions.
Surgical Hypothesis wedge - pure functions only, nightly runs.
"""

import sys
from pathlib import Path
from typing import Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


def build_where_clause(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Placeholder SQL WHERE clause builder.
    Replace with actual implementation.
    """
    if not filters:
        return "", []

    conditions = []
    params = []

    for key, value in filters.items():
        if value is None:
            conditions.append(f"{key} IS NULL")
        else:
            conditions.append(f"{key} = %s")
            params.append(value)

    where_clause = " AND ".join(conditions)
    return where_clause, params


def build_select_query(table: str, columns: list[str], filters: dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Placeholder SELECT query builder.
    Replace with actual implementation.
    """
    if not columns:
        columns = ["*"]

    select_clause = f"SELECT {', '.join(columns)} FROM {table}"
    where_clause, params = build_where_clause(filters)

    if where_clause:
        query = f"{select_clause} WHERE {where_clause}"
    else:
        query = select_clause

    return query, params


class TestSQLProperties:
    """Property-based tests for SQL query building invariants."""

    @pytest.mark.prop
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_sql_placeholder_parity(self, filters: dict[str, Any]) -> None:
        """Placeholder count should equal parameter count"""
        sql, params = build_where_clause(filters)

        placeholder_count = sql.count("%s")
        param_count = len(params)

        assert (
            placeholder_count == param_count
        ), f"Placeholder/param mismatch: {placeholder_count} placeholders, {param_count} params in '{sql}'"

    @pytest.mark.prop
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_sql_no_unbalanced_quotes(self, filters: dict[str, Any]) -> None:
        """SQL should not have unbalanced quotes"""
        sql, _ = build_where_clause(filters)

        single_quotes = sql.count("'")
        double_quotes = sql.count('"')

        assert single_quotes % 2 == 0, f"Unbalanced single quotes in SQL: '{sql}'"
        assert double_quotes % 2 == 0, f"Unbalanced double quotes in SQL: '{sql}'"

    @pytest.mark.prop
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_sql_identifier_safety(self, filters: dict[str, Any]) -> None:
        """SQL should only contain safe identifiers"""
        sql, _ = build_where_clause(filters)

        # Check for dangerous SQL injection patterns
        dangerous_patterns = ["--", "/*", "*/", "xp_", "sp_", "DROP", "DELETE", "INSERT", "UPDATE"]

        for pattern in dangerous_patterns:
            assert pattern.upper() not in sql.upper(), f"Dangerous pattern '{pattern}' found in SQL: '{sql}'"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=30).filter(str.isidentifier),
        st.lists(st.text(min_size=1, max_size=30).filter(str.isidentifier), min_size=1, max_size=10),
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        ),
    )
    @settings(max_examples=25, deadline=50)
    def test_select_query_structure(self, table: str, columns: list[str], filters: dict[str, Any]) -> None:
        """SELECT queries should have proper structure"""
        query, params = build_select_query(table, columns, filters)

        # Should start with SELECT
        assert query.upper().startswith("SELECT"), f"Query doesn't start with SELECT: '{query}'"

        # Should contain FROM
        assert "FROM" in query.upper(), f"Query missing FROM clause: '{query}'"

        # Should contain table name
        assert table.upper() in query.upper(), f"Query missing table name '{table}': '{query}'"

        # Placeholder/param parity
        placeholder_count = query.count("%s")
        param_count = len(params)
        assert (
            placeholder_count == param_count
        ), f"Placeholder/param mismatch: {placeholder_count} placeholders, {param_count} params"

    @pytest.mark.prop
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_empty_filters_handling(self, filters: dict[str, Any]) -> None:
        """Empty filters should produce empty WHERE clause"""
        if not filters:
            sql, params = build_where_clause(filters)
            assert sql == "", f"Empty filters should produce empty WHERE clause: '{sql}'"
            assert params == [], f"Empty filters should produce empty params: {params}"

    @pytest.mark.prop
    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=30).filter(str.isidentifier),
            values=st.one_of(st.integers(), st.text(max_size=100), st.none()),
            max_size=6,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_sql_parameter_types(self, filters: dict[str, Any]) -> None:
        """SQL parameters should match filter values"""
        sql, params = build_where_clause(filters)

        # Count non-NULL values in filters
        non_null_values = [v for v in filters.values() if v is not None]

        assert len(params) == len(
            non_null_values
        ), f"Param count mismatch: {len(params)} params, {len(non_null_values)} non-null values"

        # Check that params match non-null values
        for param in params:
            assert param in non_null_values, f"Param {param} not in filter values: {non_null_values}"
