#!/usr/bin/env python3
"""
Performance quality gates for workflow validation.
Enforces performance standards and quality thresholds automatically.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from .performance_schema import PerformanceSchema

logger = logging.getLogger(__name__)


class QualityGateStatus(Enum):
    """Quality gate status enumeration"""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    ERROR = "error"


class QualityGateType(Enum):
    """Quality gate type enumeration"""

    PERFORMANCE_THRESHOLD = "performance_threshold"
    DURATION_LIMIT = "duration_limit"
    ERROR_RATE = "error_rate"
    SUCCESS_RATE = "success_rate"
    BOTTLENECK_DETECTION = "bottleneck_detection"
    MEMORY_USAGE = "memory_usage"
    COLLECTION_POINT_LIMIT = "collection_point_limit"


@dataclass
class QualityGateRule:
    """Individual quality gate rule configuration"""

    name: str
    gate_type: QualityGateType
    threshold: Union[float, int]
    operator: str = "lte"  # lte, gte, eq, ne
    severity: str = "warn"  # warn, fail, error
    description: str = ""
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateResult:
    """Result of a quality gate evaluation"""

    rule_name: str
    gate_type: QualityGateType
    status: QualityGateStatus
    actual_value: Union[float, int]
    threshold: Union[float, int]
    operator: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QualityGateSuite:
    """Complete quality gate suite configuration"""

    name: str
    description: str = ""
    rules: List[QualityGateRule] = field(default_factory=list)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


class QualityGateEvaluator:
    """Evaluates quality gates against performance data"""

    def __init__(self, schema: Optional[PerformanceSchema] = None):
        self.schema = schema or PerformanceSchema()
        self.default_suite = self._create_default_suite()

    def _create_default_suite(self) -> QualityGateSuite:
        """Create default quality gate suite"""
        return QualityGateSuite(
            name="Default Performance Gates",
            description="Standard performance quality gates for workflow validation",
            rules=[
                QualityGateRule(
                    name="Total Duration Limit",
                    gate_type=QualityGateType.DURATION_LIMIT,
                    threshold=30000.0,  # 30 seconds
                    operator="lte",
                    severity="fail",
                    description="Workflow total duration must be under 30 seconds",
                ),
                QualityGateRule(
                    name="Performance Score Minimum",
                    gate_type=QualityGateType.PERFORMANCE_THRESHOLD,
                    threshold=70.0,  # 70% minimum score
                    operator="gte",
                    severity="warn",
                    description="Workflow performance score must be at least 70%",
                ),
                QualityGateRule(
                    name="Error Rate Maximum",
                    gate_type=QualityGateType.ERROR_RATE,
                    threshold=0.05,  # 5% maximum error rate
                    operator="lte",
                    severity="fail",
                    description="Error rate must be under 5%",
                ),
                QualityGateRule(
                    name="Success Rate Minimum",
                    gate_type=QualityGateType.SUCCESS_RATE,
                    threshold=0.95,  # 95% minimum success rate
                    operator="gte",
                    severity="fail",
                    description="Success rate must be at least 95%",
                ),
                QualityGateRule(
                    name="Collection Point Duration",
                    gate_type=QualityGateType.COLLECTION_POINT_LIMIT,
                    threshold=5000.0,  # 5 seconds per collection point
                    operator="lte",
                    severity="warn",
                    description="Individual collection points must complete within 5 seconds",
                ),
                QualityGateRule(
                    name="Bottleneck Detection",
                    gate_type=QualityGateType.BOTTLENECK_DETECTION,
                    threshold=2,  # Maximum 2 bottlenecks
                    operator="lte",
                    severity="warn",
                    description="No more than 2 performance bottlenecks allowed",
                ),
            ],
        )

    def evaluate_workflow(self, workflow_analysis: Dict[str, Any]) -> List[QualityGateResult]:
        """Evaluate all quality gates against workflow analysis"""
        results = []

        for rule in self.default_suite.rules:
            if not rule.enabled:
                continue

            try:
                result = self._evaluate_rule(rule, workflow_analysis)
                results.append(result)
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                results.append(
                    QualityGateResult(
                        rule_name=rule.name,
                        gate_type=rule.gate_type,
                        status=QualityGateStatus.ERROR,
                        actual_value=0,
                        threshold=rule.threshold,
                        operator=rule.operator,
                        message=f"Error evaluating rule: {e}",
                    )
                )

        return results

    def _evaluate_rule(self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]) -> QualityGateResult:
        """Evaluate a single quality gate rule"""

        if rule.gate_type == QualityGateType.DURATION_LIMIT:
            return self._evaluate_duration_limit(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.PERFORMANCE_THRESHOLD:
            return self._evaluate_performance_threshold(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.ERROR_RATE:
            return self._evaluate_error_rate(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.SUCCESS_RATE:
            return self._evaluate_success_rate(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.BOTTLENECK_DETECTION:
            return self._evaluate_bottleneck_detection(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.COLLECTION_POINT_LIMIT:
            return self._evaluate_collection_point_limit(rule, workflow_analysis)
        elif rule.gate_type == QualityGateType.MEMORY_USAGE:
            return self._evaluate_memory_usage(rule, workflow_analysis)
        else:
            return QualityGateResult(
                rule_name=rule.name,
                gate_type=rule.gate_type,
                status=QualityGateStatus.ERROR,
                actual_value=0,
                threshold=rule.threshold,
                operator=rule.operator,
                message=f"Unknown gate type: {rule.gate_type}",
            )

    def _evaluate_duration_limit(self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]) -> QualityGateResult:
        """Evaluate duration limit quality gate"""
        actual_duration = workflow_analysis.get("total_duration_ms", 0)
        passed = self._compare_values(actual_duration, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=actual_duration,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Duration: {actual_duration:.1f}ms {'≤' if rule.operator == 'lte' else '≥'} {rule.threshold}ms",
        )

    def _evaluate_performance_threshold(
        self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]
    ) -> QualityGateResult:
        """Evaluate performance threshold quality gate"""
        actual_score = workflow_analysis.get("performance_score", 0)
        passed = self._compare_values(actual_score, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=actual_score,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Performance score: {actual_score:.1f} {'≥' if rule.operator == 'gte' else '≤'} {rule.threshold}",
        )

    def _evaluate_error_rate(self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]) -> QualityGateResult:
        """Evaluate error rate quality gate"""
        error_count = workflow_analysis.get("error_count", 0)
        total_points = len(workflow_analysis.get("collection_points", []))
        # Only count collection points that actually had errors, not workflow start/completion
        error_rate = error_count / max(total_points - 2, 1) if total_points > 2 else 0.0
        passed = self._compare_values(error_rate, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=error_rate,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Error rate: {error_rate:.3f} ({error_count}/{total_points}) {'≤' if rule.operator == 'lte' else '≥'} {rule.threshold}",
        )

    def _evaluate_success_rate(self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]) -> QualityGateResult:
        """Evaluate success rate quality gate"""
        success = workflow_analysis.get("success", False)
        success_rate = 1.0 if success else 0.0
        passed = self._compare_values(success_rate, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=success_rate,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Success rate: {success_rate:.3f} {'≥' if rule.operator == 'gte' else '≤'} {rule.threshold}",
        )

    def _evaluate_bottleneck_detection(
        self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]
    ) -> QualityGateResult:
        """Evaluate bottleneck detection quality gate"""
        bottlenecks = workflow_analysis.get("bottlenecks", [])
        bottleneck_count = len(bottlenecks)
        passed = self._compare_values(bottleneck_count, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=bottleneck_count,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Bottlenecks: {bottleneck_count} {'≤' if rule.operator == 'lte' else '≥'} {rule.threshold}",
        )

    def _evaluate_collection_point_limit(
        self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]
    ) -> QualityGateResult:
        """Evaluate collection point duration limit quality gate"""
        collection_points = workflow_analysis.get("collection_points", [])
        max_duration = 0

        for point in collection_points:
            duration = point.get("duration_ms", 0)
            max_duration = max(max_duration, duration)

        passed = self._compare_values(max_duration, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=max_duration,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Max collection point duration: {max_duration:.1f}ms {'≤' if rule.operator == 'lte' else '≥'} {rule.threshold}ms",
        )

    def _evaluate_memory_usage(self, rule: QualityGateRule, workflow_analysis: Dict[str, Any]) -> QualityGateResult:
        """Evaluate memory usage quality gate"""
        memory_usage = workflow_analysis.get("memory_usage_mb", 0)
        passed = self._compare_values(memory_usage, rule.threshold, rule.operator)

        return QualityGateResult(
            rule_name=rule.name,
            gate_type=rule.gate_type,
            status=self._get_status(passed, rule.severity),
            actual_value=memory_usage,
            threshold=rule.threshold,
            operator=rule.operator,
            message=f"Memory usage: {memory_usage:.1f}MB {'≤' if rule.operator == 'lte' else '≥'} {rule.threshold}MB",
        )

    def _compare_values(self, actual: Union[float, int], threshold: Union[float, int], operator: str) -> bool:
        """Compare actual value against threshold using specified operator"""
        if operator == "lte":
            return actual <= threshold
        elif operator == "gte":
            return actual >= threshold
        elif operator == "eq":
            return actual == threshold
        elif operator == "ne":
            return actual != threshold
        elif operator == "lt":
            return actual < threshold
        elif operator == "gt":
            return actual > threshold
        else:
            logger.warning(f"Unknown operator: {operator}, defaulting to lte")
            return actual <= threshold

    def _get_status(self, passed: bool, severity: str) -> QualityGateStatus:
        """Get quality gate status based on pass/fail and severity"""
        if passed:
            return QualityGateStatus.PASS
        elif severity == "error":
            return QualityGateStatus.ERROR
        elif severity == "fail":
            return QualityGateStatus.FAIL
        else:
            return QualityGateStatus.WARN


class QualityGateEnforcer:
    """Enforces quality gates and takes action based on results"""

    def __init__(self, evaluator: QualityGateEvaluator):
        self.evaluator = evaluator
        self.enforcement_actions = {
            QualityGateStatus.FAIL: self._handle_fail,
            QualityGateStatus.ERROR: self._handle_error,
            QualityGateStatus.WARN: self._handle_warn,
        }

    def enforce_quality_gates(self, workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce quality gates and return enforcement results"""
        enforcement_result = {
            "workflow_id": workflow_analysis.get("workflow_id"),
            "timestamp": datetime.utcnow(),
            "gate_results": [],
            "overall_status": QualityGateStatus.PASS,
            "actions_taken": [],
            "recommendations": [],
        }

        # Evaluate all quality gates
        gate_results = self.evaluator.evaluate_workflow(workflow_analysis)
        enforcement_result["gate_results"] = gate_results

        # Determine overall status
        overall_status = QualityGateStatus.PASS
        for result in gate_results:
            if result.status == QualityGateStatus.ERROR:
                overall_status = QualityGateStatus.ERROR
                break
            elif result.status == QualityGateStatus.FAIL:
                overall_status = QualityGateStatus.FAIL
            elif result.status == QualityGateStatus.WARN and overall_status == QualityGateStatus.PASS:
                overall_status = QualityGateStatus.WARN

        enforcement_result["overall_status"] = overall_status

        # Take enforcement actions
        for result in gate_results:
            if result.status in self.enforcement_actions:
                action = self.enforcement_actions[result.status](result, workflow_analysis)
                if action:
                    enforcement_result["actions_taken"].append(action)

        # Generate recommendations
        enforcement_result["recommendations"] = self._generate_recommendations(gate_results, workflow_analysis)

        return enforcement_result

    def _handle_fail(self, result: QualityGateResult, workflow_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle failed quality gate"""
        logger.warning(f"Quality gate failed: {result.rule_name} - {result.message}")

        return {
            "action": "workflow_failed",
            "rule": result.rule_name,
            "message": f"Workflow failed quality gate: {result.message}",
            "severity": "high",
        }

    def _handle_error(self, result: QualityGateResult, workflow_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle error in quality gate evaluation"""
        logger.error(f"Quality gate error: {result.rule_name} - {result.message}")

        return {
            "action": "workflow_error",
            "rule": result.rule_name,
            "message": f"Quality gate evaluation error: {result.message}",
            "severity": "critical",
        }

    def _handle_warn(self, result: QualityGateResult, workflow_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle warning in quality gate"""
        logger.info(f"Quality gate warning: {result.rule_name} - {result.message}")

        return {
            "action": "workflow_warning",
            "rule": result.rule_name,
            "message": f"Workflow quality warning: {result.message}",
            "severity": "medium",
        }

    def _generate_recommendations(
        self, gate_results: List[QualityGateResult], workflow_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on quality gate results"""
        recommendations = []

        for result in gate_results:
            if result.status in [QualityGateStatus.FAIL, QualityGateStatus.WARN]:
                if result.gate_type == QualityGateType.DURATION_LIMIT:
                    recommendations.append(
                        f"Optimize workflow to reduce total duration from {result.actual_value:.1f}ms to under {result.threshold}ms"
                    )
                elif result.gate_type == QualityGateType.PERFORMANCE_THRESHOLD:
                    recommendations.append(
                        f"Improve workflow performance score from {result.actual_value:.1f} to at least {result.threshold}"
                    )
                elif result.gate_type == QualityGateType.ERROR_RATE:
                    recommendations.append(
                        f"Reduce error rate from {result.actual_value:.3f} to under {result.threshold}"
                    )
                elif result.gate_type == QualityGateType.BOTTLENECK_DETECTION:
                    recommendations.append(
                        f"Address {result.actual_value} performance bottlenecks identified in the workflow"
                    )
                elif result.gate_type == QualityGateType.COLLECTION_POINT_LIMIT:
                    recommendations.append(
                        f"Optimize collection points to complete within {result.threshold}ms (current max: {result.actual_value:.1f}ms)"
                    )

        return recommendations


class QualityGateManager:
    """Manages quality gates and provides high-level interface"""

    def __init__(self, schema: Optional[PerformanceSchema] = None):
        self.evaluator = QualityGateEvaluator(schema)
        self.enforcer = QualityGateEnforcer(self.evaluator)

    def validate_workflow(self, workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate workflow against quality gates"""
        return self.enforcer.enforce_quality_gates(workflow_analysis)

    def get_quality_gate_summary(self, workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Get summary of quality gate results"""
        enforcement_result = self.validate_workflow(workflow_analysis)

        summary = {
            "workflow_id": enforcement_result["workflow_id"],
            "overall_status": enforcement_result["overall_status"].value,
            "total_gates": len(enforcement_result["gate_results"]),
            "passed_gates": len([r for r in enforcement_result["gate_results"] if r.status == QualityGateStatus.PASS]),
            "failed_gates": len([r for r in enforcement_result["gate_results"] if r.status == QualityGateStatus.FAIL]),
            "warning_gates": len([r for r in enforcement_result["gate_results"] if r.status == QualityGateStatus.WARN]),
            "error_gates": len([r for r in enforcement_result["gate_results"] if r.status == QualityGateStatus.ERROR]),
            "actions_taken": len(enforcement_result["actions_taken"]),
            "recommendations": enforcement_result["recommendations"],
        }

        return summary

    def is_workflow_approved(self, workflow_analysis: Dict[str, Any]) -> bool:
        """Check if workflow passes all critical quality gates"""
        enforcement_result = self.validate_workflow(workflow_analysis)
        return enforcement_result["overall_status"] not in [QualityGateStatus.FAIL, QualityGateStatus.ERROR]


# Global quality gate manager instance
quality_gate_manager = QualityGateManager()


# Convenience functions for easy integration
def validate_workflow_quality(workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Validate workflow against quality gates"""
    return quality_gate_manager.validate_workflow(workflow_analysis)


def get_quality_summary(workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Get quality gate summary for workflow"""
    return quality_gate_manager.get_quality_gate_summary(workflow_analysis)


def is_workflow_approved(workflow_analysis: Dict[str, Any]) -> bool:
    """Check if workflow is approved by quality gates"""
    return quality_gate_manager.is_workflow_approved(workflow_analysis)


def add_custom_quality_gate(
    name: str,
    gate_type: QualityGateType,
    threshold: Union[float, int],
    operator: str = "lte",
    severity: str = "warn",
    description: str = "",
) -> bool:
    """Add a custom quality gate rule"""
    try:
        rule = QualityGateRule(
            name=name,
            gate_type=gate_type,
            threshold=threshold,
            operator=operator,
            severity=severity,
            description=description,
        )
        quality_gate_manager.evaluator.default_suite.rules.append(rule)
        logger.info(f"Added custom quality gate: {name}")
        return True
    except Exception as e:
        logger.error(f"Failed to add custom quality gate: {e}")
        return False
