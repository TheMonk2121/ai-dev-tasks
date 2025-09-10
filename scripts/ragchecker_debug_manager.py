#!/usr/bin/env python3
"""
RAGChecker Debug Manager with Enhanced Debugging Integration
Integrates enhanced debugging capabilities with RAGChecker evaluation workflows.
"""

import logging
import os
import sys
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, Optional

# Add dspy-rag-system to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))

try:
    from pydantic import BaseModel, Field
    from src.dspy_modules.enhanced_debugging import (
        DebuggingContext,
        EnhancedDebuggingManager,
        RichErrorMessage,
        StructuredLogEntry,
        enhanced_debugging,
    )
    from src.dspy_modules.error_taxonomy import ErrorSeverity
except ImportError as e:
    print(f"⚠️  Warning: Could not import enhanced debugging modules: {e}")
    print("   Enhanced debugging will be disabled")
    EnhancedDebuggingManager = None
    enhanced_debugging = None
    DebuggingContext = None
    RichErrorMessage = None
    StructuredLogEntry = None
    ErrorSeverity = None

    # Provide safe fallbacks so type checking and runtime don't break
    class _FallbackBaseModel:  # minimal stand-in for Pydantic BaseModel
        pass

    def _fallback_field(*args, **kwargs):  # returns a sentinel None/default
        default = kwargs.get("default", None)
        # If default_factory provided, prefer callable() at runtime when used
        if "default_factory" in kwargs:
            try:
                return kwargs["default_factory"]()
            except Exception:
                return None
        return default

    BaseModel = _FallbackBaseModel  # type: ignore[assignment]
    Field = _fallback_field  # type: ignore[assignment]

# Static typing aliases to satisfy pyright while keeping runtime fallbacks
if TYPE_CHECKING:
    from pydantic import BaseModel as PydanticModel
    from pydantic import Field as PydField
else:
    PydanticModel = BaseModel  # type: ignore[assignment]
    PydField = Field  # type: ignore[assignment]


class RAGCheckerDebugContext(PydanticModel):
    """RAGChecker-specific debugging context"""

    evaluation_id: str = PydField(..., description="Unique evaluation identifier")
    evaluation_type: str = PydField(..., description="Type of evaluation (input, metrics, result)")
    validation_stage: str = PydField(..., description="Current validation stage")
    pydantic_validation_context: Dict[str, Any] = PydField(
        default_factory=dict, description="Pydantic validation context"
    )
    constitution_validation_context: Dict[str, Any] = PydField(
        default_factory=dict, description="Constitution validation context"
    )
    error_taxonomy_context: Dict[str, Any] = PydField(default_factory=dict, description="Error taxonomy context")
    performance_metrics: Dict[str, Any] = PydField(default_factory=dict, description="Performance metrics")
    timestamp: datetime = PydField(default_factory=datetime.now, description="Context timestamp")


class RAGCheckerDebugManager:
    """Enhanced debugging manager for RAGChecker evaluation workflows"""

    def __init__(self, enable_privacy: bool = True, capture_variables: bool = True):
        """Initialize RAGChecker debug manager"""
        self.enable_privacy = enable_privacy
        self.capture_variables = capture_variables

        # Initialize enhanced debugging manager if available
        self.debug_manager: Optional[Any] = None
        self.enhanced_debugging_enabled = False

        if EnhancedDebuggingManager is not None:
            self.debug_manager = EnhancedDebuggingManager(enable_privacy=enable_privacy, max_context_history=100)
            self.enhanced_debugging_enabled = True

        # RAGChecker-specific logging
        self.logger = logging.getLogger("ragchecker_debug")
        self.logger.setLevel(logging.DEBUG)

        # Create console handler if none exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

    def capture_ragchecker_context(
        self, evaluation_id: str, evaluation_type: str, validation_stage: str, **context_data
    ) -> RAGCheckerDebugContext:
        """Capture RAGChecker-specific debugging context"""
        context = RAGCheckerDebugContext(
            evaluation_id=evaluation_id,
            evaluation_type=evaluation_type,
            validation_stage=validation_stage,
            **context_data,
        )

        # Log context capture
        self.logger.debug(f"Captured RAGChecker context: {evaluation_id} - {evaluation_type} - {validation_stage}")

        return context

    def log_pydantic_validation(
        self, context: RAGCheckerDebugContext, validation_result: Dict[str, Any], performance_overhead: float
    ) -> None:
        """Log Pydantic validation with enhanced debugging"""
        # Update context with validation results
        context.pydantic_validation_context = {
            "validation_result": validation_result,
            "performance_overhead": performance_overhead,
            "timestamp": datetime.now().isoformat(),
        }

        # Log to standard logger
        self.logger.info(
            f"Pydantic validation completed for {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Overhead: {performance_overhead:.4f}s"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            self.debug_manager.log_structured_entry(
                level="INFO",
                message=f"Pydantic validation completed for {context.evaluation_id}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "performance_overhead": performance_overhead,
                    "validation_result": validation_result,
                },
                source="ragchecker_pydantic_validation",
            )

    def log_constitution_validation(
        self, context: RAGCheckerDebugContext, validation_result: Dict[str, Any], compliance_score: float
    ) -> None:
        """Log constitution validation with enhanced debugging"""
        # Update context with validation results
        context.constitution_validation_context = {
            "validation_result": validation_result,
            "compliance_score": compliance_score,
            "timestamp": datetime.now().isoformat(),
        }

        # Log to standard logger
        self.logger.info(
            f"Constitution validation completed for {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Compliance: {compliance_score:.3f}"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            self.debug_manager.log_structured_entry(
                level="INFO",
                message=f"Constitution validation completed for {context.evaluation_id}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "compliance_score": compliance_score,
                    "validation_result": validation_result,
                },
                source="ragchecker_constitution_validation",
            )

    def log_error_taxonomy_mapping(
        self, context: RAGCheckerDebugContext, mapping_result: Dict[str, Any], categorization_success_rate: float
    ) -> None:
        """Log error taxonomy mapping with enhanced debugging"""
        # Update context with mapping results
        context.error_taxonomy_context = {
            "mapping_result": mapping_result,
            "categorization_success_rate": categorization_success_rate,
            "timestamp": datetime.now().isoformat(),
        }

        # Log to standard logger
        self.logger.info(
            f"Error taxonomy mapping completed for {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Success Rate: {categorization_success_rate:.3f}"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            self.debug_manager.log_structured_entry(
                level="INFO",
                message=f"Error taxonomy mapping completed for {context.evaluation_id}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "categorization_success_rate": categorization_success_rate,
                    "mapping_result": mapping_result,
                },
                source="ragchecker_error_taxonomy",
            )

    def log_performance_metrics(self, context: RAGCheckerDebugContext, metrics: Dict[str, float]) -> None:
        """Log performance metrics with enhanced debugging"""
        # Update context with performance metrics
        context.performance_metrics.update(metrics)
        context.performance_metrics["timestamp"] = datetime.now().isoformat()

        # Log to standard logger
        self.logger.info(
            f"Performance metrics recorded for {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Metrics: {metrics}"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            self.debug_manager.log_structured_entry(
                level="INFO",
                message=f"Performance metrics recorded for {context.evaluation_id}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "performance_metrics": metrics,
                },
                source="ragchecker_performance",
            )

    def log_validation_error(
        self, context: RAGCheckerDebugContext, error: Exception, error_type: str, error_details: Dict[str, Any]
    ) -> None:
        """Log validation errors with enhanced debugging"""
        # Log to standard logger
        self.logger.error(
            f"Validation error in {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Type: {error_type}, Details: {error_details}"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            # Create rich error message
            rich_error = self.debug_manager.create_rich_error_message(
                error=error, debugging_context=self._convert_to_debugging_context(context)
            )

            # Log structured error
            self.debug_manager.log_structured_entry(
                level="ERROR",
                message=f"Validation error in {context.evaluation_id}: {rich_error.user_friendly_message}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "error_type": error_type,
                    "error_details": error_details,
                    "error_id": rich_error.error_id,
                },
                source="ragchecker_validation_error",
            )

    def log_validation_warning(
        self, context: RAGCheckerDebugContext, warning_message: str, warning_details: Dict[str, Any]
    ) -> None:
        """Log validation warnings with enhanced debugging"""
        # Log to standard logger
        self.logger.warning(
            f"Validation warning in {context.evaluation_id} - "
            f"Stage: {context.validation_stage}, Message: {warning_message}"
        )

        # Use enhanced debugging if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            self.debug_manager.log_structured_entry(
                level="WARNING",
                message=f"Validation warning in {context.evaluation_id}: {warning_message}",
                context_data={
                    "evaluation_id": context.evaluation_id,
                    "validation_stage": context.validation_stage,
                    "warning_details": warning_details,
                },
                source="ragchecker_validation_warning",
            )

    def get_debugging_summary(self) -> Dict[str, Any]:
        """Get debugging summary for RAGChecker workflows"""
        summary = {
            "ragchecker_contexts": [],
            "enhanced_debugging_enabled": self.enhanced_debugging_enabled,
            "timestamp": datetime.now().isoformat(),
        }

        # Add enhanced debugging summary if available
        if self.enhanced_debugging_enabled and self.debug_manager:
            enhanced_summary = self.debug_manager.get_debugging_summary()
            summary["enhanced_debugging_summary"] = enhanced_summary

        return summary

    def _convert_to_debugging_context(self, context: RAGCheckerDebugContext) -> Optional[Any]:
        """Convert RAGChecker context to enhanced debugging context"""
        if not self.enhanced_debugging_enabled or not self.debug_manager:
            return None

        if DebuggingContext is None:
            return None

        try:
            return DebuggingContext(
                context_id=context.evaluation_id,
                user_context=None,
                role_context=None,
                correlation_id=context.evaluation_id,
                variable_snapshot={
                    "evaluation_type": context.evaluation_type,
                    "validation_stage": context.validation_stage,
                    "pydantic_context": context.pydantic_validation_context,
                    "constitution_context": context.constitution_validation_context,
                    "taxonomy_context": context.error_taxonomy_context,
                    "performance_metrics": context.performance_metrics,
                },
                timestamp=context.timestamp,
            )
        except Exception as e:
            self.logger.error(f"Failed to convert context: {e}")
            return None


def create_ragchecker_debug_manager(
    enable_privacy: bool = True, capture_variables: bool = True
) -> RAGCheckerDebugManager:
    """Factory function to create a RAGChecker debug manager"""
    return RAGCheckerDebugManager(enable_privacy=enable_privacy, capture_variables=capture_variables)


def ragchecker_debug_logging(evaluation_type: str = "general"):
    """Decorator for RAGChecker debugging with enhanced logging"""

    def decorator(func):
        if enhanced_debugging is not None:
            # Use enhanced debugging decorator
            @enhanced_debugging(enable_privacy=True)
            def enhanced_wrapper(*args, **kwargs):
                return func(*args, **kwargs)

            return enhanced_wrapper
        else:
            # Fallback to basic logging
            def basic_wrapper(*args, **kwargs):
                logger = logging.getLogger("ragchecker_debug")
                logger.info(f"Executing {func.__name__} for {evaluation_type}")
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"Successfully executed {func.__name__}")
                    return result
                except Exception as e:
                    logger.error(f"Error executing {func.__name__}: {e}")
                    raise

            return basic_wrapper

    return decorator


# Example usage
if __name__ == "__main__":
    # Test the debug manager
    debug_manager = create_ragchecker_debug_manager()

    # Test context capture
    context = debug_manager.capture_ragchecker_context(
        evaluation_id="test_001", evaluation_type="input_validation", validation_stage="pydantic_validation"
    )

    # Test logging
    debug_manager.log_pydantic_validation(
        context=context, validation_result={"valid": True, "errors": []}, performance_overhead=0.001
    )

    # Test summary
    summary = debug_manager.get_debugging_summary()
    print("Debug summary:", summary)
