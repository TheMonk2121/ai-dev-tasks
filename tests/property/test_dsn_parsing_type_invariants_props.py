from __future__ import annotations

import json
from typing import Any, Optional, Union
from urllib.parse import urlparse

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.common.db_dsn import _parse  # type: ignore[import]

from ._regression_capture import record_case

# Type alias for the _parse function return type
DSNParseResult = dict[str, str | int]


# Type cast function to help type checker
def parse_dsn(dsn: str) -> DSNParseResult:
    """Type-safe wrapper for _parse function."""
    return _parse(dsn)  # type: ignore[return-value]


@pytest.mark.prop
class TestDSNParsingTypeInvariants:
    """Property-based tests for DSN parsing type invariants."""

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
            st.just("postgresql://user:pass@host/db"),
            st.just("postgresql://user@host/db"),
            st.just("postgresql://host"),
            st.just("postgresql://"),
            st.just(""),
            st.text(min_size=1, max_size=200),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_returns_dict_with_string_values(self, dsn: str) -> None:
        """Test that _parse returns a dict with string values for valid DSNs."""
        try:
            result = parse_dsn(dsn)

            # Check that result is a dictionary
            assert isinstance(result, dict)

            # Check that all values are strings (except port which is int)
            for key, value in result.items():
                assert isinstance(key, str)
                if key == "port":
                    assert isinstance(value, int)
                else:
                    assert isinstance(value, str)

            # Check that all expected keys are present
            expected_keys = {"scheme", "user", "host", "port", "db"}
            for key in expected_keys:
                assert key in result

        except Exception as e:
            record_case(
                "dsn_parse_returns_dict_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_preserves_scheme_user_host_db(self, dsn: str) -> None:
        """Test that _parse preserves scheme, user, host, and db components."""
        try:
            result = parse_dsn(dsn)

            # Parse with urlparse for comparison
            parsed = urlparse(dsn)

            # Check that scheme is preserved
            assert result["scheme"] == parsed.scheme

            # Check that user is preserved (or empty string if None)
            expected_user = parsed.username or ""
            assert result["user"] == expected_user

            # Check that host is preserved (or empty string if None)
            expected_host = parsed.hostname or ""
            assert result["host"] == expected_host

            # Check that db is preserved (path without leading slash)
            expected_db = (parsed.path or "").lstrip("/")
            assert result["db"] == expected_db

        except Exception as e:
            record_case(
                "dsn_parse_preserves_components_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_port_is_integer_string(self, dsn: str) -> None:
        """Test that _parse returns port as integer string."""
        try:
            result = parse_dsn(dsn)

            # Check that port is an integer
            assert isinstance(result["port"], int)
            assert result["port"] > 0

        except Exception as e:
            record_case(
                "dsn_parse_port_is_integer_string_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_handles_missing_components_gracefully(self, dsn: str) -> None:
        """Test that _parse handles missing components gracefully."""
        try:
            result = parse_dsn(dsn)

            # Check that all expected keys are present
            expected_keys = {"scheme", "user", "host", "port", "db"}
            for key in expected_keys:
                assert key in result

            # Check that missing components are empty strings
            parsed = urlparse(dsn)

            if not parsed.username:
                assert result["user"] == ""
            if not parsed.hostname:
                assert result["host"] == ""
            if not parsed.path:
                assert result["db"] == ""

        except Exception as e:
            record_case(
                "dsn_parse_handles_missing_components_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("invalid://dsn"),
            st.just("not-a-url"),
            st.just("postgresql://"),
            st.just(""),
            st.text(min_size=1, max_size=50),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_handles_invalid_dsns_gracefully(self, dsn: str) -> None:
        """Test that _parse handles invalid DSNs gracefully."""
        try:
            result = parse_dsn(dsn)

            # Should return a dictionary even for invalid DSNs
            assert isinstance(result, dict)

            # Should have all expected keys
            expected_keys = {"scheme", "user", "host", "port", "db"}
            for key in expected_keys:
                assert key in result

            # All values should be strings (except port which is int)
            for key, value in result.items():
                assert isinstance(key, str)
                if key == "port":
                    assert isinstance(value, int)
                else:
                    assert isinstance(value, str)

        except Exception as e:
            record_case(
                "dsn_parse_handles_invalid_dsns_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_result_is_json_serializable(self, dsn: str) -> None:
        """Test that _parse result is JSON serializable."""
        try:
            result = parse_dsn(dsn)

            # Should be able to serialize to JSON
            json_str = json.dumps(result)
            assert isinstance(json_str, str)

            # Should be able to deserialize back
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)
            assert deserialized == result

        except Exception as e:
            record_case(
                "dsn_parse_result_json_serializable_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise

    @given(
        dsn=st.one_of(
            st.just("postgresql://user:pass@host:5432/db"),
            st.just("postgresql://user@host:5432/db"),
            st.just("postgresql://host:5432/db"),
            st.just("postgresql://host/db"),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_dsn_parse_is_deterministic(self, dsn: str) -> None:
        """Test that _parse is deterministic for the same input."""
        try:
            result1 = parse_dsn(dsn)
            result2 = parse_dsn(dsn)

            # Results should be identical
            assert result1 == result2

            # All values should be the same
            for key in result1:
                assert result1[key] == result2[key]

        except Exception as e:
            record_case(
                "dsn_parse_is_deterministic_failed",
                {
                    "dsn": dsn,
                    "error": str(e),
                },
            )
            raise
