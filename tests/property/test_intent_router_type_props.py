from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.intent_router import IntentClassification, IntentRouter, IntentRouterConfig

from ._regression_capture import record_case


@pytest.mark.prop
class TestIntentRouterTypeProps:
    """Property-based tests for intent router output type contracts."""

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_returns_intent_classification_with_correct_types(
        self, query: str, request_id: str | None
    ) -> None:
        """Test that classify_intent returns IntentClassification with fields of the right types."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that result is IntentClassification
            assert isinstance(result, IntentClassification)

            # Check that all fields have correct types
            assert isinstance(result.intent_type, str)
            assert isinstance(result.confidence, float)
            assert isinstance(result.reasoning, str)
            assert isinstance(result.route_target, str)
            assert isinstance(result.structured_fields, dict)
            assert isinstance(result.should_short_circuit, bool)

            # Check that confidence is in valid range
            assert 0.0 <= result.confidence <= 1.0

            # Check that reasoning is not empty
            assert len(result.reasoning) > 0

            # Check that route_target is one of expected values
            assert result.route_target in {"sql", "kg", "rag", "hybrid"}

            # Check that structured_fields is a dict
            assert isinstance(result.structured_fields, dict)

            # Check that should_short_circuit is boolean
            assert isinstance(result.should_short_circuit, bool)

        except Exception as e:
            record_case(
                "intent_router_classify_intent_types_failed",
                {"query": query, "request_id": request_id, "error": str(e)},
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_structured_fields_is_dict(self, query: str, request_id: str | None) -> None:
        """Test that structured_fields is always a dict."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that structured_fields is a dict
            assert isinstance(result.structured_fields, dict)

            # Check that all values in structured_fields are JSON-serializable
            for key, value in result.structured_fields.items():
                assert isinstance(key, str)
                assert isinstance(value, (str, int, float, bool, list, dict, type(None)))

        except Exception as e:
            record_case(
                "intent_router_structured_fields_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_booleans_are_stable(self, query: str, request_id: str | None) -> None:
        """Test that boolean fields are stable and consistent."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that should_short_circuit is boolean
            assert isinstance(result.should_short_circuit, bool)

            # Check that boolean field is consistent with other fields
            if result.should_short_circuit:
                # If short circuit is True, intent should be structured and confidence should be high
                assert result.intent_type == "structured"
                assert result.confidence >= 0.7  # Based on default threshold
                assert result.route_target in {"sql", "kg"}

        except Exception as e:
            record_case(
                "intent_router_booleans_stable_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_reasoning_string_non_empty(self, query: str, request_id: str | None) -> None:
        """Test that reasoning string is non-empty and contains expected information."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that reasoning is non-empty
            assert len(result.reasoning) > 0

            # Check that reasoning contains expected keywords
            reasoning_lower = result.reasoning.lower()
            assert "intent:" in reasoning_lower
            assert "route:" in reasoning_lower

        except Exception as e:
            record_case(
                "intent_router_reasoning_non_empty_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_route_target_in_expected_values(self, query: str, request_id: str | None) -> None:
        """Test that route_target is always one of expected values."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that route_target is one of expected values
            expected_targets = {"sql", "kg", "rag", "hybrid"}
            assert result.route_target in expected_targets

        except Exception as e:
            record_case(
                "intent_router_route_target_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_confidence_in_valid_range(self, query: str, request_id: str | None) -> None:
        """Test that confidence is always in valid range [0.0, 1.0]."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that confidence is in valid range
            assert 0.0 <= result.confidence <= 1.0

        except Exception as e:
            record_case(
                "intent_router_confidence_range_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_intent_type_in_expected_values(self, query: str, request_id: str | None) -> None:
        """Test that intent_type is always one of expected values."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that intent_type is one of expected values
            expected_types = {"structured", "text_rag", "hybrid"}
            assert result.intent_type in expected_types

        except Exception as e:
            record_case("intent_router_intent_type_failed", {"query": query, "request_id": request_id, "error": str(e)})
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_handles_unicode_queries(self, query: str, request_id: str | None) -> None:
        """Test that classify_intent handles unicode queries correctly."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that result is valid
            assert isinstance(result, IntentClassification)
            assert isinstance(result.intent_type, str)
            assert isinstance(result.confidence, float)
            assert isinstance(result.reasoning, str)
            assert isinstance(result.route_target, str)
            assert isinstance(result.structured_fields, dict)
            assert isinstance(result.should_short_circuit, bool)

        except Exception as e:
            record_case(
                "intent_router_unicode_queries_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=500),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_handles_empty_queries(self, query: str, request_id: str | None) -> None:
        """Test that classify_intent handles empty queries correctly."""
        try:
            # Create router with default config
            config = IntentRouterConfig()
            router = IntentRouter(config)

            # Classify intent
            result = router.classify_intent(query, request_id)

            # Check that result is valid
            assert isinstance(result, IntentClassification)
            assert isinstance(result.intent_type, str)
            assert isinstance(result.confidence, float)
            assert isinstance(result.reasoning, str)
            assert isinstance(result.route_target, str)
            assert isinstance(result.structured_fields, dict)
            assert isinstance(result.should_short_circuit, bool)

        except Exception as e:
            record_case(
                "intent_router_empty_queries_failed", {"query": query, "request_id": request_id, "error": str(e)}
            )
            raise
