#!/usr/bin/env python3
"""
Constitution-Aware Validation for DSPy AI System
Implements constitution-aware validation with existing Pydantic infrastructure for B-1007
"""

import logging
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from .context_models import BaseContext
from .error_taxonomy import (
    ConstitutionErrorMapper,
    ErrorSeverity,
)

_LOG = logging.getLogger("constitution_validation")

# ---------- Constitution Compliance Models ----------


class ConstitutionCompliance(BaseModel):
    """Model for constitution compliance validation"""

    is_compliant: bool = Field(..., description="Whether the output complies with constitution")
    compliance_score: float = Field(..., ge=0.0, le=1.0, description="Compliance score (0-1)")
    violations: list[str] = Field(default_factory=list, description="List of constitution violations")
    recommendations: list[str] = Field(default_factory=list, description="Recommendations for improvement")
    validation_timestamp: datetime = Field(default_factory=datetime.now, description="Validation timestamp")

    @field_validator("compliance_score")
    @classmethod
    def validate_compliance_score(cls, v: float) -> float:
        """Validate compliance score is within bounds"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Compliance score must be between 0.0 and 1.0")
        return v

    @field_validator("violations")
    @classmethod
    def validate_violations(cls, v: list[str]) -> list[str]:
        """Validate violations list"""
        return [violation.strip() for violation in v if violation.strip()]

    @field_validator("recommendations")
    @classmethod
    def validate_recommendations(cls, v: list[str]) -> list[str]:
        """Validate recommendations list"""
        return [rec.strip() for rec in v if rec.strip()]


class ProgramOutput(BaseModel):
    """Model for program output validation"""

    output_content: str = Field(..., description="The program output content")
    output_type: str = Field(..., description="Type of output (text, code, data, etc.)")
    context: BaseContext | None = Field(None, description="Context for the output")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Output metadata")
    constitution_compliance: ConstitutionCompliance | None = Field(
        None, description="Constitution compliance validation"
    )

    @field_validator("output_content")
    @classmethod
    def validate_output_content(cls, v: str) -> str:
        """Validate output content is not empty"""
        if not v or not v.strip():
            raise ValueError("Output content cannot be empty")
        return v.strip()

    @field_validator("output_type")
    @classmethod
    def validate_output_type(cls, v: str) -> str:
        """Validate output type"""
        valid_types = ["text", "code", "data", "json", "xml", "markdown", "html"]
        if v.lower() not in valid_types:
            raise ValueError(f"Output type must be one of: {valid_types}")
        return v.lower()


# ---------- Constitution Validation Rules ----------


class ConstitutionRule(BaseModel):
    """Model for individual constitution rules"""

    rule_id: str = Field(..., description="Unique rule identifier")
    rule_name: str = Field(..., description="Human-readable rule name")
    rule_description: str = Field(..., description="Rule description")
    rule_type: str = Field(..., description="Type of rule (validation, coherence, security, etc.)")
    severity: ErrorSeverity = Field(..., description="Rule violation severity")
    enabled: bool = Field(default=True, description="Whether the rule is enabled")

    @field_validator("rule_id")
    @classmethod
    def validate_rule_id(cls, v: str) -> str:
        """Validate rule ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Rule ID must be at least 3 characters")
        return v.strip()

    @field_validator("rule_name")
    @classmethod
    def validate_rule_name(cls, v: str) -> str:
        """Validate rule name"""
        if not v or len(v.strip()) < 5:
            raise ValueError("Rule name must be at least 5 characters")
        return v.strip()


class ConstitutionRuleSet(BaseModel):
    """Model for a set of constitution rules"""

    ruleset_id: str = Field(..., description="Unique ruleset identifier")
    ruleset_name: str = Field(..., description="Human-readable ruleset name")
    ruleset_description: str = Field(..., description="Ruleset description")
    rules: list[ConstitutionRule] = Field(default_factory=list, description="List of rules in this ruleset")
    version: str = Field(default="1.0.0", description="Ruleset version")

    @field_validator("ruleset_id")
    @classmethod
    def validate_ruleset_id(cls, v: str) -> str:
        """Validate ruleset ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Ruleset ID must be at least 3 characters")
        return v.strip()

    @field_validator("rules")
    @classmethod
    def validate_rules(cls, v: list[ConstitutionRule]) -> list[ConstitutionRule]:
        """Validate rules list"""
        if not v:
            raise ValueError("Ruleset must contain at least one rule")
        return v


# ---------- Constitution Validator ----------


class ConstitutionValidator:
    """Validates program outputs against constitution rules"""

    def __init__(self, ruleset: ConstitutionRuleSet):
        """Initialize validator with a ruleset"""
        self.ruleset = ruleset
        self._enabled_rules = [rule for rule in ruleset.rules if rule.enabled]

    def validate_output(self, output: ProgramOutput) -> ConstitutionCompliance:
        """Validate program output against constitution rules"""

        violations = []
        recommendations = []
        total_score = 0.0
        valid_rules = 0

        for rule in self._enabled_rules:
            try:
                rule_result = self._apply_rule(rule, output)
                if rule_result["compliant"]:
                    total_score += 1.0
                    valid_rules += 1
                else:
                    violations.append(f"{rule.rule_name}: {rule_result['reason']}")
                    if rule_result.get("recommendation"):
                        recommendations.append(rule_result["recommendation"])
            except Exception as e:
                _LOG.error(f"Error applying rule {rule.rule_id}: {e}")
                violations.append(f"{rule.rule_name}: Rule application failed")

        # Calculate compliance score
        compliance_score = total_score / len(self._enabled_rules) if self._enabled_rules else 1.0
        is_compliant = compliance_score >= 0.8  # 80% threshold for compliance

        return ConstitutionCompliance(
            is_compliant=is_compliant,
            compliance_score=compliance_score,
            violations=violations,
            recommendations=recommendations,
        )

    def _apply_rule(self, rule: ConstitutionRule, output: ProgramOutput) -> dict[str, Any]:
        """Apply a specific rule to the output"""

        # This is a simplified rule application - in practice, this would be more sophisticated
        rule_type = rule.rule_type.lower()

        if rule_type == "validation":
            return self._apply_validation_rule(rule, output)
        elif rule_type == "coherence":
            return self._apply_coherence_rule(rule, output)
        elif rule_type == "security":
            return self._apply_security_rule(rule, output)
        elif rule_type == "quality":
            return self._apply_quality_rule(rule, output)
        else:
            return {"compliant": True, "reason": "Unknown rule type", "recommendation": None}

    def _apply_validation_rule(self, rule: ConstitutionRule, output: ProgramOutput) -> dict[str, Any]:
        """Apply validation rule"""
        # Example validation: check output content length
        if len(output.output_content) < 10:
            return {
                "compliant": False,
                "reason": "Output content too short",
                "recommendation": "Provide more detailed output",
            }
        return {"compliant": True, "reason": None, "recommendation": None}

    def _apply_coherence_rule(self, rule: ConstitutionRule, output: ProgramOutput) -> dict[str, Any]:
        """Apply coherence rule"""
        # Example coherence: check for logical consistency
        if output.context and hasattr(output.context, "role"):
            # Check if output is appropriate for the role
            if output.context.role.value == "coder" and "code" not in output.output_content.lower():
                return {
                    "compliant": False,
                    "reason": "Output not appropriate for coder role",
                    "recommendation": "Include code examples or technical details",
                }
        return {"compliant": True, "reason": None, "recommendation": None}

    def _apply_security_rule(self, rule: ConstitutionRule, output: ProgramOutput) -> dict[str, Any]:
        """Apply security rule"""
        # Example security: check for sensitive information
        sensitive_patterns = ["password", "secret", "key", "token"]
        content_lower = output.output_content.lower()

        for pattern in sensitive_patterns:
            if pattern in content_lower:
                return {
                    "compliant": False,
                    "reason": f"Potential sensitive information detected: {pattern}",
                    "recommendation": "Remove or mask sensitive information",
                }
        return {"compliant": True, "reason": None, "recommendation": None}

    def _apply_quality_rule(self, rule: ConstitutionRule, output: ProgramOutput) -> dict[str, Any]:
        """Apply quality rule"""
        # Example quality: check for proper formatting
        if output.output_type == "code" and not output.output_content.strip().startswith(
            ("def ", "class ", "import ", "from ")
        ):
            return {
                "compliant": False,
                "reason": "Code output not properly formatted",
                "recommendation": "Ensure code follows proper Python syntax",
            }
        return {"compliant": True, "reason": None, "recommendation": None}


# ---------- Constitution-Aware Validation Integration ----------


class ConstitutionAwareValidator:
    """Integrates constitution-aware validation with existing Pydantic infrastructure"""

    def __init__(self, validator: ConstitutionValidator):
        """Initialize with a constitution validator"""
        self.validator = validator

    def validate_program_output(self, output: ProgramOutput) -> ProgramOutput:
        """Validate program output with constitution awareness"""

        # Perform constitution compliance validation
        compliance = self.validator.validate_output(output)

        # Update output with compliance information
        output.constitution_compliance = compliance

        # If not compliant, create structured error
        if not compliance.is_compliant:
            self._create_constitution_violation_error(output, compliance)

        return output

    def _create_constitution_violation_error(self, output: ProgramOutput, compliance: ConstitutionCompliance) -> None:
        """Create structured error for constitution violations"""

        # Map constitution violations to error types
        for violation in compliance.violations:
            if "validation" in violation.lower():
                error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    failure_mode="validation_failure",
                    message=f"Constitution validation failed: {violation}",
                    severity=ErrorSeverity.HIGH,
                    context={
                        "output_type": output.output_type,
                        "compliance_score": compliance.compliance_score,
                        "recommendations": compliance.recommendations,
                    },
                )
            elif "coherence" in violation.lower():
                error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    failure_mode="coherence_violation",
                    message=f"Constitution coherence violation: {violation}",
                    severity=ErrorSeverity.HIGH,
                    context={
                        "output_type": output.output_type,
                        "compliance_score": compliance.compliance_score,
                        "recommendations": compliance.recommendations,
                    },
                )
            elif "security" in violation.lower():
                error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    failure_mode="security_violation",
                    message=f"Constitution security violation: {violation}",
                    severity=ErrorSeverity.CRITICAL,
                    context={
                        "output_type": output.output_type,
                        "compliance_score": compliance.compliance_score,
                        "recommendations": compliance.recommendations,
                    },
                )
            else:
                error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                    failure_mode="runtime_exception",
                    message=f"Constitution violation: {violation}",
                    severity=ErrorSeverity.MEDIUM,
                    context={
                        "output_type": output.output_type,
                        "compliance_score": compliance.compliance_score,
                        "recommendations": compliance.recommendations,
                    },
                )

            _LOG.warning(f"Constitution violation detected: {error.message}")


# ---------- Default Constitution Rules ----------


def create_default_constitution_ruleset() -> ConstitutionRuleSet:
    """Create default constitution ruleset"""

    rules = [
        ConstitutionRule(
            rule_id="VAL001",
            rule_name="Output Content Validation",
            rule_description="Ensures output content is not empty and has sufficient detail",
            rule_type="validation",
            severity=ErrorSeverity.MEDIUM,
        ),
        ConstitutionRule(
            rule_id="COH001",
            rule_name="Role Appropriateness",
            rule_description="Ensures output is appropriate for the AI role",
            rule_type="coherence",
            severity=ErrorSeverity.HIGH,
        ),
        ConstitutionRule(
            rule_id="SEC001",
            rule_name="Sensitive Information Check",
            rule_description="Checks for potential sensitive information in output",
            rule_type="security",
            severity=ErrorSeverity.CRITICAL,
        ),
        ConstitutionRule(
            rule_id="QUAL001",
            rule_name="Code Quality Check",
            rule_description="Ensures code output follows proper syntax and formatting",
            rule_type="quality",
            severity=ErrorSeverity.MEDIUM,
        ),
    ]

    return ConstitutionRuleSet(
        ruleset_id="DEFAULT",
        ruleset_name="Default Constitution Rules",
        ruleset_description="Default constitution rules for DSPy AI system",
        rules=rules,
        version="1.0.0",
    )


# ---------- Performance Monitoring ----------


class ConstitutionValidationMetrics(BaseModel):
    """Metrics for constitution validation performance"""

    total_validations: int = Field(default=0, description="Total number of validations performed")
    compliant_outputs: int = Field(default=0, description="Number of compliant outputs")
    non_compliant_outputs: int = Field(default=0, description="Number of non-compliant outputs")
    avg_compliance_score: float = Field(default=0.0, description="Average compliance score")
    validation_times: list[float] = Field(default_factory=list, description="Validation execution times")

    @property
    def compliance_rate(self) -> float:
        """Calculate compliance rate"""
        if self.total_validations == 0:
            return 0.0
        return self.compliant_outputs / self.total_validations

    @property
    def avg_validation_time(self) -> float:
        """Calculate average validation time"""
        if not self.validation_times:
            return 0.0
        return sum(self.validation_times) / len(self.validation_times)
