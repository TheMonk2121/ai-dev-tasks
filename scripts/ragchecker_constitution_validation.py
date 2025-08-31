#!/usr/bin/env python3
"""
Constitution-Aware Validation for RAGChecker Evaluation System

Extends RAGChecker Pydantic models with constitution-aware validation
from the existing B-1007 validation infrastructure.
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator
from ragchecker_pydantic_models import RAGCheckerInput, RAGCheckerMetrics, RAGCheckerResult

_LOG = logging.getLogger("ragchecker_constitution_validation")


# ---------- RAGChecker-Specific Constitution Rules ----------


class RAGCheckerConstitutionRule(BaseModel):
    """Constitution rule specific to RAGChecker evaluation"""

    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    rule_description: str = Field(..., description="Rule description")
    rule_type: str = Field(..., description="Type of rule (validation, coherence, security, quality)")
    severity: str = Field(..., description="Rule violation severity (low, medium, high, critical)")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")

    @field_validator("rule_id")
    @classmethod
    def validate_rule_id(cls, v: str) -> str:
        """Validate rule ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Rule ID must be at least 3 characters")
        return v.strip()

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """Validate severity level"""
        valid_severities = ["low", "medium", "high", "critical"]
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class RAGCheckerConstitutionCompliance(BaseModel):
    """Constitution compliance validation for RAGChecker"""

    is_compliant: bool = Field(..., description="Whether the output complies with constitution")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    violations: List[str] = Field(default_factory=list, description="List of constitution violations")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations for improvement")
    validation_timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")

    @field_validator("compliance_score")
    @classmethod
    def validate_compliance_score(cls, v: float) -> float:
        """Validate compliance score is within bounds"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Compliance score must be between 0.0 and 1.0")
        return v


# ---------- Constitution-Aware RAGChecker Models ----------


class ConstitutionAwareRAGCheckerInput(RAGCheckerInput):
    """RAGChecker input with constitution-aware validation"""

    constitution_compliance: Optional[RAGCheckerConstitutionCompliance] = Field(
        default=None, description="Constitution compliance validation"
    )

    @field_validator("query")
    @classmethod
    def validate_query_constitution(cls, v: str) -> str:
        """Validate query against constitution rules"""
        # Check for potentially harmful content
        harmful_patterns = [
            r"\b(hack|exploit|bypass|circumvent)\b",
            r"\b(admin|root|sudo)\s+(password|passwd|credential)",
            r"\b(delete|drop|truncate)\s+(table|database)",
        ]

        for pattern in harmful_patterns:
            if re.search(pattern, v.lower()):
                _LOG.warning(f"Query contains potentially harmful pattern: {pattern}")

        return v

    @field_validator("gt_answer")
    @classmethod
    def validate_gt_answer_constitution(cls, v: str) -> str:
        """Validate ground truth answer against constitution rules"""
        # Check for bias or inappropriate content
        bias_patterns = [
            r"\b(always|never|all|none)\b",
            r"\b(better|worse|superior|inferior)\b",
        ]

        for pattern in bias_patterns:
            if re.search(pattern, v.lower()):
                _LOG.warning(f"Ground truth answer contains potentially biased language: {pattern}")

        return v


class ConstitutionAwareRAGCheckerMetrics(RAGCheckerMetrics):
    """RAGChecker metrics with constitution-aware validation"""

    constitution_compliance: Optional[RAGCheckerConstitutionCompliance] = Field(
        default=None, description="Constitution compliance validation"
    )

    @field_validator("hallucination")
    @classmethod
    def validate_hallucination_constitution(cls, v: float) -> float:
        """Validate hallucination score against constitution rules"""
        # High hallucination scores should trigger warnings
        if v > 0.7:
            _LOG.warning(f"High hallucination score detected: {v}")
        return v

    @field_validator("faithfulness")
    @classmethod
    def validate_faithfulness_constitution(cls, v: float) -> float:
        """Validate faithfulness score against constitution rules"""
        # Low faithfulness scores should trigger warnings
        if v < 0.3:
            _LOG.warning(f"Low faithfulness score detected: {v}")
        return v


class ConstitutionAwareRAGCheckerResult(RAGCheckerResult):
    """RAGChecker result with constitution-aware validation"""

    constitution_compliance: Optional[RAGCheckerConstitutionCompliance] = Field(
        default=None, description="Constitution compliance validation"
    )

    @field_validator("recommendation")
    @classmethod
    def validate_recommendation_constitution(cls, v: str) -> str:
        """Validate recommendation against constitution rules"""
        # Check for actionable recommendations
        action_words = ["improve", "enhance", "optimize", "fix", "update", "modify"]
        has_action = any(word in v.lower() for word in action_words)

        if not has_action:
            _LOG.warning("Recommendation lacks actionable guidance")

        return v


# ---------- RAGChecker Constitution Validator ----------


class RAGCheckerConstitutionValidator:
    """Validates RAGChecker outputs against constitution rules"""

    def __init__(self):
        """Initialize validator with RAGChecker-specific rules"""
        self.rules = self._create_default_rules()

    def _create_default_rules(self) -> List[RAGCheckerConstitutionRule]:
        """Create default constitution rules for RAGChecker"""
        return [
            RAGCheckerConstitutionRule(
                rule_id="RC001",
                rule_name="Query Safety Validation",
                rule_description="Ensure queries don't contain harmful patterns",
                rule_type="security",
                severity="high",
            ),
            RAGCheckerConstitutionRule(
                rule_id="RC002",
                rule_name="Ground Truth Bias Check",
                rule_description="Check for biased language in ground truth answers",
                rule_type="quality",
                severity="medium",
            ),
            RAGCheckerConstitutionRule(
                rule_id="RC003",
                rule_name="Hallucination Threshold",
                rule_description="Warn on high hallucination scores",
                rule_type="quality",
                severity="medium",
            ),
            RAGCheckerConstitutionRule(
                rule_id="RC004",
                rule_name="Faithfulness Threshold",
                rule_description="Warn on low faithfulness scores",
                rule_type="quality",
                severity="medium",
            ),
            RAGCheckerConstitutionRule(
                rule_id="RC005",
                rule_name="Actionable Recommendations",
                rule_description="Ensure recommendations are actionable",
                rule_type="quality",
                severity="low",
            ),
        ]

    def validate_input(self, input_data: ConstitutionAwareRAGCheckerInput) -> RAGCheckerConstitutionCompliance:
        """Validate RAGChecker input against constitution rules"""
        violations = []
        recommendations = []
        total_score = 0.0
        total_rules = 0

        for rule in self.rules:
            if not rule.enabled:
                continue

            total_rules += 1
            try:
                rule_result = self._apply_input_rule(rule, input_data)
                if rule_result["compliant"]:
                    total_score += 1.0
                else:
                    violations.append(f"{rule.rule_name}: {rule_result['reason']}")
                    if rule_result.get("recommendation"):
                        recommendations.append(rule_result["recommendation"])
            except Exception as e:
                _LOG.error(f"Error applying rule {rule.rule_id}: {e}")
                violations.append(f"{rule.rule_name}: Rule application failed")

        # Calculate compliance score
        compliance_score = total_score / total_rules if total_rules > 0 else 1.0
        is_compliant = compliance_score >= 0.8  # 80% threshold for compliance

        return RAGCheckerConstitutionCompliance(
            is_compliant=is_compliant,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_metrics(self, metrics: ConstitutionAwareRAGCheckerMetrics) -> RAGCheckerConstitutionCompliance:
        """Validate RAGChecker metrics against constitution rules"""
        violations = []
        recommendations = []
        total_score = 0.0
        total_rules = 0

        for rule in self.rules:
            if not rule.enabled:
                continue

            total_rules += 1
            try:
                rule_result = self._apply_metrics_rule(rule, metrics)
                if rule_result["compliant"]:
                    total_score += 1.0
                else:
                    violations.append(f"{rule.rule_name}: {rule_result['reason']}")
                    if rule_result.get("recommendation"):
                        recommendations.append(rule_result["recommendation"])
            except Exception as e:
                _LOG.error(f"Error applying rule {rule.rule_id}: {e}")
                violations.append(f"{rule.rule_name}: Rule application failed")

        # Calculate compliance score
        compliance_score = total_score / total_rules if total_rules > 0 else 1.0
        is_compliant = compliance_score >= 0.8  # 80% threshold for compliance

        return RAGCheckerConstitutionCompliance(
            is_compliant=is_compliant,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations,
        )

    def validate_result(self, result: ConstitutionAwareRAGCheckerResult) -> RAGCheckerConstitutionCompliance:
        """Validate RAGChecker result against constitution rules"""
        violations = []
        recommendations = []
        total_score = 0.0
        total_rules = 0

        for rule in self.rules:
            if not rule.enabled:
                continue

            total_rules += 1
            try:
                rule_result = self._apply_result_rule(rule, result)
                if rule_result["compliant"]:
                    total_score += 1.0
                else:
                    violations.append(f"{rule.rule_name}: {rule_result['reason']}")
                    if rule_result.get("recommendation"):
                        recommendations.append(rule_result["recommendation"])
            except Exception as e:
                _LOG.error(f"Error applying rule {rule.rule_id}: {e}")
                violations.append(f"{rule.rule_name}: Rule application failed")

        # Calculate compliance score
        compliance_score = total_score / total_rules if total_rules > 0 else 1.0
        is_compliant = compliance_score >= 0.8  # 80% threshold for compliance

        return RAGCheckerConstitutionCompliance(
            is_compliant=is_compliant,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations,
        )

    def _apply_input_rule(
        self, rule: RAGCheckerConstitutionRule, input_data: ConstitutionAwareRAGCheckerInput
    ) -> Dict[str, Any]:
        """Apply a specific rule to RAGChecker input"""
        rule_type = rule.rule_type.lower()

        if rule_type == "security":
            return self._apply_security_rule_to_input(rule, input_data)
        elif rule_type == "quality":
            return self._apply_quality_rule_to_input(rule, input_data)
        else:
            return {"compliant": True, "reason": "Unknown rule type", "recommendation": None}

    def _apply_metrics_rule(
        self, rule: RAGCheckerConstitutionRule, metrics: ConstitutionAwareRAGCheckerMetrics
    ) -> Dict[str, Any]:
        """Apply a specific rule to RAGChecker metrics"""
        rule_type = rule.rule_type.lower()

        if rule_type == "quality":
            return self._apply_quality_rule_to_metrics(rule, metrics)
        else:
            return {"compliant": True, "reason": "Unknown rule type", "recommendation": None}

    def _apply_result_rule(
        self, rule: RAGCheckerConstitutionRule, result: ConstitutionAwareRAGCheckerResult
    ) -> Dict[str, Any]:
        """Apply a specific rule to RAGChecker result"""
        rule_type = rule.rule_type.lower()

        if rule_type == "quality":
            return self._apply_quality_rule_to_result(rule, result)
        else:
            return {"compliant": True, "reason": "Unknown rule type", "recommendation": None}

    def _apply_security_rule_to_input(
        self, rule: RAGCheckerConstitutionRule, input_data: ConstitutionAwareRAGCheckerInput
    ) -> Dict[str, Any]:
        """Apply security rule to input"""
        if rule.rule_id == "RC001":
            # Check for harmful patterns in query
            harmful_patterns = [
                r"\b(hack|exploit|bypass|circumvent)\b",
                r"\b(admin|root|sudo)\s+(password|passwd|credential)",
                r"\b(delete|drop|truncate)\s+(table|database|tables)",
                r"\bdelete\s+all\s+tables\b",
            ]

            for pattern in harmful_patterns:
                if re.search(pattern, input_data.query.lower()):
                    return {
                        "compliant": False,
                        "reason": f"Query contains potentially harmful pattern: {pattern}",
                        "recommendation": "Review query for security implications",
                    }

            return {"compliant": True, "reason": "Query passes security validation"}

        return {"compliant": True, "reason": "Unknown security rule"}

    def _apply_quality_rule_to_input(
        self, rule: RAGCheckerConstitutionRule, input_data: ConstitutionAwareRAGCheckerInput
    ) -> Dict[str, Any]:
        """Apply quality rule to input"""
        if rule.rule_id == "RC002":
            # Check for bias in ground truth answer
            bias_patterns = [
                r"\b(always|never|all|none)\b",
                r"\b(better|worse|superior|inferior)\b",
            ]

            for pattern in bias_patterns:
                if re.search(pattern, input_data.gt_answer.lower()):
                    return {
                        "compliant": False,
                        "reason": f"Ground truth answer contains potentially biased language: {pattern}",
                        "recommendation": "Review ground truth answer for bias",
                    }

            return {"compliant": True, "reason": "Ground truth answer passes bias check"}

        return {"compliant": True, "reason": "Unknown quality rule"}

    def _apply_quality_rule_to_metrics(
        self, rule: RAGCheckerConstitutionRule, metrics: ConstitutionAwareRAGCheckerMetrics
    ) -> Dict[str, Any]:
        """Apply quality rule to metrics"""
        if rule.rule_id == "RC003":
            # Check hallucination threshold
            if metrics.hallucination > 0.7:
                return {
                    "compliant": False,
                    "reason": f"High hallucination score: {metrics.hallucination}",
                    "recommendation": "Consider improving response generation to reduce hallucinations",
                }
            return {"compliant": True, "reason": "Hallucination score within acceptable range"}

        elif rule.rule_id == "RC004":
            # Check faithfulness threshold
            if metrics.faithfulness < 0.3:
                return {
                    "compliant": False,
                    "reason": f"Low faithfulness score: {metrics.faithfulness}",
                    "recommendation": "Consider improving response faithfulness to source material",
                }
            return {"compliant": True, "reason": "Faithfulness score within acceptable range"}

        return {"compliant": True, "reason": "Unknown quality rule"}

    def _apply_quality_rule_to_result(
        self, rule: RAGCheckerConstitutionRule, result: ConstitutionAwareRAGCheckerResult
    ) -> Dict[str, Any]:
        """Apply quality rule to result"""
        if rule.rule_id == "RC005":
            # Check for actionable recommendations
            action_words = ["improve", "enhance", "optimize", "fix", "update", "modify"]
            has_action = any(word in result.recommendation.lower() for word in action_words)

            if not has_action:
                return {
                    "compliant": False,
                    "reason": "Recommendation lacks actionable guidance",
                    "recommendation": "Include specific actionable steps in recommendations",
                }
            return {"compliant": True, "reason": "Recommendation is actionable"}

        return {"compliant": True, "reason": "Unknown quality rule"}


# ---------- Backward Compatibility Functions ----------


def create_constitution_aware_input(
    query_id: str, query: str, gt_answer: str, response: str, retrieved_context: List[str]
) -> ConstitutionAwareRAGCheckerInput:
    """Create constitution-aware RAGChecker input with backward compatibility"""
    return ConstitutionAwareRAGCheckerInput(
        query_id=query_id,
        query=query,
        gt_answer=gt_answer,
        response=response,
        retrieved_context=retrieved_context,
        constitution_compliance=None,
    )


def create_constitution_aware_metrics(
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
) -> ConstitutionAwareRAGCheckerMetrics:
    """Create constitution-aware RAGChecker metrics with backward compatibility"""
    return ConstitutionAwareRAGCheckerMetrics(
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
        constitution_compliance=None,
    )


def create_constitution_aware_result(
    test_case_name: str,
    query: str,
    custom_score: float,
    ragchecker_scores: Dict[str, float],
    ragchecker_overall: float,
    comparison: Dict[str, Any],
    recommendation: str,
) -> ConstitutionAwareRAGCheckerResult:
    """Create constitution-aware RAGChecker result with backward compatibility"""
    return ConstitutionAwareRAGCheckerResult(
        test_case_name=test_case_name,
        query=query,
        custom_score=custom_score,
        ragchecker_scores=ragchecker_scores,
        ragchecker_overall=ragchecker_overall,
        comparison=comparison,
        recommendation=recommendation,
        constitution_compliance=None,
    )
