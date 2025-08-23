# DEPRECATED: This demo file is being archived. See 400_guides/ for essential examples.
#!/usr/bin/env python3
"""
Metrics Dashboard Demonstration

Demonstrates the metrics dashboard and measurement system with real-time
monitoring, historical tracking, and clear visualization of optimization progress.
"""

import json
import os
import sys
import time
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature
from dspy_modules.metrics_dashboard import (
    DashboardView,
    MetricType,
    get_dashboard_view,
    get_metrics_dashboard,
    record_optimization_metrics,
)
from dspy_modules.optimization_loop import get_optimization_loop


class TestSignature(Signature):
    """Test signature for optimization"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class TestModule(Module):
    """Test module for optimization demonstration"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """
        Forward pass with comprehensive quality improvements

        Args:
            input_field: Input string to process

        Returns:
            Dictionary with processed result and metadata
        """
        try:
            # Input validation
            if not isinstance(input_field, str):
                raise ValueError("Input must be a string")

            if not input_field.strip():
                raise ValueError("Input cannot be empty")

            # Input sanitization
            sanitized_input = input_field.strip().replace("<script>", "").replace("</script>", "")

            # Process input
            result = self.predictor(input_field=sanitized_input)

            return {"output_field": result.output_field, "input_field": sanitized_input, "validation_status": "passed"}

        except Exception as e:
            # Comprehensive error handling
            return {
                "error": str(e),
                "error_type": type(e).__name__,
                "input_field": input_field,
                "validation_status": "failed",
            }


def demonstrate_metrics_dashboard():
    """Demonstrate the metrics dashboard and measurement system"""

    print("📊 DSPy v2 Optimization: Metrics Dashboard and Measurement System")
    print("=" * 80)
    print()
    print("Real-time monitoring, historical tracking, and clear visualization")
    print("of optimization progress with actionable metrics and alerts.")
    print()

    # Initialize dashboard and optimization loop
    dashboard = get_metrics_dashboard()
    optimization_loop = get_optimization_loop()
    dashboard.connect_optimization_loop(optimization_loop)

    print("🔧 Metrics Dashboard Initialized")
    print(f"  Metric types: {[mt.value for mt in MetricType]}")
    print(f"  Dashboard views: {[dv.value for dv in DashboardView]}")
    print(f"  Connected to optimization loop: {dashboard.optimization_loop is not None}")
    print()

    # Test inputs for optimization cycles
    test_inputs = {
        "module_class": TestModule,
        "optimization_objectives": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
        "target_metrics": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
        "test_data": [
            {"input_field": "normal input"},
            {"input_field": "<script>alert('xss')</script>"},  # Security test
            {"input_field": ""},  # Empty input test
            {"input_field": "very long input " * 100},  # Performance test
        ],
        "deployment_config": {"environment": "production", "monitoring_enabled": True, "rollback_enabled": True},
    }

    print("=" * 80)

    # Generate optimization cycles and record metrics
    print("🔄 Generating Optimization Cycles and Recording Metrics")
    print("-" * 50)

    cycles = []
    for i in range(5):
        print(f"  Cycle {i+1}: Running optimization...")
        cycle = optimization_loop.run_cycle(test_inputs)
        cycles.append(cycle)

        # Record metrics automatically
        record_optimization_metrics(cycle)

        print(f"  Cycle {i+1}: Completed ({cycle.duration:.3f}s)")
        print(f"    Status: {cycle.overall_status.value}")
        print(f"    Success: {'✅ Yes' if cycle.success else '❌ No'}")

        # Small delay to create time separation
        time.sleep(0.1)

    print()
    print(f"✅ Generated {len(cycles)} optimization cycles")
    print("✅ Recorded metrics for all cycles")
    print()

    print("=" * 80)

    # Dashboard Overview View
    print("📊 Dashboard Overview View")
    print("-" * 50)

    overview_data = get_dashboard_view(DashboardView.OVERVIEW)

    print("Summary Statistics:")
    summary = overview_data["summary"]
    print(f"  📈 Total cycles: {summary['total_cycles']}")
    print(f"  ✅ Successful cycles: {summary['successful_cycles']}")
    print(f"  ⚠️  Active alerts: {summary['active_alerts']}")
    print(f"  🕒 Last cycle time: {summary['last_cycle_time']:.0f}")
    print()

    print("Current Metrics:")
    current_metrics = overview_data["current_metrics"]
    for metric_name, metric_data in current_metrics.items():
        value = metric_data["value"]
        unit = metric_data["unit"]
        status = metric_data["status"]
        status_emoji = {"good": "✅", "medium": "⚠️", "high": "🔴", "critical": "🚨"}.get(status, "❓")
        print(f"  {status_emoji} {metric_name.title()}: {value:.1f}{unit} ({status})")
    print()

    print("Trends (1-hour window):")
    trends = overview_data["trends"]
    for metric_name, trend_data in trends.items():
        slope = trend_data["slope"]
        direction = trend_data["direction"]
        direction_emoji = {"improving": "📈", "declining": "📉", "stable": "➡️"}.get(direction, "❓")
        print(f"  {direction_emoji} {metric_name.title()}: {direction} (slope: {slope:.3f})")
    print()

    print("Recent Alerts:")
    alerts = overview_data["alerts"]
    if alerts["count"] > 0:
        for alert in alerts["recent"][:3]:
            severity_emoji = {"critical": "🚨", "high": "🔴", "medium": "⚠️", "low": "🟡"}.get(alert["severity"], "❓")
            print(f"  {severity_emoji} {alert['message']}")
    else:
        print("  ✅ No active alerts")
    print()

    print("=" * 80)

    # Dashboard Detailed View
    print("📊 Dashboard Detailed View")
    print("-" * 50)

    detailed_data = get_dashboard_view(DashboardView.DETAILED)

    print("Detailed Metrics:")
    metrics = detailed_data["metrics"]
    for metric_name, metric_data in metrics.items():
        current = metric_data["current"]
        avg_1h = metric_data["average_1h"]
        avg_24h = metric_data["average_24h"]
        trend_1h = metric_data["trend_1h"]
        unit = metric_data["unit"]

        print(f"  📊 {metric_name.title()}:")
        print(f"    Current: {current:.1f}{unit}" if current is not None else "    Current: N/A")
        print(f"    Avg (1h): {avg_1h:.1f}{unit}" if avg_1h is not None else "    Avg (1h): N/A")
        print(f"    Avg (24h): {avg_24h:.1f}{unit}" if avg_24h is not None else "    Avg (24h): N/A")
        print(f"    Trend (1h): {trend_1h:.3f}" if trend_1h is not None else "    Trend (1h): N/A")
        print()

    print("Phase Statistics:")
    phases = detailed_data["phases"]
    for phase_name, phase_data in phases.items():
        count = phase_data["count"]
        success_rate = phase_data["success_rate"]
        avg_duration = phase_data["avg_duration"]

        print(f"  🔄 {phase_name.title()}:")
        print(f"    Count: {count}")
        print(f"    Success rate: {success_rate:.1%}")
        print(f"    Avg duration: {avg_duration:.3f}s")
        print()

    print("Cycle Statistics:")
    cycles_data = detailed_data["cycles"]
    print(f"  📈 Total cycles: {cycles_data['total']}")
    print(f"  ✅ Successful: {cycles_data['successful']}")
    print(f"  ❌ Failed: {cycles_data['failed']}")
    print(f"  ⏱️  Avg duration: {cycles_data['avg_duration']:.3f}s")
    print(f"  🔄 Recent cycles: {cycles_data['recent_cycles']}")
    print()

    print("=" * 80)

    # Dashboard Historical View
    print("📊 Dashboard Historical View")
    print("-" * 50)

    historical_data = get_dashboard_view(DashboardView.HISTORICAL)

    print("Historical Data Analysis:")
    print(f"  📅 Time ranges: {historical_data['time_ranges']}")
    print()

    metrics_history = historical_data["metrics"]
    for metric_name, metric_data in metrics_history.items():
        data_points = metric_data["data_points"]
        stats = metric_data["statistics"]

        print(f"  📊 {metric_name.title()}:")
        print(f"    Data points: {len(data_points)}")
        print(f"    Min: {stats['min']:.1f}" if stats["min"] else "    Min: N/A")
        print(f"    Max: {stats['max']:.1f}" if stats["max"] else "    Max: N/A")
        print(f"    Average: {stats['avg']:.1f}" if stats["avg"] else "    Average: N/A")
        print()

    print("=" * 80)

    # Dashboard Comparison View
    print("📊 Dashboard Comparison View")
    print("-" * 50)

    comparison_data = get_dashboard_view(DashboardView.COMPARISON)

    print("Performance Comparisons:")
    comparisons = comparison_data["comparisons"]
    for metric_name, comparison_data in comparisons.items():
        current = comparison_data["current"]
        avg_24h = comparison_data["avg_24h"]
        avg_7d = comparison_data["avg_7d"]
        change_24h = comparison_data["change_24h"]
        change_7d = comparison_data["change_7d"]
        unit = comparison_data["unit"]

        print(f"  📊 {metric_name.title()}:")
        print(f"    Current: {current:.1f}{unit}")
        print(f"    Avg (24h): {avg_24h:.1f}{unit}" if avg_24h else "    Avg (24h): N/A")
        print(f"    Avg (7d): {avg_7d:.1f}{unit}" if avg_7d else "    Avg (7d): N/A")
        print(f"    Change (24h): {change_24h:+.1f}%")
        print(f"    Change (7d): {change_7d:+.1f}%")
        print()

    print("=" * 80)

    # Dashboard Alerts View
    print("📊 Dashboard Alerts View")
    print("-" * 50)

    alerts_data = get_dashboard_view(DashboardView.ALERTS)

    alerts_summary = alerts_data["alerts"]["summary"]
    print("Alerts Summary:")
    print(f"  📊 Total alerts: {alerts_summary['total']}")
    print(f"  ⚠️  Active alerts: {alerts_summary['active']}")
    print(f"  ✅ Acknowledged alerts: {alerts_summary['acknowledged']}")
    print(f"  📈 By severity: {alerts_summary['by_severity']}")
    print()

    active_alerts = alerts_data["alerts"]["active"]
    if active_alerts:
        print("Active Alerts:")
        for alert in active_alerts[:5]:  # Show first 5
            severity_emoji = {"critical": "🚨", "high": "🔴", "medium": "⚠️", "low": "🟡"}.get(alert["severity"], "❓")
            print(f"  {severity_emoji} {alert['message']}")
            print(f"    ID: {alert['alert_id']}")
            print(f"    Severity: {alert['severity']}")
            print(f"    Time: {alert['timestamp']:.0f}")
            print()
    else:
        print("  ✅ No active alerts")
    print()

    print("=" * 80)

    # Dashboard Statistics
    print("📊 Dashboard Statistics")
    print("-" * 50)

    stats = dashboard.get_statistics()

    print("System Statistics:")
    print(f"  📊 Total metrics: {stats['total_metrics']}")
    print(f"  📈 Total data points: {stats['total_data_points']}")
    print(f"  ⚠️  Total alerts: {stats['total_alerts']}")
    print(f"  🔴 Active alerts: {stats['active_alerts']}")
    print(f"  🔗 Connected to loop: {stats['connected_to_loop']}")
    print()

    # Show metric-specific statistics
    print("Metric-Specific Statistics:")
    for metric_type in MetricType:
        data_points_key = f"{metric_type.value}_data_points"
        latest_key = f"{metric_type.value}_latest"
        avg_24h_key = f"{metric_type.value}_avg_24h"

        if data_points_key in stats:
            print(f"  📊 {metric_type.value.title()}:")
            print(f"    Data points: {stats[data_points_key]}")
            print(
                f"    Latest: {stats[latest_key]:.1f}"
                if latest_key in stats and stats[latest_key]
                else "    Latest: N/A"
            )
            print(
                f"    Avg (24h): {stats[avg_24h_key]:.1f}"
                if avg_24h_key in stats and stats[avg_24h_key]
                else "    Avg (24h): N/A"
            )
            print()

    print("=" * 80)

    # Data Export Demonstration
    print("📊 Data Export Demonstration")
    print("-" * 50)

    try:
        exported_data = dashboard.export_data(format="json")
        parsed_data = json.loads(exported_data)

        print("Export Statistics:")
        print("  📄 Export format: JSON")
        print(f"  📏 Export size: {len(exported_data)} characters")
        print(f"  📊 Metric series: {len(parsed_data['metric_series'])}")
        print(f"  ⚠️  Alerts: {len(parsed_data['alerts'])}")
        print(f"  📅 Dashboard info: {parsed_data['dashboard_info']}")
        print()

        print("✅ Data export successful - dashboard data can be saved and analyzed")
        print()

    except Exception as e:
        print(f"❌ Data export failed: {e}")
        print()

    print("=" * 80)

    # Alert Management Demonstration
    print("📊 Alert Management Demonstration")
    print("-" * 50)

    if dashboard.alerts:
        # Acknowledge first alert
        first_alert = dashboard.alerts[0]
        print(f"Acknowledging alert: {first_alert.alert_id}")
        success = dashboard.acknowledge_alert(first_alert.alert_id)
        print(f"Acknowledgment success: {success}")
        print(f"Alert acknowledged: {first_alert.acknowledged}")
        print()

        # Show updated alert counts
        updated_stats = dashboard.get_statistics()
        print("Updated alert counts:")
        print(f"  Total alerts: {updated_stats['total_alerts']}")
        print(f"  Active alerts: {updated_stats['active_alerts']}")
        print()
    else:
        print("No alerts to manage")
        print()

    print("=" * 80)

    # Summary and Key Features
    print("📋 Metrics Dashboard Summary and Key Features")
    print("-" * 50)

    print("✅ Metrics Dashboard Successfully Implemented!")
    print()
    print("Key Features Demonstrated:")
    print("  📊 Real-time monitoring of optimization progress")
    print("  📈 Historical tracking with trend analysis")
    print("  ⚠️  Automated alert system with threshold violations")
    print("  🔄 Multiple dashboard views (Overview, Detailed, Historical, Comparison, Alerts)")
    print("  📊 Comprehensive metrics collection (Reliability, Performance, Quality, Duration, etc.)")
    print("  📈 Trend analysis with linear regression")
    print("  ⚡ Automatic metric recording from optimization cycles")
    print("  📄 Data export capabilities (JSON format)")
    print("  🔧 Alert management (acknowledgment, cleanup)")
    print("  📊 Statistical analysis and reporting")
    print()
    print("Dashboard Views Available:")
    for view in DashboardView:
        print(f"  📊 {view.value.title()}: {_get_view_description(view)}")
    print()
    print("Metrics Tracked:")
    for metric_type in MetricType:
        print(f"  📈 {metric_type.value.title()}: {_get_metric_description(metric_type)}")
    print()
    print("Alert Thresholds:")
    for metric_type, thresholds in dashboard.alert_thresholds.items():
        print(f"  ⚠️  {metric_type.value.title()}: {thresholds}")
    print()
    print("Integration Benefits:")
    print("  🔄 Seamless integration with four-part optimization loop")
    print("  📊 Automatic metric collection from all optimization phases")
    print("  📈 Real-time performance monitoring and trend analysis")
    print("  ⚠️  Proactive alerting for performance degradation")
    print("  📊 Comprehensive reporting and data export")
    print("  🔧 Actionable insights for optimization improvement")
    print()
    print("Adam LK Transcript Alignment:")
    print("  ✅ Systematic measurement and metrics implementation")
    print("  ✅ Real-time monitoring of optimization progress")
    print("  ✅ Historical tracking for trend analysis")
    print("  ✅ Actionable metrics for continuous improvement")
    print("  ✅ Clear visualization of optimization results")
    print("  ✅ Foundation for data-driven optimization decisions")

    print("\n" + "=" * 80)
    print("🎉 Metrics Dashboard and Measurement System Demonstration Complete!")
    print()
    print("The metrics dashboard provides comprehensive monitoring, tracking,")
    print("and visualization of optimization progress with real-time alerts")
    print("and historical analysis. This enables data-driven optimization")
    print("decisions and continuous improvement of DSPy programs.")


def _get_view_description(view: DashboardView) -> str:
    """Get description for a dashboard view"""
    descriptions = {
        DashboardView.OVERVIEW: "High-level summary with current metrics and trends",
        DashboardView.DETAILED: "Detailed metrics, phase statistics, and cycle analysis",
        DashboardView.HISTORICAL: "Historical data with time-series analysis",
        DashboardView.COMPARISON: "Performance comparisons across time periods",
        DashboardView.ALERTS: "Alert management and threshold monitoring",
    }
    return descriptions.get(view, "Unknown view")


def _get_metric_description(metric_type: MetricType) -> str:
    """Get description for a metric type"""
    descriptions = {
        MetricType.RELIABILITY: "Module reliability and error handling",
        MetricType.PERFORMANCE: "Execution time and efficiency",
        MetricType.QUALITY: "Code quality and best practices",
        MetricType.DURATION: "Optimization cycle duration",
        MetricType.SUCCESS_RATE: "Optimization success rate",
        MetricType.IMPROVEMENT: "Performance improvement metrics",
        MetricType.OPTIMIZATION_COUNT: "Number of optimizations applied",
        MetricType.ERROR_RATE: "Error and failure rates",
    }
    return descriptions.get(metric_type, "Unknown metric")


if __name__ == "__main__":
    demonstrate_metrics_dashboard()
