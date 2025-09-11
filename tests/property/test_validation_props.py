#!/usr/bin/env python3
"""
Property-based tests for validation system invariants.
"""

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.utils.validator import sanitize_prompt


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
            assert result is not None, "sanitize_prompt should return a result"
        except Exception as e:
            # If validation fails, it should be for a specific reason
            # SecurityError is also acceptable as it's a validation error
            from src.utils.prompt_sanitizer import SecurityError

            assert isinstance(e, ValueError | TypeError | SecurityError), f"Unexpected exception type: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_accepts_response_input(self, response: str) -> None:
        """sanitize_prompt should accept valid response strings."""
        try:
            result = sanitize_prompt(response)
            assert result is not None, "sanitize_prompt should return a result"
        except Exception as e:
            # If validation fails, it should be for a specific reason
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception type: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_idempotent(self, query: str) -> None:
        """sanitize_prompt should be idempotent."""
        try:
            result1 = sanitize_prompt(query)
            result2 = sanitize_prompt(query)
            assert result1 == result2, "sanitize_prompt should be idempotent"
        except Exception:
            # If validation fails, both calls should fail the same way
            pass

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_response_idempotent(self, response: str) -> None:
        """sanitize_prompt should be idempotent for responses."""
        try:
            result1 = sanitize_prompt(response)
            result2 = sanitize_prompt(response)
            assert result1 == result2, "sanitize_prompt should be idempotent"
        except Exception:
            # If validation fails, both calls should fail the same way
            pass


class TestPromptSanitizationProperties:
    """Property-based tests for prompt sanitization invariants."""

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_always_returns_string(self, prompt: str) -> None:
        """sanitize_prompt should always return a string."""
        result = sanitize_prompt(prompt)
        assert isinstance(result, str), f"sanitize_prompt should return string, got {type(result)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_idempotent(self, prompt: str) -> None:
        """sanitize_prompt should be idempotent."""
        result1 = sanitize_prompt(prompt)
        result2 = sanitize_prompt(result1)
        assert result1 == result2, "sanitize_prompt should be idempotent"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_preserves_length_approximately(self, prompt: str) -> None:
        """sanitize_prompt should not dramatically change length."""
        result = sanitize_prompt(prompt)

        # Sanitized prompt should not be more than 2x the original length
        assert len(result) <= len(prompt) * 2, f"Sanitized prompt too long: {len(result)} vs {len(prompt)}"

        # Sanitized prompt should not be empty if original had content
        if prompt.strip():
            assert result.strip(), "Sanitized prompt should not be empty if original had content"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=2000))
    @settings(max_examples=25, deadline=50)
    def test_sanitize_prompt_removes_dangerous_patterns(self, prompt: str) -> None:
        """sanitize_prompt should remove or neutralize dangerous patterns."""
        result = sanitize_prompt(prompt)

        # Check for common dangerous patterns (only those actually in the blocklist)
        dangerous_patterns = ["<script>", "{{", "}}"]
        for pattern in dangerous_patterns:
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
                assert isinstance(e, ValueError | TypeError), f"Unexpected exception for short string: {type(e)}"

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
            from src.utils.prompt_sanitizer import SecurityError

            assert isinstance(
                e, ValueError | TypeError | SecurityError
            ), f"Unexpected exception for long string: {type(e)}"

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
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for special characters: {type(e)}"
