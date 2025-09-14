from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime
from typing import Any
    from monitoring.health_endpoints import HealthEndpointManager
    from monitoring.metrics import get_metrics, get_performance_summary
    from monitoring.production_monitor import ProductionMonitor
import argparse
from typing import Any, Optional, Union
#!/usr/bin/env python3
"""
Monitoring Dashboard for AI Development Tasks

Provides a real-time monitoring dashboard with:
- System health status
- Performance metrics
- Alert management
- Resource utilization
"""

# Add src directory to Python path for monitoring modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

try:
except ImportError as e:
    print(f"❌ Monitoring modules not available: {e}")
    sys.exit(1)

class MonitoringDashboard:
    """Real-time monitoring dashboard"""

    def __init__(self):
        self.health_manager = HealthEndpointManager()
        self.production_monitor = ProductionMonitor()
        self.start_time = datetime.now()

    def display_header(self):
        """Display dashboard header"""
        print("=" * 80)
        print("🚀 AI Development Tasks - Monitoring Dashboard")
        print("=" * 80)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Uptime: {datetime.now() - self.start_time}")
        print("=" * 80)

    def display_system_health(self):
        """Display system health status"""
        print("\n📊 SYSTEM HEALTH STATUS")
        print("-" * 40)

        try:
            health_status = self.health_manager.get_health_status()

            # Overall status
            status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}
            print(
                f"Overall Status: {status_emoji.get(health_status['status'], '❓')} {health_status['status'].upper()}"
            )

            # Dependencies
            print(f"Unhealthy: {health_status['unhealthy_dependencies']}")
            print(f"Degraded: {health_status['degraded_dependencies']}")

            # Individual components
            for dep in health_status["dependencies"]:
                dep_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}
                print(f"  {dep['name']}: {dep_emoji.get(dep['status'], '❓')} {dep['status']}")
                if "details" in dep:
                    print(f"    {dep['details']}")

        except Exception as e:
            print(f"❌ Error getting health status: {e}")

    def display_performance_metrics(self):
        """Display performance metrics"""
        print("\n⚡ PERFORMANCE METRICS")
        print("-" * 40)

        try:
            metrics = get_metrics()

            # System resources
            if "error" not in metrics["system_metrics"]:
                sys_metrics = metrics["system_metrics"]
                print(f"Memory Usage: {sys_metrics['memory']['percent_used']:.1f}%")
                print(f"Disk Usage: {sys_metrics['disk']['percent_used']:.1f}%")
                print(f"CPU Usage: {sys_metrics['cpu']['percent_used']:.1f}%")

            # Database metrics
            if "error" not in metrics["database_metrics"]:
                db_metrics = metrics["database_metrics"]
                print(f"Database Size: {db_metrics.get('database_size', 'unknown')}")
                print(f"Top Tables: {len(db_metrics.get('top_tables', []))}")

            # RAG metrics
            if "error" not in metrics["rag_metrics"]:
                rag_metrics = metrics["rag_metrics"]
                edge_cases = rag_metrics.get("edge_cases_count", 0)
                hypothesis_examples = rag_metrics.get("hypothesis_examples_count", 0)
                print(f"Edge Cases: {edge_cases}")
                print(f"Hypothesis Examples: {hypothesis_examples}")

        except Exception as e:
            print(f"❌ Error getting performance metrics: {e}")

    def display_alerts(self):
        """Display current alerts"""
        print("\n🚨 ALERTS & NOTIFICATIONS")
        print("-" * 40)

        try:
            # Check for new alerts
            new_alerts = self.production_monitor.check_alerts()
            alert_summary = self.production_monitor.get_alert_summary()

            if alert_summary["total_alerts"] == 0:
                print("✅ No active alerts")
            else:
                print(f"Total Alerts: {alert_summary['total_alerts']}")
                print(f"Recent Alerts: {alert_summary['recent_alerts']}")
                print(f"Critical: {alert_summary['critical_alerts']}")
                print(f"Warnings: {alert_summary['warning_alerts']}")

                # Show latest alerts
                for alert in alert_summary["latest_alerts"]:
                    severity_emoji = {"critical": "🔴", "warning": "🟡", "info": "🔵"}
                    print(f"  {severity_emoji.get(alert['severity'], '⚪')} {alert['message']}")

        except Exception as e:
            print(f"❌ Error getting alerts: {e}")

    def display_quick_stats(self):
        """Display quick statistics"""
        print("\n📈 QUICK STATS")
        print("-" * 40)

        try:
            # Get some quick stats
            health_status = self.health_manager.get_health_status()
            performance_summary = get_performance_summary()

            print(f"System Status: {health_status['status'].upper()}")
            print(f"Uptime: {datetime.now() - self.start_time}")

            if "key_metrics" in performance_summary:
                for key, value in performance_summary["key_metrics"].items():
                    print(f"{key.replace('_', ' ').title()}: {value}")

        except Exception as e:
            print(f"❌ Error getting quick stats: {e}")

    def run_dashboard(self, watch_mode: bool = False, interval: int = 30):
        """Run the monitoring dashboard"""
        if watch_mode:
            print("🔄 Starting watch mode... Press Ctrl+C to stop")
            try:
                while True:
                    self.display_header()
                    self.display_system_health()
                    self.display_performance_metrics()
                    self.display_alerts()
                    self.display_quick_stats()

                    print(f"\n⏰ Next update in {interval} seconds...")
                    time.sleep(interval)

            except KeyboardInterrupt:
                print("\n\n👋 Dashboard stopped by user")
        else:
            # Single run
            self.display_header()
            self.display_system_health()
            self.display_performance_metrics()
            self.display_alerts()
            self.display_quick_stats()

    def save_dashboard_report(self, filename: str | None = None):
        """Save dashboard report to file"""
        if filename is None:
            filename = f"dashboard_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            dashboard_data = self.production_monitor.get_monitoring_dashboard_data()

            with open(filename, "w") as f:
                json.dump(dashboard_data, f, indent=2, default=str)

            print(f"📊 Dashboard report saved: {filename}")
            return filename

        except Exception as e:
            print(f"❌ Error saving dashboard report: {e}")
            return None

def main():
    """Main function"""

    parser = argparse.ArgumentParser(description="AI Development Tasks Monitoring Dashboard")
    parser.add_argument("--watch", action="store_true", help="Watch mode - continuously monitor")
    parser.add_argument("--interval", type=int, default=30, help="Watch interval in seconds")
    parser.add_argument("--save-report", action="store_true", help="Save dashboard report to file")
    parser.add_argument("--report-file", type=str, help="Custom report filename")

    args = parser.parse_args()

    dashboard = MonitoringDashboard()

    if args.save_report:
        dashboard.save_dashboard_report(args.report_file)

    dashboard.run_dashboard(watch_mode=args.watch, interval=args.interval)

if __name__ == "__main__":
    main()
