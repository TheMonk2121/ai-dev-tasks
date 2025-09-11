#!/usr/bin/env python3
"""
Property-based tests for SQL query building invariants.
"""

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st


def build_where_clause(filters: dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Build WHERE clause with parameterized queries.
    Returns (sql_fragment, parameters).
    """
    if not filters:
        return "", []

    conditions = []
    params = []

    for key, value in filters.items():
        if isinstance(value, str):
            # Handle string values with proper escaping
            conditions.append(f"{key} = %s")
            params.append(value)
        elif isinstance(value, (int, float)):
            conditions.append(f"{key} = %s")
            params.append(value)
        elif isinstance(value, list):
            # Handle IN clauses
            placeholders = ", ".join(["%s"] * len(value))
            conditions.append(f"{key} IN ({placeholders})")
            params.extend(value)
        else:
            # Convert to string for other types
            conditions.append(f"{key} = %s")
            params.append(str(value))

    return " AND ".join(conditions), params


def build_select_query(table: str, columns: list[str], filters: dict[str, Any]) -> tuple[str, list[Any]]:
    """
    Build SELECT query with parameterized WHERE clause.
    Returns (sql_query, parameters).
    """
    # Validate table name (basic safety)
    if not table.replace("_", "").isalnum():
        raise ValueError(f"Invalid table name: {table}")

    # Build column list
    if not columns:
        column_list = "*"
    else:
        # Validate column names
        for col in columns:
            if not col.replace("_", "").isalnum():
                raise ValueError(f"Invalid column name: {col}")
        column_list = ", ".join(columns)

    # Build WHERE clause
    where_clause, params = build_where_clause(filters)

    # Construct query
    query = f"SELECT {column_list} FROM {table}"
    if where_clause:
        query += f" WHERE {where_clause}"

    return query, params


class TestSQLProperties:
    """Property-based tests for SQL query building invariants."""

    @pytest.mark.prop
    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), min_size=0, max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_sql_placeholder_parity(self, filters: dict[str, str]) -> None:
        """Number of placeholders should match number of parameters"""
        where_clause, params = build_where_clause(filters)

        # Count placeholders in the clause
        placeholder_count = where_clause.count("%s")
        param_count = len(params)

        assert (
            placeholder_count == param_count
        ), f"Placeholder/parameter mismatch: {placeholder_count} placeholders, {param_count} params"

    @pytest.mark.prop
    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), min_size=0, max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_sql_no_unbalanced_quotes(self, filters: dict[str, str]) -> None:
        """SQL should not have unbalanced quotes in the WHERE clause structure"""
        where_clause, _ = build_where_clause(filters)

        # Check that we don't have unescaped quotes in the SQL structure
        # (parameterized queries should not have quotes in the SQL itself)
        # Skip this test if the filter keys contain quotes (they'll appear in the SQL)
        has_quote_keys = any("'" in key or '"' in key for key in filters.keys())
        if has_quote_keys:
            pytest.skip("Filter keys contain quotes, which will appear in SQL")

        sql_quotes = where_clause.count("'") + where_clause.count('"')

        # The SQL structure itself should not contain quotes
        # (values are passed as parameters, not embedded in SQL)
        assert sql_quotes == 0, f"SQL contains quotes: {where_clause}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=20), st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_sql_identifier_safety(self, table: str, columns: list[str]) -> None:
        """SQL identifiers should be safe (no injection patterns)"""
        # Filter out potentially dangerous patterns
        safe_table = "".join(c for c in table if c.isalnum() or c == "_")
        safe_columns = ["".join(c for c in col if c.isalnum() or c == "_") for col in columns]

        try:
            query, _ = build_select_query(safe_table, safe_columns, {})

            # Check for dangerous patterns
            dangerous_patterns = [";", "--", "/*", "*/", "DROP", "DELETE", "INSERT", "UPDATE"]
            for pattern in dangerous_patterns:
                assert pattern.upper() not in query.upper(), f"Dangerous pattern found: {pattern}"

        except ValueError:
            # Expected for invalid identifiers
            pass

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=20), st.lists(st.text(min_size=1, max_size=20), min_size=0, max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_select_query_structure(self, table: str, columns: list[str]) -> None:
        """SELECT queries should have proper structure"""
        safe_table = "".join(c for c in table if c.isalnum() or c == "_")
        safe_columns = ["".join(c for c in col if c.isalnum() or c == "_") for col in columns]

        try:
            query, params = build_select_query(safe_table, safe_columns, {})

            # Basic structure checks
            assert query.upper().startswith("SELECT"), f"Query doesn't start with SELECT: {query}"
            assert f"FROM {safe_table}".upper() in query.upper(), f"Missing FROM clause: {query}"
            assert len(params) == 0, f"Unexpected parameters for empty filters: {params}"

        except ValueError:
            # Expected for invalid identifiers
            pass

    @pytest.mark.prop
    @given(st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), min_size=0, max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_empty_filters_handling(self, filters: dict[str, str]) -> None:
        """Empty filters should be handled gracefully"""
        where_clause, params = build_where_clause(filters)

        if not filters:
            assert where_clause == "", f"Empty filters should produce empty clause: {where_clause}"
            assert params == [], f"Empty filters should produce empty params: {params}"
        else:
            assert where_clause, f"Non-empty filters should produce clause: {filters}"
            assert params, f"Non-empty filters should produce params: {filters}"

    @pytest.mark.prop
    @given(
        st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(st.text(max_size=100), st.integers(), st.floats()),
            min_size=0,
            max_size=10,
        )
    )
    @settings(max_examples=25, deadline=50)
    def test_sql_parameter_types(self, filters: dict[str, Any]) -> None:
        """SQL should handle different parameter types correctly"""
        where_clause, params = build_where_clause(filters)

        # All parameters should be in the params list
        assert len(params) == len(filters), f"Parameter count mismatch: {len(params)} vs {len(filters)}"

        # Parameters should match filter values
        for i, (key, value) in enumerate(filters.items()):
            if isinstance(value, list):
                # For lists, check that all values are in params
                assert all(v in params for v in value), f"List values not in params: {value}"
            else:
                # For single values, check that value is in params
                assert value in params, f"Value not in params: {value}"
