"""
Quality Gates for Retrieval Evaluation

Implements soft and hard quality gates based on evaluation metrics
to ensure retrieval performance meets minimum standards.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QualityGateResult:
    passed: bool
    warnings: list[str]
    errors: list[str]
    metrics: dict[str, float]

    def format_report(self) -> str:
        """Format validation result as human-readable report."""
        lines = []

        if self.passed:
            lines.append("✅ Quality Gates: PASSED")
        else:
            lines.append("❌ Quality Gates: FAILED")

        lines.append("")
        lines.append("📊 Metrics:")
        for metric, value in self.metrics.items():
            lines.append(f"  {metric}: {value:.3f}")

        if self.warnings:
            lines.append("")
            lines.append("⚠️  Warnings:")
            for warning in self.warnings:
                lines.append(f"  {warning}")

        if self.errors:
            lines.append("")
            lines.append("❌ Errors:")
            for error in self.errors:
                lines.append(f"  {error}")

        return "\n".join(lines)


class QualityGateValidator:
    """Validates evaluation metrics against configured thresholds."""

    def __init__(self, config: dict[str, Any]):
        self.soft_gates = config.get("soft", {})
        self.hard_gates = config.get("hard", {})

    def validate(self, metrics: dict[str, float]) -> QualityGateResult:
        """Validate metrics against soft and hard gates.

        Args:
            metrics: Evaluation results (e.g., {"recall_at_20": 0.25, "f1_score": 0.15})

        Returns:
            QualityGateResult with pass/fail status and messages
        """
        warnings = []
        errors = []

        # Check soft gates (warnings)
        for metric, threshold in self.soft_gates.items():
            value = metrics.get(metric)
            if value is not None and value < threshold:
                warnings.append(f"⚠️  {metric}: {value:.3f} below soft threshold {threshold:.3f}")

        # Check hard gates (errors)
        for metric, threshold in self.hard_gates.items():
            value = metrics.get(metric)
            if value is not None and value < threshold:
                errors.append(f"❌ {metric}: {value:.3f} below hard threshold {threshold:.3f}")

        return QualityGateResult(passed=len(errors) == 0, warnings=warnings, errors=errors, metrics=metrics.copy())


def load_quality_gates(config_path: str = "config/retrieval.yaml") -> QualityGateValidator | None:
    """Load quality gate configuration from YAML file."""
    try:
        import pathlib

        import yaml  # type: ignore

        cfg = yaml.safe_load(pathlib.Path(config_path).read_text())
        tuning_config = cfg.get("tuning", {})
        gates_config = tuning_config.get("quality_gates", {})

        if gates_config:
            return QualityGateValidator(gates_config)
        return None
    except Exception:
        return None


def validate_evaluation_results(
    metrics: dict[str, float], config_path: str = "config/retrieval.yaml"
) -> QualityGateResult:
    """Convenience function to validate metrics against configured gates."""
    validator = load_quality_gates(config_path)
    if validator:
        return validator.validate(metrics)

    # No gates configured - always pass
    return QualityGateResult(passed=True, warnings=[], errors=[], metrics=metrics.copy())
