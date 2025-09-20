"""
Advanced Hypothesis features demonstration and testing.

This module showcases the full capabilities of Hypothesis including:
- @composite strategies
- Stateful testing
- assume() preconditions
- @example decorators
- Custom domain strategies
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import assume, given, settings
from hypothesis import strategies as st
from hypothesis.stateful import run_state_machine_as_test

from tests.property.hypothesis_strategies import (
    COMMON_STRATEGIES,
    CRITICAL_DSN_EXAMPLES,
    CRITICAL_EVAL_PROFILES,
    CRITICAL_MEMORY_SYSTEMS,
    CRITICAL_MESSAGE_EXAMPLES,
    STATEFUL_MACHINES,
    conversation_message_strategy,
    critical_examples,
    database_dsn_strategy,
    embedding_vector_strategy,
    eval_profile_strategy,
    evaluation_metrics_strategy,
    memory_system_strategy,
    retrieval_result_strategy,
    with_assume_preconditions,
)


class TestCompositeStrategies:
    """Test @composite strategy functionality."""

    @pytest.mark.prop
    @given(profile=eval_profile_strategy())
    @settings(max_examples=20, deadline=200)
    def test_eval_profile_generation(self, profile: str) -> None:
        """Test evaluation profile strategy generates valid profiles."""
        assert profile in ["gold", "real", "mock"]
        assert isinstance(profile, str)
        assert len(profile) > 0

    @pytest.mark.prop
    @given(system=memory_system_strategy())
    @settings(max_examples=20, deadline=200)
    def test_memory_system_generation(self, system: str) -> None:
        """Test memory system strategy generates valid systems."""
        assert system in ["ltst", "cursor", "go_cli", "prime"]
        assert isinstance(system, str)
        assert len(system) > 0

    @pytest.mark.prop
    @given(dsn=database_dsn_strategy())
    @settings(max_examples=30, deadline=300)
    def test_database_dsn_generation(self, dsn: str) -> None:
        """Test database DSN strategy generates valid DSNs."""
        assert isinstance(dsn, str)
        assert len(dsn) > 0
        assert "://" in dsn

        # Check for valid schemes
        valid_schemes = ["postgresql", "postgres", "mysql", "sqlite"]
        assert any(dsn.startswith(scheme) for scheme in valid_schemes)

    @pytest.mark.prop
    @given(message=conversation_message_strategy())
    @settings(max_examples=25, deadline=250)
    def test_conversation_message_generation(self, message: dict) -> None:
        """Test conversation message strategy generates valid messages."""
        required_fields = ["message_id", "thread_id", "content", "role", "timestamp", "metadata"]
        for field in required_fields:
            assert field in message

        assert message is not None
        assert isinstance(message, dict)
        assert len(message) > 0

    @pytest.mark.prop
    @given(result=retrieval_result_strategy())
    @settings(max_examples=25, deadline=250)
    def test_retrieval_result_generation(self, result: dict) -> None:
        """Test retrieval result strategy generates valid results."""
        required_fields = ["chunk_id", "content", "score", "source_path", "metadata"]
        for field in required_fields:
            assert field in result

        assert 0.0 <= result["score"] <= 1.0
        assert isinstance(result["metadata"], dict)
        assert len(result["content"]) > 0

    @pytest.mark.prop
    @given(vector=embedding_vector_strategy())
    @settings(max_examples=20, deadline=200)
    def test_embedding_vector_generation(self, vector) -> None:
        """Test embedding vector strategy generates valid vectors."""
        assert vector.shape == (384,)
        assert vector.dtype == "float32"
        assert all(-1.0 <= val <= 1.0 for val in vector)
        assert not any(np.isnan(vector))
        assert not any(np.isinf(vector))

    @pytest.mark.prop
    @given(metrics=evaluation_metrics_strategy())
    @settings(max_examples=20, deadline=200)
    def test_evaluation_metrics_generation(self, metrics: dict) -> None:
        """Test evaluation metrics strategy generates valid metrics."""
        required_metrics = ["precision", "recall", "f1_score", "faithfulness", "latency_ms"]
        for metric in required_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], float)
            assert metrics[metric] >= 0.0


class TestAssumePreconditions:
    """Test assume() preconditions functionality."""

    @pytest.mark.prop
    @given(a=st.integers(), b=st.integers())
    @settings(max_examples=20, deadline=200)
    def test_division_with_assume(self, a: int, b: int) -> None:
        """Test division with assume() preconditions."""
        assume(b != 0)  # Skip tests where b is 0
        assume(a % b == 0)  # Only test cases where a is divisible by b

        result = a / b
        assert isinstance(result, int | float)
        assert result * b == a

    @pytest.mark.prop
    @given(text=st.text(), pattern=st.text())
    @settings(max_examples=20, deadline=200)
    def test_string_operations_with_assume(self, text: str, pattern: str) -> None:
        """Test string operations with assume() preconditions."""
        assume(len(text) > 0)  # Skip empty strings
        assume(len(pattern) > 0)  # Skip empty patterns
        assume(pattern in text)  # Only test cases where pattern is found

        # Test that pattern is found in text
        assert text.find(pattern) >= 0
        assert text.count(pattern) > 0

    @pytest.mark.prop
    @given(profile=eval_profile_strategy(), system=memory_system_strategy())
    @settings(max_examples=20, deadline=200)
    def test_profile_system_combination_with_assume(self, profile: str, system: str) -> None:
        """Test profile and system combination with assume() preconditions."""
        assume(profile == "gold")  # Only test gold profile
        assume(system in ["ltst", "cursor"])  # Only test specific systems

        # Test that we have the expected combination
        assert profile == "gold"
        assert system in ["ltst", "cursor"]


class TestExampleDecorators:
    """Test @example decorators functionality."""

    @pytest.mark.prop
    @given(dsn=st.text())
    @critical_examples(*CRITICAL_DSN_EXAMPLES)
    @settings(max_examples=20, deadline=200)
    def test_dsn_parsing_with_examples(self, dsn: str) -> None:
        """Test DSN parsing with critical examples."""
        # Test that DSN contains required components
        assert "://" in dsn
        assert len(dsn) > 0

    @pytest.mark.prop
    @given(profile=st.text())
    @critical_examples(*CRITICAL_EVAL_PROFILES)
    @settings(max_examples=20, deadline=200)
    def test_eval_profile_with_examples(self, profile: str) -> None:
        """Test evaluation profile with critical examples."""
        assert profile in ["gold", "real", "mock"]

    @pytest.mark.prop
    @given(system=st.text())
    @critical_examples(*CRITICAL_MEMORY_SYSTEMS)
    @settings(max_examples=20, deadline=200)
    def test_memory_system_with_examples(self, system: str) -> None:
        """Test memory system with critical examples."""
        assert system in ["ltst", "cursor", "go_cli", "prime"]

    @pytest.mark.prop
    @given(message=st.dictionaries(st.text(), st.text()))
    @critical_examples(*CRITICAL_MESSAGE_EXAMPLES)
    @settings(max_examples=20, deadline=200)
    def test_message_processing_with_examples(self, message: dict) -> None:
        """Test message processing with critical examples."""
        assert "role" in message
        assert "content" in message
        assert isinstance(message, dict)


class TestStatefulTesting:
    """Test stateful testing functionality."""

    @pytest.mark.prop
    @settings(max_examples=5, deadline=1000)
    def test_memory_system_state_machine(self) -> None:
        """Test memory system state machine."""
        run_state_machine_as_test()

    @pytest.mark.prop
    @settings(max_examples=5, deadline=1000)
    def test_database_state_machine(self) -> None:
        """Test database state machine."""
        run_state_machine_as_test()


class TestAdvancedFeatures:
    """Test advanced Hypothesis features."""

    @pytest.mark.prop
    @given(
        profiles=st.lists(eval_profile_strategy(), min_size=1, max_size=5),
        systems=st.lists(memory_system_strategy(), min_size=1, max_size=3),
    )
    @settings(max_examples=15, deadline=300)
    def test_strategy_combinations(self, profiles: list, systems: list) -> None:
        """Test combining multiple strategies."""
        assert len(profiles) > 0
        assert len(systems) > 0

        for profile in profiles:
            assert profile in ["gold", "real", "mock"]

        for system in systems:
            assert system in ["ltst", "cursor", "go_cli", "prime"]

    @pytest.mark.prop
    @given(
        messages=st.lists(conversation_message_strategy(), min_size=1, max_size=10),
        results=st.lists(retrieval_result_strategy(), min_size=1, max_size=5),
    )
    @settings(max_examples=10, deadline=500)
    def test_complex_data_structures(self, messages: list, results: list) -> None:
        """Test complex data structure generation."""
        assert len(messages) > 0
        assert len(results) > 0

        # Test message properties
        for message in messages:
            assert "role" in message
            assert "content" in message
            assert isinstance(message, dict)

        # Test result properties
        for result in results:
            assert "score" in result
            assert 0.0 <= result

    @pytest.mark.prop
    @given(vectors=st.lists(embedding_vector_strategy(), min_size=1, max_size=5), metrics=evaluation_metrics_strategy())
    @settings(max_examples=10, deadline=400)
    def test_numerical_data_generation(self, vectors: list, metrics: dict) -> None:
        """Test numerical data generation."""
        assert len(vectors) > 0

        for vector in vectors:
            assert vector.shape == (384,)
            assert vector.dtype == "float32"
            assert not any(np.isnan(vector))
            assert not any(np.isinf(vector))

        # Test metrics
        for metric_name, metric_value in metrics.items():
            assert isinstance(metric_value, float)
            assert metric_value >= 0.0


class TestStrategyReusability:
    """Test strategy reusability and composition."""

    @pytest.mark.prop
    @given(data=st.data())
    @settings(max_examples=20, deadline=200)
    def test_reusable_strategies(self, data: dict) -> None:
        """Test that reusable strategies work correctly."""
        assert "role" in data
        assert "content" in data
        assert isinstance(data, dict)

    @pytest.mark.prop
    @given(
        profile=st.sampled_from(["gold", "real", "mock"]),
        system=st.sampled_from(["ltst", "cursor", "go_cli", "prime"]),
        dsn=st.text(min_size=10, max_size=100)
    )
    @settings(max_examples=15, deadline=300)
    def test_strategy_composition(self, profile: str, system: str, dsn: str) -> None:
        """Test composing multiple reusable strategies."""
        assert profile in ["gold", "real", "mock"]
        assert system in ["ltst", "cursor", "go_cli", "prime"]
        assert "://" in dsn
        assert len(dsn) > 0
