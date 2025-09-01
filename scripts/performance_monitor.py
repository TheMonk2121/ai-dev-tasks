#!/usr/bin/env python3
"""
Automated Performance Monitoring System for Memory Context System
Implements monitoring, alerts, dashboards, and historical data collection
"""

import json
import logging
import queue
import sqlite3
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    """Performance metric types"""

    F1_SCORE = "f1_score"
    LATENCY = "latency"
    TOKEN_USAGE = "token_usage"
    MEMORY_USAGE = "memory_usage"
    CONTEXT_UTILIZATION = "context_utilization"
    ADAPTATION_SUCCESS_RATE = "adaptation_success_rate"
    OVERFLOW_FREQUENCY = "overflow_frequency"


@dataclass
class PerformanceMetric:
    """Individual performance metric"""

    timestamp: float
    metric_type: MetricType
    value: float
    model: str
    context_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Alert:
    """Performance alert"""

    timestamp: float
    level: AlertLevel
    message: str
    metric_type: MetricType
    current_value: float
    threshold: float
    model: str
    context_size: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time"""

    timestamp: float
    model: str
    context_size: int
    f1_score: float
    latency: float
    token_usage: int
    memory_usage: float
    context_utilization: float
    adaptation_success_rate: float
    overflow_frequency: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MonitoringConfig:
    """Configuration for performance monitoring"""

    # Database settings
    db_path: str = "performance_monitor.db"

    # Alert thresholds
    f1_score_warning: float = 0.80
    f1_score_error: float = 0.75
    f1_score_critical: float = 0.70

    latency_warning: float = 5.0
    latency_error: float = 10.0
    latency_critical: float = 20.0

    token_usage_warning: int = 15000
    token_usage_error: int = 20000
    token_usage_critical: int = 25000

    # Monitoring intervals
    snapshot_interval: int = 60  # seconds
    alert_check_interval: int = 30  # seconds
    data_retention_days: int = 30

    # Dashboard settings
    dashboard_refresh_interval: int = 10  # seconds
    max_data_points: int = 1000

    # Integration settings
    enable_benchmark_integration: bool = True
    enable_overflow_integration: bool = True
    enable_adaptation_integration: bool = True


class PerformanceDatabase:
    """SQLite database for performance metrics and alerts"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        if self.db_path == ":memory:":
            # For in-memory database, maintain a single connection
            self.connection = sqlite3.connect(self.db_path)
        else:
            # For file-based database, create new connections as needed
            self.connection = None

        self._create_tables()

    def _create_tables(self):
        """Create database tables"""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Performance metrics table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                metric_type TEXT NOT NULL,
                value REAL NOT NULL,
                model TEXT NOT NULL,
                context_size INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Alerts table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_type TEXT NOT NULL,
                current_value REAL NOT NULL,
                threshold REAL NOT NULL,
                model TEXT NOT NULL,
                context_size INTEGER NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Performance snapshots table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS performance_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                model TEXT NOT NULL,
                context_size INTEGER NOT NULL,
                f1_score REAL NOT NULL,
                latency REAL NOT NULL,
                token_usage INTEGER NOT NULL,
                memory_usage REAL NOT NULL,
                context_utilization REAL NOT NULL,
                adaptation_success_rate REAL NOT NULL,
                overflow_frequency REAL NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_type ON performance_metrics(metric_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_metrics_model ON performance_metrics(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_timestamp ON performance_snapshots(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_model ON performance_snapshots(model)")

        conn.commit()

    def _get_connection(self):
        """Get database connection"""
        if self.db_path == ":memory:" and self.connection:
            return self.connection
        else:
            return sqlite3.connect(self.db_path)

    def store_metric(self, metric: PerformanceMetric):
        """Store a performance metric"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO performance_metrics
            (timestamp, metric_type, value, model, context_size, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                metric.timestamp,
                metric.metric_type.value,
                metric.value,
                metric.model,
                metric.context_size,
                json.dumps(metric.metadata),
            ),
        )
        conn.commit()

    def store_alert(self, alert: Alert):
        """Store an alert"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO alerts
            (timestamp, level, message, metric_type, current_value, threshold, model, context_size, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                alert.timestamp,
                alert.level.value,
                alert.message,
                alert.metric_type.value,
                alert.current_value,
                alert.threshold,
                alert.model,
                alert.context_size,
                json.dumps(alert.metadata),
            ),
        )
        conn.commit()

    def store_snapshot(self, snapshot: PerformanceSnapshot):
        """Store a performance snapshot"""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO performance_snapshots
            (timestamp, model, context_size, f1_score, latency, token_usage, memory_usage,
             context_utilization, adaptation_success_rate, overflow_frequency, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                snapshot.timestamp,
                snapshot.model,
                snapshot.context_size,
                snapshot.f1_score,
                snapshot.latency,
                snapshot.token_usage,
                snapshot.memory_usage,
                snapshot.context_utilization,
                snapshot.adaptation_success_rate,
                snapshot.overflow_frequency,
                json.dumps(snapshot.metadata),
            ),
        )
        conn.commit()

    def get_recent_metrics(self, metric_type: MetricType, hours: int = 24) -> List[PerformanceMetric]:
        """Get recent metrics of a specific type"""
        cutoff_time = time.time() - (hours * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT timestamp, metric_type, value, model, context_size, metadata
            FROM performance_metrics
            WHERE metric_type = ? AND timestamp > ?
            ORDER BY timestamp DESC
        """,
            (metric_type.value, cutoff_time),
        )

        metrics = []
        for row in cursor.fetchall():
            metadata = json.loads(row[5]) if row[5] else {}
            metric = PerformanceMetric(
                timestamp=row[0],
                metric_type=MetricType(row[1]),
                value=row[2],
                model=row[3],
                context_size=row[4],
                metadata=metadata,
            )
            metrics.append(metric)

        return metrics

    def get_recent_alerts(self, level: Optional[AlertLevel] = None, hours: int = 24) -> List[Alert]:
        """Get recent alerts, optionally filtered by level"""
        cutoff_time = time.time() - (hours * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        if level:
            cursor.execute(
                """
                SELECT timestamp, level, message, metric_type, current_value, threshold, model, context_size, metadata
                FROM alerts
                WHERE level = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """,
                (level.value, cutoff_time),
            )
        else:
            cursor.execute(
                """
                SELECT timestamp, level, message, metric_type, current_value, threshold, model, context_size, metadata
                FROM alerts
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """,
                (cutoff_time,),
            )

        alerts = []
        for row in cursor.fetchall():
            metadata = json.loads(row[8]) if row[8] else {}
            alert = Alert(
                timestamp=row[0],
                level=AlertLevel(row[1]),
                message=row[2],
                metric_type=MetricType(row[3]),
                current_value=row[4],
                threshold=row[5],
                model=row[6],
                context_size=row[7],
                metadata=metadata,
            )
            alerts.append(alert)

        return alerts

    def get_recent_snapshots(self, model: Optional[str] = None, hours: int = 24) -> List[PerformanceSnapshot]:
        """Get recent performance snapshots, optionally filtered by model"""
        cutoff_time = time.time() - (hours * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        if model:
            cursor.execute(
                """
                SELECT timestamp, model, context_size, f1_score, latency, token_usage, memory_usage,
                       context_utilization, adaptation_success_rate, overflow_frequency, metadata
                FROM performance_snapshots
                WHERE model = ? AND timestamp > ?
                ORDER BY timestamp DESC
            """,
                (model, cutoff_time),
            )
        else:
            cursor.execute(
                """
                SELECT timestamp, model, context_size, f1_score, latency, token_usage, memory_usage,
                       context_utilization, adaptation_success_rate, overflow_frequency, metadata
                FROM performance_snapshots
                WHERE timestamp > ?
                ORDER BY timestamp DESC
            """,
                (cutoff_time,),
            )

        snapshots = []
        for row in cursor.fetchall():
            metadata = json.loads(row[10]) if row[10] else {}
            snapshot = PerformanceSnapshot(
                timestamp=row[0],
                model=row[1],
                context_size=row[2],
                f1_score=row[3],
                latency=row[4],
                token_usage=row[5],
                memory_usage=row[6],
                context_utilization=row[7],
                adaptation_success_rate=row[8],
                overflow_frequency=row[9],
                metadata=metadata,
            )
            snapshots.append(snapshot)

        return snapshots

    def cleanup_old_data(self, days: int):
        """Clean up data older than specified days"""
        cutoff_time = time.time() - (days * 24 * 3600)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Clean up old metrics
        cursor.execute("DELETE FROM performance_metrics WHERE timestamp < ?", (cutoff_time,))
        metrics_deleted = cursor.rowcount

        # Clean up old alerts
        cursor.execute("DELETE FROM alerts WHERE timestamp < ?", (cutoff_time,))
        alerts_deleted = cursor.rowcount

        # Clean up old snapshots
        cursor.execute("DELETE FROM performance_snapshots WHERE timestamp < ?", (cutoff_time,))
        snapshots_deleted = cursor.rowcount

        conn.commit()

        logger.info(
            f"Cleaned up old data: {metrics_deleted} metrics, {alerts_deleted} alerts, {snapshots_deleted} snapshots"
        )


class AlertManager:
    """Manages performance alerts and thresholds"""

    def __init__(self, config: MonitoringConfig, database: PerformanceDatabase):
        self.config = config
        self.database = database
        self.alert_queue = queue.Queue()
        self.alert_handlers = []

        # Start alert processing thread
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()

    def add_alert_handler(self, handler):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)

    def check_metrics(self, metrics: List[PerformanceMetric]) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []

        for metric in metrics:
            if metric.metric_type == MetricType.F1_SCORE:
                alert = self._check_f1_score(metric)
                if alert:
                    alerts.append(alert)

            elif metric.metric_type == MetricType.LATENCY:
                alert = self._check_latency(metric)
                if alert:
                    alerts.append(alert)

            elif metric.metric_type == MetricType.TOKEN_USAGE:
                alert = self._check_token_usage(metric)
                if alert:
                    alerts.append(alert)

        # Store alerts in database
        for alert in alerts:
            self.database.store_alert(alert)
            self.alert_queue.put(alert)

        return alerts

    def _check_f1_score(self, metric: PerformanceMetric) -> Optional[Alert]:
        """Check F1 score against thresholds"""
        if metric.value <= self.config.f1_score_critical:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.CRITICAL,
                message=f"Critical F1 score degradation: {metric.value:.3f}",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.f1_score_critical,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value <= self.config.f1_score_error:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.ERROR,
                message=f"Error F1 score degradation: {metric.value:.3f}",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.f1_score_error,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value <= self.config.f1_score_warning:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.WARNING,
                message=f"Warning F1 score degradation: {metric.value:.3f}",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.f1_score_warning,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )

        return None

    def _check_latency(self, metric: PerformanceMetric) -> Optional[Alert]:
        """Check latency against thresholds"""
        if metric.value >= self.config.latency_critical:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.CRITICAL,
                message=f"Critical latency increase: {metric.value:.3f}s",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.latency_critical,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value >= self.config.latency_error:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.ERROR,
                message=f"Error latency increase: {metric.value:.3f}s",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.latency_error,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value >= self.config.latency_warning:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.WARNING,
                message=f"Warning latency increase: {metric.value:.3f}s",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.latency_warning,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )

        return None

    def _check_token_usage(self, metric: PerformanceMetric) -> Optional[Alert]:
        """Check token usage against thresholds"""
        if metric.value >= self.config.token_usage_critical:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.CRITICAL,
                message=f"Critical token usage: {metric.value:,} tokens",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.token_usage_critical,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value >= self.config.token_usage_error:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.ERROR,
                message=f"Error token usage: {metric.value:,} tokens",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.token_usage_error,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )
        elif metric.value >= self.config.token_usage_warning:
            return Alert(
                timestamp=metric.timestamp,
                level=AlertLevel.WARNING,
                message=f"Warning token usage: {metric.value:,} tokens",
                metric_type=metric.metric_type,
                current_value=metric.value,
                threshold=self.config.token_usage_warning,
                model=metric.model,
                context_size=metric.context_size,
                metadata=metric.metadata,
            )

        return None

    def _process_alerts(self):
        """Process alerts from the queue"""
        while True:
            try:
                alert = self.alert_queue.get(timeout=1)
                self._handle_alert(alert)
                self.alert_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing alert: {e}")

    def _handle_alert(self, alert: Alert):
        """Handle an individual alert"""
        logger.warning(f"ALERT [{alert.level.value.upper()}] {alert.message}")

        # Call all registered alert handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"Error in alert handler: {e}")


class PerformanceDashboard:
    """Performance metrics dashboard"""

    def __init__(self, database: PerformanceDatabase, config: MonitoringConfig):
        self.database = database
        self.config = config

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get comprehensive dashboard data"""
        current_time = time.time()

        # Get recent snapshots
        recent_snapshots = self.database.get_recent_snapshots(hours=24)

        # Get recent alerts
        recent_alerts = self.database.get_recent_alerts(hours=24)

        # Calculate summary statistics
        summary = self._calculate_summary_stats(recent_snapshots)

        # Calculate trends
        trends = self._calculate_trends(recent_snapshots)

        # Get model-specific performance
        model_performance = self._get_model_performance(recent_snapshots)

        # Get alert summary
        alert_summary = self._get_alert_summary(recent_alerts)

        return {
            "timestamp": current_time,
            "summary": summary,
            "trends": trends,
            "model_performance": model_performance,
            "alert_summary": alert_summary,
            "recent_alerts": [asdict(alert) for alert in recent_alerts[:10]],
            "recent_snapshots": [asdict(snapshot) for snapshot in recent_snapshots[:20]],
        }

    def _calculate_summary_stats(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate summary statistics from snapshots"""
        if not snapshots:
            return {}

        f1_scores = [s.f1_score for s in snapshots]
        latencies = [s.latency for s in snapshots]
        token_usages = [s.token_usage for s in snapshots]

        return {
            "total_snapshots": len(snapshots),
            "avg_f1_score": sum(f1_scores) / len(f1_scores),
            "min_f1_score": min(f1_scores),
            "max_f1_score": max(f1_scores),
            "avg_latency": sum(latencies) / len(latencies),
            "min_latency": min(latencies),
            "max_latency": max(latencies),
            "avg_token_usage": sum(token_usages) / len(token_usages),
            "min_token_usage": min(token_usages),
            "max_token_usage": max(token_usages),
        }

    def _calculate_trends(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(snapshots) < 2:
            return {}

        # Sort by timestamp
        sorted_snapshots = sorted(snapshots, key=lambda x: x.timestamp)

        # Calculate trends over last 6 hours
        recent_cutoff = time.time() - (6 * 3600)
        recent_snapshots = [s for s in sorted_snapshots if s.timestamp >= recent_cutoff]

        if len(recent_snapshots) < 2:
            return {}

        # Calculate F1 score trend
        recent_f1 = [s.f1_score for s in recent_snapshots]
        f1_trend = (recent_f1[-1] - recent_f1[0]) / len(recent_f1)

        # Calculate latency trend
        recent_latency = [s.latency for s in recent_snapshots]
        latency_trend = (recent_latency[-1] - recent_latency[0]) / len(recent_latency)

        return {
            "f1_score_trend": f1_trend,
            "latency_trend": latency_trend,
            "f1_score_direction": "improving" if f1_trend > 0 else "degrading",
            "latency_direction": "improving" if latency_trend < 0 else "degrading",
        }

    def _get_model_performance(self, snapshots: List[PerformanceSnapshot]) -> Dict[str, Any]:
        """Get performance breakdown by model"""
        model_stats = {}

        for snapshot in snapshots:
            if snapshot.model not in model_stats:
                model_stats[snapshot.model] = {"count": 0, "f1_scores": [], "latencies": [], "token_usages": []}

            model_stats[snapshot.model]["count"] += 1
            model_stats[snapshot.model]["f1_scores"].append(snapshot.f1_score)
            model_stats[snapshot.model]["latencies"].append(snapshot.latency)
            model_stats[snapshot.model]["token_usages"].append(snapshot.token_usage)

        # Calculate averages for each model
        for model, stats in model_stats.items():
            if stats["f1_scores"]:
                stats["avg_f1_score"] = sum(stats["f1_scores"]) / len(stats["f1_scores"])
                stats["avg_latency"] = sum(stats["latencies"]) / len(stats["latencies"])
                stats["avg_token_usage"] = sum(stats["token_usages"]) / len(stats["token_usages"])

                # Remove raw data to keep response clean
                del stats["f1_scores"]
                del stats["latencies"]
                del stats["token_usages"]

        return model_stats

    def _get_alert_summary(self, alerts: List[Alert]) -> Dict[str, Any]:
        """Get summary of recent alerts"""
        alert_counts = {level.value: 0 for level in AlertLevel}

        for alert in alerts:
            alert_counts[alert.level.value] += 1

        return {
            "total_alerts": len(alerts),
            "alert_counts": alert_counts,
            "has_critical": alert_counts["critical"] > 0,
            "has_error": alert_counts["error"] > 0,
            "has_warning": alert_counts["warning"] > 0,
        }

    def generate_dashboard_report(self) -> str:
        """Generate a text-based dashboard report"""
        data = self.get_dashboard_data()

        report = []
        report.append("=" * 80)
        report.append("🚀 PERFORMANCE MONITORING DASHBOARD")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.fromtimestamp(data['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Summary section
        if data["summary"]:
            report.append("📊 PERFORMANCE SUMMARY")
            report.append("-" * 40)
            summary = data["summary"]
            report.append(f"Total Snapshots: {summary['total_snapshots']}")
            report.append(
                f"F1 Score: {summary['avg_f1_score']:.3f} (min: {summary['min_f1_score']:.3f}, max: {summary['max_f1_score']:.3f})"
            )
            report.append(
                f"Latency: {summary['avg_latency']:.3f}s (min: {summary['min_latency']:.3f}s, max: {summary['max_latency']:.3f}s)"
            )
            report.append(
                f"Token Usage: {summary['avg_token_usage']:,} (min: {summary['min_token_usage']:,}, max: {summary['max_token_usage']:,})"
            )
            report.append("")

        # Trends section
        if data["trends"]:
            report.append("📈 PERFORMANCE TRENDS")
            report.append("-" * 40)
            trends = data["trends"]
            report.append(f"F1 Score: {trends['f1_score_direction']} (trend: {trends['f1_score_trend']:+.4f})")
            report.append(f"Latency: {trends['latency_direction']} (trend: {trends['latency_trend']:+.4f})")
            report.append("")

        # Model performance section
        if data["model_performance"]:
            report.append("🤖 MODEL PERFORMANCE")
            report.append("-" * 40)
            for model, stats in data["model_performance"].items():
                report.append(f"{model}:")
                report.append(f"  Snapshots: {stats['count']}")
                report.append(f"  Avg F1: {stats['avg_f1_score']:.3f}")
                report.append(f"  Avg Latency: {stats['avg_latency']:.3f}s")
                report.append(f"  Avg Tokens: {stats['avg_token_usage']:,}")
                report.append("")

        # Alert summary section
        if data["alert_summary"]:
            report.append("🚨 ALERT SUMMARY")
            report.append("-" * 40)
            alert_summary = data["alert_summary"]
            report.append(f"Total Alerts: {alert_summary['total_alerts']}")
            for level, count in alert_summary["alert_counts"].items():
                if count > 0:
                    report.append(f"{level.title()}: {count}")

            if alert_summary["has_critical"]:
                report.append("⚠️  CRITICAL ALERTS DETECTED!")
            elif alert_summary["has_error"]:
                report.append("⚠️  ERROR ALERTS DETECTED!")
            elif alert_summary["has_warning"]:
                report.append("⚠️  WARNING ALERTS DETECTED!")
            report.append("")

        # Recent alerts section
        if data["recent_alerts"]:
            report.append("🔔 RECENT ALERTS")
            report.append("-" * 40)
            for alert in data["recent_alerts"][:5]:  # Show last 5 alerts
                timestamp = datetime.fromtimestamp(alert["timestamp"]).strftime("%H:%M:%S")
                level_str = alert["level"].value if hasattr(alert["level"], "value") else str(alert["level"])
                report.append(f"[{timestamp}] {level_str.upper()}: {alert['message']}")
                report.append(f"  Model: {alert['model']}, Context: {alert['context_size']:,} tokens")
            report.append("")

        report.append("=" * 80)

        return "\n".join(report)


class PerformanceMonitor:
    """Main performance monitoring system"""

    def __init__(self, config: Optional[MonitoringConfig] = None):
        self.config = config or MonitoringConfig()
        self.database = PerformanceDatabase(self.config.db_path)
        self.alert_manager = AlertManager(self.config, self.database)
        self.dashboard = PerformanceDashboard(self.database, self.config)

        # Performance data collection
        self.metrics_buffer: List[PerformanceMetric] = []
        self.snapshots_buffer: List[PerformanceSnapshot] = []

        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None

        # Add default alert handler
        self.alert_manager.add_alert_handler(self._default_alert_handler)

        logger.info("Performance monitoring system initialized")

    def start_monitoring(self):
        """Start continuous performance monitoring"""
        if self.is_monitoring:
            logger.warning("Monitoring already started")
            return

        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop continuous performance monitoring"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")

    def add_metric(self, metric: PerformanceMetric):
        """Add a performance metric"""
        self.metrics_buffer.append(metric)
        self.database.store_metric(metric)

        # Check for alerts
        self.alert_manager.check_metrics([metric])

    def add_snapshot(self, snapshot: PerformanceSnapshot):
        """Add a performance snapshot"""
        self.snapshots_buffer.append(snapshot)
        self.database.store_snapshot(snapshot)

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        return self.dashboard.get_dashboard_data()

    def generate_report(self) -> str:
        """Generate dashboard report"""
        return self.dashboard.generate_dashboard_report()

    def get_recent_alerts(self, level: Optional[AlertLevel] = None, hours: int = 24) -> List[Alert]:
        """Get recent alerts"""
        return self.database.get_recent_alerts(level, hours)

    def get_recent_metrics(self, metric_type: MetricType, hours: int = 24) -> List[PerformanceMetric]:
        """Get recent metrics"""
        return self.database.get_recent_metrics(metric_type, hours)

    def cleanup_old_data(self):
        """Clean up old performance data"""
        self.database.cleanup_old_data(self.config.data_retention_days)

    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_snapshot_time = time.time()
        last_cleanup_time = time.time()

        while self.is_monitoring:
            current_time = time.time()

            # Take periodic snapshots
            if current_time - last_snapshot_time >= self.config.snapshot_interval:
                self._take_performance_snapshot()
                last_snapshot_time = current_time

            # Clean up old data periodically
            if current_time - last_cleanup_time >= 3600:  # Every hour
                self.cleanup_old_data()
                last_cleanup_time = current_time

            time.sleep(1)

    def _take_performance_snapshot(self):
        """Take a performance snapshot"""
        # This would typically collect current system metrics
        # For now, we'll create a synthetic snapshot based on recent metrics

        recent_metrics = self.database.get_recent_metrics(MetricType.F1_SCORE, hours=1)
        if not recent_metrics:
            return

        # Calculate averages from recent metrics
        f1_scores = [m.value for m in recent_metrics if m.metric_type == MetricType.F1_SCORE]
        latencies = [m.value for m in recent_metrics if m.metric_type == MetricType.LATENCY]
        token_usages = [m.value for m in recent_metrics if m.metric_type == MetricType.TOKEN_USAGE]

        if not f1_scores:
            return

        # Get most recent model and context size
        latest_metric = recent_metrics[0]

        snapshot = PerformanceSnapshot(
            timestamp=time.time(),
            model=latest_metric.model,
            context_size=latest_metric.context_size,
            f1_score=sum(f1_scores) / len(f1_scores),
            latency=sum(latencies) / len(latencies) if latencies else 0.0,
            token_usage=int(sum(token_usages) / len(token_usages)) if token_usages else 0,
            memory_usage=0.0,  # Would be collected from system
            context_utilization=0.0,  # Would be calculated
            adaptation_success_rate=0.0,  # Would be calculated
            overflow_frequency=0.0,  # Would be calculated
            metadata={"source": "synthetic_snapshot"},
        )

        self.add_snapshot(snapshot)

    def _default_alert_handler(self, alert: Alert):
        """Default alert handler - logs alerts"""
        level_emoji = {AlertLevel.INFO: "ℹ️", AlertLevel.WARNING: "⚠️", AlertLevel.ERROR: "❌", AlertLevel.CRITICAL: "🚨"}

        emoji = level_emoji.get(alert.level, "❓")
        timestamp = datetime.fromtimestamp(alert.timestamp).strftime("%H:%M:%S")

        print(f"{emoji} [{timestamp}] {alert.level.value.upper()}: {alert.message}")
        print(f"   Model: {alert.model}, Context: {alert.context_size:,} tokens")
        print(f"   Current: {alert.current_value:.3f}, Threshold: {alert.threshold:.3f}")


def test_performance_monitor():
    """Test the performance monitoring system"""
    print("🧪 Testing Performance Monitoring System...")

    # Create configuration
    config = MonitoringConfig(
        db_path=":memory:",  # Use in-memory database for testing
        f1_score_warning=0.80,
        f1_score_error=0.75,
        f1_score_critical=0.70,
        latency_warning=5.0,
        latency_error=10.0,
        latency_critical=20.0,
        token_usage_warning=15000,
        token_usage_error=20000,
        token_usage_critical=25000,
        snapshot_interval=5,  # Short interval for testing
        alert_check_interval=5,
    )

    # Initialize monitoring system
    monitor = PerformanceMonitor(config)

    print("✅ Performance monitoring system initialized")

    # Test metric collection
    print("\n📊 Testing metric collection...")

    test_metrics = [
        PerformanceMetric(
            timestamp=time.time(),
            metric_type=MetricType.F1_SCORE,
            value=0.85,
            model="mistral-7b",
            context_size=4000,
            metadata={"test": True},
        ),
        PerformanceMetric(
            timestamp=time.time(),
            metric_type=MetricType.F1_SCORE,
            value=0.70,  # Should trigger critical alert
            model="mistral-7b",
            context_size=8000,
            metadata={"test": True},
        ),
        PerformanceMetric(
            timestamp=time.time(),
            metric_type=MetricType.LATENCY,
            value=15.0,  # Should trigger error alert
            model="mixtral-8x7b",
            context_size=16000,
            metadata={"test": True},
        ),
        PerformanceMetric(
            timestamp=time.time(),
            metric_type=MetricType.TOKEN_USAGE,
            value=22000,  # Should trigger error alert
            model="gpt-4o",
            context_size=32000,
            metadata={"test": True},
        ),
    ]

    # Add metrics
    for metric in test_metrics:
        monitor.add_metric(metric)
        print(f"  Added metric: {metric.metric_type.value} = {metric.value}")

    # Wait for processing
    time.sleep(2)

    # Test dashboard
    print("\n📈 Testing dashboard...")
    dashboard_data = monitor.get_dashboard_data()
    print(f"  Dashboard data collected: {len(dashboard_data)} sections")

    # Test report generation
    print("\n📋 Testing report generation...")
    report = monitor.generate_report()
    print("  Report generated successfully")

    # Test alert retrieval
    print("\n🚨 Testing alert retrieval...")
    recent_alerts = monitor.get_recent_alerts(hours=1)
    print(f"  Recent alerts: {len(recent_alerts)}")

    for alert in recent_alerts:
        print(f"    [{alert.level.value.upper()}] {alert.message}")

    # Test monitoring start/stop
    print("\n🔄 Testing monitoring start/stop...")
    monitor.start_monitoring()
    time.sleep(3)
    monitor.stop_monitoring()
    print("  Monitoring start/stop test completed")

    # Test data cleanup
    print("\n🧹 Testing data cleanup...")
    monitor.cleanup_old_data()
    print("  Data cleanup test completed")

    print("\n🎉 Performance monitoring system testing completed!")


if __name__ == "__main__":
    test_performance_monitor()
