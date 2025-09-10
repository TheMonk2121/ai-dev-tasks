#!/usr/bin/env python3
"""
Metrics Dashboard and Measurement System

Provides systematic measurement and visualization of optimization progress
with real-time monitoring, historical tracking, and actionable metrics.
"""

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .optimization_loop import (
    FourPartOptimizationLoop,
    OptimizationCycle,
    PhaseResult,
)

_LOG = logging.getLogger("dspy_metrics_dashboard")


class MetricType(Enum):
    """Types of metrics tracked by the dashboard"""

    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    QUALITY = "quality"
    DURATION = "duration"
    SUCCESS_RATE = "success_rate"
    IMPROVEMENT = "improvement"
    OPTIMIZATION_COUNT = "optimization_count"
    ERROR_RATE = "error_rate"


class DashboardView(Enum):
    """Available dashboard views"""

    OVERVIEW = "overview"
    DETAILED = "detailed"
    HISTORICAL = "historical"
    COMPARISON = "comparison"
    ALERTS = "alerts"


@dataclass
class MetricPoint:
    """A single metric data point"""

    timestamp: float
    value: float
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {"timestamp": self.timestamp, "value": self.value, "metadata": self.metadata}


@dataclass
class MetricSeries:
    """A series of metric data points"""

    metric_type: MetricType
    data_points: list[MetricPoint] = field(default_factory=list)
    max_points: int = 1000  # Limit memory usage

    def add_point(self, value: float, metadata: dict[str, Any] | None = None):
        """Add a new data point to the series"""
        point = MetricPoint(timestamp=time.time(), value=value, metadata=metadata or {})

        self.data_points.append(point)

        # Maintain max points limit
        if len(self.data_points) > self.max_points:
            self.data_points.pop(0)

    def get_latest_value(self) -> float | None:
        """Get the most recent value"""
        if self.data_points:
            return self.data_points[-1].value
        return None

    def get_average(self, window_minutes: int = 60) -> float | None:
        """Get average value over a time window"""
        if not self.data_points:
            return None

        cutoff_time = time.time() - (window_minutes * 60)
        recent_points = [p for p in self.data_points if p.timestamp >= cutoff_time]

        if not recent_points:
            return None

        return sum(p.value for p in recent_points) / len(recent_points)

    def get_trend(self, window_minutes: int = 60) -> float | None:
        """Get trend (slope) over a time window"""
        if not self.data_points:
            return None

        cutoff_time = time.time() - (window_minutes * 60)
        recent_points = [p for p in self.data_points if p.timestamp >= cutoff_time]

        if len(recent_points) < 2:
            return None

            # Simple linear regression
        x_values = [p.timestamp for p in recent_points]
        y_values = [p.value for p in recent_points]

        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)

        denominator = n * sum_x2 - sum_x * sum_x
        if denominator == 0:
            return 0.0  # No trend if denominator is zero

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        return slope

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "metric_type": self.metric_type.value,
            "data_points": [p.to_dict() for p in self.data_points],
            "max_points": self.max_points,
        }


@dataclass
class Alert:
    """Alert for metric threshold violations"""

    alert_id: str
    metric_type: MetricType
    threshold: float
    current_value: float
    severity: str  # "low", "medium", "high", "critical"
    message: str
    timestamp: float
    acknowledged: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "alert_id": self.alert_id,
            "metric_type": self.metric_type.value,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp,
            "acknowledged": self.acknowledged,
        }


class MetricsDashboard:
    """Main metrics dashboard for optimization tracking"""

    def __init__(self, max_history_days: int = 30):
        """Initialize the metrics dashboard"""
        self.max_history_days = max_history_days
        self.metric_series: dict[MetricType, MetricSeries] = {}
        self.alerts: list[Alert] = []
        self.optimization_loop: FourPartOptimizationLoop | None = None
        self.alert_thresholds: dict[MetricType, dict[str, float]] = {
            MetricType.RELIABILITY: {"critical": 50.0, "high": 70.0, "medium": 85.0},
            MetricType.PERFORMANCE: {"critical": 0.3, "high": 0.5, "medium": 0.7},
            MetricType.QUALITY: {"critical": 0.3, "high": 0.5, "medium": 0.7},
            MetricType.SUCCESS_RATE: {"critical": 0.5, "high": 0.7, "medium": 0.9},
            MetricType.ERROR_RATE: {"critical": 0.5, "high": 0.3, "medium": 0.1},
        }

        # Initialize metric series
        for metric_type in MetricType:
            self.metric_series[metric_type] = MetricSeries(metric_type=metric_type)

        _LOG.info("Metrics Dashboard initialized")

    def connect_optimization_loop(self, loop: FourPartOptimizationLoop):
        """Connect to an optimization loop for automatic metric collection"""
        self.optimization_loop = loop
        _LOG.info("Connected to optimization loop for automatic metric collection")

    def record_cycle_metrics(self, cycle: OptimizationCycle):
        """Record metrics from an optimization cycle"""
        if not cycle:
            return

        # Record cycle-level metrics
        self._record_cycle_duration(cycle)
        self._record_cycle_success_rate(cycle)
        self._record_cycle_improvements(cycle)

        # Record phase-level metrics
        for phase in cycle.phases:
            self._record_phase_metrics(phase)

        # Check for alerts
        self._check_alerts()

        _LOG.debug(f"Recorded metrics for cycle {cycle.cycle_id}")

    def _record_cycle_duration(self, cycle: OptimizationCycle):
        """Record cycle duration metrics"""
        duration = cycle.duration
        self.metric_series[MetricType.DURATION].add_point(
            duration, metadata={"cycle_id": cycle.cycle_id, "phases_count": len(cycle.phases)}
        )

    def _record_cycle_success_rate(self, cycle: OptimizationCycle):
        """Record cycle success rate metrics"""
        success_rate = 1.0 if cycle.success else 0.0
        self.metric_series[MetricType.SUCCESS_RATE].add_point(
            success_rate, metadata={"cycle_id": cycle.cycle_id, "status": cycle.overall_status.value}
        )

    def _record_cycle_improvements(self, cycle: OptimizationCycle):
        """Record cycle improvement metrics"""
        if not cycle.overall_metrics:
            return

        # Record reliability improvements
        if "optimize_reliability_improvement" in cycle.overall_metrics:
            improvement = cycle.overall_metrics["optimize_reliability_improvement"]
            self.metric_series[MetricType.IMPROVEMENT].add_point(
                improvement, metadata={"cycle_id": cycle.cycle_id, "type": "reliability"}
            )

        # Record overall improvements
        if "optimize_overall_improvement" in cycle.overall_metrics:
            improvement = cycle.overall_metrics["optimize_overall_improvement"]
            self.metric_series[MetricType.IMPROVEMENT].add_point(
                improvement, metadata={"cycle_id": cycle.cycle_id, "type": "overall"}
            )

    def _record_phase_metrics(self, phase: PhaseResult):
        """Record phase-level metrics"""
        if not phase.metrics:
            return

        # Record reliability metrics
        if "reliability_score" in phase.metrics:
            reliability = phase.metrics["reliability_score"]
            self.metric_series[MetricType.RELIABILITY].add_point(
                reliability, metadata={"phase": phase.phase.value, "status": phase.status.value}
            )

        # Record performance metrics
        if "performance_score" in phase.metrics:
            performance = phase.metrics["performance_score"]
            self.metric_series[MetricType.PERFORMANCE].add_point(
                performance, metadata={"phase": phase.phase.value, "status": phase.status.value}
            )

        # Record quality metrics
        if "quality_score" in phase.metrics:
            quality = phase.metrics["quality_score"]
            self.metric_series[MetricType.QUALITY].add_point(
                quality, metadata={"phase": phase.phase.value, "status": phase.status.value}
            )

    def _check_alerts(self):
        """Check for metric threshold violations and create alerts"""
        for metric_type, thresholds in self.alert_thresholds.items():
            series = self.metric_series.get(metric_type)
            if not series:
                continue

            latest_value = series.get_latest_value()
            if latest_value is None:
                continue

            # Check thresholds in order of severity
            for severity, threshold in thresholds.items():
                if metric_type == MetricType.ERROR_RATE:
                    # For error rate, alert when value is above threshold
                    if latest_value > threshold:
                        self._create_alert(metric_type, threshold, latest_value, severity)
                        break
                else:
                    # For other metrics, alert when value is below threshold
                    if latest_value < threshold:
                        self._create_alert(metric_type, threshold, latest_value, severity)
                        break

    def _create_alert(self, metric_type: MetricType, threshold: float, current_value: float, severity: str):
        """Create a new alert"""
        alert_id = f"alert_{metric_type.value}_{int(time.time())}"

        if metric_type == MetricType.ERROR_RATE:
            message = f"Error rate ({current_value:.1%}) is above {severity} threshold ({threshold:.1%})"
        else:
            message = (
                f"{metric_type.value.title()} ({current_value:.1%}) is below {severity} threshold ({threshold:.1%})"
            )

        alert = Alert(
            alert_id=alert_id,
            metric_type=metric_type,
            threshold=threshold,
            current_value=current_value,
            severity=severity,
            message=message,
            timestamp=time.time(),
        )

        self.alerts.append(alert)
        _LOG.warning(f"Alert created: {message}")

    def get_dashboard_data(self, view: DashboardView = DashboardView.OVERVIEW) -> dict[str, Any]:
        """Get dashboard data for the specified view"""
        if view == DashboardView.OVERVIEW:
            return self._get_overview_data()
        elif view == DashboardView.DETAILED:
            return self._get_detailed_data()
        elif view == DashboardView.HISTORICAL:
            return self._get_historical_data()
        elif view == DashboardView.COMPARISON:
            return self._get_comparison_data()
        elif view == DashboardView.ALERTS:
            return self._get_alerts_data()
        else:
            return {"error": f"Unknown view: {view}"}

    def _get_overview_data(self) -> dict[str, Any]:
        """Get overview dashboard data"""
        data = {
            "timestamp": time.time(),
            "view": "overview",
            "summary": {},
            "current_metrics": {},
            "trends": {},
            "alerts": {},
        }

        # Summary statistics
        data["summary"] = {
            "total_cycles": len(self.optimization_loop.cycles) if self.optimization_loop else 0,
            "successful_cycles": (
                len([c for c in self.optimization_loop.cycles if c.success]) if self.optimization_loop else 0
            ),
            "active_alerts": len([a for a in self.alerts if not a.acknowledged]),
            "last_cycle_time": self._get_last_cycle_time(),
        }

        # Current metrics
        for metric_type in MetricType:
            series = self.metric_series.get(metric_type)
            if series:
                latest_value = series.get_latest_value()
                if latest_value is not None:
                    data["current_metrics"][metric_type.value] = {
                        "value": latest_value,
                        "unit": self._get_metric_unit(metric_type),
                        "status": self._get_metric_status(metric_type, latest_value),
                    }

        # Trends (1-hour window)
        for metric_type in MetricType:
            series = self.metric_series.get(metric_type)
            if series:
                trend = series.get_trend(window_minutes=60)
                if trend is not None:
                    data["trends"][metric_type.value] = {
                        "slope": trend,
                        "direction": "improving" if trend > 0 else "declining" if trend < 0 else "stable",
                    }

        # Recent alerts
        recent_alerts = [a for a in self.alerts if not a.acknowledged and time.time() - a.timestamp < 3600]
        data["alerts"] = {"count": len(recent_alerts), "recent": [a.to_dict() for a in recent_alerts[:5]]}

        return data

    def _get_detailed_data(self) -> dict[str, Any]:
        """Get detailed dashboard data"""
        data = {"timestamp": time.time(), "view": "detailed", "metrics": {}, "phases": {}, "cycles": {}}

        # Detailed metrics for each type
        for metric_type in MetricType:
            series = self.metric_series.get(metric_type)
            if series:
                data["metrics"][metric_type.value] = {
                    "current": series.get_latest_value(),
                    "average_1h": series.get_average(window_minutes=60),
                    "average_24h": series.get_average(window_minutes=1440),
                    "trend_1h": series.get_trend(window_minutes=60),
                    "data_points": len(series.data_points),
                    "unit": self._get_metric_unit(metric_type),
                }

        # Phase-level statistics
        if self.optimization_loop:
            phase_stats = defaultdict(lambda: {"count": 0, "success_count": 0, "avg_duration": 0.0})

            for cycle in self.optimization_loop.cycles:
                for phase in cycle.phases:
                    phase_stats[phase.phase.value]["count"] += 1
                    if phase.success:
                        phase_stats[phase.phase.value]["success_count"] += 1
                    phase_stats[phase.phase.value]["avg_duration"] += phase.duration

            # Calculate averages
            for phase_name, stats in phase_stats.items():
                if stats["count"] > 0:
                    stats["avg_duration"] /= stats["count"]
                    stats["success_rate"] = stats["success_count"] / stats["count"]

            data["phases"] = dict(phase_stats)

        # Cycle-level statistics
        if self.optimization_loop:
            data["cycles"] = {
                "total": len(self.optimization_loop.cycles),
                "successful": len([c for c in self.optimization_loop.cycles if c.success]),
                "failed": len([c for c in self.optimization_loop.cycles if not c.success]),
                "avg_duration": (
                    sum(c.duration for c in self.optimization_loop.cycles) / len(self.optimization_loop.cycles)
                    if self.optimization_loop.cycles
                    else 0.0
                ),
                "recent_cycles": [c.cycle_id for c in self.optimization_loop.cycles[-5:]],
            }

        return data

    def _get_historical_data(self) -> dict[str, Any]:
        """Get historical dashboard data"""
        data = {
            "timestamp": time.time(),
            "view": "historical",
            "time_ranges": ["1h", "6h", "24h", "7d", "30d"],
            "metrics": {},
        }

        # Historical data for each metric type
        for metric_type in MetricType:
            series = self.metric_series.get(metric_type)
            if series:
                data["metrics"][metric_type.value] = {
                    "data_points": [p.to_dict() for p in series.data_points[-100:]],  # Last 100 points
                    "statistics": {
                        "min": min(p.value for p in series.data_points) if series.data_points else None,
                        "max": max(p.value for p in series.data_points) if series.data_points else None,
                        "avg": (
                            sum(p.value for p in series.data_points) / len(series.data_points)
                            if series.data_points
                            else None
                        ),
                    },
                }

        return data

    def _get_comparison_data(self) -> dict[str, Any]:
        """Get comparison dashboard data"""
        data = {"timestamp": time.time(), "view": "comparison", "comparisons": {}}

        # Compare current vs historical performance
        for metric_type in MetricType:
            series = self.metric_series.get(metric_type)
            if series and series.data_points:
                current = series.get_latest_value()
                avg_24h = series.get_average(window_minutes=1440)
                avg_7d = series.get_average(window_minutes=10080)

                if current is not None and avg_24h is not None:
                    change_24h = ((current - avg_24h) / avg_24h) * 100 if avg_24h != 0 else 0
                else:
                    change_24h = 0

                if current is not None and avg_7d is not None:
                    change_7d = ((current - avg_7d) / avg_7d) * 100 if avg_7d != 0 else 0
                else:
                    change_7d = 0

                data["comparisons"][metric_type.value] = {
                    "current": current,
                    "avg_24h": avg_24h,
                    "avg_7d": avg_7d,
                    "change_24h": change_24h,
                    "change_7d": change_7d,
                    "unit": self._get_metric_unit(metric_type),
                }

        return data

    def _get_alerts_data(self) -> dict[str, Any]:
        """Get alerts dashboard data"""
        data = {
            "timestamp": time.time(),
            "view": "alerts",
            "alerts": {
                "active": [a.to_dict() for a in self.alerts if not a.acknowledged],
                "acknowledged": [a.to_dict() for a in self.alerts if a.acknowledged],
                "summary": {
                    "total": len(self.alerts),
                    "active": len([a for a in self.alerts if not a.acknowledged]),
                    "acknowledged": len([a for a in self.alerts if a.acknowledged]),
                    "by_severity": self._get_alerts_by_severity(),
                },
            },
        }

        return data

    def _get_alerts_by_severity(self) -> dict[str, int]:
        """Get alert counts by severity"""
        severity_counts = defaultdict(int)
        for alert in self.alerts:
            if not alert.acknowledged:
                severity_counts[alert.severity] += 1
        return dict(severity_counts)

    def _get_metric_unit(self, metric_type: MetricType) -> str:
        """Get the unit for a metric type"""
        units = {
            MetricType.RELIABILITY: "%",
            MetricType.PERFORMANCE: "%",
            MetricType.QUALITY: "%",
            MetricType.DURATION: "s",
            MetricType.SUCCESS_RATE: "%",
            MetricType.IMPROVEMENT: "%",
            MetricType.OPTIMIZATION_COUNT: "count",
            MetricType.ERROR_RATE: "%",
        }
        return units.get(metric_type, "")

    def _get_metric_status(self, metric_type: MetricType, value: float) -> str:
        """Get the status for a metric value"""
        thresholds = self.alert_thresholds.get(metric_type, {})

        if metric_type == MetricType.ERROR_RATE:
            # For error rate, lower is better
            if value > thresholds.get("critical", 0.5):
                return "critical"
            elif value > thresholds.get("high", 0.3):
                return "high"
            elif value > thresholds.get("medium", 0.1):
                return "medium"
            else:
                return "good"
        else:
            # For other metrics, higher is better
            if value < thresholds.get("critical", 50.0):
                return "critical"
            elif value < thresholds.get("high", 70.0):
                return "high"
            elif value < thresholds.get("medium", 85.0):
                return "medium"
            else:
                return "good"

    def _get_last_cycle_time(self) -> float | None:
        """Get the timestamp of the last optimization cycle"""
        if self.optimization_loop and self.optimization_loop.cycles:
            return self.optimization_loop.cycles[-1].start_time
        return None

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                _LOG.info(f"Alert {alert_id} acknowledged")
                return True
        return False

    def clear_old_alerts(self, days: int = 7):
        """Clear alerts older than specified days"""
        cutoff_time = time.time() - (days * 24 * 3600)
        self.alerts = [a for a in self.alerts if a.timestamp >= cutoff_time]
        _LOG.info(f"Cleared alerts older than {days} days")

    def export_data(self, format: str = "json") -> str:
        """Export dashboard data"""
        if format.lower() == "json":
            data = {
                "dashboard_info": {"timestamp": time.time(), "max_history_days": self.max_history_days},
                "metric_series": {
                    metric_type.value: series.to_dict() for metric_type, series in self.metric_series.items()
                },
                "alerts": [a.to_dict() for a in self.alerts],
            }
            return json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def get_statistics(self) -> dict[str, Any]:
        """Get dashboard statistics"""
        stats = {
            "total_metrics": len(self.metric_series),
            "total_data_points": sum(len(series.data_points) for series in self.metric_series.values()),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts if not a.acknowledged]),
            "connected_to_loop": self.optimization_loop is not None,
        }

        # Add metric-specific statistics
        for metric_type, series in self.metric_series.items():
            if series.data_points:
                stats[f"{metric_type.value}_data_points"] = len(series.data_points)
                stats[f"{metric_type.value}_latest"] = series.get_latest_value()
                stats[f"{metric_type.value}_avg_24h"] = series.get_average(window_minutes=1440)

        return stats


# Global dashboard instance
_dashboard = None


def get_metrics_dashboard() -> MetricsDashboard:
    """Get the global metrics dashboard instance"""
    global _dashboard
    if _dashboard is None:
        _dashboard = MetricsDashboard()
    return _dashboard


def record_optimization_metrics(cycle: OptimizationCycle):
    """Convenience function to record optimization metrics"""
    dashboard = get_metrics_dashboard()
    dashboard.record_cycle_metrics(cycle)


def get_dashboard_view(view: DashboardView = DashboardView.OVERVIEW) -> dict[str, Any]:
    """Convenience function to get dashboard view"""
    dashboard = get_metrics_dashboard()
    return dashboard.get_dashboard_data(view)
