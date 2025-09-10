"""
Unified Evaluation Schemas

Standardized schemas for all evaluation components to ensure consistency
across the entire evaluation system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, field_validator

# Type aliases for consistency
EvaluationMode = Literal["retrieval", "reader", "decision"]
MetricName = Literal[
    "precision",
    "recall",
    "f1",
    "faithfulness",
    "unsupported_rate",
    "evidence_precision",
    "context_utilization",
    "latency_p50_ms",
    "latency_p95_ms",
]


@dataclass(frozen=True)
class UnifiedGoldCase:
    """
    Unified gold case schema for all evaluation types.
    Replaces GoldCase, Case, QuerySample, and EvalItem schemas.
    """

    # Core identification
    id: str
    mode: EvaluationMode
    query: str
    tags: List[str]

    # Optional metadata
    category: Optional[str] = None
    notes: Optional[str] = None

    # Ground truth data (mode-dependent)
    gt_answer: Optional[str] = None  # For reader mode
    expected_files: Optional[List[str]] = None  # For retrieval mode
    globs: Optional[List[str]] = None  # For retrieval mode
    expected_decisions: Optional[List[str]] = None  # For decision mode

    # Legacy compatibility fields (deprecated)
    qvec: Optional[List[float]] = None  # Deprecated: use embeddings instead
    file_path: Optional[str] = None  # Deprecated: use expected_files instead
    answers: Optional[List[str]] = None  # Deprecated: use gt_answer instead

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("ID cannot be empty")
        return v.strip()

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, v: List[str]) -> List[str]:
        if not v:
            raise ValueError("Tags cannot be empty")
        return [tag.strip() for tag in v if tag.strip()]


class EvaluationResult(BaseModel):
    """
    Unified evaluation result schema.
    Replaces RAGCheckerResult and other result schemas.
    """

    # Core identification
    case_id: str = Field(..., description="ID of the evaluated case")
    query: str = Field(..., description="The query that was evaluated")

    # Scores and metrics
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall evaluation score (0-1)")
    metrics: Dict[str, float] = Field(..., description="Individual metric scores")

    # Detailed results
    response: Optional[str] = Field(None, description="System response")
    retrieved_docs: Optional[List[str]] = Field(None, description="Retrieved document IDs")
    evidence: Optional[List[str]] = Field(None, description="Evidence used in response")

    # Metadata
    evaluation_mode: EvaluationMode = Field(..., description="Type of evaluation performed")
    timestamp: Optional[str] = Field(None, description="Evaluation timestamp")
    model_used: Optional[str] = Field(None, description="Model used for evaluation")

    # Analysis
    reasoning: Optional[str] = Field(None, description="Reasoning for the score")
    recommendations: Optional[List[str]] = Field(None, description="Improvement recommendations")

    @field_validator("case_id")
    @classmethod
    def validate_case_id(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Case ID cannot be empty")
        return v.strip()

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class EvaluationBatch(BaseModel):
    """
    Batch evaluation results for multiple cases.
    """

    batch_id: str = Field(..., description="Unique batch identifier")
    cases: List[EvaluationResult] = Field(..., description="Individual case results")
    summary_metrics: Dict[str, float] = Field(..., description="Aggregated metrics")
    timestamp: str = Field(..., description="Batch evaluation timestamp")

    @field_validator("cases")
    @classmethod
    def validate_cases(cls, v: List[EvaluationResult]) -> List[EvaluationResult]:
        if not v:
            raise ValueError("Batch must contain at least one case")
        return v


# Legacy compatibility functions
def convert_legacy_case(legacy_data: Dict[str, Any]) -> UnifiedGoldCase:
    """Convert legacy case data to unified schema"""
    # Handle different legacy formats
    case_id = legacy_data.get("id") or legacy_data.get("case_id") or legacy_data.get("query_id") or ""
    query = legacy_data.get("query") or legacy_data.get("question", "")
    tags = legacy_data.get("tags", [])
    if isinstance(tags, str):
        tags = [tags]

    # Handle singular tag field
    if not tags and "tag" in legacy_data:
        tags = [legacy_data["tag"]]

    # Handle different answer fields
    gt_answer = legacy_data.get("gt_answer") or legacy_data.get("expected_answer") or legacy_data.get("response")

    # Handle answers array
    if not gt_answer and "answers" in legacy_data:
        answers = legacy_data["answers"]
        if isinstance(answers, list) and answers:
            gt_answer = answers[0]  # Take first answer

    # Handle file path fields
    expected_files = legacy_data.get("expected_files") or legacy_data.get("file_paths")
    if not expected_files and "file_path" in legacy_data:
        expected_files = [legacy_data["file_path"]]

    return UnifiedGoldCase(
        id=case_id,
        mode=legacy_data.get("mode", "retrieval"),
        query=query,
        tags=tags,
        category=legacy_data.get("category"),
        notes=legacy_data.get("notes"),
        gt_answer=gt_answer,
        expected_files=expected_files,
        globs=legacy_data.get("globs"),
        expected_decisions=legacy_data.get("expected_decisions"),
        # Legacy fields for compatibility
        qvec=legacy_data.get("qvec"),
        file_path=legacy_data.get("file_path"),
        answers=legacy_data.get("answers"),
    )


def convert_legacy_result(legacy_data: Dict[str, Any]) -> EvaluationResult:
    """Convert legacy result data to unified schema"""
    return EvaluationResult(
        case_id=legacy_data.get("test_case_name") or legacy_data.get("case_id", ""),
        query=legacy_data.get("query", ""),
        overall_score=legacy_data.get("custom_score") or legacy_data.get("ragchecker_overall", 0.0),
        metrics=legacy_data.get("ragchecker_scores", {}),
        response=legacy_data.get("response"),
        retrieved_docs=legacy_data.get("retrieved_docs"),
        evidence=legacy_data.get("evidence"),
        evaluation_mode=legacy_data.get("evaluation_mode", "reader"),
        timestamp=legacy_data.get("timestamp"),
        model_used=legacy_data.get("model_used"),
        reasoning=legacy_data.get("reasoning"),
        recommendations=legacy_data.get("recommendations", []),
    )
