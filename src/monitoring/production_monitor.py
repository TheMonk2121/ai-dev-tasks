"""
Production Monitor for AI Development Tasks

Provides production monitoring capabilities including:
- Real-time system monitoring
- Alert management
- Performance tracking
- Health status reporting
"""

import json
import time
from datetime import datetime, timedelta
from typing import Any

from .health_endpoints import HealthEndpointManager
from .metrics import get_metrics, get_performance_summary


class ProductionMonitor:
    """Production monitoring for AI development tasks"""

    def __init__(self):
        self.health_manager: HealthEndpointManager = HealthEndpointManager()
        self.alert_thresholds: dict[str, float] = {
            "memory_usage_percent": 80.0,
            "disk_usage_percent": 90.0,
            "database_response_time": 5.0,
        }
        self.alerts: list[dict[str, Any]] = []
        self.monitoring_start_time: datetime = datetime.now()

    def get_production_status(self) -> dict[str, Any]:
        """Get current production status"""
        health_status = self.health_manager.get_health_status()
        performance_summary = get_performance_summary()

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime": str(datetime.now() - self.monitoring_start_time),
            "overall_status": health_status["status"],
            "performance_summary": performance_summary,
            "active_alerts": len(self.alerts),
            "unhealthy_dependencies": health_status["unhealthy_dependencies"],
            "degraded_dependencies": health_status["degraded_dependencies"],
        }

    def check_alerts(self) -> list[dict[str, Any]]:
        """Check for alert conditions"""
        new_alerts = []
        current_time = datetime.now()

        try:
            # Get current metrics
            metrics = get_metrics()

            # Check system resource alerts
            if "error" not in metrics["system_metrics"]:
                memory_percent = metrics["system_metrics"]["memory"]["percent_used"]
                disk_percent = metrics["system_metrics"]["disk"]["percent_used"]

                if memory_percent > self.alert_thresholds["memory_usage_percent"]:
                    alert = {
                        "type": "memory_usage",
                        "severity": "warning" if memory_percent < 90 else "critical",
                        "message": f"High memory usage: {memory_percent:.1f}%",
                        "timestamp": current_time.isoformat(),
                        "value": memory_percent,
                        "threshold": self.alert_thresholds["memory_usage_percent"],
                    }
                    new_alerts.append(alert)

                if disk_percent > self.alert_thresholds["disk_usage_percent"]:
                    alert = {
                        "type": "disk_usage",
                        "severity": "warning" if disk_percent < 95 else "critical",
                        "message": f"High disk usage: {disk_percent:.1f}%",
                        "timestamp": current_time.isoformat(),
                        "value": disk_percent,
                        "threshold": self.alert_thresholds["disk_usage_percent"],
                    }
                    new_alerts.append(alert)

            # Check database performance alerts
            if "error" not in metrics["database_metrics"]:
                # Check for slow queries
                slow_queries = metrics["database_metrics"].get("slow_queries", [])
                for query in slow_queries:
                    if query.get("mean_time", 0) > self.alert_thresholds["database_response_time"]:
                        alert = {
                            "type": "slow_query",
                            "severity": "warning",
                            "message": f"Slow query detected: {query.get('mean_time', 0):.3f}s",
                            "timestamp": current_time.isoformat(),
                            "query": (
                                query.get("query", "")[:100] + "..."
                                if len(query.get("query", "")) > 100
                                else query.get("query", "")
                            ),
                            "mean_time": query.get("mean_time", 0),
                        }
                        new_alerts.append(alert)

            # Check health status alerts
            health_status = self.health_manager.get_health_status()
            if health_status["status"] == "unhealthy":
                alert = {
                    "type": "system_health",
                    "severity": "critical",
                    "message": f"System unhealthy: {health_status['unhealthy_dependencies']} unhealthy dependencies",
                    "timestamp": current_time.isoformat(),
                    "unhealthy_count": health_status["unhealthy_dependencies"],
                }
                new_alerts.append(alert)
            elif health_status["status"] == "degraded":
                alert = {
                    "type": "system_health",
                    "severity": "warning",
                    "message": f"System degraded: {health_status['degraded_dependencies']} degraded dependencies",
                    "timestamp": current_time.isoformat(),
                    "degraded_count": health_status["degraded_dependencies"],
                }
                new_alerts.append(alert)

        except Exception as e:
            alert = {
                "type": "monitoring_error",
                "severity": "critical",
                "message": f"Monitoring system error: {str(e)}",
                "timestamp": current_time.isoformat(),
                "error": str(e),
            }
            new_alerts.append(alert)

        # Add new alerts to the alerts list
        self.alerts.extend(new_alerts)

        # Keep only recent alerts (last 24 hours)
        cutoff_time = current_time - timedelta(hours=24)
        self.alerts = [alert for alert in self.alerts if datetime.fromisoformat(alert["timestamp"]) > cutoff_time]

        return new_alerts

    def get_alert_summary(self) -> dict[str, Any]:
        """Get summary of current alerts"""
        current_time = datetime.now()
        recent_alerts = [
            alert
            for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > current_time - timedelta(hours=1)
        ]

        # Group alerts by severity
        critical_alerts = [a for a in recent_alerts if a["severity"] == "critical"]
        warning_alerts = [a for a in recent_alerts if a["severity"] == "warning"]

        return {
            "total_alerts": len(self.alerts),
            "recent_alerts": len(recent_alerts),
            "critical_alerts": len(critical_alerts),
            "warning_alerts": len(warning_alerts),
            "latest_alerts": recent_alerts[-5:] if recent_alerts else [],
        }

    def get_monitoring_dashboard_data(self) -> dict[str, Any]:
        """Get data for monitoring dashboard"""
        production_status = self.get_production_status()
        alert_summary = self.get_alert_summary()
        metrics = get_metrics()

        return {
            "production_status": production_status,
            "alert_summary": alert_summary,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat(),
        }

    def save_monitoring_report(self, filepath: str = "monitoring_report.json") -> str:
        """Save comprehensive monitoring report"""
        dashboard_data = self.get_monitoring_dashboard_data()

        with open(filepath, "w") as f:
            json.dump(dashboard_data, f, indent=2, default=str)

        return filepath

    def run_continuous_monitoring(self, interval_seconds: int = 60, duration_minutes: int = 60):
        """Run continuous monitoring for specified duration"""
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)

        print(f"Starting continuous monitoring for {duration_minutes} minutes...")
        print(f"Monitoring interval: {interval_seconds} seconds")
        print(f"Start time: {start_time.isoformat()}")
        print(f"End time: {end_time.isoformat()}")
        print("-" * 50)

        while datetime.now() < end_time:
            try:
                # Check for new alerts
                new_alerts = self.check_alerts()

                # Print status
                status = self.get_production_status()
                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Status: {status['overall_status']} | "
                    + f"Alerts: {status['active_alerts']} | "
                    + f"Uptime: {status['uptime']}"
                )

                # Print new alerts
                for alert in new_alerts:
                    print(f"  🚨 {alert['severity'].upper()}: {alert['message']}")

                # Save periodic report
                if len(self.alerts) > 0 and len(self.alerts) % 10 == 0:
                    report_file = f"monitoring_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    _ = self.save_monitoring_report(report_file)
                    print(f"  📊 Report saved: {report_file}")

                time.sleep(interval_seconds)

            except KeyboardInterrupt:
                print("\nMonitoring stopped by user")
                break
            except Exception as e:
                print(f"Monitoring error: {e}")
                time.sleep(interval_seconds)

        print(f"\nMonitoring completed at {datetime.now().isoformat()}")
        print(f"Total alerts generated: {len(self.alerts)}")

        # Save final report
        final_report = self.save_monitoring_report("final_monitoring_report.json")
        print(f"Final report saved: {final_report}")
