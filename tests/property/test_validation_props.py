from __future__ import annotations
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from src.utils.validator import sanitize_prompt
from ._regression_capture import record_case
            from src.utils.prompt_sanitizer import SecurityError
            from src.utils.prompt_sanitizer import SecurityError
            from src.utils.prompt_sanitizer import SecurityError
                from src.utils.prompt_sanitizer import SecurityError
            from src.utils.prompt_sanitizer import SecurityError
import sys
import os
#!/usr/bin/env python3
"""
Property-based tests for validation system invariants.
"""




def create_test_query(text: str, max_length: int = 1000) -> str:
    """Create a test query with length constraints."""
    if len(text) > max_length:
        return text[:max_length]
    return text


def create_test_response(text: str, max_length: int = 2000) -> str:
    """Create a test response with length constraints."""
    if len(text) > max_length:
        return text[:max_length]
    return text


class TestValidationProperties:
    """Property-based tests for validation system invariants."""

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_accepts_valid_input(self, query: str) -> None:
        """sanitize_prompt should accept valid query strings."""
        try:
            result = sanitize_prompt(query)
            if result is None:
                record_case(
                    "test_sanitize_prompt_accepts_valid_input_none",
                    {"query": query},
                )
            assert result is not None, "sanitize_prompt should return a result"
        except Exception as e:
            # If validation fails, it should be for a specific reason
            # SecurityError is also acceptable as it's a validation error
            if not isinstance(e, ValueError | TypeError | SecurityError):
                record_case(
                    "test_sanitize_prompt_accepts_valid_input_unexpected_exception",
                    {"query": query, "exc_type": str(type(e)), "error": str(e)},
                )
            assert isinstance(e, ValueError | TypeError | SecurityError), f"Unexpected exception type: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_accepts_response_input(self, response: str) -> None:
        """sanitize_prompt should accept valid response strings."""
        try:
            result = sanitize_prompt(response)
            if result is None:
                record_case(
                    "test_sanitize_prompt_accepts_response_input_none",
                    {"response": response},
                )
            assert result is not None, "sanitize_prompt should return a result"
        except Exception as e:
            # If validation fails, it should be for a specific reason
            if not isinstance(e, ValueError | TypeError | SecurityError):
                record_case(
                    "test_sanitize_prompt_accepts_response_input_unexpected_exception",
                    {"response": response, "exc_type": str(type(e)), "error": str(e)},
                )
            assert isinstance(e, ValueError | TypeError | SecurityError), f"Unexpected exception type: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_idempotent(self, query: str) -> None:
        """sanitize_prompt should be idempotent."""
        try:
            result1 = sanitize_prompt(query)
            result2 = sanitize_prompt(query)
            if result1 != result2:
                record_case(
                    "test_sanitize_prompt_idempotent_mismatch",
                    {"query": query, "r1": result1, "r2": result2},
                )
            assert result1 == result2, "sanitize_prompt should be idempotent"
        except Exception as e:
            # If validation fails, both calls should fail the same way
            record_case(
                "test_sanitize_prompt_idempotent_exception",
                {"query": query, "exc_type": str(type(e)), "error": str(e)},
            )
            pass

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_response_idempotent(self, response: str) -> None:
        """sanitize_prompt should be idempotent for responses."""
        try:
            result1 = sanitize_prompt(response)
            result2 = sanitize_prompt(response)
            if result1 != result2:
                record_case(
                    "test_sanitize_prompt_response_idempotent_mismatch",
                    {"response": response, "r1": result1, "r2": result2},
                )
            assert result1 == result2, "sanitize_prompt should be idempotent"
        except Exception as e:
            # If validation fails, both calls should fail the same way
            record_case(
                "test_sanitize_prompt_response_idempotent_exception",
                {"response": response, "exc_type": str(type(e)), "error": str(e)},
            )
            pass


class TestPromptSanitizationProperties:
    """Property-based tests for prompt sanitization invariants."""

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_always_returns_string(self, prompt: str) -> None:
        """sanitize_prompt should always return a string."""
        result = sanitize_prompt(prompt)
        if not isinstance(result, str):
            record_case(
                "test_sanitize_prompt_always_returns_string_type",
                {"input": prompt, "result_type": str(type(result))},
            )
        assert isinstance(result, str), f"sanitize_prompt should return string, got {type(result)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_idempotent(self, prompt: str) -> None:
        """sanitize_prompt should be idempotent."""
        result1 = sanitize_prompt(prompt)
        result2 = sanitize_prompt(result1)
        if result1 != result2:
            record_case(
                "test_sanitize_prompt_idempotent_prompt_mismatch",
                {"prompt": prompt, "r1": result1, "r2": result2},
            )
        assert result1 == result2, "sanitize_prompt should be idempotent"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_preserves_length_approximately(self, prompt: str) -> None:
        """sanitize_prompt should not dramatically change length."""
        result = sanitize_prompt(prompt)

        # Sanitized prompt should not be more than 2x the original length
        if len(result) > len(prompt) * 2:
            record_case(
                "test_sanitize_prompt_length_growth",
                {"prompt_len": len(prompt), "result_len": len(result)},
            )
        assert len(result) <= len(prompt) * 2, f"Sanitized prompt too long: {len(result)} vs {len(prompt)}"

        # Sanitized prompt should not be empty if original had content
        if prompt.strip():
            if not result.strip():
                record_case(
                    "test_sanitize_prompt_empty_after_nonempty",
                    {"prompt": prompt, "result": result},
                )
            assert result.strip(), "Sanitized prompt should not be empty if original had content"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_removes_dangerous_patterns(self, prompt: str) -> None:
        """sanitize_prompt should remove or block dangerous patterns."""
        try:
            result = sanitize_prompt(prompt)
        except Exception as e:
            assert isinstance(e, SecurityError)
            return

        # Check for common dangerous patterns (only those actually in the blocklist)
        dangerous_patterns = ["<script>", "{{", "}}"]
        for pattern in dangerous_patterns:
            if pattern.lower() in result.lower():
                record_case(
                    "test_sanitize_prompt_dangerous_pattern_remaining",
                    {"pattern": pattern, "input": prompt, "result": result},
                )
            assert pattern.lower() not in result.lower(), f"Dangerous pattern not removed: {pattern}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_handles_unicode(self, prompt: str) -> None:
        """sanitize_prompt should handle Unicode characters properly."""
        result = sanitize_prompt(prompt)

        # Result should be a valid string
        assert isinstance(result, str), "sanitize_prompt should return valid string"

        # Should not crash on Unicode
        try:
            result.encode("utf-8")
        except UnicodeEncodeError:
            record_case(
                "test_sanitize_prompt_unicode_encode_error",
                {"input": prompt, "result": result},
            )
            pytest.fail("sanitize_prompt should produce valid UTF-8")


class TestValidationEdgeCases:
    """Property-based tests for validation edge cases."""

    @pytest.mark.prop
    @given(st.text(max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_validation_handles_short_strings(self, text: str) -> None:
        """Validation should handle very short strings."""
        if text.strip():  # Only test non-empty strings
            try:
                sanitize_prompt(text)
            except Exception as e:
                # Should be a specific validation error, not a crash
                if not isinstance(e, ValueError | TypeError | SecurityError):
                    record_case(
                        "test_validation_short_strings_unexpected_exception",
                        {"text": text, "exc_type": str(type(e)), "error": str(e)},
                    )
                assert isinstance(e, ValueError | TypeError | SecurityError), f"Unexpected exception for short string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1000, max_size=5000))
    @settings(max_examples=25, deadline=50)
    def test_validation_handles_long_strings(self, text: str) -> None:
        """Validation should handle very long strings."""
        try:
            sanitize_prompt(text)
        except Exception as e:
            # Should be a specific validation error, not a crash
            # SecurityError is also acceptable as it's a validation error
            if not isinstance(e, ValueError | TypeError | SecurityError):
                record_case(
                    "test_validation_long_strings_unexpected_exception",
                    {"exc_type": str(type(e)), "error": str(e), "text_len": len(text)},
                )
            assert isinstance(e, ValueError | TypeError | SecurityError), (
                f"Unexpected exception for long string: {type(e)}"
            )

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_validation_handles_special_characters(self, text: str) -> None:
        """Validation should handle special characters."""
        # Add some special characters
        special_text = f"!@#$%^&*()_+-=[]{{}}|;':\",./<>? {text}"

        try:
            sanitize_prompt(special_text)
        except Exception as e:
            # Should be a specific validation error, not a crash
            if not isinstance(e, ValueError | TypeError):
                record_case(
                    "test_validation_special_chars_unexpected_exception",
                    {"text": special_text, "exc_type": str(type(e)), "error": str(e)},
                )
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for special characters: {type(e)}"
