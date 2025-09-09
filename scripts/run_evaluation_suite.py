#!/usr/bin/env python3
"""
Comprehensive Evaluation Suite Runner
Runs both ops smoke (non-gold) and repo-gold evaluations with appropriate gates
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


class EvaluationSuiteRunner:
    """Runner for comprehensive evaluation suite."""

    def __init__(self):
        self.results_dir = Path("metrics/baseline_evaluations")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Evaluation configurations - now using gold profiles
        self.configs = {
            "ops_smoke": {
                "env_file": "configs/precision_elevated.env",
                "gold_profile": "ops_smoke",
                "has_gold": False,
                "gates": ["breadth", "coverage", "latency"],
                "description": "Ops Smoke Test - Non-gold breadth and coverage validation",
            },
            "repo_gold": {
                "env_file": "configs/repo_gold_evaluation.env",
                "gold_profile": "repo_gold",
                "has_gold": True,
                "gates": ["oracle", "reader", "f1", "precision_drift", "latency"],
                "description": "Repo-Gold Evaluation - Strict accuracy gates",
            },
        }

    def load_env_config(self, env_file: str) -> dict[str, str]:
        """Load environment configuration from file."""
        config = {}
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        config[key] = value
        return config

    def set_environment(self, config: dict[str, str]):
        """Set environment variables from config."""
        for key, value in config.items():
            os.environ[key] = value

    def run_leakage_guard(self, eval_type: str) -> bool:
        """Run leakage guard validation."""
        if eval_type == "repo_gold":
            print("🔒 Running leakage guard validation...")
            try:
                result = subprocess.run(
                    [
                        "python3",
                        "scripts/leakage_guard.py",
                        "--action",
                        "assert-clean",
                        "--eval-file",
                        self.configs[eval_type]["dataset"],
                    ],
                    capture_output=True,
                    text=True,
                    check=True,
                )
                print("✅ Leakage guard passed")
                return True
            except subprocess.CalledProcessError as e:
                print(f"❌ Leakage guard failed: {e.stderr}")
                return False
        return True

    def run_evaluation(self, eval_type: str) -> dict[str, Any]:
        """Run evaluation for specified type."""
        config_info = self.configs[eval_type]
        print(f"\n🚀 Running {eval_type.upper()} Evaluation")
        print("=" * 50)
        print(f"📋 {config_info['description']}")
        print(f"📁 Dataset: {config_info['dataset']}")
        print(f"⚙️ Config: {config_info['env_file']}")
        print(f"🎯 Gates: {', '.join(config_info['gates'])}")

        # Load and set environment
        env_config = self.load_env_config(config_info["env_file"])
        self.set_environment(env_config)

        # Run leakage guard for repo-gold
        if not self.run_leakage_guard(eval_type):
            return {"status": "failed", "error": "leakage_guard_failed"}

        # Run evaluation
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = self.results_dir / f"{eval_type}_evaluation_{timestamp}.json"

        try:
            cmd = [
                "python3",
                "scripts/ragchecker_official_evaluation.py",
                "--gold-profile",
                config_info["gold_profile"],
                "--outdir",
                str(self.results_dir),
                "--use-bedrock",
                "--bypass-cli",
                "--concurrency",
                "3",
            ]

            print(f"🔧 Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            # Find the actual output file (ragchecker creates timestamped files)
            # Look for files created in the last few minutes
            import glob

            pattern = str(self.results_dir / "ragchecker_*_*.json")
            all_files = glob.glob(pattern)

            # Find the most recent file
            if all_files:
                actual_output = max(all_files, key=os.path.getctime)
            else:
                actual_output = output_file

            print(f"✅ Evaluation completed: {actual_output}")

            # Load results
            with open(actual_output) as f:
                results = json.load(f)

            return {
                "status": "success",
                "eval_type": eval_type,
                "output_file": str(actual_output),
                "results": results,
                "timestamp": timestamp,
            }

        except subprocess.CalledProcessError as e:
            print(f"❌ Evaluation failed: {e.stderr}")
            return {"status": "failed", "eval_type": eval_type, "error": e.stderr, "timestamp": timestamp}

    def run_gate_validation(self, eval_type: str, results: dict[str, Any]) -> dict[str, Any]:
        """Run gate validation for evaluation results."""
        config_info = self.configs[eval_type]

        if eval_type == "repo_gold":
            print(f"\n🚪 Running Gate Validation for {eval_type.upper()}")
            print("=" * 50)

            # Create temporary results file for gate validation
            temp_results_file = self.results_dir / f"temp_{eval_type}_results.json"
            with open(temp_results_file, "w") as f:
                json.dump(results, f)

            try:
                cmd = [
                    "python3",
                    "scripts/gate_and_promote.py",
                    "--action",
                    "gate",
                    "--config-hash",
                    f"{eval_type}_{time.strftime('%Y%m%d_%H%M%S')}",
                    "--evaluation-results",
                    str(temp_results_file),
                ]

                print(f"🔧 Running: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)

                print("✅ Gate validation completed")

                # Clean up temp file
                temp_results_file.unlink()

                return {"status": "success", "gate_result": result.stdout}

            except subprocess.CalledProcessError as e:
                print(f"❌ Gate validation failed: {e.stderr}")
                # Clean up temp file
                if temp_results_file.exists():
                    temp_results_file.unlink()
                return {"status": "failed", "error": e.stderr}

        return {"status": "skipped", "reason": "no_gates_for_ops_smoke"}

    def run_full_suite(self, eval_types: list[str] = None) -> dict[str, Any]:
        """Run full evaluation suite."""
        if eval_types is None:
            eval_types = ["ops_smoke", "repo_gold"]

        print("🎯 COMPREHENSIVE EVALUATION SUITE")
        print("=" * 60)
        print(f"📋 Running evaluations: {', '.join(eval_types)}")
        print(f"📁 Results directory: {self.results_dir}")

        suite_results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "evaluations": {},
            "summary": {
                "total_evaluations": len(eval_types),
                "successful": 0,
                "failed": 0,
                "gate_passed": 0,
                "gate_failed": 0,
            },
        }

        for eval_type in eval_types:
            if eval_type not in self.configs:
                print(f"⚠️ Unknown evaluation type: {eval_type}")
                continue

            # Run evaluation
            eval_result = self.run_evaluation(eval_type)
            suite_results["evaluations"][eval_type] = eval_result

            if eval_result["status"] == "success":
                suite_results["summary"]["successful"] += 1

                # Run gate validation for successful evaluations
                gate_result = self.run_gate_validation(eval_type, eval_result["results"])
                eval_result["gate_validation"] = gate_result

                if gate_result["status"] == "success":
                    suite_results["summary"]["gate_passed"] += 1
                elif gate_result["status"] == "failed":
                    suite_results["summary"]["gate_failed"] += 1
            else:
                suite_results["summary"]["failed"] += 1

        # Save suite results
        suite_output = self.results_dir / f"evaluation_suite_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(suite_output, "w") as f:
            json.dump(suite_results, f, indent=2)

        # Print summary
        print("\n📊 EVALUATION SUITE SUMMARY")
        print("=" * 50)
        print(
            f"✅ Successful evaluations: {suite_results['summary']['successful']}/{suite_results['summary']['total_evaluations']}"
        )
        print(f"❌ Failed evaluations: {suite_results['summary']['failed']}")
        print(f"🚪 Gates passed: {suite_results['summary']['gate_passed']}")
        print(f"🚫 Gates failed: {suite_results['summary']['gate_failed']}")
        print(f"📁 Suite results: {suite_output}")

        return suite_results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Comprehensive Evaluation Suite Runner")
    parser.add_argument(
        "--eval-types", nargs="+", choices=["ops_smoke", "repo_gold"], help="Evaluation types to run (default: both)"
    )
    parser.add_argument("--ops-smoke-only", action="store_true", help="Run only ops smoke evaluation")
    parser.add_argument("--repo-gold-only", action="store_true", help="Run only repo-gold evaluation")

    args = parser.parse_args()

    # Determine evaluation types
    if args.ops_smoke_only:
        eval_types = ["ops_smoke"]
    elif args.repo_gold_only:
        eval_types = ["repo_gold"]
    elif args.eval_types:
        eval_types = args.eval_types
    else:
        eval_types = ["ops_smoke", "repo_gold"]

    runner = EvaluationSuiteRunner()
    results = runner.run_full_suite(eval_types)

    # Exit with appropriate code
    if results["summary"]["failed"] > 0:
        sys.exit(1)
    elif results["summary"]["gate_failed"] > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
