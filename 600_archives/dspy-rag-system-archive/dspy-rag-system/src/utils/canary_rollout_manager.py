#!/usr/bin/env python3
"""
Canary Rollout Manager - 48-Hour Production Rollout with Instant Rollback
Manages traffic routing, monitoring, and instant rollback capabilities
"""

import json
import logging
import time
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any

LOG = logging.getLogger(__name__)


class RolloutStage(Enum):
    """Canary rollout stages."""

    PREPARATION = "preparation"
    CANARY_10 = "canary_10"
    CANARY_50 = "canary_50"
    FULL_ROLLOUT = "full_rollout"
    ROLLBACK = "rollback"
    COMPLETED = "completed"


class RolloutStatus(Enum):
    """Rollout status."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class RolloutConfig:
    """Configuration for canary rollout."""

    config_hash: str
    ingest_run_id: str
    chunk_size: int
    overlap_ratio: float
    jaccard_threshold: float
    prefix_policy: str
    description: str
    created_at: float
    created_by: str


@dataclass
class RolloutMetrics:
    """Metrics for rollout monitoring."""

    oracle_prefilter: float
    reader_used_gold: float
    f1_score: float
    precision: float
    p95_latency_ms: float
    prefix_leakage: int
    budget_violations: int
    timestamp: float


@dataclass
class RolloutState:
    """Current rollout state."""

    stage: RolloutStage
    status: RolloutStatus
    traffic_percentage: float
    start_time: float
    last_check_time: float
    metrics_history: list[RolloutMetrics]
    alerts: list[dict[str, Any]]
    rollback_reason: str | None = None


class CanaryRolloutManager:
    """Manages 48-hour canary rollout with instant rollback."""

    def __init__(self, state_file: str = "metrics/canary_rollout_state.json"):
        self.state_file = Path(state_file)
        self.state: RolloutState | None = None
        self.config: RolloutConfig | None = None

        # Load existing state
        self._load_state()

        # Alert thresholds
        self.alert_thresholds = {
            "oracle_prefilter_drop": -5,  # points
            "reader_used_gold_drop": -3,  # points
            "f1_score_drop": -2,  # points
            "p95_latency_increase": 20,  # percent
            "prefix_leakage_max": 0,  # count
            "budget_violations_max": 0,  # count
        }

    def _load_state(self):
        """Load rollout state from file."""
        if self.state_file.exists():
            try:
                with open(self.state_file) as f:
                    data = json.load(f)
                    self.state = RolloutState(**data)
                    LOG.info(f"Loaded rollout state: {self.state.stage.value}")
            except Exception as e:
                LOG.error(f"Failed to load rollout state: {e}")
                self.state = None

    def _save_state(self):
        """Save rollout state to file."""
        if self.state:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, "w") as f:
                json.dump(asdict(self.state), f, indent=2)

    def start_rollout(self, config: RolloutConfig) -> dict[str, Any]:
        """Start a new canary rollout."""
        if self.state and self.state.status == RolloutStatus.IN_PROGRESS:
            return {"success": False, "error": "Rollout already in progress", "current_stage": self.state.stage.value}

        # Initialize rollout state
        self.state = RolloutState(
            stage=RolloutStage.PREPARATION,
            status=RolloutStatus.IN_PROGRESS,
            traffic_percentage=0.0,
            start_time=time.time(),
            last_check_time=time.time(),
            metrics_history=[],
            alerts=[],
        )

        self.config = config

        # Save state
        self._save_state()

        LOG.info(f"Started canary rollout for config: {config.config_hash}")

        return {
            "success": True,
            "rollout_id": config.config_hash,
            "stage": self.state.stage.value,
            "start_time": self.state.start_time,
        }

    def advance_stage(self) -> dict[str, Any]:
        """Advance to the next rollout stage."""
        if not self.state or self.state.status != RolloutStatus.IN_PROGRESS:
            return {"success": False, "error": "No active rollout to advance"}

        # Check if current stage is healthy before advancing
        if not self._is_stage_healthy():
            return {
                "success": False,
                "error": "Current stage is not healthy - cannot advance",
                "alerts": self.state.alerts[-5:],  # Last 5 alerts
            }

        # Advance stage
        stage_advancement = {
            RolloutStage.PREPARATION: RolloutStage.CANARY_10,
            RolloutStage.CANARY_10: RolloutStage.CANARY_50,
            RolloutStage.CANARY_50: RolloutStage.FULL_ROLLOUT,
            RolloutStage.FULL_ROLLOUT: RolloutStage.COMPLETED,
        }

        if self.state.stage in stage_advancement:
            old_stage = self.state.stage
            self.state.stage = stage_advancement[self.state.stage]
            self.state.traffic_percentage = self._get_traffic_percentage()
            self.state.last_check_time = time.time()

            # Save state
            self._save_state()

            LOG.info(f"Advanced rollout from {old_stage.value} to {self.state.stage.value}")

            return {
                "success": True,
                "old_stage": old_stage.value,
                "new_stage": self.state.stage.value,
                "traffic_percentage": self.state.traffic_percentage,
            }
        else:
            return {"success": False, "error": f"Cannot advance from stage: {self.state.stage.value}"}

    def _get_traffic_percentage(self) -> float:
        """Get traffic percentage for current stage."""
        traffic_map = {
            RolloutStage.PREPARATION: 0.0,
            RolloutStage.CANARY_10: 10.0,
            RolloutStage.CANARY_50: 50.0,
            RolloutStage.FULL_ROLLOUT: 100.0,
            RolloutStage.COMPLETED: 100.0,
        }
        return traffic_map.get(self.state.stage, 0.0)

    def rollback(self, reason: str) -> dict[str, Any]:
        """Instant rollback to previous configuration."""
        if not self.state:
            return {"success": False, "error": "No active rollout to rollback"}

        # Set rollback state
        self.state.stage = RolloutStage.ROLLBACK
        self.state.status = RolloutStatus.ROLLED_BACK
        self.state.rollback_reason = reason
        self.state.traffic_percentage = 0.0
        self.state.last_check_time = time.time()

        # Save state
        self._save_state()

        # Execute rollback (this would integrate with your actual rollback mechanism)
        rollback_success = self._execute_rollback()

        if rollback_success:
            LOG.warning(f"Rollout rolled back: {reason}")
            return {
                "success": True,
                "stage": self.state.stage.value,
                "reason": reason,
                "rollback_time": self.state.last_check_time,
            }
        else:
            return {"success": False, "error": "Rollback execution failed"}

    def _execute_rollback(self) -> bool:
        """Execute the actual rollback."""
        try:
            # This would integrate with your actual rollback mechanism
            # For now, we'll simulate the rollback

            # 1. Clear active configuration
            # 2. Revert to previous configuration
            # 3. Clear caches
            # 4. Verify rollback success

            LOG.info("Executing rollback...")

            # Simulate rollback steps
            time.sleep(1)  # Simulate rollback time

            return True

        except Exception as e:
            LOG.error(f"Rollback execution failed: {e}")
            return False

    def update_metrics(self, metrics: RolloutMetrics) -> dict[str, Any]:
        """Update rollout metrics and check for alerts."""
        if not self.state:
            return {"success": False, "error": "No active rollout"}

        # Add metrics to history
        self.state.metrics_history.append(metrics)
        self.state.last_check_time = time.time()

        # Check for alerts
        alerts = self._check_metrics_alerts(metrics)
        self.state.alerts.extend(alerts)

        # Save state
        self._save_state()

        return {
            "success": True,
            "metrics_added": 1,
            "alerts_triggered": len(alerts),
            "total_alerts": len(self.state.alerts),
        }

    def _check_metrics_alerts(self, metrics: RolloutMetrics) -> list[dict[str, Any]]:
        """Check metrics against alert thresholds."""
        alerts = []

        # Get baseline metrics (from previous successful stage or initial)
        baseline = self._get_baseline_metrics()

        if baseline:
            # Check oracle prefilter drop
            if metrics.oracle_prefilter < baseline.oracle_prefilter + self.alert_thresholds["oracle_prefilter_drop"]:
                alerts.append(
                    {
                        "timestamp": metrics.timestamp,
                        "metric": "oracle_prefilter",
                        "current": metrics.oracle_prefilter,
                        "baseline": baseline.oracle_prefilter,
                        "threshold": self.alert_thresholds["oracle_prefilter_drop"],
                        "severity": "CRITICAL",
                        "message": f"Oracle prefilter dropped by {baseline.oracle_prefilter - metrics.oracle_prefilter:.1f} points",
                    }
                )

            # Check reader used gold drop
            if metrics.reader_used_gold < baseline.reader_used_gold + self.alert_thresholds["reader_used_gold_drop"]:
                alerts.append(
                    {
                        "timestamp": metrics.timestamp,
                        "metric": "reader_used_gold",
                        "current": metrics.reader_used_gold,
                        "baseline": baseline.reader_used_gold,
                        "threshold": self.alert_thresholds["reader_used_gold_drop"],
                        "severity": "CRITICAL",
                        "message": f"Reader used gold dropped by {baseline.reader_used_gold - metrics.reader_used_gold:.1f} points",
                    }
                )

            # Check F1 score drop
            if metrics.f1_score < baseline.f1_score + self.alert_thresholds["f1_score_drop"]:
                alerts.append(
                    {
                        "timestamp": metrics.timestamp,
                        "metric": "f1_score",
                        "current": metrics.f1_score,
                        "baseline": baseline.f1_score,
                        "threshold": self.alert_thresholds["f1_score_drop"],
                        "severity": "CRITICAL",
                        "message": f"F1 score dropped by {baseline.f1_score - metrics.f1_score:.1f} points",
                    }
                )

            # Check latency increase
            latency_increase = ((metrics.p95_latency_ms - baseline.p95_latency_ms) / baseline.p95_latency_ms) * 100
            if latency_increase > self.alert_thresholds["p95_latency_increase"]:
                alerts.append(
                    {
                        "timestamp": metrics.timestamp,
                        "metric": "p95_latency",
                        "current": metrics.p95_latency_ms,
                        "baseline": baseline.p95_latency_ms,
                        "increase_percent": latency_increase,
                        "threshold": self.alert_thresholds["p95_latency_increase"],
                        "severity": "WARNING",
                        "message": f"P95 latency increased by {latency_increase:.1f}%",
                    }
                )

        # Check absolute thresholds
        if metrics.prefix_leakage > self.alert_thresholds["prefix_leakage_max"]:
            alerts.append(
                {
                    "timestamp": metrics.timestamp,
                    "metric": "prefix_leakage",
                    "current": metrics.prefix_leakage,
                    "threshold": self.alert_thresholds["prefix_leakage_max"],
                    "severity": "CRITICAL",
                    "message": f"Prefix leakage detected: {metrics.prefix_leakage} chunks",
                }
            )

        if metrics.budget_violations > self.alert_thresholds["budget_violations_max"]:
            alerts.append(
                {
                    "timestamp": metrics.timestamp,
                    "metric": "budget_violations",
                    "current": metrics.budget_violations,
                    "threshold": self.alert_thresholds["budget_violations_max"],
                    "severity": "CRITICAL",
                    "message": f"Budget violations detected: {metrics.budget_violations} chunks",
                }
            )

        return alerts

    def _get_baseline_metrics(self) -> RolloutMetrics | None:
        """Get baseline metrics for comparison."""
        if len(self.state.metrics_history) < 2:
            return None

        # Use metrics from the beginning of current stage
        # This is a simplified approach - in practice, you'd want more sophisticated baseline selection
        return self.state.metrics_history[0]

    def _is_stage_healthy(self) -> bool:
        """Check if current stage is healthy enough to advance."""
        if not self.state or not self.state.metrics_history:
            return True  # No metrics yet, assume healthy

        # Get recent metrics (last 3 measurements)
        self.state.metrics_history[-3:]

        # Check for critical alerts in recent metrics
        recent_alerts = [alert for alert in self.state.alerts[-10:] if alert["severity"] == "CRITICAL"]

        # If there are critical alerts, stage is not healthy
        if recent_alerts:
            return False

        # Additional health checks could be added here
        return True

    def get_rollout_status(self) -> dict[str, Any]:
        """Get current rollout status."""
        if not self.state:
            return {"active": False, "message": "No active rollout"}

        return {
            "active": self.state.status == RolloutStatus.IN_PROGRESS,
            "stage": self.state.stage.value,
            "status": self.state.status.value,
            "traffic_percentage": self.state.traffic_percentage,
            "start_time": self.state.start_time,
            "last_check_time": self.state.last_check_time,
            "metrics_count": len(self.state.metrics_history),
            "alerts_count": len(self.state.alerts),
            "critical_alerts": len([a for a in self.state.alerts if a["severity"] == "CRITICAL"]),
            "rollback_reason": self.state.rollback_reason,
            "config": asdict(self.config) if self.config else None,
        }

    def get_rollout_report(self) -> dict[str, Any]:
        """Generate comprehensive rollout report."""
        if not self.state:
            return {"error": "No active rollout"}

        # Calculate stage duration
        stage_duration = time.time() - self.state.start_time

        # Get recent metrics
        recent_metrics = self.state.metrics_history[-5:] if self.state.metrics_history else []

        # Get recent alerts
        recent_alerts = self.state.alerts[-10:] if self.state.alerts else []

        return {
            "rollout_id": self.config.config_hash if self.config else "unknown",
            "stage": self.state.stage.value,
            "status": self.state.status.value,
            "traffic_percentage": self.state.traffic_percentage,
            "stage_duration_hours": stage_duration / 3600,
            "total_metrics": len(self.state.metrics_history),
            "total_alerts": len(self.state.alerts),
            "critical_alerts": len([a for a in self.state.alerts if a["severity"] == "CRITICAL"]),
            "recent_metrics": [asdict(m) for m in recent_metrics],
            "recent_alerts": recent_alerts,
            "health_status": "healthy" if self._is_stage_healthy() else "unhealthy",
            "rollback_reason": self.state.rollback_reason,
            "config": asdict(self.config) if self.config else None,
        }


# Global instance
_rollout_manager = None


def get_rollout_manager() -> CanaryRolloutManager:
    """Get or create the global rollout manager instance."""
    global _rollout_manager
    if _rollout_manager is None:
        _rollout_manager = CanaryRolloutManager()
    return _rollout_manager


if __name__ == "__main__":
    # Test the rollout manager
    manager = CanaryRolloutManager()

    # Create test config
    config = RolloutConfig(
        config_hash="deb4bee72d017024",
        ingest_run_id="2025-09-07T21-45-00-dedup07",
        chunk_size=450,
        overlap_ratio=0.1,
        jaccard_threshold=0.8,
        prefix_policy="A",
        description="Production chunking configuration",
        created_at=time.time(),
        created_by="system",
    )

    # Start rollout
    result = manager.start_rollout(config)
    print("Start rollout:", result)

    # Get status
    status = manager.get_rollout_status()
    print("Rollout status:", json.dumps(status, indent=2))

    # Generate report
    report = manager.get_rollout_report()
    print("Rollout report:", json.dumps(report, indent=2))
