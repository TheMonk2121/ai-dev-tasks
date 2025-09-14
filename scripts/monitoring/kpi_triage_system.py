from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
KPI Triage System
Fast triage for KPI threshold breaches with specific remediation actions.
"""

class KPITriageSystem:
    """Fast triage system for KPI threshold breaches."""

    def __init__(self, config_dir: str = "configs/triage"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.triage_log_file = self.config_dir / "triage_log.jsonl"

    def triage_kpi_breach(
        self, metric_name: str, current_value: float, threshold_value: float, breach_type: str = "below"
    ) -> dict[str, Any]:
        """Triage KPI breach and provide remediation actions."""
        print(f"🚨 KPI TRIAGE: {metric_name}")
        print("=" * 50)
        print(f"📊 Current: {current_value:.3f}")
        print(f"🎯 Threshold: {threshold_value:.3f}")
        print(f"📈 Breach: {breach_type}")

        # Determine triage category
        triage_category = self._categorize_breach(metric_name, breach_type)

        # Get remediation actions
        remediation_actions = self._get_remediation_actions(triage_category, metric_name)

        # Execute triage
        triage_result = {
            "timestamp": datetime.now().isoformat(),
            "metric_name": metric_name,
            "current_value": current_value,
            "threshold_value": threshold_value,
            "breach_type": breach_type,
            "triage_category": triage_category,
            "remediation_actions": remediation_actions,
            "executed_actions": [],
            "status": "in_progress",
        }

        # Execute remediation actions
        for action in remediation_actions:
            action_result = self._execute_remediation_action(action)
            triage_result["executed_actions"].append(action_result)

        # Log triage result
        self._log_triage_result(triage_result)

        # Determine final status
        if all(action["success"] for action in triage_result["executed_actions"]):
            triage_result["status"] = "resolved"
            print("✅ KPI breach triaged successfully")
        else:
            triage_result["status"] = "requires_manual_intervention"
            print("⚠️ KPI breach requires manual intervention")

        return triage_result

    def _categorize_breach(self, metric_name: str, breach_type: str) -> str:
        """Categorize the type of KPI breach."""
        if metric_name in ["oracle_prefilter_rate", "oracle_retrieval_hit_prefilter"]:
            return "retrieval_quality"
        elif metric_name in ["reader_used_gold_rate", "f1_score", "precision", "recall"]:
            return "generation_quality"
        elif metric_name in ["p95_latency", "avg_latency"]:
            return "performance"
        elif metric_name in ["error_rate", "timeout_rate"]:
            return "reliability"
        elif metric_name in ["tool_schema_conformance", "dry_run_usage"]:
            return "governance"
        else:
            return "unknown"

    def _get_remediation_actions(self, triage_category: str, metric_name: str) -> list[dict[str, Any]]:
        """Get specific remediation actions for the triage category."""
        actions = []

        if triage_category == "retrieval_quality":
            if metric_name in ["oracle_prefilter_rate", "oracle_retrieval_hit_prefilter"]:
                actions = [
                    {
                        "action": "check_run_gating",
                        "description": "Verify retrieved contexts span current RUN only",
                        "command": "python3 scripts/verify_real_rag_parity.py --check-run-gating",
                    },
                    {
                        "action": "adjust_rrf_weights",
                        "description": "Recheck RRF weights for dense/sparse fusion",
                        "command": "python3 scripts/adjust_rrf_weights.py --increase-dense-weight",
                    },
                    {
                        "action": "disable_hyde_prf",
                        "description": "Ensure HyDE/PRF is off-by-default",
                        "command": "python3 scripts/disable_hyde_prf.py",
                    },
                ]

        elif triage_category == "generation_quality":
            if metric_name in ["reader_used_gold_rate"]:
                actions = [
                    {
                        "action": "refresh_few_shots",
                        "description": "Refresh deterministic few-shots with leakage guard",
                        "command": "python3 scripts/refresh_few_shots.py --deterministic --leakage-guard",
                    },
                    {
                        "action": "disable_cot",
                        "description": "Keep CoT off until stable",
                        "command": "python3 scripts/disable_cot.py",
                    },
                ]
            elif metric_name in ["f1_score", "precision", "recall"]:
                actions = [
                    {
                        "action": "adjust_evidence_selector",
                        "description": "Raise evidence budget and use novelty-first",
                        "command": "python3 scripts/adjust_evidence_selector.py --raise-budget --novelty-first",
                    },
                    {
                        "action": "adjust_per_doc_cap",
                        "description": "Adjust per-document cap for evidence selection",
                        "command": "python3 scripts/adjust_per_doc_cap.py --increase-cap",
                    },
                ]

        elif triage_category == "performance":
            if metric_name in ["p95_latency", "avg_latency"]:
                actions = [
                    {
                        "action": "prewarm_reranker",
                        "description": "Prewarm reranker model to prevent cold starts",
                        "command": "python3 scripts/prewarm_reranker.py",
                    },
                    {
                        "action": "cap_workers",
                        "description": "Cap workers to 2-3 to prevent resource contention",
                        "command": "python3 scripts/cap_workers.py --max-workers 3",
                    },
                    {
                        "action": "verify_indexes",
                        "description": "Verify vector indexes are being used",
                        "command": "python3 scripts/verify_indexes.py",
                    },
                ]

        elif triage_category == "reliability":
            if metric_name in ["error_rate", "timeout_rate"]:
                actions = [
                    {
                        "action": "check_model_availability",
                        "description": "Check model availability and health",
                        "command": "python3 scripts/check_model_availability.py",
                    },
                    {
                        "action": "restart_services",
                        "description": "Restart critical services if needed",
                        "command": "python3 scripts/restart_services.py",
                    },
                ]

        elif triage_category == "governance":
            if metric_name in ["tool_schema_conformance", "dry_run_usage"]:
                actions = [
                    {
                        "action": "validate_tool_schemas",
                        "description": "Validate tool schemas and compliance",
                        "command": "python3 scripts/validate_tool_schemas.py",
                    },
                    {
                        "action": "enforce_dry_run",
                        "description": "Enforce dry-run for all mutating tools",
                        "command": "python3 scripts/enforce_dry_run.py",
                    },
                ]

        return actions

    def _execute_remediation_action(self, action: dict[str, Any]) -> dict[str, Any]:
        """Execute a remediation action."""
        print(f"🔧 Executing: {action['action']}")
        print(f"📝 Description: {action['description']}")

        action_result = {
            "action": action["action"],
            "description": action["description"],
            "command": action["command"],
            "success": False,
            "output": "",
            "error": "",
            "timestamp": datetime.now().isoformat(),
        }

        try:
            # Execute command
            result = subprocess.run(
                action["command"], shell=True, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            action_result["output"] = result.stdout
            action_result["error"] = result.stderr
            action_result["success"] = result.returncode == 0

            if action_result["success"]:
                print(f"✅ {action['action']} completed successfully")
            else:
                print(f"❌ {action['action']} failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            action_result["error"] = "Command timed out after 5 minutes"
            print(f"⏰ {action['action']} timed out")

        except Exception as e:
            action_result["error"] = str(e)
            print(f"❌ {action['action']} failed with exception: {e}")

        return action_result

    def _log_triage_result(self, triage_result: dict[str, Any]):
        """Log triage result to triage log."""
        log_entry = {"timestamp": datetime.now().isoformat(), "type": "kpi_triage", "data": triage_result}

        with open(self.triage_log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_triage_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent triage history."""
        triage_history = []

        if not self.triage_log_file.exists():
            return triage_history

        with open(self.triage_log_file) as f:
            lines = f.readlines()

        # Get recent entries
        recent_lines = lines[-limit:] if len(lines) > limit else lines

        for line in recent_lines:
            try:
                log_entry = json.loads(line.strip())
                if log_entry.get("type") == "kpi_triage":
                    triage_history.append(log_entry["data"])
            except json.JSONDecodeError:
                continue

        return triage_history

    def get_kpi_status(self) -> dict[str, Any]:
        """Get current KPI status and thresholds."""
        # This would integrate with your actual KPI monitoring system
        # For now, return a placeholder structure

        kpi_status = {
            "timestamp": datetime.now().isoformat(),
            "kpis": {
                "oracle_prefilter_rate": {"current": 0.87, "threshold": 0.85, "status": "healthy"},
                "reader_used_gold_rate": {"current": 0.72, "threshold": 0.70, "status": "healthy"},
                "f1_score": {"current": 0.24, "threshold": 0.22, "status": "healthy"},
                "p95_latency": {"current": 1.2, "threshold": 1.15, "status": "warning"},
                "tool_schema_conformance": {"current": 0.96, "threshold": 0.95, "status": "healthy"},
            },
            "overall_status": "healthy",
        }

        return kpi_status

def main():
    """Main entry point for KPI triage system."""

    parser = argparse.ArgumentParser(description="KPI triage system")
    parser.add_argument("--action", choices=["triage", "history", "status"], required=True)
    parser.add_argument("--metric", help="Metric name for triage action")
    parser.add_argument("--current-value", type=float, help="Current metric value")
    parser.add_argument("--threshold", type=float, help="Threshold value")
    parser.add_argument("--breach-type", choices=["below", "above"], default="below")
    parser.add_argument("--limit", type=int, default=10, help="Limit for history action")

    args = parser.parse_args()

    triage_system = KPITriageSystem()

    if args.action == "triage":
        if not all([args.metric, args.current_value is not None, args.threshold is not None]):
            print("❌ --metric, --current-value, and --threshold required for triage action")
            sys.exit(1)

        result = triage_system.triage_kpi_breach(
            metric_name=args.metric,
            current_value=args.current_value,
            threshold_value=args.threshold,
            breach_type=args.breach_type,
        )

        print(f"📊 Triage result: {result['status']}")

    elif args.action == "history":
        history = triage_system.get_triage_history(limit=args.limit)
        print(f"📋 Recent Triage History (last {len(history)} entries):")
        for entry in history:
            status_emoji = (
                "✅"
                if entry["status"] == "resolved"
                else "⚠️" if entry["status"] == "requires_manual_intervention" else "🔄"
            )
            print(f"{status_emoji} {entry['metric_name']} - {entry['timestamp']} ({entry['status']})")

    elif args.action == "status":
        status = triage_system.get_kpi_status()
        print("📊 Current KPI Status:")
        for metric, info in status["kpis"].items():
            status_emoji = "✅" if info["status"] == "healthy" else "⚠️" if info["status"] == "warning" else "❌"
            print(f"{status_emoji} {metric}: {info['current']:.3f} (threshold: {info['threshold']:.3f})")

if __name__ == "__main__":
    main()
