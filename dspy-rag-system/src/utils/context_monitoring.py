#!/usr/bin/env python3
"""
Context Integration Monitoring and Observability

Provides comprehensive monitoring, metrics collection, and alerting
for the context integration system in the DSPy multi-agent system.
"""

import json
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

_LOG = logging.getLogger("context_monitoring")


@dataclass
class ContextMetrics:
    """Metrics for context integration operations"""

    # Timing metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0

    # Performance metrics
    avg_response_time_ms: float = 0.0
    min_response_time_ms: float = float("inf")
    max_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0

    # Error metrics
    timeout_errors: int = 0
    subprocess_errors: int = 0
    parsing_errors: int = 0
    fallback_usage: int = 0

    # Resource metrics
    memory_usage_mb: float = 0.0
    cache_size: int = 0
    cache_evictions: int = 0

    # Role-specific metrics
    role_requests: Dict[str, int] = None
    role_errors: Dict[str, int] = None
    role_avg_times: Dict[str, float] = None

    def __post_init__(self):
        if self.role_requests is None:
            self.role_requests = defaultdict(int)
        if self.role_errors is None:
            self.role_errors = defaultdict(int)
        if self.role_avg_times is None:
            self.role_avg_times = defaultdict(float)


class ContextMonitor:
    """Monitor for context integration system"""

    def __init__(self, metrics_file: str = "context_metrics.json", max_history: int = 1000):
        """
        Initialize the context monitor.

        Args:
            metrics_file: File to persist metrics
            max_history: Maximum number of historical data points to keep
        """
        self.metrics_file = Path(metrics_file)
        self.max_history = max_history
        self.current_metrics = ContextMetrics()
        self.historical_data = deque(maxlen=max_history)
        self.response_times = deque(maxlen=max_history)
        self.alerts = []

        # Load existing metrics if available
        self._load_metrics()

    def record_request(
        self,
        role: str,
        task: str,
        start_time: float,
        success: bool,
        response_time: float,
        cache_hit: bool = False,
        error_type: Optional[str] = None,
        fallback_used: bool = False,
    ):
        """
        Record a context request.

        Args:
            role: AI role (planner, implementer, coder, researcher)
            task: Task description
            start_time: Request start time
            success: Whether request was successful
            response_time: Response time in seconds
            cache_hit: Whether cache was hit
            error_type: Type of error if any
            fallback_used: Whether fallback context was used
        """
        # Update basic metrics
        self.current_metrics.total_requests += 1

        if success:
            self.current_metrics.successful_requests += 1
        else:
            self.current_metrics.failed_requests += 1

        if cache_hit:
            self.current_metrics.cache_hits += 1
        else:
            self.current_metrics.cache_misses += 1

        if fallback_used:
            self.current_metrics.fallback_usage += 1

        # Update timing metrics
        response_time_ms = response_time * 1000
        self.response_times.append(response_time_ms)

        # Update min/max
        if response_time_ms < self.current_metrics.min_response_time_ms:
            self.current_metrics.min_response_time_ms = response_time_ms
        if response_time_ms > self.current_metrics.max_response_time_ms:
            self.current_metrics.max_response_time_ms = response_time_ms

        # Update role-specific metrics
        self.current_metrics.role_requests[role] += 1
        if not success:
            self.current_metrics.role_errors[role] += 1

        # Update role average times
        current_avg = self.current_metrics.role_avg_times[role]
        count = self.current_metrics.role_requests[role]
        self.current_metrics.role_avg_times[role] = (current_avg * (count - 1) + response_time_ms) / count

        # Update error counts
        if error_type:
            if error_type == "timeout":
                self.current_metrics.timeout_errors += 1
            elif error_type == "subprocess":
                self.current_metrics.subprocess_errors += 1
            elif error_type == "parsing":
                self.current_metrics.parsing_errors += 1

        # Calculate percentiles
        if len(self.response_times) >= 5:
            sorted_times = sorted(self.response_times)
            self.current_metrics.p95_response_time_ms = sorted_times[int(len(sorted_times) * 0.95)]
            self.current_metrics.p99_response_time_ms = sorted_times[int(len(sorted_times) * 0.99)]

        # Calculate overall average
        self.current_metrics.avg_response_time_ms = sum(self.response_times) / len(self.response_times)

        # Check for alerts
        self._check_alerts(role, response_time_ms, success, error_type)

        # Log the request
        _LOG.info(
            f"Context request: role={role}, success={success}, " f"time={response_time_ms:.2f}ms, cache_hit={cache_hit}"
        )

    def record_cache_metrics(self, cache_size: int, evictions: int = 0):
        """Record cache-related metrics."""
        self.current_metrics.cache_size = cache_size
        self.current_metrics.cache_evictions += evictions

    def record_memory_usage(self, memory_mb: float):
        """Record memory usage metrics."""
        self.current_metrics.memory_usage_mb = memory_mb

    def _check_alerts(self, role: str, response_time_ms: float, success: bool, error_type: Optional[str]):
        """Check for alert conditions."""
        timestamp = datetime.now(timezone.utc).isoformat()

        # High response time alert
        if response_time_ms > 10000:  # 10 seconds
            alert = {
                "timestamp": timestamp,
                "level": "WARNING",
                "type": "high_response_time",
                "message": f"High response time for role {role}: {response_time_ms:.2f}ms",
                "role": role,
                "response_time_ms": response_time_ms,
            }
            self.alerts.append(alert)
            _LOG.warning(f"ALERT: {alert['message']}")

        # Error rate alert
        if not success:
            error_rate = (self.current_metrics.failed_requests / max(self.current_metrics.total_requests, 1)) * 100
            if error_rate > 20:  # 20% error rate
                alert = {
                    "timestamp": timestamp,
                    "level": "ERROR",
                    "type": "high_error_rate",
                    "message": f"High error rate: {error_rate:.1f}%",
                    "error_rate": error_rate,
                    "error_type": error_type,
                }
                self.alerts.append(alert)
                _LOG.error(f"ALERT: {alert['message']}")

        # Role-specific error alert
        role_errors = self.current_metrics.role_errors[role]
        role_requests = self.current_metrics.role_requests[role]
        if role_requests > 10:  # Only alert after sufficient requests
            role_error_rate = (role_errors / role_requests) * 100
            if role_error_rate > 30:  # 30% error rate for specific role
                alert = {
                    "timestamp": timestamp,
                    "level": "ERROR",
                    "type": "role_error_rate",
                    "message": f"High error rate for role {role}: {role_error_rate:.1f}%",
                    "role": role,
                    "error_rate": role_error_rate,
                }
                self.alerts.append(alert)
                _LOG.error(f"ALERT: {alert['message']}")

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get a summary of current metrics."""
        return {
            "current_metrics": asdict(self.current_metrics),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime": self._calculate_uptime(),
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get a detailed performance report."""
        if not self.response_times:
            return {"error": "No data available"}

        sorted_times = sorted(self.response_times)
        return {
            "response_time_stats": {
                "count": len(self.response_times),
                "min_ms": min(self.response_times),
                "max_ms": max(self.response_times),
                "avg_ms": sum(self.response_times) / len(self.response_times),
                "p50_ms": sorted_times[len(sorted_times) // 2],
                "p95_ms": sorted_times[int(len(sorted_times) * 0.95)],
                "p99_ms": sorted_times[int(len(sorted_times) * 0.99)],
            },
            "cache_stats": {
                "hit_rate": (self.current_metrics.cache_hits / max(self.current_metrics.total_requests, 1)) * 100,
                "cache_size": self.current_metrics.cache_size,
                "evictions": self.current_metrics.cache_evictions,
            },
            "error_stats": {
                "total_errors": self.current_metrics.failed_requests,
                "error_rate": (self.current_metrics.failed_requests / max(self.current_metrics.total_requests, 1))
                * 100,
                "timeout_errors": self.current_metrics.timeout_errors,
                "subprocess_errors": self.current_metrics.subprocess_errors,
                "parsing_errors": self.current_metrics.parsing_errors,
                "fallback_usage": self.current_metrics.fallback_usage,
            },
            "role_stats": {
                role: {
                    "requests": count,
                    "errors": self.current_metrics.role_errors[role],
                    "avg_time_ms": self.current_metrics.role_avg_times[role],
                    "error_rate": (self.current_metrics.role_errors[role] / count) * 100,
                }
                for role, count in self.current_metrics.role_requests.items()
            },
        }

    def _calculate_uptime(self) -> str:
        """Calculate system uptime."""
        # This is a simplified uptime calculation
        # In a real system, you'd track actual start time
        return "Unknown"  # Placeholder

    def _load_metrics(self):
        """Load metrics from file."""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r") as f:
                    data = json.load(f)
                    # Load historical data if available
                    if "historical_data" in data:
                        self.historical_data = deque(data["historical_data"], maxlen=self.max_history)
            except Exception as e:
                _LOG.warning(f"Failed to load metrics: {e}")

    def save_metrics(self):
        """Save metrics to file."""
        try:
            data = {
                "current_metrics": asdict(self.current_metrics),
                "historical_data": list(self.historical_data),
                "alerts": self.alerts[-50:],  # Keep last 50 alerts
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            with open(self.metrics_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            _LOG.error(f"Failed to save metrics: {e}")

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts.clear()

    def export_metrics(self, format: str = "json") -> str:
        """Export metrics in specified format."""
        if format == "json":
            return json.dumps(self.get_metrics_summary(), indent=2)
        elif format == "csv":
            return self._export_csv()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_csv(self) -> str:
        """Export metrics as CSV."""
        import csv
        import io

        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(
            [
                "timestamp",
                "total_requests",
                "successful_requests",
                "failed_requests",
                "avg_response_time_ms",
                "cache_hit_rate",
                "error_rate",
            ]
        )

        # Write data
        metrics = self.current_metrics
        cache_hit_rate = (metrics.cache_hits / max(metrics.total_requests, 1)) * 100
        error_rate = (metrics.failed_requests / max(metrics.total_requests, 1)) * 100

        writer.writerow(
            [
                datetime.now(timezone.utc).isoformat(),
                metrics.total_requests,
                metrics.successful_requests,
                metrics.failed_requests,
                f"{metrics.avg_response_time_ms:.2f}",
                f"{cache_hit_rate:.2f}",
                f"{error_rate:.2f}",
            ]
        )

        return output.getvalue()


# Global monitor instance
_context_monitor = None


def get_context_monitor() -> ContextMonitor:
    """Get the global context monitor instance."""
    global _context_monitor
    if _context_monitor is None:
        _context_monitor = ContextMonitor()
    return _context_monitor


def record_context_request(
    role: str,
    task: str,
    start_time: float,
    success: bool,
    response_time: float,
    cache_hit: bool = False,
    error_type: Optional[str] = None,
    fallback_used: bool = False,
):
    """Record a context request using the global monitor."""
    monitor = get_context_monitor()
    monitor.record_request(role, task, start_time, success, response_time, cache_hit, error_type, fallback_used)


def get_context_metrics() -> Dict[str, Any]:
    """Get current context metrics."""
    monitor = get_context_monitor()
    return monitor.get_metrics_summary()


def get_performance_report() -> Dict[str, Any]:
    """Get detailed performance report."""
    monitor = get_context_monitor()
    return monitor.get_performance_report()


def save_context_metrics():
    """Save context metrics to file."""
    monitor = get_context_monitor()
    monitor.save_metrics()


if __name__ == "__main__":
    # Example usage
    monitor = ContextMonitor()

    # Record some example requests
    monitor.record_request("coder", "test task", time.time(), True, 1.5, cache_hit=True)
    monitor.record_request("planner", "test task", time.time(), False, 12.0, error_type="timeout")

    # Get metrics
    print(json.dumps(monitor.get_metrics_summary(), indent=2))
    print("\nPerformance Report:")
    print(json.dumps(monitor.get_performance_report(), indent=2))
