#!/usr/bin/env python3
"""
Error Taxonomy Integration for RAGChecker Evaluation System

Extends RAGChecker Pydantic models with structured error taxonomy
from the existing B-1007 error taxonomy infrastructure.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from ragchecker_constitution_validation import (
    ConstitutionAwareRAGCheckerInput,
    ConstitutionAwareRAGCheckerMetrics,
    ConstitutionAwareRAGCheckerResult,
)

_LOG = logging.getLogger("ragchecker_error_taxonomy")


# ---------- RAGChecker-Specific Error Types ----------


class RAGCheckerErrorType:
    """RAGChecker-specific error types extending the base error taxonomy"""

    # RAGChecker-specific error types
    RETRIEVAL_ERROR = "retrieval_error"
    GENERATION_ERROR = "generation_error"
    EVALUATION_ERROR = "evaluation_error"
    METRIC_CALCULATION_ERROR = "metric_calculation_error"
    CONTEXT_VALIDATION_ERROR = "context_validation_error"
    RESPONSE_QUALITY_ERROR = "response_quality_error"


# ---------- RAGChecker Error Models ----------


class RAGCheckerValidationError(BaseModel):
    """RAGChecker-specific validation error"""

    error_type: str = Field(..., description="Type of RAGChecker error")
    severity: str = Field(..., description="Error severity (low, medium, high, critical)")
    message: str = Field(..., description="Human-readable error message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error occurrence timestamp")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context information")
    error_code: Optional[str] = Field(default=None, description="Error code for programmatic handling")

    # RAGChecker-specific fields
    query_id: Optional[str] = Field(default=None, description="Query ID where error occurred")
    metric_name: Optional[str] = Field(default=None, description="Metric name if metric-related error")
    validation_rule: Optional[str] = Field(default=None, description="Validation rule that was violated")
    expected_value: Optional[str] = Field(default=None, description="Expected value or format")
    actual_value: Optional[str] = Field(default=None, description="Actual value that failed validation")

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate error message is meaningful"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Error message must be at least 5 characters")
        return v.strip()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level"""
        valid_severities = ["low", "medium", "high", "critical"]
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class RAGCheckerErrorCollection(BaseModel):
    """Collection of RAGChecker errors with taxonomy classification"""

    errors: List[RAGCheckerValidationError] = Field(default_factory=list, description="List of errors")
    total_errors: int = Field(default=0, description="Total number of errors")
    error_types: Dict[str, int] = Field(default_factory=dict, description="Error type distribution")
    severity_distribution: Dict[str, int] = Field(default_factory=dict, description="Severity distribution")
    avg_severity_score: float = Field(default=0.0, description="Average severity score")
    most_common_error_type: Optional[str] = Field(default=None, description="Most common error type")
    critical_errors_count: int = Field(default=0, description="Number of critical errors")

    @model_validator(mode="after")
    def update_statistics(self):
        """Update statistics after model creation - optimized to run only once"""
        total_errors = len(self.errors)
        error_types = {}
        severity_distribution = {}
        severity_scores = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        total_severity_score = 0
        critical_errors_count = 0

        for error in self.errors:
            # Count error types
            error_type = error.error_type
            error_types[error_type] = error_types.get(error_type, 0) + 1

            # Count severity levels
            severity = error.severity
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1

            # Calculate severity score
            total_severity_score += severity_scores.get(severity, 0)

            # Count critical errors
            if severity == "critical":
                critical_errors_count += 1

        avg_severity_score = total_severity_score / total_errors if total_errors > 0 else 0.0
        most_common_error_type = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None

        # Update the model with calculated statistics
        self.total_errors = total_errors
        self.error_types = error_types
        self.severity_distribution = severity_distribution
        self.avg_severity_score = avg_severity_score
        self.most_common_error_type = most_common_error_type
        self.critical_errors_count = critical_errors_count

        return self


# ---------- Error Taxonomy-Aware RAGChecker Models ----------


class ErrorTaxonomyAwareRAGCheckerInput(ConstitutionAwareRAGCheckerInput):
    """RAGChecker input with error taxonomy integration"""

    error_collection: Optional[RAGCheckerErrorCollection] = Field(
        default=None, description="Collection of errors with taxonomy classification"
    )

    @field_validator("query")
    @classmethod
    def validate_query_with_error_tracking(cls, v: str) -> str:
        """Validate query with error tracking"""
        errors = []

        # Check for empty query
        if not v or not v.strip():
            errors.append(
                RAGCheckerValidationError(
                    error_type="validation_error",
                    severity="high",
                    message="Query cannot be empty",
                    validation_rule="non_empty_query",
                    expected_value="non-empty string",
                    actual_value="empty or whitespace",
                    error_code="VAL001",
                    query_id="unknown",
                    metric_name="query_validation",
                )
            )

        # Check for query length
        if len(v) > 10000:
            errors.append(
                RAGCheckerValidationError(
                    error_type="validation_error",
                    severity="medium",
                    message="Query exceeds maximum length",
                    validation_rule="max_query_length",
                    expected_value="<= 10000 characters",
                    actual_value=f"{len(v)} characters",
                    error_code="VAL002",
                    query_id="unknown",
                    metric_name="query_validation",
                )
            )

        # If errors found, create error collection
        if errors:
            cls.error_collection = RAGCheckerErrorCollection(errors=errors)

        return v


class ErrorTaxonomyAwareRAGCheckerMetrics(ConstitutionAwareRAGCheckerMetrics):
    """RAGChecker metrics with error taxonomy integration"""

    error_collection: Optional[RAGCheckerErrorCollection] = Field(
        default=None, description="Collection of errors with taxonomy classification"
    )

    @field_validator("precision")
    @classmethod
    def validate_precision_with_error_tracking(cls, v: float) -> float:
        """Validate precision with error tracking"""
        # Note: Pydantic field validation happens before this, so we only track additional errors
        # The main validation is handled by Pydantic's built-in validation
        return v

    @field_validator("recall")
    @classmethod
    def validate_recall_with_error_tracking(cls, v: float) -> float:
        """Validate recall with error tracking"""
        # Note: Pydantic field validation happens before this, so we only track additional errors
        # The main validation is handled by Pydantic's built-in validation
        return v

    @field_validator("f1_score")
    @classmethod
    def validate_f1_score_with_error_tracking(cls, v: float, info) -> float:
        """Validate F1 score with error tracking"""
        errors = []

        # Check range
        if v < 0.0 or v > 1.0:
            errors.append(
                RAGCheckerValidationError(
                    error_type="metric_calculation_error",
                    severity="high",
                    message="F1 score out of valid range",
                    metric_name="f1_score",
                    validation_rule="score_range",
                    expected_value="0.0 to 1.0",
                    actual_value=str(v),
                    error_code="MET001",
                    query_id="unknown",
                )
            )

        # Check consistency with precision and recall
        precision = info.data.get("precision", 0.0)
        recall = info.data.get("recall", 0.0)

        if precision > 0 and recall > 0:
            expected_f1 = 2 * (precision * recall) / (precision + recall)
            if abs(v - expected_f1) > 0.05:
                errors.append(
                    RAGCheckerValidationError(
                        error_type="metric_calculation_error",
                        severity="medium",
                        message="F1 score inconsistent with precision and recall",
                        metric_name="f1_score",
                        validation_rule="f1_consistency",
                        expected_value=f"{expected_f1:.3f}",
                        actual_value=f"{v:.3f}",
                        error_code="MET002",
                        query_id="unknown",
                    )
                )

        if errors:
            cls.error_collection = RAGCheckerErrorCollection(errors=errors)

        return v

    @model_validator(mode="after")
    def validate_model_with_error_tracking(self):
        """Validate the entire model and track errors"""
        errors = []

        # Check for metric consistency issues
        if self.precision > 0 and self.recall > 0:
            expected_f1 = 2 * (self.precision * self.recall) / (self.precision + self.recall)
            if abs(self.f1_score - expected_f1) > 0.05:
                errors.append(
                    RAGCheckerValidationError(
                        error_type="metric_calculation_error",
                        severity="medium",
                        message="F1 score inconsistent with precision and recall",
                        metric_name="f1_score",
                        validation_rule="f1_consistency",
                        expected_value=f"{expected_f1:.3f}",
                        actual_value=f"{self.f1_score:.3f}",
                        error_code="MET002",
                        query_id="unknown",
                    )
                )

        # Check for extreme values that might indicate issues
        if self.hallucination > 0.8:
            errors.append(
                RAGCheckerValidationError(
                    error_type="response_quality_error",
                    severity="high",
                    message="Extremely high hallucination score detected",
                    metric_name="hallucination",
                    validation_rule="hallucination_threshold",
                    expected_value="< 0.8",
                    actual_value=f"{self.hallucination:.3f}",
                    error_code="QUAL001",
                    query_id="unknown",
                )
            )

        if self.faithfulness < 0.2:
            errors.append(
                RAGCheckerValidationError(
                    error_type="response_quality_error",
                    severity="high",
                    message="Extremely low faithfulness score detected",
                    metric_name="faithfulness",
                    validation_rule="faithfulness_threshold",
                    expected_value="> 0.2",
                    actual_value=f"{self.faithfulness:.3f}",
                    error_code="QUAL002",
                    query_id="unknown",
                )
            )

        if errors:
            self.error_collection = RAGCheckerErrorCollection(errors=errors)

        return self


class ErrorTaxonomyAwareRAGCheckerResult(ConstitutionAwareRAGCheckerResult):
    """RAGChecker result with error taxonomy integration"""

    error_collection: Optional[RAGCheckerErrorCollection] = Field(
        default=None, description="Collection of errors with taxonomy classification"
    )

    @field_validator("custom_score")
    @classmethod
    def validate_custom_score_with_error_tracking(cls, v: float) -> float:
        """Validate custom score with error tracking"""
        errors = []

        if v < 0.0 or v > 1.0:
            errors.append(
                RAGCheckerValidationError(
                    error_type="evaluation_error",
                    severity="high",
                    message="Custom score out of valid range",
                    validation_rule="score_range",
                    expected_value="0.0 to 1.0",
                    actual_value=str(v),
                    error_code="EVAL001",
                    query_id="unknown",
                    metric_name="custom_score",
                )
            )

        if errors:
            cls.error_collection = RAGCheckerErrorCollection(errors=errors)

        return v

    @field_validator("ragchecker_overall")
    @classmethod
    def validate_ragchecker_overall_with_error_tracking(cls, v: float, info) -> float:
        """Validate RAGChecker overall score with error tracking"""
        errors = []

        # Check range
        if v < 0.0 or v > 1.0:
            errors.append(
                RAGCheckerValidationError(
                    error_type="evaluation_error",
                    severity="high",
                    message="RAGChecker overall score out of valid range",
                    validation_rule="score_range",
                    expected_value="0.0 to 1.0",
                    actual_value=str(v),
                    error_code="EVAL002",
                    query_id="unknown",
                    metric_name="ragchecker_overall",
                )
            )

        # Check consistency with individual scores
        scores = info.data.get("ragchecker_scores", {})
        if scores:
            avg_score = sum(scores.values()) / len(scores)
            if abs(v - avg_score) > 0.2:  # Allow some difference for weighted averages
                errors.append(
                    RAGCheckerValidationError(
                        error_type="evaluation_error",
                        severity="medium",
                        message="RAGChecker overall score differs significantly from average",
                        validation_rule="overall_score_consistency",
                        expected_value=f"close to {avg_score:.3f}",
                        actual_value=f"{v:.3f}",
                        error_code="EVAL003",
                        query_id="unknown",
                        metric_name="ragchecker_overall",
                    )
                )

        if errors:
            cls.error_collection = RAGCheckerErrorCollection(errors=errors)

        return v

    @model_validator(mode="after")
    def validate_model_with_error_tracking(self):
        """Validate the entire model and track errors"""
        errors = []

        # Check for score consistency issues
        if self.ragchecker_scores:
            avg_score = sum(self.ragchecker_scores.values()) / len(self.ragchecker_scores)
            if abs(self.ragchecker_overall - avg_score) > 0.2:
                errors.append(
                    RAGCheckerValidationError(
                        error_type="evaluation_error",
                        severity="medium",
                        message="RAGChecker overall score differs significantly from average",
                        validation_rule="overall_score_consistency",
                        expected_value=f"close to {avg_score:.3f}",
                        actual_value=f"{self.ragchecker_overall:.3f}",
                        error_code="EVAL003",
                        query_id="unknown",
                        metric_name="ragchecker_overall",
                    )
                )

        # Check for recommendation quality
        action_words = ["improve", "enhance", "optimize", "fix", "update", "modify"]
        has_action = any(word in self.recommendation.lower() for word in action_words)
        if not has_action:
            errors.append(
                RAGCheckerValidationError(
                    error_type="evaluation_error",
                    severity="low",
                    message="Recommendation lacks actionable guidance",
                    validation_rule="actionable_recommendation",
                    expected_value="actionable recommendation",
                    actual_value="non-actionable recommendation",
                )
            )

        if errors:
            self.error_collection = RAGCheckerErrorCollection(errors=errors)

        return self


# ---------- RAGChecker Error Taxonomy Manager ----------


class RAGCheckerErrorTaxonomyManager:
    """Manages error taxonomy for RAGChecker evaluation system"""

    def __init__(self):
        """Initialize error taxonomy manager"""
        self.error_collections: List[RAGCheckerErrorCollection] = []

    def add_error_collection(self, error_collection: RAGCheckerErrorCollection) -> None:
        """Add an error collection to the manager"""
        self.error_collections.append(error_collection)

    def get_aggregated_error_stats(self) -> Dict[str, Any]:
        """Get aggregated error statistics across all collections"""
        if not self.error_collections:
            return {
                "total_collections": 0,
                "total_errors": 0,
                "error_types": {},
                "severity_distribution": {},
                "avg_severity_score": 0.0,
                "most_common_error_type": None,
                "critical_errors_count": 0,
            }

        # Aggregate statistics
        total_errors = sum(collection.total_errors for collection in self.error_collections)
        error_types = {}
        severity_distribution = {}
        total_severity_score = 0
        critical_errors_count = 0

        for collection in self.error_collections:
            # Aggregate error types
            for error_type, count in collection.error_types.items():
                error_types[error_type] = error_types.get(error_type, 0) + count

            # Aggregate severity distribution
            for severity, count in collection.severity_distribution.items():
                severity_distribution[severity] = severity_distribution.get(severity, 0) + count

            # Aggregate severity scores
            total_severity_score += collection.avg_severity_score * collection.total_errors
            critical_errors_count += collection.critical_errors_count

        avg_severity_score = total_severity_score / total_errors if total_errors > 0 else 0.0
        most_common_error_type = max(error_types.items(), key=lambda x: x[1])[0] if error_types else None

        return {
            "total_collections": len(self.error_collections),
            "total_errors": total_errors,
            "error_types": error_types,
            "severity_distribution": severity_distribution,
            "avg_severity_score": avg_severity_score,
            "most_common_error_type": most_common_error_type,
            "critical_errors_count": critical_errors_count,
        }

    def get_error_classification_report(self) -> Dict[str, Any]:
        """Generate comprehensive error classification report"""
        stats = self.get_aggregated_error_stats()

        # Add classification insights
        report = {"summary": stats, "insights": {}, "recommendations": []}

        # Generate insights
        if stats["total_errors"] > 0:
            # Most common error type insight
            if stats["most_common_error_type"]:
                report["insights"]["most_common_error"] = {
                    "type": stats["most_common_error_type"],
                    "count": stats["error_types"][stats["most_common_error_type"]],
                    "percentage": (stats["error_types"][stats["most_common_error_type"]] / stats["total_errors"]) * 100,
                }

            # Critical errors insight
            if stats["critical_errors_count"] > 0:
                report["insights"]["critical_errors"] = {
                    "count": stats["critical_errors_count"],
                    "percentage": (stats["critical_errors_count"] / stats["total_errors"]) * 100,
                }

            # Severity distribution insight
            if "high" in stats["severity_distribution"] or "critical" in stats["severity_distribution"]:
                high_critical_count = stats["severity_distribution"].get("high", 0) + stats[
                    "severity_distribution"
                ].get("critical", 0)
                report["insights"]["high_severity_errors"] = {
                    "count": high_critical_count,
                    "percentage": (high_critical_count / stats["total_errors"]) * 100,
                }

        # Generate recommendations
        if stats["total_errors"] > 0:
            if stats["critical_errors_count"] > 0:
                report["recommendations"].append(
                    "Address critical errors immediately as they may indicate system failures"
                )

            if stats["most_common_error_type"] == "validation_error":
                report["recommendations"].append("Improve input validation to reduce validation errors")

            if stats["most_common_error_type"] == "metric_calculation_error":
                report["recommendations"].append("Review metric calculation logic for accuracy")

            if stats["avg_severity_score"] > 2.5:
                report["recommendations"].append("High average severity suggests systematic issues that need attention")

        return report

    def clear_error_collections(self) -> None:
        """Clear all error collections"""
        self.error_collections.clear()


# ---------- Backward Compatibility Functions ----------


def create_error_taxonomy_aware_input(
    query_id: str, query: str, gt_answer: str, response: str, retrieved_context: List[str]
) -> ErrorTaxonomyAwareRAGCheckerInput:
    """Create error taxonomy-aware RAGChecker input with backward compatibility"""
    return ErrorTaxonomyAwareRAGCheckerInput(
        query_id=query_id, query=query, gt_answer=gt_answer, response=response, retrieved_context=retrieved_context
    )


def create_error_taxonomy_aware_metrics(
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
) -> ErrorTaxonomyAwareRAGCheckerMetrics:
    """Create error taxonomy-aware RAGChecker metrics with backward compatibility"""
    return ErrorTaxonomyAwareRAGCheckerMetrics(
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


def create_error_taxonomy_aware_result(
    test_case_name: str,
    query: str,
    custom_score: float,
    ragchecker_scores: Dict[str, float],
    ragchecker_overall: float,
    comparison: Dict[str, Any],
    recommendation: str,
) -> ErrorTaxonomyAwareRAGCheckerResult:
    """Create error taxonomy-aware RAGChecker result with backward compatibility"""
    return ErrorTaxonomyAwareRAGCheckerResult(
        test_case_name=test_case_name,
        query=query,
        custom_score=custom_score,
        ragchecker_scores=ragchecker_scores,
        ragchecker_overall=ragchecker_overall,
        comparison=comparison,
        recommendation=recommendation,
    )
