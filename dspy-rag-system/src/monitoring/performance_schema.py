#!/usr/bin/env python3
"""
Performance metrics schema for PRD creation workflow.
Defines data structures and collection points for performance monitoring.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class WorkflowPhase(Enum):
    """Workflow phases for performance tracking"""

    PRD_CREATION = "prd_creation"
    TASK_GENERATION = "task_generation"
    TASK_EXECUTION = "task_execution"
    VALIDATION = "validation"
    COMPLETION = "completion"


class CollectionPoint(Enum):
    """Key collection points in the workflow"""

    WORKFLOW_START = "workflow_start"
    SECTION_ANALYSIS = "section_analysis"
    TEMPLATE_PROCESSING = "template_processing"
    CONTEXT_INTEGRATION = "context_integration"
    VALIDATION_CHECK = "validation_check"
    WORKFLOW_COMPLETE = "workflow_complete"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class PerformanceMetric:
    """Base performance metric structure"""

    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    collection_point: CollectionPoint = CollectionPoint.WORKFLOW_START
    workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION
    duration_ms: float = 0.0
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowPerformanceData:
    """Complete workflow performance data"""

    workflow_id: str = field(default_factory=lambda: str(uuid4()))
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: datetime | None = None
    total_duration_ms: float = 0.0
    phase_durations: dict[WorkflowPhase, float] = field(default_factory=dict)
    collection_points: list[PerformanceMetric] = field(default_factory=list)
    success: bool = True
    error_count: int = 0
    backlog_item_id: str | None = None
    prd_file_path: str | None = None
    task_count: int = 0
    context_size_bytes: int = 0


@dataclass
class PerformanceSchema:
    """Performance metrics schema configuration"""

    # Schema validation rules
    max_duration_ms: float = 30000.0  # 30 seconds max per workflow
    min_duration_ms: float = 1.0  # 1ms minimum
    max_metadata_size: int = 1024  # 1KB max metadata
    max_collection_points: int = 100  # Max collection points per workflow

    # Performance thresholds
    warning_threshold_ms: float = 5000.0  # 5 seconds warning
    error_threshold_ms: float = 15000.0  # 15 seconds error

    # Data retention
    retention_days: int = 30  # Keep data for 30 days
    max_workflows_per_day: int = 1000  # Max workflows per day

    # Validation rules
    required_fields: list[str] = field(default_factory=lambda: ["collection_point", "workflow_phase"])

    # Collection point definitions
    collection_points: dict[CollectionPoint, dict[str, Any]] = field(
        default_factory=lambda: {
            CollectionPoint.WORKFLOW_START: {
                "description": "Workflow initialization",
                "expected_duration_ms": 100.0,
                "critical": True,
            },
            CollectionPoint.SECTION_ANALYSIS: {
                "description": "PRD section analysis and processing",
                "expected_duration_ms": 500.0,
                "critical": False,
            },
            CollectionPoint.TEMPLATE_PROCESSING: {
                "description": "Template processing and generation",
                "expected_duration_ms": 1000.0,
                "critical": True,
            },
            CollectionPoint.CONTEXT_INTEGRATION: {
                "description": "Context integration and validation",
                "expected_duration_ms": 200.0,
                "critical": False,
            },
            CollectionPoint.VALIDATION_CHECK: {
                "description": "Final validation and quality checks",
                "expected_duration_ms": 300.0,
                "critical": True,
            },
            CollectionPoint.WORKFLOW_COMPLETE: {
                "description": "Workflow completion and cleanup",
                "expected_duration_ms": 50.0,
                "critical": False,
            },
            CollectionPoint.ERROR_OCCURRED: {
                "description": "Error handling and recovery",
                "expected_duration_ms": 100.0,
                "critical": True,
            },
        }
    )


class PerformanceValidator:
    """Validates performance metrics against schema rules"""

    def __init__(self, schema: PerformanceSchema):
        self.schema = schema

    def validate_metric(self, metric: PerformanceMetric) -> list[str]:
        """Validate a single performance metric"""
        errors = []

        # Check required fields (except for workflow start/completion which may have 0 duration)
        for required_field in self.schema.required_fields:
            if not hasattr(metric, required_field) or getattr(metric, required_field) is None:
                errors.append(f"Missing required field: {required_field}")

        # Check duration bounds (allow 0ms for workflow start/completion)
        if metric.duration_ms < 0:
            errors.append(f"Duration cannot be negative: {metric.duration_ms}ms")
        elif metric.duration_ms > 0 and metric.duration_ms < self.schema.min_duration_ms:
            errors.append(f"Duration too short: {metric.duration_ms}ms < {self.schema.min_duration_ms}ms")

        if metric.duration_ms > self.schema.max_duration_ms:
            errors.append(f"Duration too long: {metric.duration_ms}ms > {self.schema.max_duration_ms}ms")

        # Check metadata size
        metadata_size = len(str(metric.metadata))
        if metadata_size > self.schema.max_metadata_size:
            errors.append(f"Metadata too large: {metadata_size} bytes > {self.schema.max_metadata_size} bytes")

        # Check collection point exists
        if metric.collection_point not in self.schema.collection_points:
            errors.append(f"Invalid collection point: {metric.collection_point}")

        return errors

    def validate_workflow_data(self, workflow_data: WorkflowPerformanceData) -> list[str]:
        """Validate complete workflow performance data"""
        errors = []

        # Check total duration
        if workflow_data.total_duration_ms > self.schema.max_duration_ms:
            errors.append(
                f"Total duration too long: {workflow_data.total_duration_ms}ms > {self.schema.max_duration_ms}ms"
            )

        # Check collection points count
        if len(workflow_data.collection_points) > self.schema.max_collection_points:
            errors.append(
                f"Too many collection points: {len(workflow_data.collection_points)} > {self.schema.max_collection_points}"
            )

        # Validate each collection point
        for metric in workflow_data.collection_points:
            metric_errors = self.validate_metric(metric)
            errors.extend([f"Collection point {metric.id}: {error}" for error in metric_errors])

        # Check workflow ID format
        if not workflow_data.workflow_id or len(workflow_data.workflow_id) < 10:
            errors.append("Invalid workflow ID format")

        return errors


class PerformanceAnalyzer:
    """Analyzes performance data for insights"""

    def __init__(self, schema: PerformanceSchema):
        self.schema = schema

    def analyze_workflow_performance(self, workflow_data: WorkflowPerformanceData) -> dict[str, Any]:
        """Analyze workflow performance and return insights"""
        analysis = {
            "workflow_id": workflow_data.workflow_id,
            "total_duration_ms": workflow_data.total_duration_ms,
            "success": workflow_data.success,
            "error_count": workflow_data.error_count,
            "performance_score": 0.0,
            "bottlenecks": [],
            "recommendations": [],
            "warnings": [],
        }

        # Calculate performance score (0-100)
        if workflow_data.success and workflow_data.total_duration_ms > 0:
            # Score based on duration and error count
            duration_score = max(0, 100 - (workflow_data.total_duration_ms / 1000))  # 100 points for 1 second
            error_penalty = workflow_data.error_count * 10  # 10 point penalty per error
            analysis["performance_score"] = max(0, duration_score - error_penalty)

        # Identify bottlenecks
        for metric in workflow_data.collection_points:
            expected_duration = self.schema.collection_points[metric.collection_point]["expected_duration_ms"]
            if metric.duration_ms > expected_duration * 2:  # 2x expected duration
                analysis["bottlenecks"].append(
                    {
                        "collection_point": metric.collection_point.value,
                        "actual_duration_ms": metric.duration_ms,
                        "expected_duration_ms": expected_duration,
                        "overhead_ms": metric.duration_ms - expected_duration,
                    }
                )

        # Generate warnings
        if workflow_data.total_duration_ms > self.schema.warning_threshold_ms:
            analysis["warnings"].append(
                f"Workflow duration ({workflow_data.total_duration_ms}ms) exceeds warning threshold ({self.schema.warning_threshold_ms}ms)"
            )

        if workflow_data.error_count > 0:
            analysis["warnings"].append(f"Workflow completed with {workflow_data.error_count} errors")

        # Generate recommendations
        if analysis["bottlenecks"]:
            slowest_bottleneck = max(analysis["bottlenecks"], key=lambda x: x["overhead_ms"])
            analysis["recommendations"].append(
                f"Optimize {slowest_bottleneck['collection_point']} - current: {slowest_bottleneck['actual_duration_ms']}ms, expected: {slowest_bottleneck['expected_duration_ms']}ms"
            )

        if workflow_data.error_count > 0:
            analysis["recommendations"].append("Review error handling and improve error recovery")

        return analysis


# Global schema instance
PERFORMANCE_SCHEMA = PerformanceSchema()
PERFORMANCE_VALIDATOR = PerformanceValidator(PERFORMANCE_SCHEMA)
PERFORMANCE_ANALYZER = PerformanceAnalyzer(PERFORMANCE_SCHEMA)


def get_schema_overhead_ms() -> float:
    """Calculate schema validation overhead"""
    start_time = time.time()

    # Simulate schema validation overhead
    test_metric = PerformanceMetric(
        collection_point=CollectionPoint.WORKFLOW_START, workflow_phase=WorkflowPhase.PRD_CREATION, duration_ms=100.0
    )

    PERFORMANCE_VALIDATOR.validate_metric(test_metric)

    overhead_ms = (time.time() - start_time) * 1000
    return overhead_ms


def validate_schema_performance() -> dict[str, Any]:
    """Validate that schema meets performance requirements"""
    overhead_ms = get_schema_overhead_ms()

    validation_result = {
        "schema_overhead_ms": overhead_ms,
        "meets_requirement": overhead_ms < 1.0,  # <1ms requirement
        "performance_grade": "A" if overhead_ms < 0.5 else "B" if overhead_ms < 1.0 else "C",
        "recommendations": [],
    }

    if overhead_ms >= 1.0:
        validation_result["recommendations"].append("Optimize schema validation to meet <1ms requirement")

    return validation_result
