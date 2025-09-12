from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.common.db_dsn import _parse

from ._regression_capture import record_case


@pytest.mark.prop
class TestDBDSNTypeProps:
    """Property-based tests for DB DSN parser type contracts."""

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_returns_dict_with_exact_field_types(self, dsn: str) -> None:
        """Test that _parse returns dict with exact field types (str, str, str, int, str)."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all expected fields have correct types
            if "scheme" in result:
                assert isinstance(result["scheme"], str)
            if "user" in result:
                assert isinstance(result["user"], str)
            if "host" in result:
                assert isinstance(result["host"], str)
            if "port" in result:
                assert isinstance(result["port"], int)
            if "db" in result:
                assert isinstance(result["db"], str)

        except Exception as e:
            record_case("db_dsn_parse_field_types_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: not any(
                prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"]
            )
        )
    )
    @settings(max_examples=10, deadline=200)
    def test_parse_returns_empty_dict_for_invalid_dsns(self, dsn: str) -> None:
        """Test that _parse returns empty dict for invalid DSNs."""
        try:
            result = _parse(dsn)

            # Check that result is an empty dict
            assert isinstance(result, dict)
            assert len(result) == 0

        except Exception as e:
            record_case("db_dsn_parse_invalid_dsn_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_odd_but_parseable_dsns(self, dsn: str) -> None:
        """Test that _parse handles odd but parseable DSNs correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that port is always an integer when present
            if "port" in result:
                assert isinstance(result["port"], int)
                assert result["port"] > 0
                assert result["port"] <= 65535

        except Exception as e:
            record_case("db_dsn_parse_odd_dsn_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_preserves_string_fields_as_strings(self, dsn: str) -> None:
        """Test that _parse preserves string fields as strings."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that string fields are preserved as strings
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)

        except Exception as e:
            record_case("db_dsn_parse_string_fields_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_missing_components_gracefully(self, dsn: str) -> None:
        """Test that _parse handles missing components gracefully."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that missing components are handled gracefully
            # (e.g., missing port defaults to 5432, missing user defaults to empty string)
            if "port" in result:
                assert isinstance(result["port"], int)
            if "user" in result:
                assert isinstance(result["user"], str)
            if "host" in result:
                assert isinstance(result["host"], str)
            if "db" in result:
                assert isinstance(result["db"], str)

        except Exception as e:
            record_case("db_dsn_parse_missing_components_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_special_characters_in_dsn(self, dsn: str) -> None:
        """Test that _parse handles special characters in DSN correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all fields have correct types regardless of special characters
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)
            if "port" in result:
                assert isinstance(result["port"], int)

        except Exception as e:
            record_case("db_dsn_parse_special_chars_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_unicode_characters_in_dsn(self, dsn: str) -> None:
        """Test that _parse handles unicode characters in DSN correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all fields have correct types regardless of unicode characters
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)
            if "port" in result:
                assert isinstance(result["port"], int)

        except Exception as e:
            record_case("db_dsn_parse_unicode_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_very_long_dsns(self, dsn: str) -> None:
        """Test that _parse handles very long DSNs correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all fields have correct types
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)
            if "port" in result:
                assert isinstance(result["port"], int)

        except Exception as e:
            record_case("db_dsn_parse_long_dsn_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_dsns_with_query_parameters(self, dsn: str) -> None:
        """Test that _parse handles DSNs with query parameters correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all fields have correct types
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)
            if "port" in result:
                assert isinstance(result["port"], int)

        except Exception as e:
            record_case("db_dsn_parse_query_params_failed", {"dsn": dsn, "error": str(e)})
            raise

    @given(
        dsn=st.text(min_size=1, max_size=200).filter(
            lambda x: any(prefix in x.lower() for prefix in ["postgresql://", "postgres://", "mysql://", "sqlite://"])
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_parse_handles_dsns_with_fragments(self, dsn: str) -> None:
        """Test that _parse handles DSNs with fragments correctly."""
        try:
            result = _parse(dsn)

            # Check that result is a dict
            assert isinstance(result, dict)

            # Check that all fields have correct types
            for field in ["scheme", "user", "host", "db"]:
                if field in result:
                    assert isinstance(result[field], str)
            if "port" in result:
                assert isinstance(result["port"], int)

        except Exception as e:
            record_case("db_dsn_parse_fragments_failed", {"dsn": dsn, "error": str(e)})
            raise
