"""Unit tests for retrieval quality gates."""

from __future__ import annotations

from typing import Any

from src.retrieval.quality_gates import QualityGateValidator


def test_missing_soft_metric_emits_warning() -> None:
    validator = QualityGateValidator({"soft": {"recall_at_20": 0.50}})

    result: Any = validator.validate({})

    assert result.passed is True
    assert result.errors == []
    assert result.warnings == ["⚠️  recall_at_20: missing metric for soft gate validation"]


def test_missing_hard_metric_emits_error_and_fails() -> None:
    validator = QualityGateValidator({"hard": {"recall_at_20": 0.50}})

    result: Any = validator.validate({})

    assert result.passed is False
    assert result.warnings == []
    assert result.errors == ["❌ recall_at_20: missing metric required for hard gate validation"]


def test_missing_soft_and_hard_metrics_report_all_names() -> None:
    validator = QualityGateValidator(
        {
            "soft": {"precision_at_10": 0.30},
            "hard": {"mrr_at_20": 0.25},
        }
    )

    result = validator.validate({"precision_at_10": None})

    assert "precision_at_10" in result.result.get("key", "")
    assert "mrr_at_20" in result.result.get("key", "")
