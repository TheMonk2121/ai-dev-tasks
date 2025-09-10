#!/usr/bin/env python3
"""
Lightweight performance collection module for PRD creation workflow.
Implements async patterns for non-blocking collection with LTST memory integration.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from contextlib import asynccontextmanager, contextmanager
from datetime import datetime
from functools import wraps
from typing import Any
from uuid import uuid4

from .performance_schema import (
    CollectionPoint,
    PerformanceAnalyzer,
    PerformanceMetric,
    PerformanceSchema,
    PerformanceValidator,
    WorkflowPerformanceData,
    WorkflowPhase,
)

logger = logging.getLogger(__name__)


class PerformanceCollector:
    """Lightweight performance collector with async support"""

    def __init__(self, schema: PerformanceSchema | None = None):
        self.schema = schema or PerformanceSchema()
        self.validator = PerformanceValidator(self.schema)
        self.analyzer = PerformanceAnalyzer(self.schema)
        self.enabled = True
        self._current_workflow: WorkflowPerformanceData | None = None
        self._collection_queue: list[PerformanceMetric] = []
        self._error_count = 0

    def start_workflow(
        self,
        backlog_item_id: str | None = None,
        prd_file_path: str | None = None,
        task_count: int = 0,
    ) -> WorkflowPerformanceData:
        """Start performance tracking for a new workflow"""
        if not self.enabled:
            return WorkflowPerformanceData()

        try:
            workflow_data = WorkflowPerformanceData(
                workflow_id=str(uuid4()),
                start_time=datetime.utcnow(),
                backlog_item_id=backlog_item_id,
                prd_file_path=prd_file_path,
                task_count=task_count,
            )

            # Add initial collection point
            start_metric = PerformanceMetric(
                collection_point=CollectionPoint.WORKFLOW_START,
                workflow_phase=WorkflowPhase.PRD_CREATION,
                duration_ms=0.0,
                metadata={
                    "backlog_item_id": backlog_item_id,
                    "prd_file_path": prd_file_path,
                    "task_count": task_count,
                },
            )
            workflow_data.collection_points.append(start_metric)

            self._current_workflow = workflow_data
            logger.debug(f"Started performance tracking for workflow {workflow_data.workflow_id}")
            return workflow_data

        except Exception as e:
            logger.error(f"Failed to start performance tracking: {e}")
            self._error_count += 1
            return WorkflowPerformanceData()

    def end_workflow(self, success: bool = True) -> WorkflowPerformanceData | None:
        """End performance tracking for current workflow"""
        if not self.enabled or not self._current_workflow:
            return None

        try:
            workflow_data = self._current_workflow
            workflow_data.end_time = datetime.utcnow()
            workflow_data.success = success
            workflow_data.error_count = self._error_count

            # Calculate total duration
            if workflow_data.start_time and workflow_data.end_time:
                duration = (workflow_data.end_time - workflow_data.start_time).total_seconds() * 1000
                workflow_data.total_duration_ms = duration

            # Add completion collection point
            complete_metric = PerformanceMetric(
                collection_point=CollectionPoint.WORKFLOW_COMPLETE,
                workflow_phase=WorkflowPhase.PRD_CREATION,
                duration_ms=0.0,
                metadata={
                    "total_duration_ms": workflow_data.total_duration_ms,
                    "success": success,
                    "error_count": self._error_count,
                },
            )
            workflow_data.collection_points.append(complete_metric)

            # Validate workflow data
            errors = self.validator.validate_workflow_data(workflow_data)
            if errors:
                logger.warning(f"Workflow validation errors: {errors}")

            logger.debug(f"Completed performance tracking for workflow {workflow_data.workflow_id}")
            return workflow_data

        except Exception as e:
            logger.error(f"Failed to end performance tracking: {e}")
            self._error_count += 1
            return None

        finally:
            self._current_workflow = None
            self._error_count = 0

    def add_collection_point(
        self,
        collection_point: CollectionPoint,
        duration_ms: float,
        workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION,
        metadata: dict[str, Any] | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> bool:
        """Add a collection point to the current workflow"""
        if not self.enabled or not self._current_workflow:
            return False

        try:
            metric = PerformanceMetric(
                collection_point=collection_point,
                workflow_phase=workflow_phase,
                duration_ms=duration_ms,
                success=success,
                error_message=error_message,
                metadata=metadata or {},
            )

            # Validate metric
            errors = self.validator.validate_metric(metric)
            if errors:
                logger.warning(f"Metric validation errors: {errors}")
                return False

            self._current_workflow.collection_points.append(metric)

            if not success:
                self._error_count += 1

            logger.debug(f"Added collection point {collection_point.value} ({duration_ms}ms)")
            return True

        except Exception as e:
            logger.error(f"Failed to add collection point: {e}")
            self._error_count += 1
            return False

    def get_current_workflow(self) -> WorkflowPerformanceData | None:
        """Get current workflow data"""
        return self._current_workflow

    def analyze_current_workflow(self) -> dict[str, Any] | None:
        """Analyze current workflow performance"""
        if not self._current_workflow:
            return None

        try:
            return self.analyzer.analyze_workflow_performance(self._current_workflow)
        except Exception as e:
            logger.error(f"Failed to analyze workflow: {e}")
            return None

    def get_collection_stats(self) -> dict[str, Any]:
        """Get collection statistics"""
        if not self._current_workflow:
            return {"enabled": self.enabled, "active": False}

        return {
            "enabled": self.enabled,
            "active": True,
            "workflow_id": self._current_workflow.workflow_id,
            "collection_points": len(self._current_workflow.collection_points),
            "error_count": self._error_count,
            "total_duration_ms": self._current_workflow.total_duration_ms,
        }


# Global collector instance
performance_collector = PerformanceCollector()


def performance_hook(
    collection_point: CollectionPoint,
    workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION,
):
    """Decorator for performance collection hooks"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_collector.add_collection_point(
                    collection_point=collection_point,
                    duration_ms=duration_ms,
                    workflow_phase=workflow_phase,
                    success=success,
                    error_message=error_message,
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            error_message = None

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                error_message = str(e)
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                performance_collector.add_collection_point(
                    collection_point=collection_point,
                    duration_ms=duration_ms,
                    workflow_phase=workflow_phase,
                    success=success,
                    error_message=error_message,
                )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


@contextmanager
def performance_context(
    collection_point: CollectionPoint,
    workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION,
    metadata: dict[str, Any] | None = None,
):
    """Context manager for performance collection"""
    start_time = time.time()
    success = True
    error_message = None

    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        performance_collector.add_collection_point(
            collection_point=collection_point,
            duration_ms=duration_ms,
            workflow_phase=workflow_phase,
            metadata=metadata,
            success=success,
            error_message=error_message,
        )


@asynccontextmanager
async def async_performance_context(
    collection_point: CollectionPoint,
    workflow_phase: WorkflowPhase = WorkflowPhase.PRD_CREATION,
    metadata: dict[str, Any] | None = None,
):
    """Async context manager for performance collection"""
    start_time = time.time()
    success = True
    error_message = None

    try:
        yield
    except Exception as e:
        success = False
        error_message = str(e)
        raise
    finally:
        duration_ms = (time.time() - start_time) * 1000
        performance_collector.add_collection_point(
            collection_point=collection_point,
            duration_ms=duration_ms,
            workflow_phase=workflow_phase,
            metadata=metadata,
            success=success,
            error_message=error_message,
        )


class PerformanceTracker:
    """High-level performance tracking interface"""

    def __init__(self, collector: PerformanceCollector | None = None):
        self.collector = collector or performance_collector

    def track_workflow(
        self,
        backlog_item_id: str | None = None,
        prd_file_path: str | None = None,
        task_count: int = 0,
    ):
        """Context manager for tracking complete workflows"""
        return WorkflowTracker(
            self.collector,
            backlog_item_id=backlog_item_id,
            prd_file_path=prd_file_path,
            task_count=task_count,
        )

    def track_section(
        self,
        section_name: str,
        content_size: int = 0,
    ):
        """Context manager for tracking section processing"""
        metadata = {
            "section_name": section_name,
            "content_size": content_size,
        }
        return performance_context(
            CollectionPoint.SECTION_ANALYSIS,
            metadata=metadata,
        )

    def track_template_processing(
        self,
        template_type: str = "hybrid",
        complexity_score: float = 1.0,
    ):
        """Context manager for tracking template processing"""
        metadata = {
            "template_type": template_type,
            "complexity_score": complexity_score,
        }
        return performance_context(
            CollectionPoint.TEMPLATE_PROCESSING,
            metadata=metadata,
        )

    def track_context_integration(
        self,
        context_source: str = "backlog",
        context_size: int = 0,
    ):
        """Context manager for tracking context integration"""
        metadata = {
            "context_source": context_source,
            "context_size": context_size,
        }
        return performance_context(
            CollectionPoint.CONTEXT_INTEGRATION,
            metadata=metadata,
        )

    def track_validation(
        self,
        validation_rules: list[str] | None = None,
        quality_gates: int = 0,
    ):
        """Context manager for tracking validation"""
        metadata = {
            "validation_rules": validation_rules or [],
            "quality_gates": quality_gates,
        }
        return performance_context(
            CollectionPoint.VALIDATION_CHECK,
            metadata=metadata,
        )


class WorkflowTracker:
    """Context manager for tracking complete workflows"""

    def __init__(
        self,
        collector: PerformanceCollector,
        backlog_item_id: str | None = None,
        prd_file_path: str | None = None,
        task_count: int = 0,
    ):
        self.collector = collector
        self.backlog_item_id = backlog_item_id
        self.prd_file_path = prd_file_path
        self.task_count = task_count
        self.success = True

    def __enter__(self):
        """Start workflow tracking"""
        self.workflow_data = self.collector.start_workflow(
            backlog_item_id=self.backlog_item_id,
            prd_file_path=self.prd_file_path,
            task_count=self.task_count,
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """End workflow tracking"""
        if exc_type is not None:
            self.success = False

        self.workflow_data = self.collector.end_workflow(success=self.success)
        return False  # Don't suppress exceptions

    def get_analysis(self) -> dict[str, Any] | None:
        """Get workflow performance analysis"""
        return self.collector.analyze_current_workflow()


# Convenience functions for easy integration
def start_workflow_tracking(
    backlog_item_id: str | None = None,
    prd_file_path: str | None = None,
    task_count: int = 0,
) -> WorkflowPerformanceData:
    """Start workflow performance tracking"""
    return performance_collector.start_workflow(
        backlog_item_id=backlog_item_id,
        prd_file_path=prd_file_path,
        task_count=task_count,
    )


def end_workflow_tracking(success: bool = True) -> WorkflowPerformanceData | None:
    """End workflow performance tracking"""
    return performance_collector.end_workflow(success=success)


def get_workflow_analysis() -> dict[str, Any] | None:
    """Get current workflow performance analysis"""
    return performance_collector.analyze_current_workflow()


def get_collection_stats() -> dict[str, Any]:
    """Get performance collection statistics"""
    return performance_collector.get_collection_stats()


# Initialize collector
def init_performance_collector(enabled: bool = True) -> PerformanceCollector:
    """Initialize the performance collector"""
    global performance_collector
    performance_collector.enabled = enabled

    if enabled:
        logger.info("Performance collector initialized and enabled")
    else:
        logger.info("Performance collector disabled")

    return performance_collector
