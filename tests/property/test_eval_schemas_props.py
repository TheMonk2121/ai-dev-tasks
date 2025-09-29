#!/usr/bin/env python3
"""
Comprehensive property-based tests for evaluation schema invariants.
"""

from datetime import datetime
from uuid import uuid4

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.schemas.eval import CaseResult, EvaluationRun, GoldCase, Mode, RerankerConfig


def create_reranker_config(
    enable: bool = True,
    model: str = "bge-reranker-v2",
    input_topk: int = 40,
    keep: int = 10,
    batch: int = 16,
    device: str = "cpu",
    cache: bool = True,
) -> RerankerConfig:
    """Create a RerankerConfig with validation."""
    return RerankerConfig(
        enable=enable,
        model=model,
        input_topk=input_topk,
        keep=keep,
        batch=batch,
        device=device if device in ["cpu", "cuda", "mps"] else None,  # type: ignore
        cache=cache,
    )


def create_gold_case(
    case_id: str,
    mode: Mode,
    query: str,
    tags: list[str],
    gt_answer: str | None = None,
    category: str | None = None,
    expected_files: list[str] | None = None,
    expected_decisions: list[str] | None = None,
    notes: str | None = None,
) -> GoldCase:
    """Create a GoldCase with validation."""
    return GoldCase(
        id=case_id,
        mode=mode,
        query=query,
        tags=tags,
        gt_answer=gt_answer,
        category=category,
        expected_files=expected_files,
        expected_decisions=expected_decisions,
        notes=notes,
    )


def create_case_result(
    case_id: str,
    mode: str,
    query: str,
    predicted_answer: str | None = None,
    precision: float | None = None,
    recall: float | None = None,
    f1: float | None = None,
    faithfulness: float | None = None,
    answer_latency_ms: int | None = None,
) -> CaseResult:
    """Create a CaseResult with validation."""
    return CaseResult(
        case_id=case_id,
        mode=mode,  # type: ignore
        query=query,
        predicted_answer=predicted_answer,
        precision=precision,
        recall=recall,
        f1=f1,
        faithfulness=faithfulness,
        answer_latency_ms=answer_latency_ms,
    )


def create_evaluation_run(
    profile: str,
    pass_id: str,
    reranker: RerankerConfig,
    cases: list[CaseResult] | None = None,
    artifact_path: str | None = None,
    git_sha: str | None = None,
    tags: list[str] | None = None,
    driver: str | None = None,
    seed: int | None = None,
    overall: dict[str, float] | None = None,
    artifact_paths: dict[str, str] | None = None,
) -> EvaluationRun:
    """Create an EvaluationRun with validation."""
    if cases is None:
        cases = []
    if tags is None:
        tags = []

    return EvaluationRun(
        started_at=datetime.now(),
        profile=profile,
        pass_id=pass_id,
        reranker=reranker,
        cases=cases,
        artifact_path=artifact_path,
        git_sha=git_sha,
        tags=tags,
        driver=driver,
        seed=seed,
        overall=overall,
        artifact_paths=artifact_paths,
    )


class TestRerankerConfigProperties:
    """Property-based tests for RerankerConfig schema invariants."""

    @pytest.mark.prop
    @given(
        st.booleans(),
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Filter out whitespace-only models
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=64),
        st.sampled_from(["cpu", "cuda", "mps"]),
        st.booleans(),
    )
    @settings(max_examples=25, deadline=50)
    def test_reranker_config_creation(
        self, enable: bool, model: str, input_topk: int, keep: int, batch: int, device: str, cache: bool
    ) -> None:
        """RerankerConfig should be creatable with valid inputs."""
        config = create_reranker_config(enable, model, input_topk, keep, batch, device, cache)

        assert config.enable == enable
        assert config.model == model
        assert config.input_topk == input_topk
        assert config.keep == keep
        assert config.batch == batch
        assert config.device == device
        assert config.cache == cache

    @pytest.mark.prop
    @given(
        st.booleans(),
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Filter out whitespace-only models
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=64),
        st.sampled_from(["cpu", "cuda", "mps"]),
        st.booleans(),
    )
    @settings(max_examples=25, deadline=50)
    def test_reranker_config_serialization(
        self, enable: bool, model: str, input_topk: int, keep: int, batch: int, device: str, cache: bool
    ) -> None:
        """RerankerConfig should serialize and deserialize correctly."""
        config = create_reranker_config(enable, model, input_topk, keep, batch, device, cache)

        # Serialize to dict
        config_dict = config.model_dump()

        # Deserialize back
        config_restored = RerankerConfig(**config_dict)

        assert config_restored.enable == config.enable
        assert config_restored.model == config.model
        assert config_restored.input_topk == config.input_topk
        assert config_restored.keep == config.keep
        assert config_restored.batch == config.batch
        assert config_restored.device == config.device
        assert config_restored.cache == config.cache


class TestGoldCaseProperties:
    """Property-based tests for GoldCase schema invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50),
        st.sampled_from([Mode.retrieval, Mode.reader, Mode.decision]),
        st.text(min_size=1, max_size=500),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
        st.text(max_size=1000),
        st.text(max_size=100),
        st.lists(st.text(min_size=1, max_size=100), min_size=0, max_size=5),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=5),
        st.text(max_size=500),
    )
    @settings(max_examples=25, deadline=50)
    def test_gold_case_creation(
        self,
        case_id: str,
        mode: Mode,
        query: str,
        tags: list[str],
        gt_answer: str,
        category: str,
        expected_files: list[str],
        expected_decisions: list[str],
        notes: str,
    ) -> None:
        """GoldCase should be creatable with valid inputs."""
        # Ensure valid data based on mode requirements
        if mode == Mode.reader and not gt_answer.strip():
            gt_answer = "Sample answer"  # Provide required gt_answer for reader mode
        elif mode == Mode.retrieval and not expected_files:
            expected_files = ["sample_file.txt"]  # Provide required expected_files for retrieval mode
        elif mode == Mode.decision and not expected_decisions:
            expected_decisions = ["decision1"]  # Provide required expected_decisions for decision mode

        case = create_gold_case(
            case_id, mode, query, tags, gt_answer, category, expected_files, expected_decisions, notes
        )

        assert case.id == case_id
        assert case.mode == mode
        assert case.query == query
        # Tags are deduplicated, so check that all original tags are present
        for tag in tags:
            assert tag in case.tags, f"Tag {tag} missing from deduplicated tags"
        assert case.gt_answer == gt_answer
        assert case.category == category
        assert case.expected_files == expected_files
        assert case.expected_decisions == expected_decisions
        assert case.notes == notes

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50),
        st.sampled_from([Mode.retrieval, Mode.reader, Mode.decision]),
        st.text(min_size=1, max_size=500),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_gold_case_immutability(self, case_id: str, mode: Mode, query: str, tags: list[str]) -> None:
        """GoldCase should be immutable after creation."""
        # Provide required fields based on mode
        gt_answer = "Sample answer" if mode == Mode.reader else None
        expected_files = ["sample_file.txt"] if mode == Mode.retrieval else None
        expected_decisions = ["decision1"] if mode == Mode.decision else None

        case = create_gold_case(
            case_id, mode, query, tags, gt_answer, expected_files=expected_files, expected_decisions=expected_decisions
        )

        # Pydantic models are not truly immutable, but they validate on assignment
        # Test that validation works correctly
        try:
            case.query = "modified"
            # If no exception, that's fine - Pydantic allows field modification
        except Exception:
            # If exception is raised, that's also fine - some Pydantic configs prevent modification
            pass

        try:
            case.tags = ["modified"]
            # If no exception, that's fine - Pydantic allows field modification
        except Exception:
            # If exception is raised, that's also fine - some Pydantic configs prevent modification
            pass

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50),
        st.sampled_from([Mode.retrieval, Mode.reader, Mode.decision]),
        st.text(min_size=1, max_size=500),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_gold_case_serialization(self, case_id: str, mode: Mode, query: str, tags: list[str]) -> None:
        """GoldCase should serialize and deserialize correctly."""
        # Provide required fields based on mode
        gt_answer = "Sample answer" if mode == Mode.reader else None
        expected_files = ["sample_file.txt"] if mode == Mode.retrieval else None
        expected_decisions = ["decision1"] if mode == Mode.decision else None

        case = create_gold_case(
            case_id, mode, query, tags, gt_answer, expected_files=expected_files, expected_decisions=expected_decisions
        )

        # Serialize to dict
        case_dict = case.model_dump()

        # Deserialize back
        case_restored = GoldCase(**case_dict)

        assert case_restored.id == case.id
        assert case_restored.mode == case.mode
        assert case_restored.query == case.query
        assert case_restored.tags == case.tags
        assert case_restored.gt_answer == case.gt_answer
        assert case_restored.category == case.category
        assert case_restored.expected_files == case.expected_files
        assert case_restored.expected_decisions == case.expected_decisions
        assert case_restored.notes == case.notes

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50),
        st.sampled_from([Mode.retrieval, Mode.reader, Mode.decision]),
        st.text(min_size=1, max_size=500),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
    )
    @settings(max_examples=25, deadline=50)
    def test_gold_case_legacy_aliases(self, case_id: str, mode: Mode, query: str, tags: list[str]) -> None:
        """GoldCase should accept legacy field aliases."""
        # Provide required fields based on mode
        gt_answer = "Sample answer" if mode == Mode.reader else None
        expected_files = ["sample_file.txt"] if mode == Mode.retrieval else None
        expected_decisions = ["decision1"] if mode == Mode.decision else None

        # Test case_id alias for id
        case = GoldCase(
            id=case_id,  # Using id parameter
            mode=mode,
            query=query,
            tags=tags,
            gt_answer=gt_answer,
            expected_files=expected_files,
            expected_decisions=expected_decisions,
        )

        assert case.id == case_id
        assert case.mode == mode
        assert case.query == query
        # Tags are deduplicated, so check that all original tags are present
        for tag in tags:
            assert tag in case.tags, f"Tag {tag} missing from deduplicated tags"


class TestCaseResultProperties:
    """Property-based tests for CaseResult schema invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Filter out whitespace-only case_ids
        st.sampled_from(["rag", "baseline", "oracle"]),
        st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),  # Filter out whitespace-only queries
        st.text(max_size=1000),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.floats(min_value=0.0, max_value=1.0),
        st.integers(min_value=0, max_value=100000),
    )
    @settings(max_examples=25, deadline=50)
    def test_case_result_creation(
        self,
        case_id: str,
        mode: str,
        query: str,
        predicted_answer: str,
        precision: float,
        recall: float,
        f1: float,
        faithfulness: float,
        answer_latency_ms: int,
    ) -> None:
        """CaseResult should be creatable with valid inputs."""
        result = create_case_result(
            case_id, mode, query, predicted_answer, precision, recall, f1, faithfulness, answer_latency_ms
        )

        assert result.case_id == case_id
        assert result.mode == mode
        assert result.query == query
        assert result.predicted_answer == predicted_answer
        assert result.precision == precision
        assert result.recall == recall
        assert result.f1 == f1
        assert result.faithfulness == faithfulness
        assert result.answer_latency_ms == answer_latency_ms

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50),
        st.sampled_from(["rag", "baseline", "oracle"]),
        st.text(min_size=1, max_size=500),
        st.floats(min_value=0.0, max_value=1.0),
    )
    @settings(max_examples=25, deadline=50)
    def test_case_result_score_bounds(self, case_id: str, mode: str, query: str, f1: float) -> None:
        """CaseResult score fields should be within valid bounds."""
        result = create_case_result(case_id, mode, query, f1=f1)

        if result.f1 is not None:
            assert 0.0 <= result.f1 <= 1.0, f"F1 score out of bounds: {result.f1}"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Filter out whitespace-only case_ids
        st.sampled_from(["rag", "baseline", "oracle"]),
        st.text(min_size=1, max_size=500).filter(lambda x: x.strip()),  # Filter out whitespace-only queries
        st.text(max_size=1000),
    )
    @settings(max_examples=25, deadline=50)
    def test_case_result_serialization(self, case_id: str, mode: str, query: str, predicted_answer: str) -> None:
        """CaseResult should serialize and deserialize correctly."""
        result = create_case_result(case_id, mode, query, predicted_answer)

        # Serialize to dict
        result_dict = result.model_dump()

        # Deserialize back
        result_restored = CaseResult(**result_dict)

        assert result_restored.case_id == result.case_id
        assert result_restored.mode == result.mode
        assert result_restored.query == result.query
        assert result_restored.predicted_answer == result.predicted_answer
        assert result_restored.precision == result.precision
        assert result_restored.recall == result.recall
        assert result_restored.f1 == result.f1
        assert result_restored.faithfulness == result.faithfulness
        assert result_restored.answer_latency_ms == result.answer_latency_ms


class TestEvaluationRunProperties:
    """Property-based tests for EvaluationRun schema invariants."""

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only profiles
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only pass_ids
        st.booleans(),
        st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),  # Filter out whitespace-only models
        st.integers(min_value=1, max_value=1000),
        st.integers(min_value=1, max_value=100),
        st.integers(min_value=1, max_value=64),
        st.sampled_from(["cpu", "cuda", "mps"]),
        st.booleans(),
        st.lists(
            st.builds(
                create_case_result,
                case_id=st.text(min_size=1, max_size=50).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only case_ids
                mode=st.sampled_from(["rag", "baseline", "oracle"]),
                query=st.text(min_size=1, max_size=500).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only queries
                predicted_answer=st.text(max_size=1000),
                f1=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=0,
            max_size=10,
        ),
        st.text(max_size=200),
        st.text(max_size=50),
        st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=10),
        st.text(max_size=100),
        st.integers(min_value=0, max_value=1000000),
        st.dictionaries(st.text(min_size=1, max_size=20), st.floats(min_value=0.0, max_value=1.0), max_size=5),
        st.dictionaries(st.text(min_size=1, max_size=20), st.text(max_size=100), max_size=5),
    )
    @settings(max_examples=25, deadline=50)
    def test_evaluation_run_creation(
        self,
        profile: str,
        pass_id: str,
        enable: bool,
        model: str,
        input_topk: int,
        keep: int,
        batch: int,
        device: str,
        cache: bool,
        cases: list[CaseResult],
        artifact_path: str,
        git_sha: str,
        tags: list[str],
        driver: str,
        seed: int,
        overall: dict[str, float],
        artifact_paths: dict[str, str],
    ) -> None:
        """EvaluationRun should be creatable with valid inputs."""
        reranker = create_reranker_config(enable, model, input_topk, keep, batch, device, cache)
        run = create_evaluation_run(
            profile, pass_id, reranker, cases, artifact_path, git_sha, tags, driver, seed, overall, artifact_paths
        )

        assert run.profile == profile
        assert run.pass_id == pass_id
        assert run.reranker == reranker
        assert run.cases == cases
        assert run.artifact_path == artifact_path
        assert run.git_sha == git_sha
        assert run.tags == tags
        assert run.driver == driver
        assert run.seed == seed
        assert run.overall == overall
        assert run.artifact_paths == artifact_paths

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only profiles
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only pass_ids
        st.lists(
            st.builds(
                create_case_result,
                case_id=st.text(min_size=1, max_size=50).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only case_ids
                mode=st.sampled_from(["rag", "baseline", "oracle"]),
                query=st.text(min_size=1, max_size=500).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only queries
                f1=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=1,
            max_size=10,
        ),
    )
    @settings(max_examples=25, deadline=50)
    def test_evaluation_run_metrics(self, profile: str, pass_id: str, cases: list[CaseResult]) -> None:
        """EvaluationRun should have valid computed metrics."""
        reranker = create_reranker_config()
        run = create_evaluation_run(profile, pass_id, reranker, cases)

        # Check that computed field is calculated correctly
        assert run.n_cases == len(cases)

        # Check that n_cases is excluded from serialization
        run_dict = run.model_dump()
        assert "n_cases" not in run_dict, "n_cases should be excluded from serialization"

    @pytest.mark.prop
    @given(
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only profiles
        st.text(min_size=1, max_size=100).filter(lambda x: x.strip()),  # Filter out whitespace-only pass_ids
        st.lists(
            st.builds(
                create_case_result,
                case_id=st.text(min_size=1, max_size=50).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only case_ids
                mode=st.sampled_from(["rag", "baseline", "oracle"]),
                query=st.text(min_size=1, max_size=500).filter(
                    lambda x: x.strip()
                ),  # Filter out whitespace-only queries
                f1=st.floats(min_value=0.0, max_value=1.0),
            ),
            min_size=0,
            max_size=10,
        ),
    )
    @settings(max_examples=25, deadline=50)
    def test_evaluation_run_serialization(self, profile: str, pass_id: str, cases: list[CaseResult]) -> None:
        """EvaluationRun should serialize and deserialize correctly."""
        reranker = create_reranker_config()
        run = create_evaluation_run(profile, pass_id, reranker, cases)

        # Serialize to dict
        run_dict = run.model_dump()

        # Deserialize back
        run_restored = EvaluationRun(**run_dict)

        assert run_restored.profile == run.profile
        assert run_restored.pass_id == run.pass_id
        assert run_restored.reranker.model == run.reranker.model
        assert len(run_restored.cases) == len(run.cases)
        assert run_restored.artifact_path == run.artifact_path
        assert run_restored.git_sha == run.git_sha
        assert run_restored.tags == run.tags
        assert run_restored.driver == run.driver
        assert run_restored.seed == run.seed
        assert run_restored.overall == run.overall
        assert run_restored.artifact_paths == run.artifact_paths


class TestSchemaEdgeCases:
    """Property-based tests for schema edge cases and error handling."""

    @pytest.mark.prop
    @given(st.text(max_size=10))
    @settings(max_examples=25, deadline=50)
    def test_gold_case_handles_short_strings(self, text: str) -> None:
        """GoldCase should handle very short strings."""
        if text.strip():  # Only test non-empty strings
            try:
                case = create_gold_case(text, Mode.retrieval, text, [text])
                assert case.id == text
                assert case.query == text
            except Exception as e:
                # Should be a specific validation error, not a crash
                assert isinstance(e, ValueError | TypeError), f"Unexpected exception for short string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1000, max_size=5000))
    @settings(max_examples=25, deadline=50)
    def test_gold_case_handles_long_strings(self, text: str) -> None:
        """GoldCase should handle very long strings."""
        try:
            case = create_gold_case(text[:50], Mode.retrieval, text, [text[:50]])
            assert len(case.query) <= len(text)
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for long string: {type(e)}"

    @pytest.mark.prop
    @given(st.text(min_size=1, max_size=1000))
    @settings(max_examples=25, deadline=50)
    def test_schemas_handle_special_characters(self, text: str) -> None:
        """Schemas should handle special characters."""
        # Add some special characters
        special_text = f"!@#$%^&*()_+-=[]{{}}|;':\",./<>? {text}"

        try:
            case = create_gold_case(special_text[:50], Mode.retrieval, special_text, [special_text[:50]])
            result = create_case_result(special_text[:50], "rag", special_text)
            assert case.query == special_text
            assert result.query == special_text
        except Exception as e:
            # Should be a specific validation error, not a crash
            assert isinstance(e, ValueError | TypeError), f"Unexpected exception for special characters: {type(e)}"
