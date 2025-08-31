#!/usr/bin/env python3
"""
Pydantic Models for RAGChecker Evaluation System

This module provides Pydantic models for enhanced data validation, type safety,
and consistency with existing Pydantic infrastructure (B-1007).
"""

import re
from typing import Any, Dict, List

from pydantic import BaseModel, Field, field_validator


class RAGCheckerInput(BaseModel):
    """RAGChecker input data structure with Pydantic validation."""

    query_id: str = Field(description="Unique identifier for the query", min_length=1, pattern=r"^[a-zA-Z0-9_-]+$")

    query: str = Field(description="The user query to be evaluated", min_length=1, max_length=10000)

    gt_answer: str = Field(description="Ground truth answer for evaluation", min_length=1, max_length=50000)

    response: str = Field(description="Generated response to be evaluated", min_length=1, max_length=50000)

    retrieved_context: List[str] = Field(description="List of retrieved context strings for evaluation")

    @field_validator("retrieved_context")
    @classmethod
    def validate_context_items(cls, v: List[str]) -> List[str]:
        """Validate that context items are non-empty strings."""
        for i, context in enumerate(v):
            if not isinstance(context, str) or not context.strip():
                raise ValueError(f"Context item {i} must be a non-empty string")
        return v

    @field_validator("query_id")
    @classmethod
    def validate_query_id(cls, v: str) -> str:
        """Validate query ID format."""
        if not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError("Query ID must contain only alphanumeric characters, underscores, and hyphens")
        return v


class RAGCheckerMetrics(BaseModel):
    """RAGChecker metrics with Pydantic validation."""

    # Overall Metrics
    precision: float = Field(description="Overall precision score", ge=0.0, le=1.0)
    recall: float = Field(description="Overall recall score", ge=0.0, le=1.0)
    f1_score: float = Field(description="Overall F1 score", ge=0.0, le=1.0)

    # Retriever Metrics
    claim_recall: float = Field(description="Claim recall score", ge=0.0, le=1.0)
    context_precision: float = Field(description="Context precision score", ge=0.0, le=1.0)

    # Generator Metrics
    context_utilization: float = Field(description="Context utilization score", ge=0.0, le=1.0)
    noise_sensitivity: float = Field(description="Noise sensitivity score", ge=0.0, le=1.0)
    hallucination: float = Field(description="Hallucination score (lower is better)", ge=0.0, le=1.0)
    self_knowledge: float = Field(description="Self knowledge score", ge=0.0, le=1.0)
    faithfulness: float = Field(description="Faithfulness score", ge=0.0, le=1.0)

    @field_validator("f1_score")
    @classmethod
    def validate_f1_score(cls, v: float, info) -> float:
        """Validate F1 score consistency with precision and recall."""
        precision = info.data.get("precision", 0.0)
        recall = info.data.get("recall", 0.0)

        if precision > 0 and recall > 0:
            expected_f1 = 2 * (precision * recall) / (precision + recall)
            if abs(v - expected_f1) > 0.05:  # Allow larger tolerance for practical use
                # This is a warning, not an error, as F1 might be calculated differently
                print(
                    f"Warning: F1 score {v} differs from expected {expected_f1:.3f} based on precision {precision} and recall {recall}"
                )

        return v


class RAGCheckerResult(BaseModel):
    """RAGChecker evaluation result with Pydantic validation."""

    test_case_name: str = Field(description="Name of the test case", min_length=1, max_length=200)

    query: str = Field(description="The query that was evaluated", min_length=1, max_length=10000)

    custom_score: float = Field(description="Custom evaluation score", ge=0.0, le=1.0)

    ragchecker_scores: Dict[str, float] = Field(
        description="Dictionary of RAGChecker metric scores", default_factory=dict
    )

    ragchecker_overall: float = Field(description="Overall RAGChecker score", ge=0.0, le=1.0)

    comparison: Dict[str, Any] = Field(
        description="Comparison data between custom and RAGChecker evaluation", default_factory=dict
    )

    recommendation: str = Field(description="Recommendation based on evaluation results", min_length=1, max_length=1000)

    @field_validator("ragchecker_scores")
    @classmethod
    def validate_scores(cls, v: Dict[str, float]) -> Dict[str, float]:
        """Validate that all scores are in valid range."""
        for metric, score in v.items():
            if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
                raise ValueError(f"Score for metric '{metric}' must be between 0.0 and 1.0, got {score}")
        return v

    @field_validator("ragchecker_overall")
    @classmethod
    def validate_overall_score(cls, v: float, info) -> float:
        """Validate overall score consistency with individual scores."""
        scores = info.data.get("ragchecker_scores", {})
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            if abs(v - avg_score) > 0.1:  # Allow some difference for weighted averages
                # This is a warning, not an error, as overall might be weighted
                print(f"Warning: Overall score {v} differs significantly from average {avg_score}")
        return v


# Backward compatibility functions
def create_ragchecker_input(
    query_id: str, query: str, gt_answer: str, response: str, retrieved_context: List[str]
) -> RAGCheckerInput:
    """Create RAGCheckerInput with backward compatibility."""
    return RAGCheckerInput(
        query_id=query_id, query=query, gt_answer=gt_answer, response=response, retrieved_context=retrieved_context
    )


def create_ragchecker_metrics(
    precision: float,
    recall: float,
    f1_score: float,
    claim_recall: float,
    context_precision: float,
    context_utilization: float,
    noise_sensitivity: float,
    hallucination: float,
    self_knowledge: float,
    faithfulness: float,
) -> RAGCheckerMetrics:
    """Create RAGCheckerMetrics with backward compatibility."""
    return RAGCheckerMetrics(
        precision=precision,
        recall=recall,
        f1_score=f1_score,
        claim_recall=claim_recall,
        context_precision=context_precision,
        context_utilization=context_utilization,
        noise_sensitivity=noise_sensitivity,
        hallucination=hallucination,
        self_knowledge=self_knowledge,
        faithfulness=faithfulness,
    )


def create_ragchecker_result(
    test_case_name: str,
    query: str,
    custom_score: float,
    ragchecker_scores: Dict[str, float],
    ragchecker_overall: float,
    comparison: Dict[str, Any],
    recommendation: str,
) -> RAGCheckerResult:
    """Create RAGCheckerResult with backward compatibility."""
    return RAGCheckerResult(
        test_case_name=test_case_name,
        query=query,
        custom_score=custom_score,
        ragchecker_scores=ragchecker_scores,
        ragchecker_overall=ragchecker_overall,
        comparison=comparison,
        recommendation=recommendation,
    )
