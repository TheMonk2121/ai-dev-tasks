#!/usr/bin/env python3
"""
Tests for performance metrics schema.
Validates schema design, validation rules, and performance requirements.
"""

import time
from datetime import datetime

import pytest

from src.monitoring.performance_schema import (
    CollectionPoint,
    PerformanceAnalyzer,
    PerformanceMetric,
    PerformanceSchema,
    PerformanceValidator,
    WorkflowPerformanceData,
    WorkflowPhase,
    get_schema_overhead_ms,
    validate_schema_performance,
)


class TestPerformanceSchema:
    """Test performance schema design and validation"""

    def test_schema_overhead_requirement(self):
        """Test that schema overhead is <1ms"""
        overhead_ms = get_schema_overhead_ms()
        assert overhead_ms < 1.0, f"Schema overhead {overhead_ms}ms exceeds 1ms requirement"

    def test_performance_validation(self):
        """Test schema performance validation"""
        result = validate_schema_performance()
        assert result["meets_requirement"] is True
        assert result["performance_grade"] in ["A", "B"]
        assert result["schema_overhead_ms"] < 1.0

    def test_metric_creation(self):
        """Test performance metric creation"""
        metric = PerformanceMetric(
            collection_point=CollectionPoint.WORKFLOW_START,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=100.0,
        )

        assert metric.id is not None
        assert len(metric.id) > 10
        assert metric.timestamp is not None
        assert metric.collection_point == CollectionPoint.WORKFLOW_START
        assert metric.workflow_phase == WorkflowPhase.PRD_CREATION
        assert metric.duration_ms == 100.0
        assert metric.success is True

    def test_workflow_data_creation(self):
        """Test workflow performance data creation"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077", prd_file_path="artifacts/prds/PRD-B-077.md", task_count=18
        )

        assert workflow_data.workflow_id is not None
        assert len(workflow_data.workflow_id) > 10
        assert workflow_data.start_time is not None
        assert workflow_data.backlog_item_id == "B-077"
        assert workflow_data.prd_file_path == "artifacts/prds/PRD-B-077.md"
        assert workflow_data.task_count == 18
        assert workflow_data.success is True
        assert workflow_data.error_count == 0

    def test_schema_configuration(self):
        """Test schema configuration values"""
        schema = PerformanceSchema()

        # Test performance thresholds
        assert schema.max_duration_ms == 30000.0
        assert schema.min_duration_ms == 1.0
        assert schema.warning_threshold_ms == 5000.0
        assert schema.error_threshold_ms == 15000.0

        # Test data retention
        assert schema.retention_days == 30
        assert schema.max_workflows_per_day == 1000

        # Test validation rules
        assert "workflow_id" in schema.required_fields
        assert "start_time" in schema.required_fields
        assert "collection_point" in schema.required_fields
        assert "workflow_phase" in schema.required_fields

    def test_collection_points_definition(self):
        """Test collection points are properly defined"""
        schema = PerformanceSchema()

        # Test all collection points exist
        for collection_point in CollectionPoint:
            assert collection_point in schema.collection_points

        # Test collection point structure
        for collection_point, config in schema.collection_points.items():
            assert "description" in config
            assert "expected_duration_ms" in config
            assert "critical" in config
            assert isinstance(config["expected_duration_ms"], (int, float))
            assert isinstance(config["critical"], bool)


class TestPerformanceValidator:
    """Test performance validation logic"""

    def setup_method(self):
        """Setup validator for each test"""
        self.schema = PerformanceSchema()
        self.validator = PerformanceValidator(self.schema)

    def test_valid_metric_validation(self):
        """Test validation of valid performance metric"""
        metric = PerformanceMetric(
            collection_point=CollectionPoint.WORKFLOW_START,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=100.0,
        )

        errors = self.validator.validate_metric(metric)
        assert len(errors) == 0, f"Valid metric should have no errors: {errors}"

    def test_invalid_duration_validation(self):
        """Test validation of invalid duration"""
        # Test duration too short
        metric_short = PerformanceMetric(
            collection_point=CollectionPoint.WORKFLOW_START,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=0.5,  # Below minimum
        )
        errors_short = self.validator.validate_metric(metric_short)
        assert len(errors_short) > 0
        assert any("Duration too short" in error for error in errors_short)

        # Test duration too long
        metric_long = PerformanceMetric(
            collection_point=CollectionPoint.WORKFLOW_START,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=35000.0,  # Above maximum
        )
        errors_long = self.validator.validate_metric(metric_long)
        assert len(errors_long) > 0
        assert any("Duration too long" in error for error in errors_long)

    def test_large_metadata_validation(self):
        """Test validation of large metadata"""
        large_metadata = {"data": "x" * 2000}  # 2KB metadata
        metric = PerformanceMetric(
            collection_point=CollectionPoint.WORKFLOW_START,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=100.0,
            metadata=large_metadata,
        )

        errors = self.validator.validate_metric(metric)
        assert len(errors) > 0
        assert any("Metadata too large" in error for error in errors)

    def test_workflow_data_validation(self):
        """Test validation of complete workflow data"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077", prd_file_path="artifacts/prds/PRD-B-077.md", task_count=18
        )

        # Add some collection points
        for i in range(5):
            metric = PerformanceMetric(
                collection_point=CollectionPoint.WORKFLOW_START,
                workflow_phase=WorkflowPhase.PRD_CREATION,
                duration_ms=100.0 + i,
            )
            workflow_data.collection_points.append(metric)

        errors = self.validator.validate_workflow_data(workflow_data)
        assert len(errors) == 0, f"Valid workflow data should have no errors: {errors}"

    def test_workflow_data_with_errors(self):
        """Test validation of workflow data with errors"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077",
            prd_file_path="artifacts/prds/PRD-B-077.md",
            task_count=18,
            total_duration_ms=35000.0,  # Above maximum
        )

        errors = self.validator.validate_workflow_data(workflow_data)
        assert len(errors) > 0
        assert any("Total duration too long" in error for error in errors)


class TestPerformanceAnalyzer:
    """Test performance analysis logic"""

    def setup_method(self):
        """Setup analyzer for each test"""
        self.schema = PerformanceSchema()
        self.analyzer = PerformanceAnalyzer(self.schema)

    def test_successful_workflow_analysis(self):
        """Test analysis of successful workflow"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077",
            prd_file_path="artifacts/prds/PRD-B-077.md",
            task_count=18,
            total_duration_ms=2000.0,  # 2 seconds
        )

        # Add collection points
        for collection_point in [
            CollectionPoint.WORKFLOW_START,
            CollectionPoint.SECTION_ANALYSIS,
            CollectionPoint.TEMPLATE_PROCESSING,
            CollectionPoint.WORKFLOW_COMPLETE,
        ]:
            metric = PerformanceMetric(
                collection_point=collection_point, workflow_phase=WorkflowPhase.PRD_CREATION, duration_ms=500.0
            )
            workflow_data.collection_points.append(metric)

        analysis = self.analyzer.analyze_workflow_performance(workflow_data)

        assert analysis["workflow_id"] == workflow_data.workflow_id
        assert analysis["total_duration_ms"] == 2000.0
        assert analysis["success"] is True
        assert analysis["error_count"] == 0
        assert analysis["performance_score"] > 0
        assert len(analysis["bottlenecks"]) == 0
        assert len(analysis["warnings"]) == 0

    def test_workflow_with_bottlenecks(self):
        """Test analysis of workflow with bottlenecks"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077",
            prd_file_path="artifacts/prds/PRD-B-077.md",
            task_count=18,
            total_duration_ms=8000.0,  # 8 seconds (above warning threshold)
        )

        # Add a bottleneck (slow template processing)
        slow_metric = PerformanceMetric(
            collection_point=CollectionPoint.TEMPLATE_PROCESSING,
            workflow_phase=WorkflowPhase.PRD_CREATION,
            duration_ms=3000.0,  # 3x expected duration
        )
        workflow_data.collection_points.append(slow_metric)

        analysis = self.analyzer.analyze_workflow_performance(workflow_data)

        assert len(analysis["bottlenecks"]) > 0
        assert len(analysis["warnings"]) > 0
        assert any("template_processing" in bottleneck["collection_point"] for bottleneck in analysis["bottlenecks"])
        assert any("warning threshold" in warning for warning in analysis["warnings"])

    def test_workflow_with_errors(self):
        """Test analysis of workflow with errors"""
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077",
            prd_file_path="artifacts/prds/PRD-B-077.md",
            task_count=18,
            total_duration_ms=2000.0,
            success=False,
            error_count=2,
        )

        analysis = self.analyzer.analyze_workflow_performance(workflow_data)

        assert analysis["success"] is False
        assert analysis["error_count"] == 2
        assert len(analysis["warnings"]) > 0
        assert any("errors" in warning for warning in analysis["warnings"])
        assert len(analysis["recommendations"]) > 0
        assert any("error handling" in rec for rec in analysis["recommendations"])


class TestIntegration:
    """Integration tests for the complete schema system"""

    def test_complete_workflow_tracking(self):
        """Test complete workflow tracking from start to finish"""
        # Create workflow data
        workflow_data = WorkflowPerformanceData(
            backlog_item_id="B-077", prd_file_path="artifacts/prds/PRD-B-077.md", task_count=18
        )

        # Simulate workflow execution with collection points
        collection_points = [
            (CollectionPoint.WORKFLOW_START, 50.0),
            (CollectionPoint.SECTION_ANALYSIS, 400.0),
            (CollectionPoint.TEMPLATE_PROCESSING, 800.0),
            (CollectionPoint.CONTEXT_INTEGRATION, 150.0),
            (CollectionPoint.VALIDATION_CHECK, 200.0),
            (CollectionPoint.WORKFLOW_COMPLETE, 30.0),
        ]

        for collection_point, duration in collection_points:
            metric = PerformanceMetric(
                collection_point=collection_point, workflow_phase=WorkflowPhase.PRD_CREATION, duration_ms=duration
            )
            workflow_data.collection_points.append(metric)

        # Calculate total duration
        workflow_data.total_duration_ms = sum(duration for _, duration in collection_points)
        workflow_data.end_time = datetime.utcnow()

        # Validate workflow data
        schema = PerformanceSchema()
        validator = PerformanceValidator(schema)
        analyzer = PerformanceAnalyzer(schema)

        # Test validation
        errors = validator.validate_workflow_data(workflow_data)
        assert len(errors) == 0, f"Workflow validation failed: {errors}"

        # Test analysis
        analysis = analyzer.analyze_workflow_performance(workflow_data)
        assert analysis["success"] is True
        assert analysis["total_duration_ms"] == workflow_data.total_duration_ms
        assert analysis["performance_score"] > 0

    def test_schema_performance_under_load(self):
        """Test schema performance under load"""
        schema = PerformanceSchema()
        validator = PerformanceValidator(schema)

        # Create multiple metrics
        metrics = []
        for i in range(100):
            metric = PerformanceMetric(
                collection_point=CollectionPoint.WORKFLOW_START,
                workflow_phase=WorkflowPhase.PRD_CREATION,
                duration_ms=100.0 + i,
            )
            metrics.append(metric)

        # Measure validation performance
        start_time = time.time()
        for metric in metrics:
            errors = validator.validate_metric(metric)
            assert len(errors) == 0
        end_time = time.time()

        total_time_ms = (end_time - start_time) * 1000
        avg_time_ms = total_time_ms / len(metrics)

        # Should be very fast (under 1ms per metric)
        assert avg_time_ms < 1.0, f"Average validation time {avg_time_ms:.3f}ms exceeds 1ms requirement"


if __name__ == "__main__":
    # Run performance validation
    result = validate_schema_performance()
    print(f"Schema Performance: {result['schema_overhead_ms']:.3f}ms ({result['performance_grade']})")
    print(f"Meets Requirement: {result['meets_requirement']}")

    # Run tests
    pytest.main([__file__, "-v"])
