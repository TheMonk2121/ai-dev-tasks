#!/usr/bin/env python3
"""
Metrics Dashboard Tests

Comprehensive test suite for the metrics dashboard and measurement system.
"""

import os
import sys
import time
import unittest
from typing import Any, Dict

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import dspy
from dspy import InputField, Module, OutputField, Signature

from dspy_modules.metrics_dashboard import (
    Alert,
    DashboardView,
    MetricPoint,
    MetricsDashboard,
    MetricSeries,
    MetricType,
    get_dashboard_view,
    get_metrics_dashboard,
    record_optimization_metrics,
)
from dspy_modules.optimization_loop import (
    FourPartOptimizationLoop,
)


class TestSignature(Signature):
    """Test signature for optimization"""

    input_field = InputField(desc="Test input")
    output_field = OutputField(desc="Test output")


class TestModule(Module):
    """Test module for optimization"""

    def __init__(self):
        super().__init__()
        self.predictor = dspy.Predict(TestSignature)

    def forward(self, input_field: str) -> Dict[str, Any]:
        """Forward pass with comprehensive quality improvements"""
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


class TestMetricsDashboard(unittest.TestCase):
    """Test cases for the metrics dashboard"""

    def setUp(self):
        """Set up test fixtures"""
        self.dashboard = MetricsDashboard()
        self.optimization_loop = FourPartOptimizationLoop()
        self.dashboard.connect_optimization_loop(self.optimization_loop)

        self.test_inputs = {
            "module_class": TestModule,
            "optimization_objectives": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "target_metrics": {"reliability_target": 98.0, "performance_target": 1.0, "quality_target": 0.9},
            "test_data": [
                {"input_field": "normal input"},
                {"input_field": "<script>alert('xss')</script>"},
                {"input_field": ""},
                {"input_field": "very long input " * 100},
            ],
            "deployment_config": {"environment": "test", "monitoring_enabled": True},
        }

    def test_dashboard_initialization(self):
        """Test dashboard initialization"""
        # Test metric series initialization
        for metric_type in MetricType:
            self.assertIn(metric_type, self.dashboard.metric_series)
            self.assertIsInstance(self.dashboard.metric_series[metric_type], MetricSeries)

        # Test alert thresholds
        self.assertIn(MetricType.RELIABILITY, self.dashboard.alert_thresholds)
        self.assertIn(MetricType.PERFORMANCE, self.dashboard.alert_thresholds)
        self.assertIn(MetricType.QUALITY, self.dashboard.alert_thresholds)

        # Test optimization loop connection
        self.assertIsNotNone(self.dashboard.optimization_loop)

        print("\nDashboard Initialization Test:")
        print(f"  Metric series count: {len(self.dashboard.metric_series)}")
        print(f"  Alert thresholds count: {len(self.dashboard.alert_thresholds)}")
        print(f"  Connected to optimization loop: {self.dashboard.optimization_loop is not None}")

    def test_metric_series_operations(self):
        """Test metric series operations"""
        series = MetricSeries(metric_type=MetricType.RELIABILITY)

        # Test adding data points with time delays to create a trend
        base_time = time.time()

        # Add points with increasing values and timestamps
        point1 = MetricPoint(timestamp=base_time, value=85.0, metadata={"test": "data"})
        point2 = MetricPoint(timestamp=base_time + 60, value=90.0, metadata={"test": "data2"})
        point3 = MetricPoint(timestamp=base_time + 120, value=95.0, metadata={})

        series.data_points = [point1, point2, point3]

        # Test latest value
        latest = series.get_latest_value()
        self.assertEqual(latest, 95.0)

        # Test average calculation
        avg = series.get_average(window_minutes=60)
        self.assertIsNotNone(avg)
        if avg is not None:
            self.assertAlmostEqual(avg, 90.0, places=1)

        # Test trend calculation
        trend = series.get_trend(window_minutes=60)
        self.assertIsNotNone(trend)
        if trend is not None:
            self.assertGreater(trend, 0)  # Should be positive trend

        print("\nMetric Series Operations Test:")
        print(f"  Data points: {len(series.data_points)}")
        print(f"  Latest value: {latest}")
        print(f"  Average (1h): {avg:.1f}")
        print(f"  Trend (1h): {trend:.3f}")

    def test_cycle_metrics_recording(self):
        """Test recording metrics from optimization cycles"""
        # Run a test cycle
        cycle = self.optimization_loop.run_cycle(self.test_inputs)

        # Record metrics
        self.dashboard.record_cycle_metrics(cycle)

        # Verify metrics were recorded
        duration_series = self.dashboard.metric_series[MetricType.DURATION]
        success_series = self.dashboard.metric_series[MetricType.SUCCESS_RATE]

        self.assertIsNotNone(duration_series.get_latest_value())
        self.assertIsNotNone(success_series.get_latest_value())

        print("\nCycle Metrics Recording Test:")
        print(f"  Duration recorded: {duration_series.get_latest_value():.3f}s")
        print(f"  Success rate recorded: {success_series.get_latest_value():.1%}")
        print(f"  Total data points: {len(duration_series.data_points)}")

    def test_alert_creation(self):
        """Test alert creation for threshold violations"""
        # Add a low reliability metric to trigger alert
        reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
        reliability_series.add_point(30.0)  # Below critical threshold

        # Check for alerts
        self.dashboard._check_alerts()

        # Verify alert was created
        self.assertGreater(len(self.dashboard.alerts), 0)

        alert = self.dashboard.alerts[0]
        self.assertEqual(alert.metric_type, MetricType.RELIABILITY)
        self.assertEqual(alert.current_value, 30.0)
        self.assertEqual(alert.severity, "critical")

        print("\nAlert Creation Test:")
        print(f"  Alerts created: {len(self.dashboard.alerts)}")
        print(f"  Alert severity: {alert.severity}")
        print(f"  Alert message: {alert.message}")

    def test_dashboard_overview_view(self):
        """Test dashboard overview view"""
        # Run multiple cycles to generate data
        for i in range(3):
            cycle = self.optimization_loop.run_cycle(self.test_inputs)
            self.dashboard.record_cycle_metrics(cycle)

        # Get overview data
        overview_data = self.dashboard.get_dashboard_data(DashboardView.OVERVIEW)

        # Verify structure
        self.assertIn("timestamp", overview_data)
        self.assertIn("view", overview_data)
        self.assertIn("summary", overview_data)
        self.assertIn("current_metrics", overview_data)
        self.assertIn("trends", overview_data)
        self.assertIn("alerts", overview_data)

        # Verify summary data
        summary = overview_data["summary"]
        self.assertIn("total_cycles", summary)
        self.assertIn("successful_cycles", summary)
        self.assertIn("active_alerts", summary)

        self.assertEqual(summary["total_cycles"], 3)
        self.assertEqual(summary["successful_cycles"], 3)

        print("\nDashboard Overview View Test:")
        print(f"  Total cycles: {summary['total_cycles']}")
        print(f"  Successful cycles: {summary['successful_cycles']}")
        print(f"  Active alerts: {summary['active_alerts']}")
        print(f"  Current metrics: {len(overview_data['current_metrics'])}")
        print(f"  Trends: {len(overview_data['trends'])}")

    def test_dashboard_detailed_view(self):
        """Test dashboard detailed view"""
        # Run a test cycle
        cycle = self.optimization_loop.run_cycle(self.test_inputs)
        self.dashboard.record_cycle_metrics(cycle)

        # Get detailed data
        detailed_data = self.dashboard.get_dashboard_data(DashboardView.DETAILED)

        # Verify structure
        self.assertIn("timestamp", detailed_data)
        self.assertIn("view", detailed_data)
        self.assertIn("metrics", detailed_data)
        self.assertIn("phases", detailed_data)
        self.assertIn("cycles", detailed_data)

        # Verify metrics data
        metrics = detailed_data["metrics"]
        self.assertIn("reliability", metrics)
        self.assertIn("performance", metrics)
        self.assertIn("quality", metrics)

        # Verify phases data
        phases = detailed_data["phases"]
        self.assertIn("create", phases)
        self.assertIn("evaluate", phases)
        self.assertIn("optimize", phases)
        self.assertIn("deploy", phases)

        print("\nDashboard Detailed View Test:")
        print(f"  Metrics tracked: {len(metrics)}")
        print(f"  Phases tracked: {len(phases)}")
        print(f"  Create phase success rate: {phases['create']['success_rate']:.1%}")
        print(f"  Evaluate phase success rate: {phases['evaluate']['success_rate']:.1%}")

    def test_dashboard_historical_view(self):
        """Test dashboard historical view"""
        # Add historical data points
        for i in range(10):
            reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
            reliability_series.add_point(80.0 + i, {"iteration": i})
            time.sleep(0.01)  # Small delay to create time separation

        # Get historical data
        historical_data = self.dashboard.get_dashboard_data(DashboardView.HISTORICAL)

        # Verify structure
        self.assertIn("timestamp", historical_data)
        self.assertIn("view", historical_data)
        self.assertIn("time_ranges", historical_data)
        self.assertIn("metrics", historical_data)

        # Verify metrics data
        metrics = historical_data["metrics"]
        self.assertIn("reliability", metrics)

        reliability_data = metrics["reliability"]
        self.assertIn("data_points", reliability_data)
        self.assertIn("statistics", reliability_data)

        # Verify statistics
        stats = reliability_data["statistics"]
        self.assertIn("min", stats)
        self.assertIn("max", stats)
        self.assertIn("avg", stats)

        self.assertEqual(stats["min"], 80.0)
        self.assertEqual(stats["max"], 89.0)

        print("\nDashboard Historical View Test:")
        print(f"  Data points: {len(reliability_data['data_points'])}")
        print(f"  Min value: {stats['min']}")
        print(f"  Max value: {stats['max']}")
        print(f"  Average: {stats['avg']:.1f}")

    def test_dashboard_comparison_view(self):
        """Test dashboard comparison view"""
        # Add data points over time
        for i in range(20):
            reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
            reliability_series.add_point(75.0 + i, {"iteration": i})
            time.sleep(0.01)

        # Get comparison data
        comparison_data = self.dashboard.get_dashboard_data(DashboardView.COMPARISON)

        # Verify structure
        self.assertIn("timestamp", comparison_data)
        self.assertIn("view", comparison_data)
        self.assertIn("comparisons", comparison_data)

        # Verify comparison data
        comparisons = comparison_data["comparisons"]
        self.assertIn("reliability", comparisons)

        reliability_comparison = comparisons["reliability"]
        self.assertIn("current", reliability_comparison)
        self.assertIn("avg_24h", reliability_comparison)
        self.assertIn("avg_7d", reliability_comparison)
        self.assertIn("change_24h", reliability_comparison)
        self.assertIn("change_7d", reliability_comparison)

        print("\nDashboard Comparison View Test:")
        print(f"  Current reliability: {reliability_comparison['current']:.1f}%")
        print(f"  24h average: {reliability_comparison['avg_24h']:.1f}%")
        print(f"  24h change: {reliability_comparison['change_24h']:+.1f}%")

    def test_dashboard_alerts_view(self):
        """Test dashboard alerts view"""
        # Create some test alerts
        reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
        reliability_series.add_point(30.0)  # Critical alert
        reliability_series.add_point(60.0)  # High alert

        self.dashboard._check_alerts()

        # Get alerts data
        alerts_data = self.dashboard.get_dashboard_data(DashboardView.ALERTS)

        # Verify structure
        self.assertIn("timestamp", alerts_data)
        self.assertIn("view", alerts_data)
        self.assertIn("alerts", alerts_data)

        alerts = alerts_data["alerts"]
        self.assertIn("active", alerts)
        self.assertIn("acknowledged", alerts)
        self.assertIn("summary", alerts)

        summary = alerts["summary"]
        self.assertIn("total", summary)
        self.assertIn("active", summary)
        self.assertIn("acknowledged", summary)
        self.assertIn("by_severity", summary)

        self.assertGreater(summary["total"], 0)
        self.assertGreater(summary["active"], 0)

        print("\nDashboard Alerts View Test:")
        print(f"  Total alerts: {summary['total']}")
        print(f"  Active alerts: {summary['active']}")
        print(f"  Acknowledged alerts: {summary['acknowledged']}")
        print(f"  By severity: {summary['by_severity']}")

    def test_alert_acknowledgment(self):
        """Test alert acknowledgment"""
        # Create a test alert
        reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
        reliability_series.add_point(30.0)
        self.dashboard._check_alerts()

        # Verify alert exists
        self.assertGreater(len(self.dashboard.alerts), 0)
        alert = self.dashboard.alerts[0]
        self.assertFalse(alert.acknowledged)

        # Acknowledge alert
        success = self.dashboard.acknowledge_alert(alert.alert_id)
        self.assertTrue(success)

        # Verify alert is acknowledged
        self.assertTrue(alert.acknowledged)

        print("\nAlert Acknowledgment Test:")
        print(f"  Alert ID: {alert.alert_id}")
        print(f"  Acknowledgment success: {success}")
        print(f"  Alert acknowledged: {alert.acknowledged}")

    def test_alert_cleanup(self):
        """Test alert cleanup"""
        # Create old alerts
        old_alert = Alert(
            alert_id="old_alert",
            metric_type=MetricType.RELIABILITY,
            threshold=50.0,
            current_value=30.0,
            severity="critical",
            message="Old alert",
            timestamp=time.time() - (10 * 24 * 3600),  # 10 days old
        )

        new_alert = Alert(
            alert_id="new_alert",
            metric_type=MetricType.RELIABILITY,
            threshold=50.0,
            current_value=30.0,
            severity="critical",
            message="New alert",
            timestamp=time.time(),  # Current time
        )

        self.dashboard.alerts = [old_alert, new_alert]

        # Clear old alerts (older than 7 days)
        self.dashboard.clear_old_alerts(days=7)

        # Verify only new alert remains
        self.assertEqual(len(self.dashboard.alerts), 1)
        self.assertEqual(self.dashboard.alerts[0].alert_id, "new_alert")

        print("\nAlert Cleanup Test:")
        print("  Alerts before cleanup: 2")
        print(f"  Alerts after cleanup: {len(self.dashboard.alerts)}")
        print(f"  Remaining alert ID: {self.dashboard.alerts[0].alert_id}")

    def test_data_export(self):
        """Test dashboard data export"""
        # Add some test data
        reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
        reliability_series.add_point(85.0, {"test": "data"})

        # Export data
        exported_data = self.dashboard.export_data(format="json")

        # Verify export is valid JSON
        import json

        parsed_data = json.loads(exported_data)

        # Verify structure
        self.assertIn("dashboard_info", parsed_data)
        self.assertIn("metric_series", parsed_data)
        self.assertIn("alerts", parsed_data)

        # Verify metric series data
        metric_series = parsed_data["metric_series"]
        self.assertIn("reliability", metric_series)

        print("\nData Export Test:")
        print("  Export format: JSON")
        print(f"  Export size: {len(exported_data)} characters")
        print(f"  Metric series exported: {len(metric_series)}")
        print(f"  Alerts exported: {len(parsed_data['alerts'])}")

    def test_dashboard_statistics(self):
        """Test dashboard statistics"""
        # Add test data
        for i in range(5):
            reliability_series = self.dashboard.metric_series[MetricType.RELIABILITY]
            reliability_series.add_point(80.0 + i)

        # Get statistics
        stats = self.dashboard.get_statistics()

        # Verify structure
        self.assertIn("total_metrics", stats)
        self.assertIn("total_data_points", stats)
        self.assertIn("total_alerts", stats)
        self.assertIn("active_alerts", stats)
        self.assertIn("connected_to_loop", stats)

        # Verify values
        self.assertEqual(stats["total_metrics"], len(MetricType))
        self.assertGreater(stats["total_data_points"], 0)
        self.assertTrue(stats["connected_to_loop"])

        print("\nDashboard Statistics Test:")
        print(f"  Total metrics: {stats['total_metrics']}")
        print(f"  Total data points: {stats['total_data_points']}")
        print(f"  Total alerts: {stats['total_alerts']}")
        print(f"  Active alerts: {stats['active_alerts']}")
        print(f"  Connected to loop: {stats['connected_to_loop']}")

    def test_global_dashboard_functions(self):
        """Test global dashboard convenience functions"""
        # Test global dashboard instance
        global_dashboard = get_metrics_dashboard()
        self.assertIsInstance(global_dashboard, MetricsDashboard)

        # Test recording metrics
        cycle = self.optimization_loop.run_cycle(self.test_inputs)
        record_optimization_metrics(cycle)

        # Test getting dashboard view
        overview = get_dashboard_view(DashboardView.OVERVIEW)
        self.assertIn("view", overview)
        self.assertEqual(overview["view"], "overview")

        print("\nGlobal Dashboard Functions Test:")
        print(f"  Global dashboard instance: {type(global_dashboard).__name__}")
        print(f"  Overview view retrieved: {overview['view']}")
        print(f"  Summary data available: {'summary' in overview}")


if __name__ == "__main__":
    unittest.main()
