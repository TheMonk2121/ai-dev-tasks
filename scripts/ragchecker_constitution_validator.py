#!/usr/bin/env python3
"""
Constitution-Aware Validation for RAGChecker Evaluation System
Integrates existing constitution validation with RAGChecker Pydantic models.
"""

import os
import sys
from typing import Any, Dict, List, Optional

# Add dspy-rag-system to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))

try:
    from pydantic import BaseModel, Field

    from src.dspy_modules.constitution_validation import (
        ConstitutionCompliance,
        ConstitutionRule,
        ConstitutionValidator,
        ErrorSeverity,
        ProgramOutput,
    )
    from src.dspy_modules.error_taxonomy import CoherenceError, ConstitutionErrorMapper, ErrorType, ValidationError
    from src.dspy_modules.error_taxonomy import ErrorSeverity as TaxonomyErrorSeverity
except ImportError as e:
    print(f"⚠️  Warning: Could not import constitution validation modules: {e}")
    print("   Constitution validation will be disabled")
    ConstitutionValidator = None
    ConstitutionCompliance = None
    ProgramOutput = None
    ConstitutionRule = None
    ErrorSeverity = None
    ConstitutionErrorMapper = None
    ValidationError = None
    CoherenceError = None
    ErrorType = None
    TaxonomyErrorSeverity = None


class RAGCheckerConstitutionValidator(BaseModel):
    """Constitution-aware validator for RAGChecker evaluation data"""

    model_config = {"arbitrary_types_allowed": True}

    enabled: bool = Field(default=True, description="Whether constitution validation is enabled")
    validation_rules: list[Any] = Field(default_factory=list, description="Active validation rules")
    error_mapper: Any | None = Field(None, description="Error taxonomy mapper")

    def __init__(self, **data):
        super().__init__(**data)
        if self.enabled and ConstitutionValidator is not None:
            self._initialize_constitution_rules()
            self._initialize_error_mapper()

    def _initialize_constitution_rules(self):
        """Initialize constitution validation rules for RAGChecker"""
        if ConstitutionRule is None or ErrorSeverity is None:
            # Taxonomy not available; skip rule initialization
            self.validation_rules = []
            return
        self.validation_rules = [
            ConstitutionRule(
                rule_id="rag_001",
                rule_name="RAG Input Validation",
                rule_description="Ensure RAGChecker input data meets quality standards",
                rule_type="validation",
                severity=ErrorSeverity.HIGH,
                enabled=True,
            ),
            ConstitutionRule(
                rule_id="rag_002",
                rule_name="RAG Metrics Coherence",
                rule_description="Ensure RAGChecker metrics are logically consistent",
                rule_type="coherence",
                severity=ErrorSeverity.MEDIUM,
                enabled=True,
            ),
            ConstitutionRule(
                rule_id="rag_003",
                rule_name="RAG Result Quality",
                rule_description="Ensure RAGChecker results meet quality thresholds",
                rule_type="quality",
                severity=ErrorSeverity.HIGH,
                enabled=True,
            ),
            ConstitutionRule(
                rule_id="rag_004",
                rule_name="RAG Security Validation",
                rule_description="Ensure RAGChecker data doesn't contain sensitive information",
                rule_type="security",
                severity=ErrorSeverity.CRITICAL,
                enabled=True,
            ),
        ]

    def _initialize_error_mapper(self):
        """Initialize error taxonomy mapper"""
        if ConstitutionErrorMapper is not None:
            self.error_mapper = ConstitutionErrorMapper()

    def validate_ragchecker_input(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker input data with constitution awareness"""
        if not self.enabled:
            return {"valid": True, "compliance": None, "errors": []}

        validation_results = {"valid": True, "compliance": None, "errors": [], "warnings": []}

        try:
            # Rule 1: Input Validation
            input_validation = self._validate_input_quality(input_data)
            if not input_validation["valid"]:
                validation_results["valid"] = False
                validation_results["errors"].extend(input_validation["errors"])

            # Rule 2: Security Validation
            security_validation = self._validate_input_security(input_data)
            if not security_validation["valid"]:
                validation_results["valid"] = False
                validation_results["errors"].extend(security_validation["errors"])

            # Rule 3: Coherence Validation
            coherence_validation = self._validate_input_coherence(input_data)
            if not coherence_validation["valid"]:
                validation_results["warnings"].extend(coherence_validation["warnings"])

            # Create constitution compliance record
            if ConstitutionCompliance is not None:
                compliance_score = 1.0 if validation_results["valid"] else 0.3
                validation_results["compliance"] = ConstitutionCompliance(
                    is_compliant=validation_results["valid"],
                    compliance_score=compliance_score,
                    violations=[error["message"] for error in validation_results["errors"]],
                    recommendations=[
                        error.get("recommendation", "")
                        for error in validation_results["errors"]
                        if error.get("recommendation")
                    ],
                )

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(
                {
                    "type": "validation_error",
                    "message": f"Constitution validation failed: {str(e)}",
                    "severity": "critical",
                }
            )

        return validation_results

    def validate_ragchecker_metrics(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker metrics with constitution awareness"""
        if not self.enabled:
            return {"valid": True, "compliance": None, "errors": []}

        validation_results = {"valid": True, "compliance": None, "errors": [], "warnings": []}

        try:
            # Rule 1: Metrics Coherence
            coherence_validation = self._validate_metrics_coherence(metrics_data)
            if not coherence_validation["valid"]:
                validation_results["valid"] = False
                validation_results["errors"].extend(coherence_validation["errors"])

            # Rule 2: Quality Thresholds
            quality_validation = self._validate_metrics_quality(metrics_data)
            if not quality_validation["valid"]:
                validation_results["warnings"].extend(quality_validation["warnings"])

            # Create constitution compliance record
            if ConstitutionCompliance is not None:
                compliance_score = 1.0 if validation_results["valid"] else 0.5
                validation_results["compliance"] = ConstitutionCompliance(
                    is_compliant=validation_results["valid"],
                    compliance_score=compliance_score,
                    violations=[error["message"] for error in validation_results["errors"]],
                    recommendations=[
                        error.get("recommendation", "")
                        for error in validation_results["errors"]
                        if error.get("recommendation")
                    ],
                )

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(
                {"type": "validation_error", "message": f"Metrics validation failed: {str(e)}", "severity": "critical"}
            )

        return validation_results

    def validate_ragchecker_result(self, result_data: dict[str, Any]) -> dict[str, Any]:
        """Validate RAGChecker result with constitution awareness"""
        if not self.enabled:
            return {"valid": True, "compliance": None, "errors": []}

        validation_results = {"valid": True, "compliance": None, "errors": [], "warnings": []}

        try:
            # Rule 1: Result Quality
            quality_validation = self._validate_result_quality(result_data)
            if not quality_validation["valid"]:
                validation_results["valid"] = False
                validation_results["errors"].extend(quality_validation["errors"])

            # Rule 2: Consistency Validation
            consistency_validation = self._validate_result_consistency(result_data)
            if not consistency_validation["valid"]:
                validation_results["warnings"].extend(consistency_validation["warnings"])

            # Create constitution compliance record
            if ConstitutionCompliance is not None:
                compliance_score = 1.0 if validation_results["valid"] else 0.4
                validation_results["compliance"] = ConstitutionCompliance(
                    is_compliant=validation_results["valid"],
                    compliance_score=compliance_score,
                    violations=[error["message"] for error in validation_results["errors"]],
                    recommendations=[
                        error.get("recommendation", "")
                        for error in validation_results["errors"]
                        if error.get("recommendation")
                    ],
                )

        except Exception as e:
            validation_results["valid"] = False
            validation_results["errors"].append(
                {"type": "validation_error", "message": f"Result validation failed: {str(e)}", "severity": "critical"}
            )

        return validation_results

    def _validate_input_quality(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Validate input data quality"""
        validation = {"valid": True, "errors": []}

        # Check for empty or missing required fields
        required_fields = ["query_id", "query", "gt_answer", "response", "retrieved_context"]
        for field in required_fields:
            if field not in input_data or not input_data[field]:
                validation["valid"] = False
                validation["errors"].append(
                    {
                        "type": "validation_error",
                        "message": f"Required field '{field}' is missing or empty",
                        "severity": "high",
                        "recommendation": f"Provide a valid value for {field}",
                    }
                )

        # Check query length
        if "query" in input_data and len(input_data["query"].strip()) < 5:
            validation["valid"] = False
            validation["errors"].append(
                {
                    "type": "validation_error",
                    "message": "Query is too short (minimum 5 characters)",
                    "severity": "medium",
                    "recommendation": "Provide a more detailed query",
                }
            )

        # Check retrieved context
        if "retrieved_context" in input_data:
            if not isinstance(input_data["retrieved_context"], list) or len(input_data["retrieved_context"]) == 0:
                validation["valid"] = False
                validation["errors"].append(
                    {
                        "type": "validation_error",
                        "message": "Retrieved context must be a non-empty list",
                        "severity": "high",
                        "recommendation": "Ensure retrieved_context contains at least one context string",
                    }
                )

        return validation

    def _validate_input_security(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Validate input data security"""
        validation = {"valid": True, "errors": []}

        # Check for sensitive information patterns
        sensitive_patterns = ["password", "secret", "key", "token", "api_key", "private_key"]
        content_fields = ["query", "gt_answer", "response"]

        for field in content_fields:
            if field in input_data:
                content = str(input_data[field]).lower()
                for pattern in sensitive_patterns:
                    if pattern in content:
                        validation["valid"] = False
                        validation["errors"].append(
                            {
                                "type": "security_error",
                                "message": f"Potential sensitive information detected in {field}: {pattern}",
                                "severity": "critical",
                                "recommendation": f"Remove or mask sensitive information from {field}",
                            }
                        )

        return validation

    def _validate_input_coherence(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Validate input data coherence"""
        validation = {"valid": True, "warnings": []}

        # Check if query and response are semantically related
        if "query" in input_data and "response" in input_data:
            query_words = set(input_data["query"].lower().split())
            response_words = set(input_data["response"].lower().split())

            # Simple overlap check (could be enhanced with semantic similarity)
            overlap = len(query_words.intersection(response_words))
            if overlap < 2:
                validation["warnings"].append(
                    {
                        "type": "coherence_warning",
                        "message": "Query and response may not be semantically related",
                        "severity": "low",
                        "recommendation": "Verify that the response addresses the query",
                    }
                )

        return validation

    def _validate_metrics_coherence(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Validate metrics coherence"""
        validation = {"valid": True, "errors": []}

        # Check if precision + recall = 1.0 (when both are 0.0 or both are 1.0)
        if "precision" in metrics_data and "recall" in metrics_data:
            precision = metrics_data["precision"]
            recall = metrics_data["recall"]

            if precision == 0.0 and recall == 0.0:
                # This is valid - no relevant documents found
                pass
            elif precision == 1.0 and recall == 1.0:
                # This is valid - perfect retrieval
                pass
            elif precision == 0.0 and recall > 0.0:
                validation["valid"] = False
                validation["errors"].append(
                    {
                        "type": "coherence_error",
                        "message": "Incoherent metrics: precision=0 but recall>0",
                        "severity": "high",
                        "recommendation": "Review precision and recall calculations",
                    }
                )

        return validation

    def _validate_metrics_quality(self, metrics_data: dict[str, Any]) -> dict[str, Any]:
        """Validate metrics quality thresholds"""
        validation = {"valid": True, "warnings": []}

        # Check for extremely low scores that might indicate issues
        low_threshold = 0.1
        for metric_name, score in metrics_data.items():
            if isinstance(score, (int, float)) and 0.0 <= score <= 1.0:
                if score < low_threshold:
                    validation["warnings"].append(
                        {
                            "type": "quality_warning",
                            "message": f"Metric '{metric_name}' is very low ({score:.3f})",
                            "severity": "medium",
                            "recommendation": f"Investigate why {metric_name} is below {low_threshold}",
                        }
                    )

        return validation

    def _validate_result_quality(self, result_data: dict[str, Any]) -> dict[str, Any]:
        """Validate result quality"""
        validation = {"valid": True, "errors": []}

        # Check for required fields
        required_fields = ["test_case_name", "query", "custom_score", "ragchecker_scores", "recommendation"]
        for field in required_fields:
            if field not in result_data or not result_data[field]:
                validation["valid"] = False
                validation["errors"].append(
                    {
                        "type": "validation_error",
                        "message": f"Required field '{field}' is missing or empty",
                        "severity": "high",
                        "recommendation": f"Provide a valid value for {field}",
                    }
                )

        # Check score ranges
        if "custom_score" in result_data:
            score = result_data["custom_score"]
            if not isinstance(score, (int, float)) or score < 0.0 or score > 1.0:
                validation["valid"] = False
                validation["errors"].append(
                    {
                        "type": "validation_error",
                        "message": f"Custom score must be between 0.0 and 1.0, got {score}",
                        "severity": "high",
                        "recommendation": "Ensure custom_score is a valid score in range [0.0, 1.0]",
                    }
                )

        return validation

    def _validate_result_consistency(self, result_data: dict[str, Any]) -> dict[str, Any]:
        """Validate result consistency"""
        validation = {"valid": True, "warnings": []}

        # Check if custom score and RAGChecker overall score are reasonably aligned
        if "custom_score" in result_data and "ragchecker_overall" in result_data:
            custom_score = result_data["custom_score"]
            ragchecker_score = result_data["ragchecker_overall"]

            if isinstance(custom_score, (int, float)) and isinstance(ragchecker_score, (int, float)):
                difference = abs(custom_score - ragchecker_score)
                if difference > 0.3:  # More than 30% difference
                    validation["warnings"].append(
                        {
                            "type": "consistency_warning",
                            "message": f"Large difference between custom score ({custom_score:.3f}) and RAGChecker score ({ragchecker_score:.3f})",
                            "severity": "medium",
                            "recommendation": "Investigate why scores differ significantly",
                        }
                    )

        return validation

    def map_validation_error_to_taxonomy(self, error_data: dict[str, Any]) -> dict[str, Any]:
        """Map validation errors to error taxonomy categories."""
        # Ensure taxonomy classes are available before attempting categorization
        if not self.error_mapper or any(
            sym is None for sym in (ValidationError, CoherenceError, ErrorType, TaxonomyErrorSeverity)
        ):
            error_data["categorized"] = False
            return error_data

        try:
            error_type = error_data.get("type", "unknown")
            message = error_data.get("message", "")
            severity = error_data.get("severity", "medium")

            # Map to taxonomy error types
            if "validation" in error_type.lower():
                taxonomy_error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    "validation_failure",
                    message,
                    severity=self._map_severity(severity),
                    field_name=error_data.get("field_name"),
                    expected_value=error_data.get("expected_value"),
                    actual_value=error_data.get("actual_value"),
                    validation_rule=error_data.get("validation_rule"),
                    context=error_data.get("context", {}),
                )
            elif "coherence" in error_type.lower():
                taxonomy_error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    "coherence_violation",
                    message,
                    severity=self._map_severity(severity),
                    conflicting_elements=error_data.get("conflicting_elements", []),
                    coherence_rule=error_data.get("coherence_rule"),
                    suggested_resolution=error_data.get("suggested_resolution"),
                    context=error_data.get("context", {}),
                )
            elif "security" in error_type.lower():
                taxonomy_error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    "security_violation",
                    message,
                    severity=self._map_severity(severity),
                    context=error_data.get("context", {}),
                )
            else:
                # Default to validation error
                taxonomy_error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    "validation_failure",
                    message,
                    severity=self._map_severity(severity),
                    context=error_data.get("context", {}),
                )

            # Add taxonomy information to error data
            error_data["taxonomy_error"] = taxonomy_error
            error_data["error_code"] = taxonomy_error.error_code
            error_data["categorized"] = True

        except Exception as e:
            error_data["taxonomy_error"] = None
            error_data["error_code"] = "TAXONOMY_MAPPING_FAILED"
            error_data["categorized"] = False
            error_data["taxonomy_error_message"] = str(e)

        return error_data

    def _map_severity(self, severity: str) -> Any:
        """Map string severity to taxonomy severity enum."""
        if TaxonomyErrorSeverity is None:
            # Fallback to string when taxonomy enum is unavailable
            fallback = {"low": "low", "medium": "medium", "high": "high", "critical": "critical"}
            return fallback.get(severity.lower(), "medium")
        severity_mapping = {
            "low": TaxonomyErrorSeverity.LOW,
            "medium": TaxonomyErrorSeverity.MEDIUM,
            "high": TaxonomyErrorSeverity.HIGH,
            "critical": TaxonomyErrorSeverity.CRITICAL,
        }
        return severity_mapping.get(severity.lower(), TaxonomyErrorSeverity.MEDIUM)

    def enhance_validation_with_taxonomy(self, validation_results: dict[str, Any]) -> dict[str, Any]:
        """Enhance validation results with error taxonomy categorization."""
        enhanced_results = validation_results.copy()

        # Enhance input validation errors
        if enhanced_results.get("input_validation") and enhanced_results["input_validation"].get("errors"):
            for error in enhanced_results["input_validation"]["errors"]:
                self.map_validation_error_to_taxonomy(error)

        # Enhance metrics validation errors
        if enhanced_results.get("metrics_validation") and enhanced_results["metrics_validation"].get("errors"):
            for error in enhanced_results["metrics_validation"]["errors"]:
                self.map_validation_error_to_taxonomy(error)

        # Enhance result validation errors
        if enhanced_results.get("result_validation") and enhanced_results["result_validation"].get("errors"):
            for error in enhanced_results["result_validation"]["errors"]:
                self.map_validation_error_to_taxonomy(error)

        # Add taxonomy summary
        enhanced_results["taxonomy_summary"] = {
            "total_categorized_errors": sum(
                [
                    len(enhanced_results.get("input_validation", {}).get("errors", [])),
                    len(enhanced_results.get("metrics_validation", {}).get("errors", [])),
                    len(enhanced_results.get("result_validation", {}).get("errors", [])),
                ]
            ),
            "categorization_success_rate": self._calculate_categorization_success_rate(enhanced_results),
            "error_type_distribution": self._get_error_type_distribution(enhanced_results),
        }

        return enhanced_results

    def _calculate_categorization_success_rate(self, validation_results: dict[str, Any]) -> float:
        """Calculate the success rate of error categorization."""
        total_errors = 0
        categorized_errors = 0

        for validation_type in ["input_validation", "metrics_validation", "result_validation"]:
            if validation_results.get(validation_type) and validation_results[validation_type].get("errors"):
                for error in validation_results[validation_type]["errors"]:
                    total_errors += 1
                    if error.get("categorized", False):
                        categorized_errors += 1

        return categorized_errors / total_errors if total_errors > 0 else 1.0

    def _get_error_type_distribution(self, validation_results: dict[str, Any]) -> dict[str, int]:
        """Get distribution of error types across validation results."""
        error_types = {}

        for validation_type in ["input_validation", "metrics_validation", "result_validation"]:
            if validation_results.get(validation_type) and validation_results[validation_type].get("errors"):
                for error in validation_results[validation_type]["errors"]:
                    error_type = error.get("type", "unknown")
                    error_types[error_type] = error_types.get(error_type, 0) + 1

        return error_types


def create_ragchecker_validator() -> RAGCheckerConstitutionValidator:
    """Factory function to create a RAGChecker constitution validator"""
    return RAGCheckerConstitutionValidator()


# Example usage
if __name__ == "__main__":
    # Test the validator
    validator = create_ragchecker_validator()

    # Test input validation
    test_input = {
        "query_id": "test_001",
        "query": "What is machine learning?",
        "gt_answer": "Machine learning is a subset of AI.",
        "response": "Machine learning is a field of AI.",
        "retrieved_context": ["AI is a broad field.", "ML uses data."],
    }

    result = validator.validate_ragchecker_input(test_input)
    print("Input validation result:", result)

    # Test metrics validation
    test_metrics = {"precision": 0.85, "recall": 0.78, "f1_score": 0.81}

    result = validator.validate_ragchecker_metrics(test_metrics)
    print("Metrics validation result:", result)
