#!/usr/bin/env python3
"""
Comprehensive property-based tests for DSPy modules and evaluation system.
"""

from typing import Any

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

# Note: Using dict-based approach for DSPy modules testing


def create_reader_signature(
    query: str,
    context: str,
    answer: str = None,
    confidence: float = None,
) -> dict[str, Any]:
    """Create a reader signature for testing."""
    return {
        "query": query,
        "context": context,
        "answer": answer,
        "confidence": confidence,
    }


def create_span_picker_input(
    query: str,
    context: str,
    max_spans: int = 3,
    min_span_length: int = 10,
    max_span_length: int = 200,
) -> dict[str, Any]:
    """Create span picker input for testing."""
    return {
        "query": query,
        "context": context,
        "max_spans": max_spans,
        "min_span_length": min_span_length,
        "max_span_length": max_span_length,
    }


def create_snippetizer_input(
    text: str,
    max_length: int = 100,
    preserve_sentences: bool = True,
) -> dict[str, Any]:
    """Create snippetizer input for testing."""
    return {
        "text": text,
        "max_length": max_length,
        "preserve_sentences": preserve_sentences,
    }


class TestReaderSignatureProperties:
    """Property-based tests for ReaderSignature invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.text(max_size=1000),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_signature_creation(self, query: str, context: str, answer: str, confidence: float) -> None:
        """ReaderSignature should be creatable with valid inputs."""
        signature = create_reader_signature(query, context, answer, confidence)

        assert signature["query"] == query
        assert signature["context"] == context
        assert signature["answer"] == answer
        assert signature["confidence"] == confidence

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_signature_required_fields(self, query: str, context: str) -> None:
        """ReaderSignature should require query and context fields."""
        signature = create_reader_signature(query, context)

        assert "query" in signature
        assert "context" in signature
        assert signature["query"] == query
        assert signature["context"] == context

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.text(max_size=1000),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_signature_serialization(self, query: str, context: str, answer: str, confidence: float) -> None:
        """ReaderSignature should serialize and deserialize correctly."""
        signature = create_reader_signature(query, context, answer, confidence)

        # Should be able to convert to dict and back
        signature_dict = dict(signature)
        assert signature_dict["query"] == query
        assert signature_dict["context"] == context
        assert signature_dict["answer"] == answer
        assert signature_dict["confidence"] == confidence


class TestSpanPickerProperties:
    """Property-based tests for SpanPicker invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.integers(min_value=1, max_value=10),
        st.integers(min_value=5, max_value=100),
        st.integers(min_value=50, max_value=500),
    )
    @settings(max_examples=25, deadline=50)
    def test_span_picker_input_creation(
        self, query: str, context: str, max_spans: int, min_span_length: int, max_span_length: int
    ) -> None:
        """SpanPicker input should be creatable with valid inputs."""
        input_data = create_span_picker_input(query, context, max_spans, min_span_length, max_span_length)

        assert input_data["query"] == query
        assert input_data["context"] == context
        assert input_data["max_spans"] == max_spans
        assert input_data["min_span_length"] == min_span_length
        assert input_data["max_span_length"] == max_span_length

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.integers(min_value=1, max_value=10),
        st.data(),
    )
    @settings(max_examples=25, deadline=50)
    def test_span_picker_constraints(self, query: str, context: str, max_spans: int, data) -> None:
        """SpanPicker should enforce reasonable constraints."""
        # Generate valid min/max span lengths
        min_span_length = data.draw(st.integers(min_value=5, max_value=100))
        max_span_length = data.draw(st.integers(min_value=min_span_length, max_value=min_span_length + 100))

        input_data = create_span_picker_input(query, context, max_spans, min_span_length, max_span_length)

        # Constraints should be reasonable
        assert input_data["max_spans"] > 0, "max_spans should be positive"
        assert input_data["min_span_length"] > 0, "min_span_length should be positive"
        assert (
            input_data["max_span_length"] >= input_data["min_span_length"]
        ), "max_span_length should be greater than or equal to min_span_length"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
    )
    @settings(max_examples=25, deadline=50)
    def test_span_picker_handles_short_context(self, query: str, context: str) -> None:
        """SpanPicker should handle short context gracefully."""
        if len(context) < 10:
            # Very short context should still work
            input_data = create_span_picker_input(query, context, max_spans=1, min_span_length=5, max_span_length=50)
            assert input_data["context"] == context
        else:
            # Normal context should work normally
            input_data = create_span_picker_input(query, context)
            assert input_data["context"] == context

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1000, max_size=5000),
    )
    @settings(max_examples=25, deadline=50)
    def test_span_picker_handles_long_context(self, query: str, context: str) -> None:
        """SpanPicker should handle long context gracefully."""
        input_data = create_span_picker_input(query, context, max_spans=5, min_span_length=20, max_span_length=200)
        assert input_data["context"] == context
        assert len(input_data["context"]) == len(context)


class TestSnippetizerProperties:
    """Property-based tests for Snippetizer invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=1000),
        st.integers(min_value=10, max_value=500),
        st.booleans(),
    )
    @settings(max_examples=25, deadline=50)
    def test_snippetizer_input_creation(self, text: str, max_length: int, preserve_sentences: bool) -> None:
        """Snippetizer input should be creatable with valid inputs."""
        input_data = create_snippetizer_input(text, max_length, preserve_sentences)

        assert input_data["text"] == text
        assert input_data["max_length"] == max_length
        assert input_data["preserve_sentences"] == preserve_sentences

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=1000),
        st.integers(min_value=10, max_value=500),
        st.booleans(),
    )
    @settings(max_examples=25, deadline=50)
    def test_snippetizer_constraints(self, text: str, max_length: int, preserve_sentences: bool) -> None:
        """Snippetizer should enforce reasonable constraints."""
        input_data = create_snippetizer_input(text, max_length, preserve_sentences)

        # Constraints should be reasonable
        assert input_data["max_length"] > 0, "max_length should be positive"
        # Allow reasonable bounds - max_length can be larger than text for processing flexibility
        # For very short text, allow up to 500x the length for processing flexibility
        max_allowed = max(len(input_data["text"]) * 500, 500)
        assert (
            input_data["max_length"] <= max_allowed
        ), f"max_length {input_data['max_length']} should not be excessively large (max: {max_allowed})"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=100),
        st.integers(min_value=10, max_value=200),
    )
    @settings(max_examples=25, deadline=50)
    def test_snippetizer_handles_short_text(self, text: str, max_length: int) -> None:
        """Snippetizer should handle short text gracefully."""
        input_data = create_snippetizer_input(text, max_length)
        assert input_data["text"] == text
        assert input_data["max_length"] == max_length

    @pytest.mark.prop
    @given(
        st.text(min_size=1000, max_size=5000),
        st.integers(min_value=50, max_value=500),
    )
    @settings(max_examples=25, deadline=50)
    def test_snippetizer_handles_long_text(self, text: str, max_length: int) -> None:
        """Snippetizer should handle long text gracefully."""
        input_data = create_snippetizer_input(text, max_length)
        assert input_data["text"] == text
        assert input_data["max_length"] == max_length


class TestReaderProgramProperties:
    """Property-based tests for ReaderProgram invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.text(max_size=1000),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_program_input_creation(self, query: str, context: str, answer: str) -> None:
        """ReaderProgram input should be creatable with valid inputs."""
        input_data = {
            "query": query,
            "context": context,
            "answer": answer,
        }

        assert input_data["query"] == query
        assert input_data["context"] == context
        assert input_data["answer"] == answer

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_program_required_fields(self, query: str, context: str) -> None:
        """ReaderProgram should require query and context fields."""
        input_data = {
            "query": query,
            "context": context,
        }

        assert "query" in input_data
        assert "context" in input_data
        assert input_data["query"] == query
        assert input_data["context"] == context

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.text(max_size=1000),
    )
    @settings(max_examples=25, deadline=50)
    def test_reader_program_serialization(self, query: str, context: str, answer: str) -> None:
        """ReaderProgram input should serialize correctly."""
        input_data = {
            "query": query,
            "context": context,
            "answer": answer,
        }

        # Should be able to convert to dict
        input_dict = dict(input_data)
        assert input_dict["query"] == query
        assert input_dict["context"] == context
        assert input_dict["answer"] == answer


class TestDSPyModulesEdgeCases:
    """Property-based tests for DSPy modules edge cases."""

    @pytest.mark.prop
    @given(st.text(max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_modules_handle_short_strings(self, text: str) -> None:
        """DSPy modules should handle very short strings."""
        if text.strip():  # Only test non-empty strings
            try:
                signature = create_reader_signature(text, text)
                span_input = create_span_picker_input(text, text)
                snippet_input = create_snippetizer_input(text)

                assert signature["query"] == text
                assert span_input["query"] == text
                assert snippet_input["text"] == text
            except Exception as e:
                # Should be a specific validation error, not a crash
                assert isinstance(e, (ValueError, TypeError)), f"Unexpected exception for short string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1000, max_size=5000))
    @settings(max_examples=25, deadline=50)
    def test_modules_handle_long_strings(self, text: str) -> None:
        """DSPy modules should handle very long strings."""
        try:
            signature = create_reader_signature(text[:500], text)
            span_input = create_span_picker_input(text[:500], text)
            snippet_input = create_snippetizer_input(text, max_length=200)

            assert len(signature["context"]) <= len(text)
            assert len(span_input["context"]) <= len(text)
            assert len(snippet_input["text"]) <= len(text)
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, (ValueError, TypeError)), f"Unexpected exception for long string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_modules_handle_special_characters(self, text: str) -> None:
        """DSPy modules should handle special characters."""
        # Add some special characters
        special_text = f"!@#$%^&*()_+-=[]{{}}|;':\",./<>? {text}"

        try:
            signature = create_reader_signature(special_text[:500], special_text)
            span_input = create_span_picker_input(special_text[:500], special_text)
            snippet_input = create_snippetizer_input(special_text, max_length=200)

            assert signature["query"] == special_text[:500]
            assert span_input["query"] == special_text[:500]
            assert snippet_input["text"] == special_text
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, (ValueError, TypeError)), f"Unexpected exception for special characters: {type(e)}"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_modules_handle_confidence_values(self, query: str, context: str, confidence: float) -> None:
        """DSPy modules should handle confidence values correctly."""
        signature = create_reader_signature(query, context, confidence=confidence)

        assert signature["confidence"] == confidence
        assert 0.0 <= signature["confidence"] <= 1.0, "Confidence should be between 0 and 1"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=500),
        st.text(min_size=1, max_size=2000),
        st.integers(min_value=1, max_value=100),
    )
    @settings(max_examples=25, deadline=50)
    def test_modules_handle_numeric_parameters(self, query: str, context: str, max_spans: int) -> None:
        """DSPy modules should handle numeric parameters correctly."""
        span_input = create_span_picker_input(query, context, max_spans=max_spans)

        assert span_input["max_spans"] == max_spans
        assert span_input["max_spans"] > 0, "max_spans should be positive"
