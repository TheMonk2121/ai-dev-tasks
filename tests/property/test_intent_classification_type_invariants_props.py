from __future__ import annotations

import json
from typing import Any, Optional, Union

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.retrieval.intent_router import IntentClassification, IntentRouter

from ._regression_capture import record_case


@pytest.mark.prop
class TestIntentClassificationTypeInvariants:
    """Property-based tests for intent classification type invariants."""

    @given(
        intent_type=st.sampled_from(["structured", "text_rag", "hybrid"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=500),
        route_target=st.sampled_from(["sql", "kg", "rag", "hybrid"]),
        structured_fields=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                ),
                min_size=0,
                max_size=10,
            ),
        ),
        should_short_circuit=st.booleans(),
    )
    @settings(max_examples=20, deadline=200)
    def test_intent_classification_fields_have_correct_types(
        self,
        intent_type: str,
        confidence: float,
        reasoning: str,
        route_target: str,
        structured_fields: dict[str, Any] | None,
        should_short_circuit: bool,
    ) -> None:
        """Test that IntentClassification fields have correct types."""
        try:
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                route_target=route_target,
                structured_fields=structured_fields or {},
                should_short_circuit=should_short_circuit,
            )

            # Check field types
            assert isinstance(classification.intent_type, str)
            assert isinstance(classification.confidence, float)
            assert isinstance(classification.reasoning, str)
            assert isinstance(classification.route_target, str)
            assert isinstance(classification.should_short_circuit, bool)

            # Check structured_fields type
            if structured_fields is None:
                assert classification.structured_fields is None
            else:
                assert isinstance(classification.structured_fields, dict)

        except Exception as e:
            record_case(
                "intent_classification_field_types_failed",
                {
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "route_target": route_target,
                    "structured_fields": structured_fields,
                    "should_short_circuit": should_short_circuit,
                    "error": str(e),
                },
            )
            raise

    @given(
        intent_type=st.sampled_from(["structured", "text_rag", "hybrid"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=500),
        route_target=st.sampled_from(["sql", "kg", "rag", "hybrid"]),
        structured_fields=st.dictionaries(
            keys=st.text(min_size=1, max_size=20),
            values=st.one_of(
                st.text(min_size=0, max_size=100),
                st.floats(min_value=0.0, max_value=1.0),
                st.integers(min_value=0, max_value=1000),
                st.booleans(),
            ),
            min_size=1,
            max_size=10,
        ),
        should_short_circuit=st.booleans(),
    )
    @settings(max_examples=20, deadline=200)
    def test_intent_classification_structured_fields_is_dict(
        self,
        intent_type: str,
        confidence: float,
        reasoning: str,
        route_target: str,
        structured_fields: dict[str, Any],
        should_short_circuit: bool,
    ) -> None:
        """Test that structured_fields is a dictionary when provided."""
        try:
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                route_target=route_target,
                structured_fields=structured_fields or {},
                should_short_circuit=should_short_circuit,
            )

            # Check that structured_fields is a dict
            assert isinstance(classification.structured_fields, dict)

            # Check that all keys are strings
            for key in classification.structured_fields:
                assert isinstance(key, str)

            # Check that all values are JSON-serializable primitives
            for key, value in classification.structured_fields.items():
                if isinstance(value, list):
                    for item in value:  # type: ignore[var-annotated]
                        assert isinstance(item, str | int | float | bool | type(None))
                else:
                    assert isinstance(value, str | int | float | bool | type(None))

        except Exception as e:
            record_case(
                "intent_classification_structured_fields_dict_failed",
                {
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "route_target": route_target,
                    "structured_fields": structured_fields,
                    "should_short_circuit": should_short_circuit,
                    "error": str(e),
                },
            )
            raise

    @given(
        intent_type=st.sampled_from(["structured", "text_rag", "hybrid"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=500),
        route_target=st.sampled_from(["sql", "kg", "rag", "hybrid"]),
        structured_fields=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                ),
                min_size=0,
                max_size=10,
            ),
        ),
        should_short_circuit=st.booleans(),
    )
    @settings(max_examples=20, deadline=200)
    def test_intent_classification_booleans_are_stable(
        self,
        intent_type: str,
        confidence: float,
        reasoning: str,
        route_target: str,
        structured_fields: dict[str, Any] | None,
        should_short_circuit: bool,
    ) -> None:
        """Test that boolean fields are stable."""
        try:
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                route_target=route_target,
                structured_fields=structured_fields or {},
                should_short_circuit=should_short_circuit,
            )

            # Check that should_short_circuit is a boolean
            assert isinstance(classification.should_short_circuit, bool)
            assert classification.should_short_circuit == should_short_circuit

        except Exception as e:
            record_case(
                "intent_classification_booleans_stable_failed",
                {
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "route_target": route_target,
                    "structured_fields": structured_fields,
                    "should_short_circuit": should_short_circuit,
                    "error": str(e),
                },
            )
            raise

    @given(
        intent_type=st.sampled_from(["structured", "text_rag", "hybrid"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=500),
        route_target=st.sampled_from(["sql", "kg", "rag", "hybrid"]),
        structured_fields=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                ),
                min_size=0,
                max_size=10,
            ),
        ),
        should_short_circuit=st.booleans(),
    )
    @settings(max_examples=20, deadline=200)
    def test_intent_classification_route_target_is_valid(
        self,
        intent_type: str,
        confidence: float,
        reasoning: str,
        route_target: str,
        structured_fields: dict[str, Any] | None,
        should_short_circuit: bool,
    ) -> None:
        """Test that route_target is one of the expected values."""
        try:
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                route_target=route_target,
                structured_fields=structured_fields or {},
                should_short_circuit=should_short_circuit,
            )

            # Check that route_target is one of the expected values
            valid_route_targets = {"sql", "kg", "rag", "hybrid"}
            assert classification.route_target in valid_route_targets

        except Exception as e:
            record_case(
                "intent_classification_route_target_valid_failed",
                {
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "route_target": route_target,
                    "structured_fields": structured_fields,
                    "should_short_circuit": should_short_circuit,
                    "error": str(e),
                },
            )
            raise

    @given(
        intent_type=st.sampled_from(["structured", "text_rag", "hybrid"]),
        confidence=st.floats(min_value=0.0, max_value=1.0),
        reasoning=st.text(min_size=1, max_size=500),
        route_target=st.sampled_from(["sql", "kg", "rag", "hybrid"]),
        structured_fields=st.one_of(
            st.none(),
            st.dictionaries(
                keys=st.text(min_size=1, max_size=20),
                values=st.one_of(
                    st.text(min_size=0, max_size=100),
                    st.floats(min_value=0.0, max_value=1.0),
                    st.integers(min_value=0, max_value=1000),
                    st.booleans(),
                ),
                min_size=0,
                max_size=10,
            ),
        ),
        should_short_circuit=st.booleans(),
    )
    @settings(max_examples=20, deadline=200)
    def test_intent_classification_is_json_serializable(
        self,
        intent_type: str,
        confidence: float,
        reasoning: str,
        route_target: str,
        structured_fields: dict[str, Any] | None,
        should_short_circuit: bool,
    ) -> None:
        """Test that IntentClassification is JSON serializable."""
        try:
            classification = IntentClassification(
                intent_type=intent_type,
                confidence=confidence,
                reasoning=reasoning,
                route_target=route_target,
                structured_fields=structured_fields or {},
                should_short_circuit=should_short_circuit,
            )

            # Should be able to serialize to JSON
            json_str = json.dumps(classification.__dict__)
            assert isinstance(json_str, str)

            # Should be able to deserialize back
            deserialized = json.loads(json_str)
            assert isinstance(deserialized, dict)

        except Exception as e:
            record_case(
                "intent_classification_json_serializable_failed",
                {
                    "intent_type": intent_type,
                    "confidence": confidence,
                    "reasoning": reasoning,
                    "route_target": route_target,
                    "structured_fields": structured_fields,
                    "should_short_circuit": should_short_circuit,
                    "error": str(e),
                },
            )
            raise

    @given(
        query=st.text(min_size=1, max_size=200),
        request_id=st.one_of(st.none(), st.text(min_size=1, max_size=50)),
    )
    @settings(max_examples=20, deadline=200)
    def test_classify_intent_returns_intent_classification(self, query: str, request_id: str | None) -> None:
        """Test that classify_intent returns IntentClassification instance."""
        try:
            # Create a mock classifier instance
            from src.retrieval.intent_router import IntentRouter, IntentRouterConfig

            config = IntentRouterConfig()
            classifier = IntentRouter(config)

            result = classifier.classify_intent(query, request_id)

            # Check that result is an IntentClassification instance
            assert isinstance(result, IntentClassification)

            # Check that all fields have correct types
            assert isinstance(result.intent_type, str)
            assert isinstance(result.confidence, float)
            assert isinstance(result.reasoning, str)
            assert isinstance(result.route_target, str)
            assert isinstance(result.should_short_circuit, bool)

        except Exception as e:
            record_case(
                "classify_intent_returns_intent_classification_failed",
                {
                    "query": query,
                    "request_id": request_id,
                    "error": str(e),
                },
            )
            raise
