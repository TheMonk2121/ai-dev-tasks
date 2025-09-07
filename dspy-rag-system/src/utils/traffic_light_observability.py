#!/usr/bin/env python3
"""
Traffic Light Observability - Production-Grade Metrics Dashboard
Traffic-light aligned metrics for retrieval, data quality, infra, and agent tool use
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

LOG = logging.getLogger(__name__)


class TrafficLightStatus(Enum):
    """Traffic light status for metrics."""

    GREEN = "🟢"
    YELLOW = "🟡"
    RED = "🔴"
    UNKNOWN = "⚪"


@dataclass
class MetricThreshold:
    """Threshold configuration for a metric."""

    green_max: float
    yellow_max: float
    red_max: float
    unit: str = ""
    description: str = ""


@dataclass
class MetricValue:
    """A single metric value with status."""

    name: str
    value: float
    status: TrafficLightStatus
    threshold: MetricThreshold
    timestamp: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TrafficLightObservability:
    """Traffic light aligned observability system."""

    def __init__(self, config_file: Optional[str] = None):
        self.metrics: Dict[str, MetricValue] = {}
        self.thresholds: Dict[str, MetricThreshold] = {}
        self.alerts: List[Dict[str, Any]] = []

        # Load configuration
        self._load_config(config_file)

        # Initialize default thresholds
        self._initialize_default_thresholds()

    def _load_config(self, config_file: Optional[str]):
        """Load configuration from file."""
        if config_file and Path(config_file).exists():
            with open(config_file, "r") as f:
                config = json.load(f)
                self.thresholds = {
                    name: MetricThreshold(**threshold) for name, threshold in config.get("thresholds", {}).items()
                }

    def _initialize_default_thresholds(self):
        """Initialize default traffic light thresholds."""
        default_thresholds = {
            # Retrieval Metrics
            "retrieval_snapshot_size": MetricThreshold(
                green_max=30,
                yellow_max=20,
                red_max=10,
                unit="chunks",
                description="Number of chunks in retrieval snapshot",
            ),
            "oracle_retrieval_hit_prefilter": MetricThreshold(
                green_max=0.8,
                yellow_max=0.6,
                red_max=0.4,
                unit="ratio",
                description="Oracle retrieval hit rate before filtering",
            ),
            "oracle_retrieval_hit_postfilter": MetricThreshold(
                green_max=0.7,
                yellow_max=0.5,
                red_max=0.3,
                unit="ratio",
                description="Oracle retrieval hit rate after filtering",
            ),
            "reader_used_gold": MetricThreshold(
                green_max=0.9, yellow_max=0.7, red_max=0.5, unit="ratio", description="Reader used gold context ratio"
            ),
            # Data Quality Metrics
            "max_embedding_token_count": MetricThreshold(
                green_max=1024,
                yellow_max=1200,
                red_max=1500,
                unit="tokens",
                description="Maximum embedding token count",
            ),
            "dedup_rate": MetricThreshold(
                green_max=0.95, yellow_max=0.9, red_max=0.8, unit="ratio", description="Chunk deduplication rate"
            ),
            "prefix_leakage": MetricThreshold(
                green_max=0, yellow_max=0, red_max=0, unit="count", description="Number of chunks with prefix leakage"
            ),
            # Infrastructure Metrics
            "reranker_cold_start_rate": MetricThreshold(
                green_max=0, yellow_max=0.05, red_max=0.1, unit="ratio", description="Reranker cold start rate"
            ),
            "bedrock_timeout_rate": MetricThreshold(
                green_max=0, yellow_max=0.02, red_max=0.05, unit="ratio", description="Bedrock API timeout rate"
            ),
            "p95_latency_ms": MetricThreshold(
                green_max=2000, yellow_max=5000, red_max=10000, unit="ms", description="95th percentile latency"
            ),
            # Agent Tool Use Metrics
            "tool_intent_log_rate": MetricThreshold(
                green_max=1.0, yellow_max=0.8, red_max=0.6, unit="ratio", description="Tool intent logging rate"
            ),
            "dry_run_rate": MetricThreshold(
                green_max=0.9, yellow_max=0.7, red_max=0.5, unit="ratio", description="Dry run validation rate"
            ),
            "schema_conformance_rate": MetricThreshold(
                green_max=0.95, yellow_max=0.85, red_max=0.7, unit="ratio", description="Schema conformance rate"
            ),
        }

        # Merge with loaded thresholds
        for name, threshold in default_thresholds.items():
            if name not in self.thresholds:
                self.thresholds[name] = threshold

    def evaluate_metric(self, name: str, value: float, metadata: Dict[str, Any] = None) -> MetricValue:
        """Evaluate a metric value against thresholds."""
        if name not in self.thresholds:
            LOG.warning(f"No threshold defined for metric: {name}")
            return MetricValue(
                name=name,
                value=value,
                status=TrafficLightStatus.UNKNOWN,
                threshold=MetricThreshold(0, 0, 0),
                timestamp=time.time(),
                metadata=metadata or {},
            )

        threshold = self.thresholds[name]

        # Determine status (lower is better for most metrics)
        if value <= threshold.green_max:
            status = TrafficLightStatus.GREEN
        elif value <= threshold.yellow_max:
            status = TrafficLightStatus.YELLOW
        elif value <= threshold.red_max:
            status = TrafficLightStatus.RED
        else:
            status = TrafficLightStatus.RED

        metric_value = MetricValue(
            name=name, value=value, status=status, threshold=threshold, timestamp=time.time(), metadata=metadata or {}
        )

        # Store metric
        self.metrics[name] = metric_value

        # Check for alerts
        self._check_alerts(metric_value)

        return metric_value

    def _check_alerts(self, metric: MetricValue):
        """Check if metric triggers alerts."""
        if metric.status == TrafficLightStatus.RED:
            alert = {
                "timestamp": metric.timestamp,
                "metric": metric.name,
                "value": metric.value,
                "threshold": metric.threshold.red_max,
                "severity": "CRITICAL",
                "message": f"{metric.name} is {metric.status.value} RED: {metric.value} > {metric.threshold.red_max}",
            }
            self.alerts.append(alert)
            LOG.error(f"ALERT: {alert['message']}")

        elif metric.status == TrafficLightStatus.YELLOW:
            alert = {
                "timestamp": metric.timestamp,
                "metric": metric.name,
                "value": metric.value,
                "threshold": metric.threshold.yellow_max,
                "severity": "WARNING",
                "message": f"{metric.name} is {metric.status.value} YELLOW: {metric.value} > {metric.threshold.yellow_max}",
            }
            self.alerts.append(alert)
            LOG.warning(f"ALERT: {alert['message']}")

    def get_retrieval_metrics(self) -> Dict[str, Any]:
        """Get retrieval-specific metrics."""
        retrieval_metrics = [
            "retrieval_snapshot_size",
            "oracle_retrieval_hit_prefilter",
            "oracle_retrieval_hit_postfilter",
            "reader_used_gold",
        ]

        return {
            "metrics": {name: asdict(self.metrics.get(name)) for name in retrieval_metrics if name in self.metrics},
            "overall_status": self._get_category_status(retrieval_metrics),
            "last_updated": max(
                [self.metrics[name].timestamp for name in retrieval_metrics if name in self.metrics], default=0
            ),
        }

    def get_data_quality_metrics(self) -> Dict[str, Any]:
        """Get data quality metrics."""
        quality_metrics = ["max_embedding_token_count", "dedup_rate", "prefix_leakage"]

        return {
            "metrics": {name: asdict(self.metrics.get(name)) for name in quality_metrics if name in self.metrics},
            "overall_status": self._get_category_status(quality_metrics),
            "last_updated": max(
                [self.metrics[name].timestamp for name in quality_metrics if name in self.metrics], default=0
            ),
        }

    def get_infrastructure_metrics(self) -> Dict[str, Any]:
        """Get infrastructure metrics."""
        infra_metrics = ["reranker_cold_start_rate", "bedrock_timeout_rate", "p95_latency_ms"]

        return {
            "metrics": {name: asdict(self.metrics.get(name)) for name in infra_metrics if name in self.metrics},
            "overall_status": self._get_category_status(infra_metrics),
            "last_updated": max(
                [self.metrics[name].timestamp for name in infra_metrics if name in self.metrics], default=0
            ),
        }

    def get_agent_tool_metrics(self) -> Dict[str, Any]:
        """Get agent tool use metrics."""
        tool_metrics = ["tool_intent_log_rate", "dry_run_rate", "schema_conformance_rate"]

        return {
            "metrics": {name: asdict(self.metrics.get(name)) for name in tool_metrics if name in self.metrics},
            "overall_status": self._get_category_status(tool_metrics),
            "last_updated": max(
                [self.metrics[name].timestamp for name in tool_metrics if name in self.metrics], default=0
            ),
        }

    def _get_category_status(self, metric_names: List[str]) -> str:
        """Get overall status for a category of metrics."""
        statuses = [self.metrics[name].status for name in metric_names if name in self.metrics]

        if not statuses:
            return TrafficLightStatus.UNKNOWN.value

        if any(status == TrafficLightStatus.RED for status in statuses):
            return TrafficLightStatus.RED.value
        elif any(status == TrafficLightStatus.YELLOW for status in statuses):
            return TrafficLightStatus.YELLOW.value
        else:
            return TrafficLightStatus.GREEN.value

    def get_overall_status(self) -> Dict[str, Any]:
        """Get overall system status."""
        all_metrics = list(self.metrics.keys())
        overall_status = self._get_category_status(all_metrics)

        # Count by status
        status_counts = {
            "green": sum(1 for m in self.metrics.values() if m.status == TrafficLightStatus.GREEN),
            "yellow": sum(1 for m in self.metrics.values() if m.status == TrafficLightStatus.YELLOW),
            "red": sum(1 for m in self.metrics.values() if m.status == TrafficLightStatus.RED),
            "unknown": sum(1 for m in self.metrics.values() if m.status == TrafficLightStatus.UNKNOWN),
        }

        return {
            "overall_status": overall_status,
            "status_counts": status_counts,
            "total_metrics": len(self.metrics),
            "active_alerts": len([a for a in self.alerts if a["severity"] == "CRITICAL"]),
            "warnings": len([a for a in self.alerts if a["severity"] == "WARNING"]),
            "last_updated": max([m.timestamp for m in self.metrics.values()], default=0),
        }

    def generate_dashboard_data(self) -> Dict[str, Any]:
        """Generate complete dashboard data."""
        return {
            "timestamp": time.time(),
            "overall": self.get_overall_status(),
            "retrieval": self.get_retrieval_metrics(),
            "data_quality": self.get_data_quality_metrics(),
            "infrastructure": self.get_infrastructure_metrics(),
            "agent_tools": self.get_agent_tool_metrics(),
            "recent_alerts": self.alerts[-10:],  # Last 10 alerts
            "thresholds": {name: asdict(threshold) for name, threshold in self.thresholds.items()},
        }

    def export_dashboard(self, filename: str):
        """Export dashboard data to JSON file."""
        dashboard_data = self.generate_dashboard_data()

        # Ensure directory exists
        Path(filename).parent.mkdir(parents=True, exist_ok=True)

        with open(filename, "w") as f:
            json.dump(dashboard_data, f, indent=2)

        LOG.info(f"Dashboard exported to: {filename}")

    def print_traffic_light_report(self):
        """Print a traffic light status report."""
        overall = self.get_overall_status()

        print("\n" + "=" * 80)
        print(f"🚦 TRAFFIC LIGHT OBSERVABILITY REPORT - {overall['overall_status']}")
        print("=" * 80)
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Metrics: {overall['total_metrics']}")
        print(f"Active Alerts: {overall['active_alerts']}")
        print(f"Warnings: {overall['warnings']}")

        # Print each category
        categories = {
            "Retrieval": self.get_retrieval_metrics(),
            "Data Quality": self.get_data_quality_metrics(),
            "Infrastructure": self.get_infrastructure_metrics(),
            "Agent Tools": self.get_agent_tool_metrics(),
        }

        for category_name, category_data in categories.items():
            print(f"\n📋 {category_name.upper()} - {category_data['overall_status']}")
            print("-" * 40)

            for metric_name, metric_data in category_data["metrics"].items():
                status_emoji = metric_data["status"]
                value = metric_data["value"]
                unit = metric_data["threshold"]["unit"]
                print(f"{status_emoji} {metric_name}: {value} {unit}")

        # Print recent alerts
        if self.alerts:
            print("\n🚨 RECENT ALERTS")
            print("-" * 40)
            for alert in self.alerts[-5:]:  # Last 5 alerts
                severity = alert["severity"]
                timestamp = time.strftime("%H:%M:%S", time.localtime(alert["timestamp"]))
                print(f"{severity} [{timestamp}] {alert['message']}")

        print("=" * 80)


# Global instance
_observability = None


def get_observability() -> TrafficLightObservability:
    """Get or create the global observability instance."""
    global _observability
    if _observability is None:
        config_file = os.getenv("OBSERVABILITY_CONFIG", "config/observability_thresholds.json")
        _observability = TrafficLightObservability(config_file)
    return _observability


def track_metric(name: str, value: float, metadata: Dict[str, Any] = None) -> MetricValue:
    """Convenience function for tracking a metric."""
    return get_observability().evaluate_metric(name, value, metadata)


if __name__ == "__main__":
    # Test the observability system
    obs = TrafficLightObservability()

    # Simulate some metrics
    obs.evaluate_metric("retrieval_snapshot_size", 25)
    obs.evaluate_metric("oracle_retrieval_hit_prefilter", 0.75)
    obs.evaluate_metric("max_embedding_token_count", 1100)
    obs.evaluate_metric("prefix_leakage", 0)
    obs.evaluate_metric("p95_latency_ms", 3000)

    # Print report
    obs.print_traffic_light_report()

    # Export dashboard
    obs.export_dashboard("metrics/traffic_light_dashboard.json")
