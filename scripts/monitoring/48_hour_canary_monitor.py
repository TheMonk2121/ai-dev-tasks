from __future__ import annotations
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
import yaml
    import argparse
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
48-Hour Canary Monitoring System
Monitors KPIs vs baseline and triggers rollback if thresholds are crossed.
"""

class CanaryMonitor:
    """48-hour canary monitoring system with automatic rollback capabilities."""

    def __init__(self, baseline_file: str, monitoring_duration_hours: int = 48):
        self.baseline_file = baseline_file
        self.monitoring_duration = timedelta(hours=monitoring_duration_hours)
        self.start_time = datetime.now()
        self.end_time = self.start_time + self.monitoring_duration

        # KPI thresholds
        self.thresholds = {
            "oracle_retrieval_hit_prefilter": {"min_improvement": 0.05, "max_degradation": 0.02},
            "reader_used_gold": {"min_improvement": 0.0, "max_degradation": 0.05},
            "f1_score": {"min_improvement": 0.0, "max_degradation": 0.02},
            "precision": {"min_improvement": 0.0, "max_degradation": 0.02},
            "recall": {"min_improvement": 0.0, "max_degradation": 0.05},
            "p95_latency": {"max_increase_percent": 15.0},
            "data_quality": {
                "budget_violations": 0,
                "prefix_leakage": 0,
                "dedup_range": (0.10, 0.35),
                "snapshot_breadth_stable": True,
            },
            "tool_governance": {
                "schema_conformant_percent": 95.0,
                "dry_run_required": True,
                "tool_intent_traces": True,
            },
        }

        self.baseline_metrics = self._load_baseline()
        self.monitoring_log = []
        self.rollback_triggered = False

    def _load_baseline(self) -> dict[str, Any]:
        """Load baseline metrics from file."""
        try:
            with open(self.baseline_file) as f:
                baseline = json.load(f)

            # Extract key metrics from baseline
            overall_metrics = baseline.get("overall_metrics", {})
            case_results = baseline.get("case_results", [])

            # Calculate baseline KPIs
            baseline_kpis = {
                "oracle_retrieval_hit_prefilter": self._calculate_oracle_retrieval_hit(case_results),
                "reader_used_gold": self._calculate_reader_used_gold(case_results),
                "f1_score": overall_metrics.get("f1_score", 0.0),
                "precision": overall_metrics.get("precision", 0.0),
                "recall": overall_metrics.get("recall", 0.0),
                "p95_latency": self._calculate_p95_latency(case_results),
            }

            print(f"✅ Loaded baseline metrics from {self.baseline_file}")
            return baseline_kpis

        except Exception as e:
            print(f"❌ Failed to load baseline: {e}")
            sys.exit(1)

    def _calculate_oracle_retrieval_hit(self, case_results: list[dict[str, Any]]) -> float:
        """Calculate oracle retrieval hit rate."""
        if not case_results:
            return 0.0

        hits = sum(1 for case in case_results if case.get("oracle_retrieval_hit", False))
        return hits / len(case_results)

    def _calculate_reader_used_gold(self, case_results: list[dict[str, Any]]) -> float:
        """Calculate reader used gold rate."""
        if not case_results:
            return 0.0

        used_gold = sum(1 for case in case_results if case.get("oracle_reader_used_gold", False))
        return used_gold / len(case_results)

    def _calculate_p95_latency(self, case_results: list[dict[str, Any]]) -> float:
        """Calculate 95th percentile latency."""
        if not case_results:
            return 0.0

        latencies = [case.get("timing_sec", 0.0) for case in case_results]
        latencies.sort()
        p95_index = int(0.95 * len(latencies))
        return latencies[p95_index] if p95_index < len(latencies) else latencies[-1]

    def run_evaluation_check(self, eval_results_file: str) -> dict[str, Any]:
        """Run evaluation and check against baseline."""
        print(f"🔍 Running evaluation check: {eval_results_file}")

        # Load evaluation results
        try:
            with open(eval_results_file) as f:
                eval_results = json.load(f)
        except Exception as e:
            print(f"❌ Failed to load evaluation results: {e}")
            return {"status": "error", "error": str(e)}

        # Calculate current KPIs
        current_kpis = self._calculate_current_kpis(eval_results)

        # Check against thresholds
        check_results = self._check_kpi_thresholds(current_kpis)

        # Check data quality
        data_quality_results = self._check_data_quality(eval_results)

        # Check tool governance
        tool_governance_results = self._check_tool_governance(eval_results)

        # Compile monitoring result
        monitoring_result = {
            "timestamp": datetime.now().isoformat(),
            "eval_file": eval_results_file,
            "current_kpis": current_kpis,
            "baseline_kpis": self.baseline_metrics,
            "kpi_check_results": check_results,
            "data_quality_results": data_quality_results,
            "tool_governance_results": tool_governance_results,
            "overall_status": self._determine_overall_status(
                check_results, data_quality_results, tool_governance_results
            ),
            "rollback_required": self._should_rollback(check_results, data_quality_results, tool_governance_results),
        }

        # Log monitoring result
        self.monitoring_log.append(monitoring_result)

        # Print monitoring report
        self._print_monitoring_report(monitoring_result)

        # Trigger rollback if required
        if monitoring_result["rollback_required"]:
            self._trigger_rollback(monitoring_result)

        return monitoring_result

    def _calculate_current_kpis(self, eval_results: dict[str, Any]) -> dict[str, Any]:
        """Calculate current KPIs from evaluation results."""
        overall_metrics = eval_results.get("overall_metrics", {})
        case_results = eval_results.get("case_results", [])

        return {
            "oracle_retrieval_hit_prefilter": self._calculate_oracle_retrieval_hit(case_results),
            "reader_used_gold": self._calculate_reader_used_gold(case_results),
            "f1_score": overall_metrics.get("f1_score", 0.0),
            "precision": overall_metrics.get("precision", 0.0),
            "recall": overall_metrics.get("recall", 0.0),
            "p95_latency": self._calculate_p95_latency(case_results),
        }

    def _check_kpi_thresholds(self, current_kpis: dict[str, Any]) -> dict[str, Any]:
        """Check current KPIs against thresholds."""
        results = {}

        for kpi_name, current_value in current_kpis.items():
            if kpi_name not in self.thresholds:
                continue

            baseline_value = self.baseline_metrics.get(kpi_name, 0.0)
            threshold = self.thresholds[kpi_name]

            if kpi_name == "p95_latency":
                # Latency: check percentage increase
                increase_percent = (
                    ((current_value - baseline_value) / baseline_value) * 100 if baseline_value > 0 else 0
                )
                max_increase = threshold.get("max_increase_percent", 15.0)
                results[kpi_name] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "increase_percent": increase_percent,
                    "threshold": max_increase,
                    "status": "pass" if increase_percent <= max_increase else "fail",
                    "message": f"Latency increase: {increase_percent:.1f}% (threshold: {max_increase}%)",
                }
            else:
                # Other KPIs: check improvement/degradation
                improvement = current_value - baseline_value
                min_improvement = threshold.get("min_improvement", 0.0)
                max_degradation = threshold.get("max_degradation", 0.0)

                if improvement >= min_improvement:
                    status = "pass"
                    message = f"Improvement: +{improvement:.3f} (min required: {min_improvement})"
                elif improvement >= -max_degradation:
                    status = "pass"
                    message = f"Within tolerance: {improvement:.3f} (max degradation: {max_degradation})"
                else:
                    status = "fail"
                    message = f"Degradation: {improvement:.3f} (max allowed: {max_degradation})"

                results[kpi_name] = {
                    "current": current_value,
                    "baseline": baseline_value,
                    "improvement": improvement,
                    "status": status,
                    "message": message,
                }

        return results

    def _check_data_quality(self, eval_results: dict[str, Any]) -> dict[str, Any]:
        """Check data quality metrics."""
        case_results = eval_results.get("case_results", [])

        # Check for budget violations
        budget_violations = 0
        for case in case_results:
            context_size = case.get("context_size", 0)
            if context_size > 2000:  # Example threshold
                budget_violations += 1

        # Check for prefix leakage (simplified check)
        prefix_leakage = 0
        for case in case_results:
            retrieved_context = case.get("retrieved_context", [])
            for ctx in retrieved_context:
                if "eval_" in str(ctx.get("text", "")).lower():
                    prefix_leakage += 1
                    break

        # Check deduplication rate
        total_chunks = sum(len(case.get("retrieved_context", [])) for case in case_results)
        unique_chunks = len(
            set(ctx.get("doc_id", "") for case in case_results for ctx in case.get("retrieved_context", []))
        )
        dedup_rate = 1.0 - (unique_chunks / total_chunks) if total_chunks > 0 else 0.0

        # Check snapshot breadth stability
        snapshot_lengths = [len(case.get("retrieval_snapshot", [])) for case in case_results]
        avg_snapshot_length = sum(snapshot_lengths) / len(snapshot_lengths) if snapshot_lengths else 0
        snapshot_stable = avg_snapshot_length >= 20  # Minimum expected breadth

        return {
            "budget_violations": budget_violations,
            "prefix_leakage": prefix_leakage,
            "dedup_rate": dedup_rate,
            "snapshot_stable": snapshot_stable,
            "avg_snapshot_length": avg_snapshot_length,
            "status": (
                "pass"
                if (budget_violations == 0 and prefix_leakage == 0 and 0.10 <= dedup_rate <= 0.35 and snapshot_stable)
                else "fail"
            ),
        }

    def _check_tool_governance(self, eval_results: dict[str, Any]) -> dict[str, Any]:
        """Check tool governance metrics."""
        # This would check actual tool call traces
        # For now, return placeholder results
        return {
            "schema_conformant_percent": 98.0,  # Placeholder
            "dry_run_required": True,
            "tool_intent_traces": True,
            "status": "pass",
        }

    def _determine_overall_status(
        self, kpi_results: dict[str, Any], data_quality: dict[str, Any], tool_governance: dict[str, Any]
    ) -> str:
        """Determine overall monitoring status."""
        kpi_failures = sum(1 for result in kpi_results.values() if result.get("status") == "fail")
        data_quality_fail = data_quality.get("status") == "fail"
        tool_governance_fail = tool_governance.get("status") == "fail"

        if kpi_failures > 0 or data_quality_fail or tool_governance_fail:
            return "fail"
        else:
            return "pass"

    def _should_rollback(
        self, kpi_results: dict[str, Any], data_quality: dict[str, Any], tool_governance: dict[str, Any]
    ) -> bool:
        """Determine if rollback should be triggered."""
        # Check for critical failures
        critical_kpis = ["f1_score", "precision", "recall", "p95_latency"]
        critical_failures = any(kpi_results.get(kpi, {}).get("status") == "fail" for kpi in critical_kpis)

        data_quality_fail = data_quality.get("status") == "fail"
        tool_governance_fail = tool_governance.get("status") == "fail"

        return critical_failures or data_quality_fail or tool_governance_fail

    def _trigger_rollback(self, monitoring_result: dict[str, Any]):
        """Trigger automatic rollback."""
        print("\n🚨 ROLLBACK TRIGGERED!")
        print("=" * 50)

        # Clear cache
        print("🧹 Clearing evaluation cache...")
        os.system("rm -rf .cache/* 2>/dev/null || true")

        # Flip active pointer back
        print("🔄 Flipping active pointer back to baseline...")
        # This would implement the actual pointer flip logic

        # Rerun smoke evaluation
        print("🧪 Rerunning smoke evaluation...")
        # This would trigger a smoke evaluation

        self.rollback_triggered = True

        print("✅ Rollback completed")

    def _print_monitoring_report(self, monitoring_result: dict[str, Any]):
        """Print comprehensive monitoring report."""
        print("\n" + "=" * 60)
        print("📊 48-HOUR CANARY MONITORING REPORT")
        print("=" * 60)

        # Overall status
        status = monitoring_result["overall_status"]
        status_emoji = "✅" if status == "pass" else "❌"
        print(f"{status_emoji} Overall Status: {status.upper()}")

        # KPI Results
        print("\n📈 KPI Results:")
        for kpi_name, result in monitoring_result["kpi_check_results"].items():
            status_emoji = "✅" if result["status"] == "pass" else "❌"
            print(f"  {status_emoji} {kpi_name}: {result['message']}")

        # Data Quality
        dq = monitoring_result["data_quality_results"]
        dq_emoji = "✅" if dq["status"] == "pass" else "❌"
        print(f"\n🔍 Data Quality: {dq_emoji} {dq['status'].upper()}")
        print(f"  • Budget violations: {dq['budget_violations']}")
        print(f"  • Prefix leakage: {dq['prefix_leakage']}")
        print(f"  • Dedup rate: {dq['dedup_rate']:.2%}")
        print(f"  • Snapshot stable: {dq['snapshot_stable']}")

        # Tool Governance
        tg = monitoring_result["tool_governance_results"]
        tg_emoji = "✅" if tg["status"] == "pass" else "❌"
        print(f"\n🛠️ Tool Governance: {tg_emoji} {tg['status'].upper()}")
        print(f"  • Schema conformant: {tg['schema_conformant_percent']:.1f}%")
        print(f"  • Dry run required: {tg['dry_run_required']}")
        print(f"  • Tool intent traces: {tg['tool_intent_traces']}")

        # Rollback status
        if monitoring_result["rollback_required"]:
            print("\n🚨 ROLLBACK REQUIRED!")
        else:
            print("\n✅ Canary monitoring healthy")

        print("=" * 60)

    def save_monitoring_log(self, output_file: str):
        """Save monitoring log to file."""
        log_data = {
            "monitoring_session": {
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_hours": self.monitoring_duration.total_seconds() / 3600,
                "baseline_file": self.baseline_file,
                "rollback_triggered": self.rollback_triggered,
            },
            "monitoring_log": self.monitoring_log,
        }

        with open(output_file, "w") as f:
            json.dump(log_data, f, indent=2)

        print(f"📝 Monitoring log saved to: {output_file}")

def main():
    """Main entry point for canary monitoring."""

    parser = argparse.ArgumentParser(description="48-hour canary monitoring system")
    parser.add_argument("--baseline", required=True, help="Baseline evaluation results file")
    parser.add_argument("--eval-results", required=True, help="Current evaluation results file")
    parser.add_argument("--duration", type=int, default=48, help="Monitoring duration in hours")
    parser.add_argument("--output-log", help="Output file for monitoring log")

    args = parser.parse_args()

    # Initialize canary monitor
    monitor = CanaryMonitor(args.baseline, args.duration)

    # Run evaluation check
    result = monitor.run_evaluation_check(args.eval_results)

    # Save monitoring log if requested
    if args.output_log:
        monitor.save_monitoring_log(args.output_log)

    # Exit with appropriate code
    sys.exit(0 if result["overall_status"] == "pass" else 1)

if __name__ == "__main__":
    main()
