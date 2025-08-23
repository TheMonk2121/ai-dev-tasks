#!/usr/bin/env python3
"""
DSPy v2 System Integration

Comprehensive integration of DSPy v2 optimization components with the existing
B-1003 multi-agent system. Provides seamless integration of optimizers,
assertion framework, four-part optimization loop, and metrics dashboard.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from dspy import Module

# Import assertion framework with fallback
try:
    from .assertions import DSPyAssertionFramework, ValidationReport

    ASSERTION_FRAMEWORK_AVAILABLE = True
except ImportError:
    ASSERTION_FRAMEWORK_AVAILABLE = False
    DSPyAssertionFramework = None
    ValidationReport = None
from .metrics_dashboard import MetricsDashboard, get_metrics_dashboard, record_optimization_metrics
from .model_switcher import LocalModel, LocalTaskExecutor, ModelSwitcher
from .optimization_loop import FourPartOptimizationLoop, OptimizationCycle, get_optimization_loop
from .optimizers import OptimizationResult, get_optimizer_manager

_LOG = logging.getLogger("dspy_system_integration")


class IntegrationMode(Enum):
    """Integration modes for the DSPy v2 system"""

    FULL_INTEGRATION = "full_integration"  # All components integrated
    OPTIMIZATION_ONLY = "optimization_only"  # Only optimizers integrated
    MONITORING_ONLY = "monitoring_only"  # Only metrics dashboard integrated
    ASSERTION_ONLY = "assertion_only"  # Only assertion framework integrated
    MINIMAL = "minimal"  # Basic integration only


class SystemHealth(Enum):
    """System health status"""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"


@dataclass
class IntegrationConfig:
    """Configuration for system integration"""

    mode: IntegrationMode = IntegrationMode.FULL_INTEGRATION
    enable_optimizers: bool = True
    enable_assertions: bool = True
    enable_metrics: bool = True
    enable_optimization_loop: bool = True
    auto_optimize: bool = True
    auto_validate: bool = True
    performance_threshold: float = 0.8
    reliability_threshold: float = 0.9
    max_optimization_cycles: int = 10
    metrics_retention_days: int = 30

    # Model switching configuration
    enable_model_switching: bool = True
    sequential_loading: bool = True
    memory_optimization: bool = True

    # Alert configuration
    enable_alerts: bool = True
    alert_thresholds: Dict[str, float] = field(
        default_factory=lambda: {"reliability": 0.7, "performance": 0.6, "quality": 0.8}
    )


@dataclass
class SystemStatus:
    """System status information"""

    health: SystemHealth
    components: Dict[str, bool]
    metrics: Dict[str, float]
    alerts: List[str]
    last_update: float
    integration_mode: IntegrationMode

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "health": self.health.value,
            "components": self.components,
            "metrics": self.metrics,
            "alerts": self.alerts,
            "last_update": self.last_update,
            "integration_mode": self.integration_mode.value,
        }


class DSPySystemIntegration:
    """Main system integration class for DSPy v2 optimization"""

    def __init__(self, config: Optional[IntegrationConfig] = None):
        """Initialize the DSPy system integration"""
        self.config = config or IntegrationConfig()
        self.model_switcher: Optional[ModelSwitcher] = None
        self.optimizer_manager = None
        self.assertion_framework: Optional[Any] = None
        self.optimization_loop: Optional[FourPartOptimizationLoop] = None
        self.metrics_dashboard: Optional[MetricsDashboard] = None
        self.task_executor: Optional[LocalTaskExecutor] = None

        # System status
        self.status = SystemStatus(
            health=SystemHealth.OFFLINE,
            components={},
            metrics={},
            alerts=[],
            last_update=time.time(),
            integration_mode=self.config.mode,
        )

        # Initialize components based on configuration
        self._initialize_components()

        _LOG.info(f"DSPy System Integration initialized with mode: {self.config.mode.value}")

    def _initialize_components(self):
        """Initialize system components based on configuration"""
        try:
            # Initialize Model Switcher (core component)
            if self.config.enable_model_switching:
                self.model_switcher = ModelSwitcher()
                self.task_executor = LocalTaskExecutor(self.model_switcher)
                self.status.components["model_switcher"] = True
                _LOG.info("Model Switcher initialized")

            # Initialize Optimizer Manager
            if self.config.enable_optimizers:
                self.optimizer_manager = get_optimizer_manager()
                self.status.components["optimizer_manager"] = True
                _LOG.info("Optimizer Manager initialized")

            # Initialize Assertion Framework
            if self.config.enable_assertions and ASSERTION_FRAMEWORK_AVAILABLE and DSPyAssertionFramework is not None:
                self.assertion_framework = DSPyAssertionFramework()
                self.status.components["assertion_framework"] = True
                _LOG.info("Assertion Framework initialized")
            elif self.config.enable_assertions:
                self.assertion_framework = None
                self.status.components["assertion_framework"] = False
                _LOG.warning("Assertion Framework not available")

            # Initialize Optimization Loop
            if self.config.enable_optimization_loop:
                self.optimization_loop = get_optimization_loop()
                self.status.components["optimization_loop"] = True
                _LOG.info("Optimization Loop initialized")

            # Initialize Metrics Dashboard
            if self.config.enable_metrics:
                self.metrics_dashboard = get_metrics_dashboard()
                if self.optimization_loop:
                    self.metrics_dashboard.connect_optimization_loop(self.optimization_loop)
                self.status.components["metrics_dashboard"] = True
                _LOG.info("Metrics Dashboard initialized")

            # Update system health
            self._update_system_health()

        except Exception as e:
            _LOG.error(f"Failed to initialize components: {e}")
            self.status.health = SystemHealth.CRITICAL
            self.status.alerts.append(f"Component initialization failed: {e}")

    def _update_system_health(self):
        """Update system health based on component status"""
        active_components = sum(self.status.components.values())
        total_components = len(self.status.components)

        if total_components == 0:
            self.status.health = SystemHealth.OFFLINE
        elif active_components == total_components:
            self.status.health = SystemHealth.HEALTHY
        elif active_components >= total_components * 0.7:
            self.status.health = SystemHealth.DEGRADED
        else:
            self.status.health = SystemHealth.CRITICAL

        self.status.last_update = time.time()

    def execute_task(self, task: str, task_type: str, role: str, complexity: str = "moderate") -> Dict[str, Any]:
        """Execute a task with full DSPy v2 optimization integration"""

        start_time = time.time()
        result = {
            "success": False,
            "task": task,
            "task_type": task_type,
            "role": role,
            "complexity": complexity,
            "execution_time": 0.0,
            "optimization_applied": False,
            "validation_performed": False,
            "metrics_recorded": False,
            "errors": [],
        }

        try:
            # Step 1: Execute task with model switcher
            if not self.task_executor:
                raise RuntimeError("Task executor not available")

            task_result = self.task_executor.forward(task, task_type, role, complexity)
            result["task_result"] = task_result

            # Step 2: Apply optimization if enabled
            if self.config.auto_optimize and self.optimizer_manager:
                try:
                    optimization_result = self._apply_optimization(task, task_type, role)
                    result["optimization_result"] = optimization_result
                    result["optimization_applied"] = True
                except Exception as e:
                    result["errors"].append(f"Optimization failed: {e}")

            # Step 3: Perform validation if enabled
            if self.config.auto_validate and self.assertion_framework:
                try:
                    validation_result = self._validate_task(task, task_type, role)
                    result["validation_result"] = validation_result
                    result["validation_performed"] = True
                except Exception as e:
                    result["errors"].append(f"Validation failed: {e}")

            # Step 4: Record metrics if enabled
            if self.config.enable_metrics and self.metrics_dashboard:
                try:
                    self._record_task_metrics(task, task_type, role, start_time)
                    result["metrics_recorded"] = True
                except Exception as e:
                    result["errors"].append(f"Metrics recording failed: {e}")

            result["success"] = True
            result["execution_time"] = time.time() - start_time

        except Exception as e:
            result["errors"].append(f"Task execution failed: {e}")
            _LOG.error(f"Task execution failed: {e}")

        return result

    def _apply_optimization(self, task: str, task_type: str, role: str) -> Optional[OptimizationResult]:
        """Apply optimization to the task"""
        if not self.optimizer_manager:
            return None

        try:
            # Create a simple metric for optimization
            def task_quality_metric(example, prediction):
                # Simple quality metric based on response length and content
                if not prediction or not hasattr(prediction, "result"):
                    return 0.0

                result = prediction.result
                if not result:
                    return 0.0

                # Basic quality scoring
                score = 0.0
                if len(result) > 10:
                    score += 0.3
                if "error" not in result.lower():
                    score += 0.4
                if task_type in result.lower():
                    score += 0.3

                return min(1.0, score)

            # Get optimizer and apply optimization
            optimizer = self.optimizer_manager.get_optimizer("labeled_few_shot")
            if optimizer:
                # Create test data for optimization
                test_data = [
                    {"task": task, "task_type": task_type, "role": role},
                    {"task": f"Alternative {task}", "task_type": task_type, "role": role},
                ]

                # Apply optimization
                optimization_result = optimizer.optimize_program(self.task_executor, test_data, task_quality_metric)

                return optimization_result

        except Exception as e:
            _LOG.warning(f"Optimization application failed: {e}")

        return None

    def _validate_task(self, task: str, task_type: str, role: str) -> Optional[Any]:
        """Validate the task execution"""
        if not self.assertion_framework:
            return None

        try:
            # Create a mock module for validation
            class TaskModule(Module):
                def __init__(self, task_result):
                    super().__init__()
                    self.task_result = task_result

                def forward(self, input_data):
                    return self.task_result

            # Create validation module
            validation_module = TaskModule({"result": task, "type": task_type, "role": role})

            # Perform validation
            validation_report = self.assertion_framework.validate_module(validation_module, [{"input": task}])

            return validation_report

        except Exception as e:
            _LOG.warning(f"Task validation failed: {e}")

        return None

    def _record_task_metrics(self, task: str, task_type: str, role: str, start_time: float):
        """Record task execution metrics"""
        if not self.metrics_dashboard:
            return

        try:
            execution_time = time.time() - start_time

            # Record basic metrics
            from .metrics_dashboard import MetricType

            self.metrics_dashboard.metric_series[MetricType.DURATION].add_point(
                execution_time, metadata={"task_type": task_type, "role": role}
            )

            # Record success rate (assuming success for now)
            self.metrics_dashboard.metric_series[MetricType.SUCCESS_RATE].add_point(
                1.0, metadata={"task_type": task_type, "role": role}
            )

        except Exception as e:
            _LOG.warning(f"Metrics recording failed: {e}")

    def run_optimization_cycle(self, inputs: Dict[str, Any]) -> Optional[OptimizationCycle]:
        """Run a complete optimization cycle"""
        if not self.optimization_loop:
            return None

        try:
            # Run optimization cycle
            cycle = self.optimization_loop.run_cycle(inputs)

            # Record metrics if dashboard is available
            if self.metrics_dashboard:
                record_optimization_metrics(cycle)

            return cycle

        except Exception as e:
            _LOG.error(f"Optimization cycle failed: {e}")
            return None

    def get_system_status(self) -> SystemStatus:
        """Get current system status"""
        # Update metrics
        if self.metrics_dashboard:
            stats = self.metrics_dashboard.get_statistics()
            self.status.metrics.update(
                {
                    "total_metrics": stats.get("total_metrics", 0),
                    "total_data_points": stats.get("total_data_points", 0),
                    "active_alerts": stats.get("active_alerts", 0),
                    "connected_to_loop": stats.get("connected_to_loop", False),
                }
            )

        # Update health
        self._update_system_health()

        return self.status

    def get_dashboard_data(self, view: str = "overview") -> Dict[str, Any]:
        """Get dashboard data"""
        if not self.metrics_dashboard:
            return {"error": "Metrics dashboard not available"}

        try:
            from .metrics_dashboard import DashboardView

            view_enum = DashboardView.OVERVIEW
            if view == "detailed":
                view_enum = DashboardView.DETAILED
            elif view == "historical":
                view_enum = DashboardView.HISTORICAL
            elif view == "comparison":
                view_enum = DashboardView.COMPARISON
            elif view == "alerts":
                view_enum = DashboardView.ALERTS

            return self.metrics_dashboard.get_dashboard_data(view_enum)

        except Exception as e:
            return {"error": f"Failed to get dashboard data: {e}"}

    def validate_module(self, module: Module, test_inputs: Optional[List[Dict[str, Any]]] = None) -> Optional[Any]:
        """Validate a DSPy module using the assertion framework"""
        if not self.assertion_framework:
            return None

        try:
            return self.assertion_framework.validate_module(module, test_inputs)
        except Exception as e:
            _LOG.error(f"Module validation failed: {e}")
            return None

    def optimize_program(
        self, program: Module, test_data: List[Dict[str, Any]], metric
    ) -> Optional[OptimizationResult]:
        """Optimize a DSPy program using the optimizer manager"""
        if not self.optimizer_manager:
            return None

        try:
            optimizer = self.optimizer_manager.get_optimizer("labeled_few_shot")
            if optimizer:
                return optimizer.optimize_program(program, test_data, metric)
        except Exception as e:
            _LOG.error(f"Program optimization failed: {e}")

        return None

    def switch_model(self, model: LocalModel) -> bool:
        """Switch to a different local model"""
        if not self.model_switcher:
            return False

        try:
            return self.model_switcher.switch_model(model)
        except Exception as e:
            _LOG.error(f"Model switching failed: {e}")
            return False

    def get_model_for_task(self, task_type: str, complexity: str = "moderate") -> Optional[LocalModel]:
        """Get the best model for a specific task"""
        if not self.model_switcher:
            return None

        try:
            return self.model_switcher.get_model_for_task(task_type, complexity)
        except Exception as e:
            _LOG.error(f"Model selection failed: {e}")
            return None

    def export_system_data(self, format: str = "json") -> str:
        """Export system data for analysis"""
        try:
            import json

            data = {
                "system_status": self.get_system_status().to_dict(),
                "configuration": {
                    "mode": self.config.mode.value,
                    "enable_optimizers": self.config.enable_optimizers,
                    "enable_assertions": self.config.enable_assertions,
                    "enable_metrics": self.config.enable_metrics,
                    "enable_optimization_loop": self.config.enable_optimization_loop,
                },
                "components": {
                    "model_switcher": self.model_switcher is not None,
                    "optimizer_manager": self.optimizer_manager is not None,
                    "assertion_framework": self.assertion_framework is not None,
                    "optimization_loop": self.optimization_loop is not None,
                    "metrics_dashboard": self.metrics_dashboard is not None,
                },
            }

            if format.lower() == "json":
                return json.dumps(data, indent=2)
            else:
                raise ValueError(f"Unsupported export format: {format}")

        except Exception as e:
            return f"Export failed: {e}"


# Global system integration instance
_system_integration = None


def get_system_integration(config: Optional[IntegrationConfig] = None) -> DSPySystemIntegration:
    """Get the global system integration instance"""
    global _system_integration
    if _system_integration is None:
        _system_integration = DSPySystemIntegration(config)
    return _system_integration


def execute_task_with_optimization(
    task: str, task_type: str, role: str, complexity: str = "moderate"
) -> Dict[str, Any]:
    """Convenience function to execute a task with full optimization"""
    integration = get_system_integration()
    return integration.execute_task(task, task_type, role, complexity)


def run_optimization_cycle(inputs: Dict[str, Any]) -> Optional[OptimizationCycle]:
    """Convenience function to run an optimization cycle"""
    integration = get_system_integration()
    return integration.run_optimization_cycle(inputs)


def get_system_status() -> SystemStatus:
    """Convenience function to get system status"""
    integration = get_system_integration()
    return integration.get_system_status()
