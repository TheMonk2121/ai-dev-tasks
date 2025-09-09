#!/usr/bin/env python3
"""
Context-Aware Tools Framework for DSPy AI System
Implements context awareness, MLflow integration, and enhanced debugging for B-1007
"""

import functools
import logging
import time
import traceback
import uuid
from datetime import datetime
from typing import Any
from collections.abc import Callable

from pydantic import BaseModel, Field, field_validator

from .context_models import BaseContext
from .dynamic_prompts import PromptContext
from .error_taxonomy import ErrorFactory
from .user_preferences import UserPreferenceManager

_LOG = logging.getLogger("context_aware_tools")

# ---------- Context-Aware Tool Models ----------


class ToolExecutionContext(BaseModel):
    """Model for tool execution context"""

    execution_id: str = Field(..., description="Unique execution identifier")
    tool_name: str = Field(..., description="Name of the tool being executed")
    user_context: PromptContext | None = Field(None, description="User context for the execution")
    role_context: BaseContext | None = Field(None, description="Role-specific context")
    execution_timestamp: datetime = Field(default_factory=datetime.now, description="Execution timestamp")
    parameters: dict[str, Any] = Field(default_factory=dict, description="Tool execution parameters")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @field_validator("execution_id")
    @classmethod
    def validate_execution_id(cls, v: str) -> str:
        """Validate execution ID format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Execution ID must be at least 3 characters")
        return v.strip()

    @field_validator("tool_name")
    @classmethod
    def validate_tool_name(cls, v: str) -> str:
        """Validate tool name format"""
        if not v or len(v.strip()) < 2:
            raise ValueError("Tool name must be at least 2 characters")
        return v.strip()


class ToolExecutionResult(BaseModel):
    """Model for tool execution result"""

    execution_id: str = Field(..., description="Execution identifier")
    success: bool = Field(..., description="Whether execution was successful")
    result: Any = Field(..., description="Tool execution result")
    execution_time: float = Field(..., description="Execution time in seconds")
    error_message: str | None = Field(None, description="Error message if failed")
    context_adaptations: list[str] = Field(default_factory=list, description="Context adaptations applied")
    mlflow_run_id: str | None = Field(None, description="MLflow run ID if tracking enabled")
    debugging_info: dict[str, Any] = Field(default_factory=dict, description="Debugging information")

    @field_validator("execution_time")
    @classmethod
    def validate_execution_time(cls, v: float) -> float:
        """Validate execution time is positive"""
        if v < 0:
            raise ValueError("Execution time cannot be negative")
        return v


class MLflowIntegration(BaseModel):
    """Model for MLflow integration configuration"""

    enabled: bool = Field(default=True, description="Whether MLflow tracking is enabled")
    experiment_name: str = Field(default="dspy-tools", description="MLflow experiment name")
    tracking_uri: str | None = Field(None, description="MLflow tracking URI")
    log_parameters: bool = Field(default=True, description="Whether to log parameters")
    log_metrics: bool = Field(default=True, description="Whether to log metrics")
    log_artifacts: bool = Field(default=False, description="Whether to log artifacts")

    @field_validator("experiment_name")
    @classmethod
    def validate_experiment_name(cls, v: str) -> str:
        """Validate experiment name format"""
        if not v or len(v.strip()) < 3:
            raise ValueError("Experiment name must be at least 3 characters")
        return v.strip()


# ---------- Context-Aware Tool Decorator ----------


class ContextAwareToolDecorator:
    """Decorator for making tools context-aware with MLflow integration"""

    def __init__(
        self,
        tool_name: str,
        mlflow_config: MLflowIntegration | None = None,
        preference_manager: UserPreferenceManager | None = None,
        enable_debugging: bool = True,
    ):
        """Initialize context-aware tool decorator"""
        self.tool_name = tool_name
        self.mlflow_config = mlflow_config or MLflowIntegration(tracking_uri=None)
        self.preference_manager = preference_manager
        self.enable_debugging = enable_debugging
        self._mlflow_client = None

    def __call__(self, func: Callable) -> Callable:
        """Apply decorator to function"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate execution ID
            execution_id = f"{self.tool_name}_{uuid.uuid4().hex[:8]}"

            # Extract context from arguments
            context = self._extract_context(args, kwargs)

            # Create execution context
            exec_context = ToolExecutionContext(
                execution_id=execution_id,
                tool_name=self.tool_name,
                user_context=context.get("user_context"),
                role_context=context.get("role_context"),
                parameters=self._extract_parameters(args, kwargs),
                metadata=self._extract_metadata(context),
            )

            # Start MLflow run if enabled
            mlflow_run_id = None
            if self.mlflow_config.enabled:
                mlflow_run_id = self._start_mlflow_run(exec_context)

            # Execute tool with timing
            start_time = time.time()
            try:
                # Apply context adaptations
                adapted_args, adapted_kwargs = self._adapt_arguments(args, kwargs, context)

                # Execute the tool
                result = func(*adapted_args, **adapted_kwargs)

                # Adapt response based on context
                adapted_result = self._adapt_response(result, context)

                execution_time = time.time() - start_time

                # Create successful result
                tool_result = ToolExecutionResult(
                    execution_id=execution_id,
                    success=True,
                    result=adapted_result,
                    execution_time=execution_time,
                    error_message=None,
                    context_adaptations=self._get_context_adaptations(context),
                    mlflow_run_id=mlflow_run_id,
                    debugging_info=self._capture_debugging_info(exec_context, result, execution_time),
                )

            except Exception as e:
                execution_time = time.time() - start_time

                # Create error result
                tool_result = ToolExecutionResult(
                    execution_id=execution_id,
                    success=False,
                    result=None,
                    execution_time=execution_time,
                    error_message=str(e),
                    context_adaptations=self._get_context_adaptations(context),
                    mlflow_run_id=mlflow_run_id,
                    debugging_info=self._capture_debugging_info(exec_context, e, execution_time),
                )

                # Log error with context
                self._log_error_with_context(e, exec_context)

            # Log to MLflow if enabled
            if self.mlflow_config.enabled and mlflow_run_id:
                self._log_to_mlflow(tool_result, exec_context)

            # Log debugging information
            if self.enable_debugging:
                self._log_debugging_info(tool_result)

            return tool_result

        return wrapper

    def _extract_context(self, args: tuple, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Extract context from function arguments"""
        context = {}

        # Look for context in kwargs
        if "user_context" in kwargs:
            context["user_context"] = kwargs["user_context"]
        if "role_context" in kwargs:
            context["role_context"] = kwargs["role_context"]
        if "context" in kwargs:
            if isinstance(kwargs["context"], PromptContext):
                context["user_context"] = kwargs["context"]
            elif isinstance(kwargs["context"], BaseContext):
                context["role_context"] = kwargs["context"]

        # Look for context in args
        for arg in args:
            if isinstance(arg, PromptContext):
                context["user_context"] = arg
            elif isinstance(arg, BaseContext):
                context["role_context"] = arg

        return context

    def _extract_parameters(self, args: tuple, kwargs: dict[str, Any]) -> dict[str, Any]:
        """Extract tool parameters from arguments"""
        parameters = {}

        # Add positional arguments
        for i, arg in enumerate(args):
            if not isinstance(arg, PromptContext | BaseContext):
                parameters[f"arg_{i}"] = str(arg)

        # Add keyword arguments
        for key, value in kwargs.items():
            if key not in ["user_context", "role_context", "context"]:
                parameters[key] = str(value)

        return parameters

    def _extract_metadata(self, context: dict[str, Any]) -> dict[str, Any]:
        """Extract metadata from context"""
        metadata = {}

        if context.get("user_context"):
            metadata["user_id"] = context["user_context"].user_id
            metadata["session_id"] = context["user_context"].session_id

        if context.get("role_context"):
            metadata["role"] = context["role_context"].role.value

        return metadata

    def _start_mlflow_run(self, exec_context: ToolExecutionContext) -> str | None:
        """Start MLflow run for tracking"""
        try:
            # Try to import mlflow, but handle gracefully if not available
            try:
                import mlflow  # type: ignore[import-untyped]
            except ImportError:
                _LOG.warning("MLflow not available - skipping tracking")
                return None

            # Set tracking URI if provided
            if self.mlflow_config.tracking_uri:
                mlflow.set_tracking_uri(self.mlflow_config.tracking_uri)

            # Set experiment
            mlflow.set_experiment(self.mlflow_config.experiment_name)

            # Start run
            with mlflow.start_run(run_name=f"{self.tool_name}_{exec_context.execution_id}") as run:
                # Log parameters if enabled
                if self.mlflow_config.log_parameters:
                    mlflow.log_params(exec_context.parameters)
                    mlflow.log_params(exec_context.metadata)

                return run.info.run_id

        except Exception as e:
            _LOG.error(f"Failed to start MLflow run: {e}")
            return None

    def _adapt_arguments(self, args: tuple, kwargs: dict[str, Any], context: dict[str, Any]) -> tuple:
        """Adapt arguments based on context"""
        adapted_args = list(args)
        adapted_kwargs = kwargs.copy()

        # Apply user preference adaptations
        if self.preference_manager and context.get("user_context"):
            user_id = context["user_context"].user_id
            preferences = self.preference_manager.get_user_preferences(user_id)

            # Adapt based on user preferences
            if "detail_level" in preferences:
                if preferences["detail_level"] == "high":
                    # Add verbose flag for high detail
                    adapted_kwargs["verbose"] = True
                elif preferences["detail_level"] == "low":
                    # Add concise flag for low detail
                    adapted_kwargs["concise"] = True

        return tuple(adapted_args), adapted_kwargs

    def _adapt_response(self, result: Any, context: dict[str, Any]) -> Any:
        """Adapt response based on context"""
        if not context.get("user_context"):
            return result

        # Apply user preference adaptations to response
        if self.preference_manager:
            user_id = context["user_context"].user_id
            preferences = self.preference_manager.get_user_preferences(user_id)

            # Adapt response format based on preferences
            if "style" in preferences:
                if preferences["style"] == "detailed" and isinstance(result, str):
                    # Add more detail to response
                    result = f"Detailed result: {result}\n\nAdditional context and explanations provided."
                elif preferences["style"] == "concise" and isinstance(result, str):
                    # Make response more concise
                    lines = result.split("\n")
                    if len(lines) > 3:
                        result = "\n".join(lines[:3]) + "\n..."

        return result

    def _get_context_adaptations(self, context: dict[str, Any]) -> list[str]:
        """Get list of context adaptations applied"""
        adaptations = []

        if context.get("user_context"):
            adaptations.append("user_context_injected")

        if context.get("role_context"):
            adaptations.append("role_context_injected")

        if self.preference_manager and context.get("user_context"):
            adaptations.append("user_preferences_applied")

        return adaptations

    def _capture_debugging_info(
        self, exec_context: ToolExecutionContext, result: Any, execution_time: float
    ) -> dict[str, Any]:
        """Capture debugging information"""
        debugging_info = {
            "execution_id": exec_context.execution_id,
            "tool_name": exec_context.tool_name,
            "execution_time": execution_time,
            "timestamp": exec_context.execution_timestamp.isoformat(),
            "parameters": exec_context.parameters,
            "metadata": exec_context.metadata,
        }

        # Add context information
        if exec_context.user_context:
            debugging_info["user_context"] = {
                "user_id": exec_context.user_context.user_id,
                "session_id": exec_context.user_context.session_id,
                "preferences": exec_context.user_context.user_preferences,
            }

        if exec_context.role_context:
            debugging_info["role_context"] = {
                "role": exec_context.role_context.role.value,
                "session_id": exec_context.role_context.session_id,
            }

        # Add result information
        if isinstance(result, Exception):
            debugging_info["error"] = {
                "type": type(result).__name__,
                "message": str(result),
                "traceback": traceback.format_exc(),
            }
        else:
            debugging_info["result_type"] = type(result).__name__
            debugging_info["result_size"] = len(str(result)) if result else 0

        return debugging_info

    def _log_error_with_context(self, error: Exception, exec_context: ToolExecutionContext) -> None:
        """Log error with full context information"""
        error_context = {
            "execution_id": exec_context.execution_id,
            "tool_name": exec_context.tool_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "user_id": exec_context.user_context.user_id if exec_context.user_context else None,
            "role": exec_context.role_context.role.value if exec_context.role_context else None,
            "parameters": exec_context.parameters,
        }

        _LOG.error(f"Tool execution failed: {error_context}")

        # Create structured error
        structured_error = ErrorFactory.create_runtime_error(
            message=f"Tool {self.tool_name} execution failed: {str(error)}",
            operation=self.tool_name,
            resource="tool_execution",
            context=error_context,
        )

        _LOG.error(f"Structured error: {structured_error.model_dump()}")

    def _log_to_mlflow(self, tool_result: ToolExecutionResult, exec_context: ToolExecutionContext) -> None:
        """Log results to MLflow"""
        try:
            # Try to import mlflow, but handle gracefully if not available
            try:
                import mlflow  # type: ignore[import-untyped]
            except ImportError:
                _LOG.warning("MLflow not available - skipping logging")
                return

            # Log metrics
            if self.mlflow_config.log_metrics:
                mlflow.log_metric("execution_time", tool_result.execution_time)
                mlflow.log_metric("success", 1 if tool_result.success else 0)
                mlflow.log_metric("context_adaptations_count", len(tool_result.context_adaptations))

            # Log debugging info as parameters
            if self.mlflow_config.log_parameters:
                for key, value in tool_result.debugging_info.items():
                    if isinstance(value, str | int | float | bool):
                        mlflow.log_param(f"debug_{key}", value)

            # Log artifacts if enabled
            if self.mlflow_config.log_artifacts and tool_result.debugging_info:
                import json
                import tempfile

                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
                    json.dump(tool_result.debugging_info, f, indent=2, default=str)
                    mlflow.log_artifact(f.name, "debugging_info.json")

        except Exception as e:
            _LOG.error(f"Failed to log to MLflow: {e}")

    def _log_debugging_info(self, tool_result: ToolExecutionResult) -> None:
        """Log debugging information"""
        debug_msg = f"Tool execution completed: {tool_result.execution_id}"
        debug_msg += f" | Success: {tool_result.success}"
        debug_msg += f" | Time: {tool_result.execution_time:.3f}s"
        debug_msg += f" | Adaptations: {len(tool_result.context_adaptations)}"

        if tool_result.mlflow_run_id:
            debug_msg += f" | MLflow: {tool_result.mlflow_run_id}"

        _LOG.info(debug_msg)


# ---------- Enhanced Tool Framework ----------


class ContextAwareToolFramework:
    """Framework for managing context-aware tools"""

    def __init__(
        self,
        mlflow_config: MLflowIntegration | None = None,
        preference_manager: UserPreferenceManager | None = None,
    ):
        """Initialize tool framework"""
        self.mlflow_config = mlflow_config or MLflowIntegration(tracking_uri=None)
        self.preference_manager = preference_manager
        self.tools: dict[str, Callable] = {}
        self.execution_history: list[ToolExecutionResult] = []

    def register_tool(self, tool_name: str, tool_func: Callable, enable_debugging: bool = True) -> None:
        """Register a tool with context awareness"""
        decorator = ContextAwareToolDecorator(
            tool_name=tool_name,
            mlflow_config=self.mlflow_config,
            preference_manager=self.preference_manager,
            enable_debugging=enable_debugging,
        )

        decorated_tool = decorator(tool_func)
        self.tools[tool_name] = decorated_tool

        _LOG.info(f"Registered context-aware tool: {tool_name}")

    def execute_tool(self, tool_name: str, *args, **kwargs) -> ToolExecutionResult:
        """Execute a context-aware tool"""
        if tool_name not in self.tools:
            raise ValueError(f"Tool not found: {tool_name}")

        tool_func = self.tools[tool_name]
        result = tool_func(*args, **kwargs)

        # Store in execution history
        self.execution_history.append(result)

        return result

    def get_execution_history(self, tool_name: str | None = None) -> list[ToolExecutionResult]:
        """Get execution history for tools"""
        if tool_name:
            return [result for result in self.execution_history if result.execution_id.startswith(tool_name)]
        return self.execution_history

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for all tools"""
        metrics = {
            "total_executions": len(self.execution_history),
            "successful_executions": len([r for r in self.execution_history if r.success]),
            "failed_executions": len([r for r in self.execution_history if not r.success]),
            "avg_execution_time": 0.0,
            "tool_metrics": {},
        }

        if self.execution_history:
            total_time = sum(r.execution_time for r in self.execution_history)
            metrics["avg_execution_time"] = total_time / len(self.execution_history)

        # Calculate per-tool metrics
        tool_executions = {}
        for result in self.execution_history:
            tool_name = result.execution_id.split("_")[0]
            if tool_name not in tool_executions:
                tool_executions[tool_name] = []
            tool_executions[tool_name].append(result)

        for tool_name, executions in tool_executions.items():
            metrics["tool_metrics"][tool_name] = {
                "total_executions": len(executions),
                "successful_executions": len([r for r in executions if r.success]),
                "avg_execution_time": sum(r.execution_time for r in executions) / len(executions),
                "context_adaptations_avg": sum(len(r.context_adaptations) for r in executions) / len(executions),
            }

        return metrics


# ---------- Backward Compatibility Layer ----------


def context_aware_tool(tool_name: str, mlflow_config: MLflowIntegration | None = None, enable_debugging: bool = True):
    """Decorator for making tools context-aware with backward compatibility"""

    def decorator(func: Callable) -> Callable:
        decorator_instance = ContextAwareToolDecorator(
            tool_name=tool_name, mlflow_config=mlflow_config, enable_debugging=enable_debugging
        )
        return decorator_instance(func)

    return decorator


# ---------- Example Tool Adaptations ----------


def adapt_tool_for_context(tool_func: Callable, context: dict[str, Any]) -> Callable:
    """Adapt a tool function for specific context"""

    @functools.wraps(tool_func)
    def adapted_tool(*args, **kwargs):
        # Apply context-specific adaptations
        if context.get("user_preferences"):
            preferences = context["user_preferences"]

            # Adapt based on user preferences
            if preferences.get("detail_level") == "high":
                kwargs["verbose"] = True
            elif preferences.get("detail_level") == "low":
                kwargs["concise"] = True

        # Execute original tool
        result = tool_func(*args, **kwargs)

        # Adapt response based on context
        if context.get("user_preferences") and isinstance(result, str):
            preferences = context["user_preferences"]

            if preferences.get("style") == "detailed":
                result = f"Detailed result: {result}\n\nAdditional context provided."
            elif preferences.get("style") == "concise":
                lines = result.split("\n")
                if len(lines) > 3:
                    result = "\n".join(lines[:3]) + "\n..."

        return result

    return adapted_tool
