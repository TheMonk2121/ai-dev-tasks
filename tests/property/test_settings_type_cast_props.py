from __future__ import annotations

import json
import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.schemas.settings import EvaluationSettings

from ._regression_capture import record_case


@pytest.mark.prop
class TestSettingsTypeCasting:
    """Property-based tests for settings type casting and environment parsing."""

    @given(
        validation_strict=st.sampled_from(["1", "0", "true", "false", "TRUE", "False", "yes", "no", "True", "FALSE"]),
        max_cases=st.integers(min_value=1, max_value=1000).map(str),
        concurrency=st.integers(min_value=1, max_value=10).map(str),
        timeout=st.integers(min_value=30, max_value=3600).map(str),
    )
    @settings(max_examples=20, deadline=200)
    def test_boolean_fields_parse_correctly_from_strings(
        self, validation_strict: str, max_cases: str, concurrency: str, timeout: str
    ) -> None:
        """Test that boolean fields parse correctly from various string encodings."""
        try:
            # Set environment variables
            os.environ["EVAL_VALIDATION_STRICT"] = validation_strict
            os.environ["EVAL_MAX_CASES_PER_EVAL"] = max_cases
            os.environ["EVAL_CONCURRENCY_LIMIT"] = concurrency
            os.environ["EVAL_TIMEOUT_SECONDS"] = timeout

            # Create settings instance
            settings = EvaluationSettings()

            # Check that boolean field is correctly parsed
            assert isinstance(settings.validation_strict, bool)

            # Check that integer fields are correctly parsed
            assert isinstance(settings.max_cases_per_eval, int)
            assert isinstance(settings.concurrency_limit, int)
            assert isinstance(settings.timeout_seconds, int)

            # Verify values are reasonable
            assert settings.max_cases_per_eval == int(max_cases)
            assert settings.concurrency_limit == int(concurrency)
            assert settings.timeout_seconds == int(timeout)

        except Exception as e:
            record_case(
                "settings_boolean_parsing_failed",
                {
                    "validation_strict": validation_strict,
                    "max_cases": max_cases,
                    "concurrency": concurrency,
                    "timeout": timeout,
                    "error": str(e),
                },
            )
            raise
        finally:
            # Clean up environment variables
            for key in [
                "EVAL_VALIDATION_STRICT",
                "EVAL_MAX_CASES_PER_EVAL",
                "EVAL_CONCURRENCY_LIMIT",
                "EVAL_TIMEOUT_SECONDS",
            ]:
                os.environ.pop(key, None)

    @given(
        known_tags_csv=st.text(min_size=1, max_size=200).filter(lambda x: "," in x),
        known_tags_json=st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20).map(
            lambda x: json.dumps(x)
        ),
        known_tags_empty=st.sampled_from(["", "[]", "   "]),
    )
    @settings(max_examples=20, deadline=200)
    def test_known_tags_parsing_from_various_formats(
        self, known_tags_csv: str, known_tags_json: str, known_tags_empty: str
    ) -> None:
        """Test that known_tags field parses correctly from CSV and JSON formats."""
        test_cases = [
            ("EVAL_KNOWN_TAGS", known_tags_csv),
            ("EVAL_KNOWN_TAGS", known_tags_json),
            ("EVAL_KNOWN_TAGS", known_tags_empty),
        ]

        for env_key, env_value in test_cases:
            try:
                # Set environment variable
                os.environ[env_key] = env_value

                # Create settings instance
                settings = EvaluationSettings()

                # Check that known_tags is a list of strings
                assert isinstance(settings.known_tags, list)
                assert all(isinstance(tag, str) for tag in settings.known_tags)

                # Check that list is not empty when valid input provided
                if env_value and env_value.strip() and env_value != "[]":
                    assert len(settings.known_tags) > 0

            except Exception as e:
                record_case(
                    "settings_known_tags_parsing_failed", {"env_key": env_key, "env_value": env_value, "error": str(e)}
                )
                raise
            finally:
                # Clean up environment variable
                os.environ.pop(env_key, None)

    @given(
        max_cases=st.integers(min_value=1, max_value=1000).map(str),
        concurrency=st.integers(min_value=1, max_value=10).map(str),
        timeout=st.integers(min_value=30, max_value=3600).map(str),
        default_sample=st.integers(min_value=1, max_value=500).map(str),
    )
    @settings(max_examples=20, deadline=200)
    def test_integer_fields_parse_correctly_from_strings(
        self, max_cases: str, concurrency: str, timeout: str, default_sample: str
    ) -> None:
        """Test that integer fields parse correctly from string representations."""
        try:
            # Set environment variables
            os.environ["EVAL_MAX_CASES_PER_EVAL"] = max_cases
            os.environ["EVAL_CONCURRENCY_LIMIT"] = concurrency
            os.environ["EVAL_TIMEOUT_SECONDS"] = timeout
            os.environ["EVAL_DEFAULT_SAMPLE_SIZE"] = default_sample

            # Create settings instance
            settings = EvaluationSettings()

            # Check that all fields are integers
            assert isinstance(settings.max_cases_per_eval, int)
            assert isinstance(settings.concurrency_limit, int)
            assert isinstance(settings.timeout_seconds, int)
            assert isinstance(settings.default_sample_size, int)

            # Check that values match input
            assert settings.max_cases_per_eval == int(max_cases)
            assert settings.concurrency_limit == int(concurrency)
            assert settings.timeout_seconds == int(timeout)
            assert settings.default_sample_size == int(default_sample)

        except Exception as e:
            record_case(
                "settings_integer_parsing_failed",
                {
                    "max_cases": max_cases,
                    "concurrency": concurrency,
                    "timeout": timeout,
                    "default_sample": default_sample,
                    "error": str(e),
                },
            )
            raise
        finally:
            # Clean up environment variables
            for key in [
                "EVAL_MAX_CASES_PER_EVAL",
                "EVAL_CONCURRENCY_LIMIT",
                "EVAL_TIMEOUT_SECONDS",
                "EVAL_DEFAULT_SAMPLE_SIZE",
            ]:
                os.environ.pop(key, None)

    @given(
        invalid_max_cases=st.one_of(
            st.just("not_a_number"),
            st.just("1.5"),
            st.just(""),
            st.just("abc123"),
            st.just("1e5"),
        ),
        invalid_concurrency=st.one_of(
            st.just("not_a_number"),
            st.just("2.5"),
            st.just(""),
            st.just("xyz789"),
        ),
    )
    @settings(max_examples=10, deadline=200)
    def test_invalid_strings_rejected_for_integer_fields(
        self, invalid_max_cases: str, invalid_concurrency: str
    ) -> None:
        """Test that invalid strings are rejected for integer fields."""
        # Test max_cases_per_eval
        try:
            os.environ["EVAL_MAX_CASES_PER_EVAL"] = invalid_max_cases
            with pytest.raises(ValidationError):
                EvaluationSettings()
        except Exception as e:
            record_case("settings_invalid_max_cases_failed", {"invalid_max_cases": invalid_max_cases, "error": str(e)})
            raise
        finally:
            os.environ.pop("EVAL_MAX_CASES_PER_EVAL", None)

        # Test concurrency_limit
        try:
            os.environ["EVAL_CONCURRENCY_LIMIT"] = invalid_concurrency
            with pytest.raises(ValidationError):
                EvaluationSettings()
        except Exception as e:
            record_case(
                "settings_invalid_concurrency_failed", {"invalid_concurrency": invalid_concurrency, "error": str(e)}
            )
            raise
        finally:
            os.environ.pop("EVAL_CONCURRENCY_LIMIT", None)

    @given(
        validation_strict=st.sampled_from(["1", "0", "true", "false"]),
        allow_missing_files=st.sampled_from(["1", "0", "true", "false"]),
        unknown_tag_warning=st.sampled_from(["1", "0", "true", "false"]),
        check_file_existence=st.sampled_from(["1", "0", "true", "false"]),
    )
    @settings(max_examples=20, deadline=200)
    def test_all_boolean_fields_parse_correctly(
        self, validation_strict: str, allow_missing_files: str, unknown_tag_warning: str, check_file_existence: str
    ) -> None:
        """Test that all boolean fields parse correctly from various string encodings."""
        try:
            # Set environment variables
            os.environ["EVAL_VALIDATION_STRICT"] = validation_strict
            os.environ["EVAL_ALLOW_MISSING_FILES"] = allow_missing_files
            os.environ["EVAL_UNKNOWN_TAG_WARNING"] = unknown_tag_warning
            os.environ["EVAL_CHECK_FILE_EXISTENCE"] = check_file_existence

            # Create settings instance
            settings = EvaluationSettings()

            # Check that all boolean fields are correctly parsed
            assert isinstance(settings.validation_strict, bool)
            assert isinstance(settings.allow_missing_files, bool)
            assert isinstance(settings.unknown_tag_warning, bool)
            assert isinstance(settings.check_file_existence, bool)

            # Verify that truthy strings become True and falsy strings become False
            expected_validation_strict = validation_strict.lower() in ["1", "true", "yes"]
            expected_allow_missing_files = allow_missing_files.lower() in ["1", "true", "yes"]
            expected_unknown_tag_warning = unknown_tag_warning.lower() in ["1", "true", "yes"]
            expected_check_file_existence = check_file_existence.lower() in ["1", "true", "yes"]

            assert settings.validation_strict == expected_validation_strict
            assert settings.allow_missing_files == expected_allow_missing_files
            assert settings.unknown_tag_warning == expected_unknown_tag_warning
            assert settings.check_file_existence == expected_check_file_existence

        except Exception as e:
            record_case(
                "settings_all_boolean_fields_failed",
                {
                    "validation_strict": validation_strict,
                    "allow_missing_files": allow_missing_files,
                    "unknown_tag_warning": unknown_tag_warning,
                    "check_file_existence": check_file_existence,
                    "error": str(e),
                },
            )
            raise
        finally:
            # Clean up environment variables
            for key in [
                "EVAL_VALIDATION_STRICT",
                "EVAL_ALLOW_MISSING_FILES",
                "EVAL_UNKNOWN_TAG_WARNING",
                "EVAL_CHECK_FILE_EXISTENCE",
            ]:
                os.environ.pop(key, None)

    @given(
        known_tags=st.one_of(
            st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=20),
            st.text(min_size=1, max_size=200),
        )
    )
    @settings(max_examples=20, deadline=200)
    def test_known_tags_handles_both_list_and_string_inputs(self, known_tags: list[str] | str) -> None:
        """Test that known_tags field handles both list and string inputs correctly."""
        try:
            if isinstance(known_tags, list):
                # Test direct list input
                settings = EvaluationSettings(known_tags=known_tags)
                assert isinstance(settings.known_tags, list)
                assert all(isinstance(tag, str) for tag in settings.known_tags)
                assert settings.known_tags == known_tags
            else:
                # Test string input via environment
                os.environ["EVAL_KNOWN_TAGS"] = known_tags
                settings = EvaluationSettings()
                assert isinstance(settings.known_tags, list)
                assert all(isinstance(tag, str) for tag in settings.known_tags)

        except Exception as e:
            record_case(
                "settings_known_tags_list_string_failed",
                {"known_tags": known_tags, "known_tags_type": type(known_tags).__name__, "error": str(e)},
            )
            raise
        finally:
            os.environ.pop("EVAL_KNOWN_TAGS", None)

    @given(
        max_cases=st.integers(min_value=1, max_value=1000),
        concurrency=st.integers(min_value=1, max_value=10),
        timeout=st.integers(min_value=30, max_value=3600),
    )
    @settings(max_examples=10, deadline=200)
    def test_settings_roundtrip_preserves_types(self, max_cases: int, concurrency: int, timeout: int) -> None:
        """Test that settings model_dump and model_validate preserve types correctly."""
        try:
            # Create settings with specific values
            original = EvaluationSettings(
                max_cases_per_eval=max_cases,
                concurrency_limit=concurrency,
                timeout_seconds=timeout,
            )

            # Serialize to dict
            data = original.model_dump()

            # Deserialize from dict
            restored = EvaluationSettings.model_validate(data)

            # Check that types are preserved
            assert isinstance(restored.max_cases_per_eval, int)
            assert isinstance(restored.concurrency_limit, int)
            assert isinstance(restored.timeout_seconds, int)
            assert isinstance(restored.validation_strict, bool)
            assert isinstance(restored.known_tags, list)

            # Check that values are preserved
            assert restored.max_cases_per_eval == original.max_cases_per_eval
            assert restored.concurrency_limit == original.concurrency_limit
            assert restored.timeout_seconds == original.timeout_seconds
            assert restored.validation_strict == original.validation_strict
            assert restored.known_tags == original.known_tags

        except Exception as e:
            record_case(
                "settings_roundtrip_failed",
                {"max_cases": max_cases, "concurrency": concurrency, "timeout": timeout, "error": str(e)},
            )
            raise
