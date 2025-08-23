#!/usr/bin/env python3
"""
Hydration Performance Dashboard
Real-time monitoring and visualization for hydration system performance
"""

import json
import os
import queue
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.database_resilience import DatabaseResilienceManager
from src.utils.logger import get_logger
from src.utils.memory_rehydrator import build_hydration_bundle

logger = get_logger(__name__)

class HydrationDashboard:
    """Real-time hydration system performance dashboard"""

    def __init__(self):
        self.metrics_history = []
        self.alerts_history = []
        self.performance_data = {
            "bundle_creation_times": [],
            "memory_usage": [],
            "quality_scores": [],
            "error_rates": [],
        }
        self.max_history_size = 1000
        self.monitoring_active = False
        self.metrics_queue = queue.Queue()

    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous monitoring"""
        if self.monitoring_active:
            logger.warning("Monitoring already active")
            return

        self.monitoring_active = True
        logger.info(f"Starting hydration monitoring (interval: {interval_seconds}s)")

        def monitor_loop():
            while self.monitoring_active:
                try:
                    metrics = self._collect_metrics()
                    self._update_history(metrics)
                    time.sleep(interval_seconds)
                except Exception as e:
                    logger.error(f"Monitoring error: {e}")
                    time.sleep(interval_seconds)

        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        self.monitoring_active = False
        logger.info("Stopped hydration monitoring")

    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        timestamp = time.time()
        metrics = {
            "timestamp": timestamp,
            "datetime": datetime.fromtimestamp(timestamp).isoformat(),
            "bundle_creation": self._measure_bundle_creation(),
            "memory_usage": self._measure_memory_usage(),
            "quality_metrics": self._measure_quality_metrics(),
            "system_health": self._check_system_health(),
        }

        return metrics

    def _measure_bundle_creation(self) -> Dict[str, Any]:
        """Measure bundle creation performance"""
        try:
            start_time = time.time()

            # Test different roles and tasks
            test_cases = [("planner", "performance test", 1200), ("implementer", "performance test", 1200)]

            results = []
            for role, task, budget in test_cases:
                bundle_start = time.time()
                bundle = build_hydration_bundle(role=role, task=task, token_budget=budget)
                bundle_time = time.time() - bundle_start

                results.append(
                    {
                        "role": role,
                        "creation_time": bundle_time,
                        "sections": bundle.meta.get("sections", 0),
                        "tokens": bundle.meta.get("tokens_est", 0),
                        "budget": budget,
                        "efficiency": bundle.meta.get("tokens_est", 0) / budget,
                    }
                )

            total_time = time.time() - start_time
            avg_time = sum(r["creation_time"] for r in results) / len(results)

            return {
                "total_time": total_time,
                "avg_creation_time": avg_time,
                "test_cases": results,
                "status": "healthy" if avg_time < 5.0 else "degraded",
            }

        except Exception as e:
            logger.error(f"Bundle creation measurement failed: {e}")
            return {"error": str(e), "status": "error"}

    def _measure_memory_usage(self) -> Dict[str, Any]:
        """Measure memory usage"""
        try:
            import psutil  # type: ignore[import-untyped]

            process = psutil.Process(os.getpid())
            memory_info = process.memory_info()

            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
                "status": "healthy",
            }

        except ImportError:
            return {"status": "psutil_not_available", "message": "Memory monitoring requires psutil"}
        except Exception as e:
            logger.error(f"Memory measurement failed: {e}")
            return {"error": str(e), "status": "error"}

    def _measure_quality_metrics(self) -> Dict[str, Any]:
        """Measure quality metrics"""
        try:
            # Test role-specific quality
            planner_bundle = build_hydration_bundle(role="planner", task="quality assessment", token_budget=1200)

            implementer_bundle = build_hydration_bundle(
                role="implementer", task="quality assessment", token_budget=1200
            )

            # Calculate quality scores
            planner_text = planner_bundle.text.lower()
            implementer_text = implementer_bundle.text.lower()

            planner_keywords = ["backlog", "priority", "system", "overview", "planning"]
            implementer_keywords = ["dspy", "development", "implementation", "code", "technical"]

            planner_score = sum(1 for kw in planner_keywords if kw in planner_text) / len(planner_keywords)
            implementer_score = sum(1 for kw in implementer_keywords if kw in implementer_text) / len(
                implementer_keywords
            )

            overall_score = (planner_score + implementer_score) / 2

            return {
                "planner_score": planner_score,
                "implementer_score": implementer_score,
                "overall_score": overall_score,
                "status": "healthy" if overall_score >= 0.7 else "degraded",
            }

        except Exception as e:
            logger.error(f"Quality measurement failed: {e}")
            return {"error": str(e), "status": "error"}

    def _check_system_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        try:
            # Database connection
            connection_string = os.getenv("POSTGRES_DSN")
            if connection_string:
                db_manager = DatabaseResilienceManager(connection_string)
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                    cursor.close()
                db_healthy = True
            else:
                db_healthy = False
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            db_healthy = False

        # Memory rehydrator health
        try:
            bundle = build_hydration_bundle(role="planner", task="health check", token_budget=500)
            rehydrator_healthy = bundle.meta.get("sections", 0) > 0
        except Exception as e:
            logger.error(f"Rehydrator health check failed: {e}")
            rehydrator_healthy = False

        return {
            "database": db_healthy,
            "memory_rehydrator": rehydrator_healthy,
            "overall": db_healthy and rehydrator_healthy,
        }

    def _update_history(self, metrics: Dict[str, Any]):
        """Update metrics history"""
        self.metrics_history.append(metrics)

        # Trim history if too long
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size :]

        # Update performance data
        if "bundle_creation" in metrics and "avg_creation_time" in metrics["bundle_creation"]:
            self.performance_data["bundle_creation_times"].append(
                {"timestamp": metrics["timestamp"], "value": metrics["bundle_creation"]["avg_creation_time"]}
            )

        if "memory_usage" in metrics and "rss_mb" in metrics["memory_usage"]:
            self.performance_data["memory_usage"].append(
                {"timestamp": metrics["timestamp"], "value": metrics["memory_usage"]["rss_mb"]}
            )

        if "quality_metrics" in metrics and "overall_score" in metrics["quality_metrics"]:
            self.performance_data["quality_scores"].append(
                {"timestamp": metrics["timestamp"], "value": metrics["quality_metrics"]["overall_score"]}
            )

    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get current dashboard data"""
        current_metrics = self._collect_metrics()

        # Calculate trends
        trends = self._calculate_trends()

        # Generate alerts
        alerts = self._generate_alerts(current_metrics)

        return {
            "current_metrics": current_metrics,
            "trends": trends,
            "alerts": alerts,
            "history_summary": self._get_history_summary(),
            "performance_data": self.performance_data,
        }

    def _calculate_trends(self) -> Dict[str, Any]:
        """Calculate performance trends"""
        if len(self.metrics_history) < 2:
            return {"status": "insufficient_data"}

        recent_metrics = self.metrics_history[-10:]  # Last 10 measurements

        # Bundle creation time trend
        creation_times = [
            m["bundle_creation"]["avg_creation_time"]
            for m in recent_metrics
            if "bundle_creation" in m and "avg_creation_time" in m["bundle_creation"]
        ]

        if len(creation_times) >= 2:
            creation_trend = "improving" if creation_times[-1] < creation_times[0] else "degrading"
        else:
            creation_trend = "stable"

        # Quality trend
        quality_scores = [
            m["quality_metrics"]["overall_score"]
            for m in recent_metrics
            if "quality_metrics" in m and "overall_score" in m["quality_metrics"]
        ]

        if len(quality_scores) >= 2:
            quality_trend = "improving" if quality_scores[-1] > quality_scores[0] else "degrading"
        else:
            quality_trend = "stable"

        return {"bundle_creation": creation_trend, "quality": quality_trend, "status": "calculated"}

    def _generate_alerts(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate alerts based on current metrics"""
        alerts = []

        # Performance alerts
        if "bundle_creation" in metrics and "avg_creation_time" in metrics["bundle_creation"]:
            avg_time = metrics["bundle_creation"]["avg_creation_time"]
            if avg_time > 5.0:
                alerts.append(
                    {
                        "type": "performance",
                        "severity": "warning",
                        "message": f"Bundle creation time high: {avg_time:.2f}s",
                        "timestamp": metrics["timestamp"],
                    }
                )
            elif avg_time > 10.0:
                alerts.append(
                    {
                        "type": "performance",
                        "severity": "critical",
                        "message": f"Bundle creation time critical: {avg_time:.2f}s",
                        "timestamp": metrics["timestamp"],
                    }
                )

        # Quality alerts
        if "quality_metrics" in metrics and "overall_score" in metrics["quality_metrics"]:
            score = metrics["quality_metrics"]["overall_score"]
            if score < 0.7:
                alerts.append(
                    {
                        "type": "quality",
                        "severity": "warning",
                        "message": f"Quality score below threshold: {score:.2f}",
                        "timestamp": metrics["timestamp"],
                    }
                )

        # System health alerts
        if "system_health" in metrics and not metrics["system_health"]["overall"]:
            alerts.append(
                {
                    "type": "system",
                    "severity": "critical",
                    "message": "System health check failed",
                    "timestamp": metrics["timestamp"],
                }
            )

        return alerts

    def _get_history_summary(self) -> Dict[str, Any]:
        """Get summary of historical data"""
        if not self.metrics_history:
            return {"status": "no_data"}

        # Calculate statistics for last 24 hours
        now = time.time()
        day_ago = now - 86400

        recent_metrics = [m for m in self.metrics_history if m["timestamp"] > day_ago]

        if not recent_metrics:
            return {"status": "no_recent_data"}

        # Bundle creation statistics
        creation_times = [
            m["bundle_creation"]["avg_creation_time"]
            for m in recent_metrics
            if "bundle_creation" in m and "avg_creation_time" in m["bundle_creation"]
        ]

        # Quality statistics
        quality_scores = [
            m["quality_metrics"]["overall_score"]
            for m in recent_metrics
            if "quality_metrics" in m and "overall_score" in m["quality_metrics"]
        ]

        return {
            "period": "24h",
            "total_measurements": len(recent_metrics),
            "bundle_creation": {
                "avg": sum(creation_times) / len(creation_times) if creation_times else 0,
                "min": min(creation_times) if creation_times else 0,
                "max": max(creation_times) if creation_times else 0,
            },
            "quality": {
                "avg": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
                "min": min(quality_scores) if quality_scores else 0,
                "max": max(quality_scores) if quality_scores else 0,
            },
        }

def create_dashboard_html(dashboard_data: Dict[str, Any]) -> str:
    """Create HTML dashboard"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hydration Performance Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .dashboard { max-width: 1200px; margin: 0 auto; }
            .header { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .metric-card { background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .metric-title { font-size: 18px; font-weight: bold; margin-bottom: 10px; color: #333; }
            .metric-value { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
            .metric-status { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
            .status-healthy { background: #d4edda; color: #155724; }
            .status-degraded { background: #fff3cd; color: #856404; }
            .status-error { background: #f8d7da; color: #721c24; }
            .alerts { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .alert { padding: 10px; margin-bottom: 10px; border-radius: 4px; }
            .alert-warning { background: #fff3cd; border: 1px solid #ffeaa7; }
            .alert-critical { background: #f8d7da; border: 1px solid #fab1a0; }
            .trends { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
            .trend-item { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #eee; }
            .trend-improving { color: #28a745; }
            .trend-degrading { color: #dc3545; }
            .trend-stable { color: #6c757d; }
        </style>
    </head>
    <body>
        <div class="dashboard">
            <div class="header">
                <h1>🚀 Hydration Performance Dashboard</h1>
                <p>Real-time monitoring of hydration system performance and quality</p>
            </div>
    """

    # Current metrics
    current = dashboard_data["current_metrics"]
    html += '<div class="metrics-grid">'

    # Bundle creation metrics
    if "bundle_creation" in current:
        bundle_data = current["bundle_creation"]
        status_class = f"status-{bundle_data.get('status', 'error')}"
        html += f"""
        <div class="metric-card">
            <div class="metric-title">Bundle Creation Performance</div>
            <div class="metric-value">{bundle_data.get('avg_creation_time', 0):.3f}s</div>
            <div class="metric-status {status_class}">{bundle_data.get('status', 'error').upper()}</div>
        </div>
        """

    # Quality metrics
    if "quality_metrics" in current:
        quality_data = current["quality_metrics"]
        status_class = f"status-{quality_data.get('status', 'error')}"
        html += f"""
        <div class="metric-card">
            <div class="metric-title">Quality Score</div>
            <div class="metric-value">{quality_data.get('overall_score', 0):.1%}</div>
            <div class="metric-status {status_class}">{quality_data.get('status', 'error').upper()}</div>
        </div>
        """

    # Memory usage
    if "memory_usage" in current:
        memory_data = current["memory_usage"]
        status_class = f"status-{memory_data.get('status', 'error')}"
        html += f"""
        <div class="metric-card">
            <div class="metric-title">Memory Usage</div>
            <div class="metric-value">{memory_data.get('rss_mb', 0):.1f} MB</div>
            <div class="metric-status {status_class}">{memory_data.get('status', 'error').upper()}</div>
        </div>
        """

    # System health
    if "system_health" in current:
        health_data = current["system_health"]
        status_class = f"status-{'healthy' if health_data.get('overall', False) else 'error'}"
        html += f"""
        <div class="metric-card">
            <div class="metric-title">System Health</div>
            <div class="metric-value">{'✅' if health_data.get('overall', False) else '❌'}</div>
            <div class="metric-status {status_class}">{'HEALTHY' if health_data.get('overall', False) else 'UNHEALTHY'}</div>
        </div>
        """

    html += "</div>"

    # Alerts
    if dashboard_data["alerts"]:
        html += '<div class="alerts"><h2>⚠️ Alerts</h2>'
        for alert in dashboard_data["alerts"]:
            severity_class = f"alert-{alert['severity']}"
            html += f"""
            <div class="alert {severity_class}">
                <strong>{alert['type'].upper()}</strong>: {alert['message']}
            </div>
            """
        html += "</div>"

    # Trends
    if "trends" in dashboard_data:
        trends = dashboard_data["trends"]
        html += '<div class="trends"><h2>📈 Trends</h2>'
        for trend_name, trend_value in trends.items():
            if trend_name != "status":
                trend_class = f"trend-{trend_value}"
                html += f"""
                <div class="trend-item">
                    <span>{trend_name.replace('_', ' ').title()}</span>
                    <span class="{trend_class}">{trend_value.upper()}</span>
                </div>
                """
        html += "</div>"

    html += """
        </div>
        <script>
            // Auto-refresh every 30 seconds
            setTimeout(() => location.reload(), 30000);
        </script>
    </body>
    </html>
    """

    return html

def main():
    """Main dashboard function"""
    logger.info("Starting hydration performance dashboard")

    dashboard = HydrationDashboard()

    # Start monitoring
    dashboard.start_monitoring(interval_seconds=30)

    # Get initial data
    dashboard_data = dashboard.get_dashboard_data()

    # Create HTML dashboard
    html_content = create_dashboard_html(dashboard_data)

    # Save to file
    dashboard_file = "hydration_dashboard.html"
    with open(dashboard_file, "w") as f:
        f.write(html_content)

    logger.info(f"Dashboard saved to {dashboard_file}")

    # Output JSON data for API
    print(json.dumps(dashboard_data, indent=2))

    return 0

if __name__ == "__main__":
    exit(main())
