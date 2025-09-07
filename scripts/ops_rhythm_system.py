#!/usr/bin/env python3
"""
Ops Rhythm System
Nightly smoke, weekly full eval, few-shot refresh with automated triage.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class OpsRhythmSystem:
    """Manages operational rhythm for production system."""

    def __init__(self, config_dir: str = "configs/ops_rhythm"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.rhythm_log_file = self.config_dir / "rhythm_log.jsonl"

    def run_nightly_smoke(self) -> Dict[str, Any]:
        """Run nightly smoke evaluation with mixed test set."""
        print("🌙 NIGHTLY SMOKE EVALUATION")
        print("="*50)
        
        smoke_result = {
            "type": "nightly_smoke",
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "tests": {},
            "overall_status": "unknown"
        }
        
        # Define smoke test categories
        smoke_tests = {
            "ops_health": {
                "description": "Operations and health checks",
                "command": "python3 scripts/health_gated_evaluation.py"
            },
            "db_workflows": {
                "description": "Database workflow validation",
                "command": "python3 scripts/validate_db_workflows.py"
            },
            "rag_qa": {
                "description": "RAG QA functionality",
                "command": "python3 scripts/ragchecker_official_evaluation.py --use-bedrock --smoke-mode"
            },
            "meta_ops": {
                "description": "Meta-operations validation",
                "command": "python3 scripts/validate_meta_ops.py"
            },
            "negatives": {
                "description": "Negative test cases",
                "command": "python3 scripts/run_negative_tests.py"
            }
        }
        
        # Run each smoke test
        for test_name, test_config in smoke_tests.items():
            print(f"🧪 Running {test_name}: {test_config['description']}")
            
            test_result = self._run_smoke_test(test_name, test_config)
            smoke_result["tests"][test_name] = test_result
            
            if not test_result["passed"]:
                print(f"❌ {test_name} failed: {test_result['error']}")
            else:
                print(f"✅ {test_name} passed")
        
        # Determine overall status
        all_passed = all(test["passed"] for test in smoke_result["tests"].values())
        smoke_result["overall_status"] = "passed" if all_passed else "failed"
        smoke_result["status"] = "completed"
        
        # Log result
        self._log_rhythm_result(smoke_result)
        
        if all_passed:
            print("✅ Nightly smoke evaluation passed")
        else:
            print("❌ Nightly smoke evaluation failed")
            # Trigger alerting
            self._trigger_smoke_alert(smoke_result)
        
        return smoke_result

    def run_weekly_full_eval(self) -> Dict[str, Any]:
        """Run weekly full evaluation with triage and SOP generation."""
        print("📅 WEEKLY FULL EVALUATION")
        print("="*50)
        
        eval_result = {
            "type": "weekly_full_eval",
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "phases": {},
            "overall_status": "unknown"
        }
        
        # Phase 1: Full evaluation
        print("📊 Phase 1: Running full evaluation...")
        full_eval_result = self._run_full_evaluation()
        eval_result["phases"]["full_evaluation"] = full_eval_result
        
        # Phase 2: Triage worst cases
        print("🔍 Phase 2: Triaging worst cases...")
        triage_result = self._triage_worst_cases(full_eval_result)
        eval_result["phases"]["triage"] = triage_result
        
        # Phase 3: Generate SOP cards
        print("📋 Phase 3: Generating SOP cards...")
        sop_result = self._generate_sop_cards(triage_result)
        eval_result["phases"]["sop_generation"] = sop_result
        
        # Phase 4: Small config nudges
        print("⚙️ Phase 4: Applying config nudges...")
        config_result = self._apply_config_nudges(triage_result)
        eval_result["phases"]["config_nudges"] = config_result
        
        # Determine overall status
        eval_result["overall_status"] = "completed"
        eval_result["status"] = "completed"
        
        # Log result
        self._log_rhythm_result(eval_result)
        
        print("✅ Weekly full evaluation completed")
        return eval_result

    def refresh_few_shots(self) -> Dict[str, Any]:
        """Refresh few-shots with deterministic KNN and leakage guard."""
        print("🔄 FEW-SHOT REFRESH")
        print("="*50)
        
        refresh_result = {
            "type": "few_shot_refresh",
            "timestamp": datetime.now().isoformat(),
            "status": "in_progress",
            "steps": {},
            "overall_status": "unknown"
        }
        
        # Step 1: Deterministic KNN selection
        print("🎯 Step 1: Deterministic KNN selection...")
        knn_result = self._run_deterministic_knn()
        refresh_result["steps"]["knn_selection"] = knn_result
        
        # Step 2: Leakage guard validation
        print("🛡️ Step 2: Leakage guard validation...")
        leakage_result = self._validate_leakage_guard()
        refresh_result["steps"]["leakage_validation"] = leakage_result
        
        # Step 3: Version under CONFIG_HASH
        print("🏷️ Step 3: Versioning under CONFIG_HASH...")
        version_result = self._version_few_shots()
        refresh_result["steps"]["versioning"] = version_result
        
        # Determine overall status
        all_steps_passed = all(
            step["success"] for step in refresh_result["steps"].values()
        )
        refresh_result["overall_status"] = "completed" if all_steps_passed else "failed"
        refresh_result["status"] = "completed"
        
        # Log result
        self._log_rhythm_result(refresh_result)
        
        if all_steps_passed:
            print("✅ Few-shot refresh completed successfully")
        else:
            print("❌ Few-shot refresh failed")
        
        return refresh_result

    def _run_smoke_test(self, test_name: str, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single smoke test."""
        try:
            result = subprocess.run(
                test_config["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "test_name": test_name,
                "description": test_config["description"],
                "command": test_config["command"],
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
        
        except subprocess.TimeoutExpired:
            return {
                "test_name": test_name,
                "description": test_config["description"],
                "command": test_config["command"],
                "passed": False,
                "error": "Test timed out after 5 minutes",
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "test_name": test_name,
                "description": test_config["description"],
                "command": test_config["command"],
                "passed": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _run_full_evaluation(self) -> Dict[str, Any]:
        """Run full evaluation."""
        try:
            result = subprocess.run(
                "python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli",
                shell=True,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _triage_worst_cases(self, eval_result: Dict[str, Any]) -> Dict[str, Any]:
        """Triage worst cases from evaluation."""
        # This would analyze evaluation results and identify worst cases
        # For now, return a placeholder structure
        
        return {
            "worst_cases": [
                {
                    "case_id": "case_001",
                    "issue": "Low oracle prefilter rate",
                    "severity": "high",
                    "recommendation": "Adjust RRF weights"
                },
                {
                    "case_id": "case_002",
                    "issue": "High latency",
                    "severity": "medium",
                    "recommendation": "Prewarm reranker"
                }
            ],
            "timestamp": datetime.now().isoformat()
        }

    def _generate_sop_cards(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SOP cards from triage results."""
        # This would generate SOP cards based on triage results
        # For now, return a placeholder structure
        
        sop_cards = []
        for case in triage_result["worst_cases"]:
            sop_cards.append({
                "sop_id": f"sop_{case['case_id']}",
                "issue": case["issue"],
                "severity": case["severity"],
                "procedure": case["recommendation"],
                "created": datetime.now().isoformat()
            })
        
        return {
            "sop_cards": sop_cards,
            "total_cards": len(sop_cards),
            "timestamp": datetime.now().isoformat()
        }

    def _apply_config_nudges(self, triage_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply small config nudges based on triage results."""
        nudges = []
        
        for case in triage_result["worst_cases"]:
            if "RRF weights" in case["recommendation"]:
                nudges.append({
                    "config": "RRF_WEIGHTS",
                    "action": "increase_dense_weight",
                    "value": 0.6
                })
            elif "reranker" in case["recommendation"]:
                nudges.append({
                    "config": "RERANK_PREWARM",
                    "action": "enable",
                    "value": True
                })
        
        return {
            "nudges": nudges,
            "total_nudges": len(nudges),
            "timestamp": datetime.now().isoformat()
        }

    def _run_deterministic_knn(self) -> Dict[str, Any]:
        """Run deterministic KNN selection for few-shots."""
        try:
            result = subprocess.run(
                "python3 scripts/deterministic_knn_selection.py",
                shell=True,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _validate_leakage_guard(self) -> Dict[str, Any]:
        """Validate leakage guard for few-shots."""
        try:
            result = subprocess.run(
                "python3 scripts/validate_leakage_guard.py",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _version_few_shots(self) -> Dict[str, Any]:
        """Version few-shots under CONFIG_HASH."""
        config_hash = os.getenv("CONFIG_HASH", "default")
        
        try:
            result = subprocess.run(
                f"python3 scripts/version_few_shots.py --config-hash {config_hash}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            return {
                "success": result.returncode == 0,
                "config_hash": config_hash,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _trigger_smoke_alert(self, smoke_result: Dict[str, Any]):
        """Trigger alerting for failed smoke tests."""
        failed_tests = [
            test_name for test_name, test_result in smoke_result["tests"].items()
            if not test_result["passed"]
        ]
        
        alert_message = f"🚨 Nightly smoke evaluation failed. Failed tests: {', '.join(failed_tests)}"
        print(alert_message)
        
        # In a real implementation, this would send alerts via Slack, email, etc.
        # For now, just log the alert
        alert_log = {
            "timestamp": datetime.now().isoformat(),
            "type": "smoke_alert",
            "message": alert_message,
            "failed_tests": failed_tests
        }
        
        with open(self.rhythm_log_file, "a") as f:
            f.write(json.dumps(alert_log) + "\n")

    def _log_rhythm_result(self, result: Dict[str, Any]):
        """Log rhythm result to rhythm log."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "rhythm_result",
            "data": result
        }
        
        with open(self.rhythm_log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def get_rhythm_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get rhythm history."""
        history = []
        
        if not self.rhythm_log_file.exists():
            return history
        
        with open(self.rhythm_log_file, "r") as f:
            lines = f.readlines()
        
        # Get recent entries
        recent_lines = lines[-limit:] if len(lines) > limit else lines
        
        for line in recent_lines:
            try:
                log_entry = json.loads(line.strip())
                if log_entry.get("type") == "rhythm_result":
                    history.append(log_entry["data"])
            except json.JSONDecodeError:
                continue
        
        return history


def main():
    """Main entry point for ops rhythm system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Ops rhythm system")
    parser.add_argument("--action", choices=["smoke", "weekly", "refresh", "history"], required=True)
    parser.add_argument("--limit", type=int, default=10, help="Limit for history action")
    
    args = parser.parse_args()
    
    rhythm_system = OpsRhythmSystem()
    
    if args.action == "smoke":
        result = rhythm_system.run_nightly_smoke()
        print(f"📊 Smoke result: {result['overall_status']}")
    
    elif args.action == "weekly":
        result = rhythm_system.run_weekly_full_eval()
        print(f"📊 Weekly eval result: {result['overall_status']}")
    
    elif args.action == "refresh":
        result = rhythm_system.refresh_few_shots()
        print(f"📊 Refresh result: {result['overall_status']}")
    
    elif args.action == "history":
        history = rhythm_system.get_rhythm_history(limit=args.limit)
        print(f"📋 Rhythm History (last {len(history)} entries):")
        for entry in history:
            status_emoji = "✅" if entry["overall_status"] == "passed" else "❌" if entry["overall_status"] == "failed" else "🔄"
            print(f"{status_emoji} {entry['type']} - {entry['timestamp']} ({entry['overall_status']})")


if __name__ == "__main__":
    main()
