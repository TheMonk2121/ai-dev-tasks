from __future__ import annotations
import json
import logging
import os
import sys
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
    from pydantic import BaseModel as PydBaseModel
    from pydantic import Field as PydField
            import psutil
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
Performance Monitoring System for RAGChecker Validation Workflows
Implements comprehensive performance monitoring, alerting, and reporting.
"""

# Add dspy-rag-system to path for imports
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dspy-rag-system"))  # REMOVED: DSPy venv consolidated into main project

try:
except ImportError as e:
    print(f"⚠️  Warning: Could not import Pydantic: {e}")

    class PydBaseModel:  # minimal shim to satisfy type system
        pass

    def PydField(*args, **kwargs):
        return None

@dataclass
class PerformanceAlert:
    """Performance alert configuration and state"""

    alert_id: str
    alert_type: str  # "threshold", "trend", "anomaly"
    metric_name: str
    threshold: float
    current_value: float
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False
    resolved: bool = False

@dataclass
class PerformanceSnapshot:
    """Snapshot of performance metrics at a specific time"""

    timestamp: datetime = field(default_factory=datetime.now)
    operation_count: int = 0
    total_execution_time: float = 0.0
    average_execution_time: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0
    memory_usage: float | None = None
    cache_hit_rate: float = 0.0
    active_operations: int = 0

class PerformanceThresholds(PydBaseModel):
    """Configurable performance thresholds for monitoring"""

    max_execution_time: float = PydField(default=1.0, description="Maximum execution time in seconds")
    min_throughput: float = PydField(default=100.0, description="Minimum throughput in ops/sec")
    max_error_rate: float = PydField(default=5.0, description="Maximum error rate percentage")
    max_memory_usage: float = PydField(default=500.0, description="Maximum memory usage in MB")
    min_cache_hit_rate: float = PydField(default=80.0, description="Minimum cache hit rate percentage")
    max_response_time: float = PydField(default=2.0, description="Maximum response time in seconds")

class PerformanceMonitor:
    """Comprehensive performance monitoring for RAGChecker workflows"""

    def __init__(
        self,
        thresholds: PerformanceThresholds | None = None,
        enable_alerting: bool = True,
        enable_logging: bool = True,
        enable_metrics_export: bool = True,
    ):
        """Initialize performance monitor"""
        self.thresholds = thresholds or PerformanceThresholds()
        self.enable_alerting = enable_alerting
        self.enable_logging = enable_logging
        self.enable_metrics_export = enable_metrics_export

        # Performance tracking
        self.performance_history: deque = deque(maxlen=10000)  # Keep last 10k snapshots
        self.current_metrics: dict[str, Any] = {}
        self.operation_counters: dict[str, int] = defaultdict(int)
        self.error_counters: dict[str, int] = defaultdict(int)
        self.timing_data: dict[str, list[float]] = defaultdict(list)

        # Alerting system
        self.active_alerts: list[PerformanceAlert] = []
        self.alert_history: list[PerformanceAlert] = []
        self.alert_callbacks: list[Callable] = []

        # Monitoring state
        self.monitoring_enabled = True
        self.last_snapshot_time = datetime.now()
        self.snapshot_interval = 1.0  # seconds

        # Threading
        self._monitor_thread = None
        self._stop_monitoring = threading.Event()

        # Logging
        self.logger = logging.getLogger("performance_monitor")
        self.logger.setLevel(logging.INFO)

        # Create console handler if none exists
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)

        # Start monitoring thread
        if self.enable_alerting:
            self._start_monitoring_thread()

    def _start_monitoring_thread(self):
        """Start background monitoring thread"""
        if self._monitor_thread is None or not self._monitor_thread.is_alive():
            self._stop_monitoring.clear()
            self._monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitor_thread.start()
            self.logger.info("Performance monitoring thread started")

    def _monitoring_loop(self):
        """Background monitoring loop"""
        while not self._stop_monitoring.is_set():
            try:
                # Take performance snapshot
                self._take_performance_snapshot()

                # Check thresholds and generate alerts
                self._check_performance_thresholds()

                # Export metrics if enabled
                if self.enable_metrics_export:
                    self._export_metrics()

                # Wait for next snapshot
                time.sleep(self.snapshot_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.snapshot_interval)

    def _take_performance_snapshot(self):
        """Take a performance snapshot"""
        current_time = datetime.now()

        # Calculate current metrics
        total_operations = sum(self.operation_counters.values())
        total_errors = sum(self.error_counters.values())
        total_time = sum(sum(times) for times in self.timing_data.values())

        avg_execution_time = total_time / total_operations if total_operations > 0 else 0.0
        throughput = total_operations / (total_time + 0.001)  # Avoid division by zero
        error_rate = (
            (total_errors / (total_operations + total_errors) * 100) if (total_operations + total_errors) > 0 else 0.0
        )

        # Get memory usage
        memory_usage = self._get_memory_usage()

        # Get cache hit rate from current metrics
        cache_hit_rate = self.current_metrics.get("cache_hit_rate", 0.0)

        # Create snapshot
        snapshot = PerformanceSnapshot(
            timestamp=current_time,
            operation_count=total_operations,
            total_execution_time=total_time,
            average_execution_time=avg_execution_time,
            throughput=throughput,
            error_rate=error_rate,
            memory_usage=memory_usage,
            cache_hit_rate=cache_hit_rate,
            active_operations=len([t for t in self.timing_data.values() if t]),
        )

        # Store snapshot
        self.performance_history.append(snapshot)
        self.last_snapshot_time = current_time

        # Update current metrics
        self.current_metrics.update(asdict(snapshot))

        if self.enable_logging:
            self.logger.debug(f"Performance snapshot taken: {snapshot}")

    def _check_performance_thresholds(self):
        """Check performance thresholds and generate alerts"""
        if not self.current_metrics:
            return

        # Check execution time
        if self.current_metrics.get("average_execution_time", 0) > self.thresholds.max_execution_time:
            self._create_alert(
                "threshold",
                "average_execution_time",
                self.thresholds.max_execution_time,
                self.current_metrics["average_execution_time"],
                "high",
                f"Average execution time ({self.current_metrics['average_execution_time']:.4f}s) exceeds threshold ({self.thresholds.max_execution_time}s)",
            )

        # Check throughput
        if self.current_metrics.get("throughput", 0) < self.thresholds.min_throughput:
            self._create_alert(
                "threshold",
                "throughput",
                self.thresholds.min_throughput,
                self.current_metrics["throughput"],
                "medium",
                f"Throughput ({self.current_metrics['throughput']:.2f} ops/sec) below threshold ({self.thresholds.min_throughput} ops/sec)",
            )

        # Check error rate
        if self.current_metrics.get("error_rate", 0) > self.thresholds.max_error_rate:
            self._create_alert(
                "threshold",
                "error_rate",
                self.thresholds.max_error_rate,
                self.current_metrics["error_rate"],
                "critical",
                f"Error rate ({self.current_metrics['error_rate']:.1f}%) exceeds threshold ({self.thresholds.max_error_rate}%)",
            )

        # Check memory usage
        if (
            self.current_metrics.get("memory_usage")
            and self.current_metrics["memory_usage"] > self.thresholds.max_memory_usage
        ):
            self._create_alert(
                "threshold",
                "memory_usage",
                self.thresholds.max_memory_usage,
                self.current_metrics["memory_usage"],
                "high",
                f"Memory usage ({self.current_metrics['memory_usage']:.1f} MB) exceeds threshold ({self.thresholds.max_memory_usage} MB)",
            )

        # Check cache hit rate
        if self.current_metrics.get("cache_hit_rate", 0) < self.thresholds.min_cache_hit_rate:
            self._create_alert(
                "threshold",
                "cache_hit_rate",
                self.thresholds.min_cache_hit_rate,
                self.current_metrics["cache_hit_rate"],
                "medium",
                f"Cache hit rate ({self.current_metrics['cache_hit_rate']:.1f}%) below threshold ({self.thresholds.min_cache_hit_rate}%)",
            )

    def _create_alert(
        self, alert_type: str, metric_name: str, threshold: float, current_value: float, severity: str, message: str
    ) -> None:
        """Create a new performance alert"""
        # Check if similar alert already exists
        for alert in self.active_alerts:
            if alert.metric_name == metric_name and alert.alert_type == alert_type and not alert.resolved:
                # Update existing alert
                alert.current_value = current_value
                alert.message = message
                alert.timestamp = datetime.now()
                return

        # Create new alert
        alert = PerformanceAlert(
            alert_id=f"alert_{int(time.time())}",
            alert_type=alert_type,
            metric_name=metric_name,
            threshold=threshold,
            current_value=current_value,
            severity=severity,
            message=message,
        )

        self.active_alerts.append(alert)
        self.alert_history.append(alert)

        # Log alert
        if self.enable_logging:
            self.logger.warning(f"Performance alert: {message}")

        # Execute alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

    def record_operation(
        self,
        operation_name: str,
        execution_time: float,
        success: bool = True,
        error_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record an operation for performance monitoring"""
        if not self.monitoring_enabled:
            return

        # Update counters
        self.operation_counters[operation_name] += 1
        if not success:
            self.error_counters[operation_name] += 1

        # Store timing data
        self.timing_data[operation_name].append(execution_time)

        # Keep only recent timing data (last 1000 operations)
        if len(self.timing_data[operation_name]) > 1000:
            self.timing_data[operation_name] = self.timing_data[operation_name][-1000:]

        # Update current metrics
        self.current_metrics["last_operation"] = {
            "name": operation_name,
            "execution_time": execution_time,
            "success": success,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }

        if self.enable_logging:
            self.logger.debug(
                f"Operation recorded: {operation_name} - {execution_time:.4f}s - {'SUCCESS' if success else 'FAILED'}"
            )

    def update_metrics(self, metrics: dict[str, Any]) -> None:
        """Update current performance metrics"""
        self.current_metrics.update(metrics)

        # Update cache hit rate if provided
        if "cache_hit_rate" in metrics:
            self.current_metrics["cache_hit_rate"] = metrics["cache_hit_rate"]

    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]) -> None:
        """Add a callback function for performance alerts"""
        self.alert_callbacks.append(callback)
        self.logger.info(f"Alert callback added: {callback.__name__}")

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge a performance alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                self.logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert"""
        for alert in self.active_alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                self.active_alerts.remove(alert)
                self.logger.info(f"Alert resolved: {alert_id}")
                return True
        return False

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary"""
        if not self.performance_history:
            return {"message": "No performance data available"}

        # Get latest snapshot
        latest_snapshot = self.performance_history[-1]

        # Calculate trends
        if len(self.performance_history) > 1:
            previous_snapshot = self.performance_history[-2]
            time_diff = (latest_snapshot.timestamp - previous_snapshot.timestamp).total_seconds()

            throughput_trend = (
                (latest_snapshot.throughput - previous_snapshot.throughput) / time_diff if time_diff > 0 else 0.0
            )
            error_rate_trend = (
                (latest_snapshot.error_rate - previous_snapshot.error_rate) / time_diff if time_diff > 0 else 0.0
            )
        else:
            throughput_trend = 0.0
            error_rate_trend = 0.0

        # Get alert summary
        active_alerts = [alert for alert in self.active_alerts if not alert.resolved]
        critical_alerts = [alert for alert in active_alerts if alert.severity == "critical"]
        high_alerts = [alert for alert in active_alerts if alert.severity == "high"]

        return {
            "current_metrics": self.current_metrics,
            "latest_snapshot": asdict(latest_snapshot),
            "trends": {"throughput_trend": throughput_trend, "error_rate_trend": error_rate_trend},
            "alerts": {
                "total_active": len(active_alerts),
                "critical": len(critical_alerts),
                "high": len(high_alerts),
                "active_alerts": [asdict(alert) for alert in active_alerts],
            },
            "operation_summary": {
                "total_operations": sum(self.operation_counters.values()),
                "total_errors": sum(self.error_counters.values()),
                "operation_breakdown": dict(self.operation_counters),
                "error_breakdown": dict(self.error_counters),
            },
            "monitoring_status": {
                "enabled": self.monitoring_enabled,
                "last_snapshot": self.last_snapshot_time.isoformat(),
                "snapshot_interval": self.snapshot_interval,
            },
        }

    def get_performance_history(
        self, start_time: datetime | None = None, end_time: datetime | None = None, max_points: int = 100
    ) -> list[dict[str, Any]]:
        """Get performance history within a time range"""
        if not self.performance_history:
            return []

        # Filter by time range
        filtered_snapshots = []
        for snapshot in self.performance_history:
            if start_time and snapshot.timestamp < start_time:
                continue
            if end_time and snapshot.timestamp > end_time:
                continue
            filtered_snapshots.append(snapshot)

        # Limit number of points
        if len(filtered_snapshots) > max_points:
            step = len(filtered_snapshots) // max_points
            filtered_snapshots = filtered_snapshots[::step]

        return [asdict(snapshot) for snapshot in filtered_snapshots]

    def export_metrics_to_file(self, filepath: str, format_type: str = "json") -> bool:
        """Export performance metrics to file"""
        try:
            summary = self.get_performance_summary()

            if format_type.lower() == "json":
                with open(filepath, "w") as f:
                    json.dump(summary, f, indent=2, default=str)
            else:
                # Default to JSON
                with open(filepath, "w") as f:
                    json.dump(summary, f, indent=2, default=str)

            self.logger.info(f"Performance metrics exported to {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            return False

    def _export_metrics(self) -> None:
        """Export metrics to default location"""
        try:
            export_dir = Path("metrics")
            export_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ragchecker_performance_{timestamp}.json"
            filepath = export_dir / filename

            self.export_metrics_to_file(str(filepath))

        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")

    def _get_memory_usage(self) -> float | None:
        """Get current memory usage in MB"""
        try:

            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return None

    def update_thresholds(self, **threshold_updates) -> None:
        """Update performance thresholds"""
        for key, value in threshold_updates.items():
            if hasattr(self.thresholds, key):
                setattr(self.thresholds, key, value)
                self.logger.info(f"Threshold updated: {key} = {value}")

    def set_snapshot_interval(self, interval: float) -> None:
        """Set snapshot interval in seconds"""
        self.snapshot_interval = max(0.1, interval)  # Minimum 0.1 seconds
        self.logger.info(f"Snapshot interval updated: {self.snapshot_interval}s")

    def enable_monitoring(self, enabled: bool = True) -> None:
        """Enable or disable performance monitoring"""
        self.monitoring_enabled = enabled
        status = "enabled" if enabled else "disabled"
        self.logger.info(f"Performance monitoring {status}")

    def clear_history(self) -> None:
        """Clear performance history"""
        self.performance_history.clear()
        self.operation_counters.clear()
        self.error_counters.clear()
        self.timing_data.clear()
        self.current_metrics.clear()
        self.logger.info("Performance history cleared")

    def stop_monitoring(self) -> None:
        """Stop performance monitoring"""
        self._stop_monitoring.set()
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=5.0)
        self.logger.info("Performance monitoring stopped")

def create_performance_monitor(
    thresholds: PerformanceThresholds | None = None,
    enable_alerting: bool = True,
    enable_logging: bool = True,
    enable_metrics_export: bool = True,
) -> PerformanceMonitor:
    """Factory function to create a performance monitor"""
    return PerformanceMonitor(
        thresholds=thresholds,
        enable_alerting=enable_alerting,
        enable_logging=enable_logging,
        enable_metrics_export=enable_metrics_export,
    )

def monitor_performance(operation_name: str = "unknown"):
    """Decorator for automatic performance monitoring"""

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            # Try to get monitor from self if it exists
            monitor = None
            if args and hasattr(args[0], "performance_monitor"):
                monitor = args[0].performance_monitor

            if monitor is None:
                # Create default monitor
                monitor = create_performance_monitor()

            start_time = time.time()
            error_type = None
            metadata = {}

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Record success
                execution_time = time.time() - start_time
                monitor.record_operation(
                    operation_name=operation_name, execution_time=execution_time, success=True, metadata=metadata
                )

                return result

            except Exception as e:
                # Record failure
                error_type = type(e).__name__
                metadata["error_message"] = str(e)

                execution_time = time.time() - start_time
                monitor.record_operation(
                    operation_name=operation_name,
                    execution_time=execution_time,
                    success=False,
                    error_type=error_type,
                    metadata=metadata,
                )

                raise

        return wrapper

    return decorator

# Example usage
if __name__ == "__main__":
    # Test the performance monitoring system
    monitor = create_performance_monitor()

    # Test performance summary
    summary = monitor.get_performance_summary()
    print("Initial performance summary:", summary)

    # Test operation recording
    monitor.record_operation("test_operation", 0.1, success=True)
    monitor.record_operation("test_operation", 0.05, success=False, error_type="ValueError")

    # Test metrics update
    monitor.update_metrics({"cache_hit_rate": 85.5})

    # Test performance summary after operations
    summary = monitor.get_performance_summary()
    print("Updated performance summary:", summary)

    # Test alert callback
    def alert_callback(alert):
        print(f"Alert received: {alert.message}")

    monitor.add_alert_callback(alert_callback)

    # Test threshold violation
    monitor.update_thresholds(max_execution_time=0.01)
    monitor.record_operation("slow_operation", 0.1, success=True)

    # Stop monitoring
    monitor.stop_monitoring()
