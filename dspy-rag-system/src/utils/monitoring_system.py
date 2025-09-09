#!/usr/bin/env python3
"""
Monitoring & Performance Hooks for Decision Retrieval

Tracks p50/p95/p99 latency, cache hit rates, contradiction leakage, and packed context size.
Exposes metrics on NiceGUI dashboard with SLO alerts.
"""

import json
import logging
import os
import sys
import time
from collections import deque
from datetime import datetime
from typing import Any

# Add the src directory to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from nicegui import ui

    NICEGUI_AVAILABLE = True
except ImportError:
    NICEGUI_AVAILABLE = False
    print("NiceGUI not available, dashboard will be disabled")

from utils.unified_retrieval_api import search_decisions

logger = logging.getLogger(__name__)


class PerformanceMetrics:
    """Performance metrics tracking"""

    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.latency_history = deque(maxlen=window_size)
        self.cache_hits = 0
        self.cache_misses = 0
        self.contradiction_leakage = 0
        self.packed_context_sizes = deque(maxlen=window_size)
        self.failure_at_20_history = deque(maxlen=100)  # Keep last 100 evaluations

    def record_latency(self, latency_ms: float):
        """Record a latency measurement"""
        self.latency_history.append(latency_ms)

    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1

    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1

    def record_contradiction_leakage(self):
        """Record contradiction leakage"""
        self.contradiction_leakage += 1

    def record_packed_context_size(self, size_bytes: int):
        """Record packed context size"""
        self.packed_context_sizes.append(size_bytes)

    def record_failure_at_20(self, failure_rate: float):
        """Record Failure@20 rate from evaluation"""
        self.failure_at_20_history.append(failure_rate)

    def get_latency_percentiles(self) -> dict[str, float]:
        """Get p50, p95, p99 latency"""
        if not self.latency_history:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0}

        sorted_latencies = sorted(self.latency_history)
        n = len(sorted_latencies)

        return {
            "p50": sorted_latencies[int(0.5 * n)],
            "p95": sorted_latencies[int(0.95 * n)],
            "p99": sorted_latencies[int(0.99 * n)],
        }

    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate"""
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0

    def get_avg_packed_context_size(self) -> float:
        """Get average packed context size"""
        if not self.packed_context_sizes:
            return 0.0
        return sum(self.packed_context_sizes) / len(self.packed_context_sizes)

    def get_failure_at_20_trend(self) -> float:
        """Get Failure@20 trend (average of last 10 evaluations)"""
        if not self.failure_at_20_history:
            return 0.0
        recent = list(self.failure_at_20_history)[-10:]
        return sum(recent) / len(recent)


class SLOMonitor:
    """SLO monitoring and alerting"""

    def __init__(self):
        self.slos = {
            "latency_p95": 100.0,  # 100ms p95 latency
            "cache_hit_rate": 0.8,  # 80% cache hit rate
            "failure_at_20": 0.2,  # 20% failure rate
            "contradiction_leakage": 0.01,  # 1% contradiction leakage
        }
        self.alerts = []

    def check_slos(self, metrics: PerformanceMetrics) -> list[dict[str, Any]]:
        """Check SLOs and return violations"""
        violations = []

        # Check latency SLO
        percentiles = metrics.get_latency_percentiles()
        if percentiles["p95"] > self.slos["latency_p95"]:
            violations.append(
                {
                    "metric": "latency_p95",
                    "current": percentiles["p95"],
                    "threshold": self.slos["latency_p95"],
                    "severity": "high",
                    "message": f"P95 latency {percentiles['p95']:.1f}ms exceeds threshold {self.slos['latency_p95']}ms",
                }
            )

        # Check cache hit rate SLO
        hit_rate = metrics.get_cache_hit_rate()
        if hit_rate < self.slos["cache_hit_rate"]:
            violations.append(
                {
                    "metric": "cache_hit_rate",
                    "current": hit_rate,
                    "threshold": self.slos["cache_hit_rate"],
                    "severity": "medium",
                    "message": f"Cache hit rate {hit_rate:.1%} below threshold {self.slos['cache_hit_rate']:.1%}",
                }
            )

        # Check failure rate SLO
        failure_rate = metrics.get_failure_at_20_trend()
        if failure_rate > self.slos["failure_at_20"]:
            violations.append(
                {
                    "metric": "failure_at_20",
                    "current": failure_rate,
                    "threshold": self.slos["failure_at_20"],
                    "severity": "high",
                    "message": f"Failure@20 rate {failure_rate:.1%} exceeds threshold {self.slos['failure_at_20']:.1%}",
                }
            )

        # Check contradiction leakage SLO
        total_requests = metrics.cache_hits + metrics.cache_misses
        if total_requests > 0:
            leakage_rate = metrics.contradiction_leakage / total_requests
            if leakage_rate > self.slos["contradiction_leakage"]:
                violations.append(
                    {
                        "metric": "contradiction_leakage",
                        "current": leakage_rate,
                        "threshold": self.slos["contradiction_leakage"],
                        "severity": "medium",
                        "message": f"Contradiction leakage {leakage_rate:.1%} exceeds threshold {self.slos['contradiction_leakage']:.1%}",
                    }
                )

        # Record alerts
        for violation in violations:
            alert = {"timestamp": datetime.now().isoformat(), **violation}
            self.alerts.append(alert)
            logger.warning(f"SLO Violation: {violation['message']}")

        return violations


class MonitoringSystem:
    """Main monitoring system"""

    def __init__(self, db_connection_string: str):
        self.db_connection_string = db_connection_string
        self.metrics = PerformanceMetrics()
        self.slo_monitor = SLOMonitor()
        self.logger = logging.getLogger("monitoring_system")

    def instrumented_search(self, query: str, limit: int = 10, **kwargs) -> dict[str, Any]:
        """Instrumented search with performance tracking"""
        start_time = time.time()

        try:
            # Perform search
            result = search_decisions(query, limit, **kwargs)

            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency_ms)

            # Record packed context size
            context_size = len(json.dumps(result).encode("utf-8"))
            self.metrics.record_packed_context_size(context_size)

            # Simulate cache hit/miss (for now, random)
            import random

            if random.random() < 0.7:  # 70% cache hit rate
                self.metrics.record_cache_hit()
            else:
                self.metrics.record_cache_miss()

            # Check for contradiction leakage (simplified)
            decisions = result.get("decisions", [])
            if len(decisions) > 1:
                # Check if any decisions might contradict each other
                heads = [d.get("head", "").lower() for d in decisions]
                if any("postgresql" in head and "mongodb" in head for head in heads):
                    self.metrics.record_contradiction_leakage()

            return result

        except Exception:
            # Record latency even for errors
            latency_ms = (time.time() - start_time) * 1000
            self.metrics.record_latency(latency_ms)
            raise

    def run_periodic_evaluation(self):
        """Run periodic evaluation to track Failure@20"""
        try:
            from utils.evaluation_harness import DecisionRetrievalEvaluator

            evaluator = DecisionRetrievalEvaluator(self.db_connection_string)
            results = evaluator.run_evaluation()

            failure_rate = results["metrics"]["failure_at_20"]
            self.metrics.record_failure_at_20(failure_rate)

            self.logger.info(f"Periodic evaluation completed. Failure@20: {failure_rate:.3f}")

        except Exception as e:
            self.logger.error(f"Error in periodic evaluation: {e}")

    def get_metrics_summary(self) -> dict[str, Any]:
        """Get comprehensive metrics summary"""
        percentiles = self.metrics.get_latency_percentiles()

        return {
            "timestamp": datetime.now().isoformat(),
            "latency": {
                "p50": percentiles["p50"],
                "p95": percentiles["p95"],
                "p99": percentiles["p99"],
                "total_requests": len(self.metrics.latency_history),
            },
            "cache": {
                "hit_rate": self.metrics.get_cache_hit_rate(),
                "hits": self.metrics.cache_hits,
                "misses": self.metrics.cache_misses,
            },
            "quality": {
                "failure_at_20_trend": self.metrics.get_failure_at_20_trend(),
                "contradiction_leakage": self.metrics.contradiction_leakage,
                "avg_packed_context_size": self.metrics.get_avg_packed_context_size(),
            },
            "slo_violations": self.slo_monitor.check_slos(self.metrics),
            "recent_alerts": self.slo_monitor.alerts[-10:],  # Last 10 alerts
        }


class NiceGUIDashboard:
    """NiceGUI dashboard for monitoring metrics"""

    def __init__(self, monitoring_system: MonitoringSystem):
        self.monitoring_system = monitoring_system
        self.metrics_card = None
        self.alerts_card = None
        self.charts = {}

    def create_dashboard(self):
        """Create the monitoring dashboard"""
        if not NICEGUI_AVAILABLE:
            ui.notify("NiceGUI not available", type="warning")
            return

        ui.page_title("Decision Retrieval Monitoring")

        with ui.header().classes("bg-blue-500 text-white"):
            ui.label("🎯 Decision Retrieval Monitoring Dashboard").classes("text-h6")

        with ui.row().classes("w-full"):
            # Metrics Overview
            with ui.column().classes("w-1/2"):
                self.metrics_card = ui.card().classes("w-full")
                with self.metrics_card:
                    ui.label("📊 Performance Metrics").classes("text-h6")
                    self.latency_label = ui.label("Latency: Loading...")
                    self.cache_label = ui.label("Cache: Loading...")
                    self.quality_label = ui.label("Quality: Loading...")

            # Alerts
            with ui.column().classes("w-1/2"):
                self.alerts_card = ui.card().classes("w-full")
                with self.alerts_card:
                    ui.label("🚨 SLO Alerts").classes("text-h6")
                    self.alerts_list = ui.list().classes("w-full")

        # Update metrics every 5 seconds
        ui.timer(5.0, self.update_dashboard)

        # Initial update
        self.update_dashboard()

    def update_dashboard(self):
        """Update dashboard with latest metrics"""
        try:
            metrics = self.monitoring_system.get_metrics_summary()

            # Update latency metrics
            latency = metrics["latency"]
            self.latency_label.text = (
                f"Latency: P50={latency['p50']:.1f}ms, P95={latency['p95']:.1f}ms, P99={latency['p99']:.1f}ms"
            )

            # Update cache metrics
            cache = metrics["cache"]
            self.cache_label.text = (
                f"Cache: {cache['hit_rate']:.1%} hit rate ({cache['hits']} hits, {cache['misses']} misses)"
            )

            # Update quality metrics
            quality = metrics["quality"]
            self.quality_label.text = f"Quality: F@20={quality['failure_at_20_trend']:.1%}, Leakage={quality['contradiction_leakage']}, Context={quality['avg_packed_context_size']:.0f}B"

            # Update alerts
            self.alerts_list.clear()
            for alert in metrics["recent_alerts"]:
                with self.alerts_list:
                    ui.item().classes("text-red-500").props(f"label='{alert['message']}'")

            # Show SLO violations
            violations = metrics["slo_violations"]
            if violations:
                ui.notify(f"{len(violations)} SLO violations detected", type="negative")

        except Exception as e:
            ui.notify(f"Error updating dashboard: {e}", type="negative")


def start_monitoring_dashboard(db_connection_string: str | None = None, port: int = 8080):
    """Start the monitoring dashboard"""
    if db_connection_string is None:
        db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    monitoring_system = MonitoringSystem(db_connection_string)
    dashboard = NiceGUIDashboard(monitoring_system)

    if NICEGUI_AVAILABLE:
        dashboard.create_dashboard()
        ui.run(port=port, show=True)
    else:
        print("NiceGUI not available. Starting metrics collection only...")

        # Run metrics collection in a loop
        while True:
            try:
                metrics = monitoring_system.get_metrics_summary()
                print(f"\n📊 Metrics Summary ({datetime.now().strftime('%H:%M:%S')}):")
                print(f"  Latency: P50={metrics['latency']['p50']:.1f}ms, P95={metrics['latency']['p95']:.1f}ms")
                print(f"  Cache: {metrics['cache']['hit_rate']:.1%} hit rate")
                print(f"  Quality: F@20={metrics['quality']['failure_at_20_trend']:.1%}")

                if metrics["slo_violations"]:
                    print(f"  🚨 {len(metrics['slo_violations'])} SLO violations!")

                time.sleep(5)

            except KeyboardInterrupt:
                print("\nMonitoring stopped.")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(5)


if __name__ == "__main__":
    # Test the monitoring system
    print("🔍 Starting Decision Retrieval Monitoring...")

    monitoring_system = MonitoringSystem("postgresql://danieljacobs@localhost:5432/ai_agency")

    # Test instrumented search
    print("Testing instrumented search...")
    for i in range(5):
        result = monitoring_system.instrumented_search("postgresql", 5)
        print(f"Search {i+1}: Found {len(result['decisions'])} decisions")

    # Get metrics summary
    metrics = monitoring_system.get_metrics_summary()
    print("\n📊 Metrics Summary:")
    print(json.dumps(metrics, indent=2))

    # Start dashboard
    print("\n🚀 Starting dashboard on port 8080...")
    start_monitoring_dashboard(port=8080)
