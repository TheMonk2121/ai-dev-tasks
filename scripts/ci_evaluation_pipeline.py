#!/usr/bin/env python3
"""
CI Evaluation Pipeline
Runs evaluation suite with proper environment setup and reporting
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path


def setup_environment():
    """Set up environment for CI evaluation."""
    print("🔧 Setting up CI evaluation environment...")

    # Set database connection
    os.environ["POSTGRES_DSN"] = "postgresql://danieljacobs@localhost:5432/ai_agency?sslmode=disable"

    # Ensure virtual environment is active
    if not os.environ.get("VIRTUAL_ENV"):
        print("⚠️ Virtual environment not detected, attempting to activate...")
        venv_path = Path(".venv")
        if venv_path.exists():
            activate_script = venv_path / "bin" / "activate"
            if activate_script.exists():
                print(f"✅ Virtual environment found at {venv_path}")
            else:
                print("❌ Virtual environment activation script not found")
                return False
        else:
            print("❌ Virtual environment not found")
            return False

    print("✅ Environment setup complete")
    return True


def run_ops_smoke_evaluation() -> dict:
    """Run ops smoke evaluation (non-gold)."""
    print("\n🚀 Running Ops Smoke Evaluation")
    print("=" * 50)

    try:
        result = subprocess.run(
            ["python3", "scripts/run_evaluation_suite.py", "--ops-smoke-only"],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ Ops smoke evaluation completed successfully")
        return {"status": "success", "output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        print(f"❌ Ops smoke evaluation failed: {e.stderr}")
        return {"status": "failed", "output": e.stdout, "error": e.stderr, "return_code": e.returncode}


def run_repo_gold_evaluation() -> dict:
    """Run repo-gold evaluation with strict gates."""
    print("\n🚀 Running Repo-Gold Evaluation")
    print("=" * 50)

    try:
        result = subprocess.run(
            ["python3", "scripts/run_evaluation_suite.py", "--repo-gold-only"],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ Repo-gold evaluation completed successfully")
        return {"status": "success", "output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        print(f"❌ Repo-gold evaluation failed: {e.stderr}")
        return {"status": "failed", "output": e.stdout, "error": e.stderr, "return_code": e.returncode}


def validate_datasets():
    """Validate that required datasets exist."""
    print("🔍 Validating datasets...")

    required_files = ["datasets/dev_gold.jsonl", "datasets/few_shot_pool.jsonl"]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False

    print("✅ All required datasets present")
    return True


def run_leakage_validation():
    """Run leakage validation."""
    print("🔒 Running leakage validation...")

    try:
        result = subprocess.run(
            [
                "python3",
                "scripts/leakage_guard.py",
                "--action",
                "assert-clean",
                "--eval-file",
                "datasets/dev_gold.jsonl",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("✅ Leakage validation passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Leakage validation failed: {e.stderr}")
        return False


def generate_ci_report(results: dict):
    """Generate CI evaluation report."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    report_file = Path("metrics/ci_evaluation_report.json")
    report_file.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "ci_run_id": f"ci_{timestamp}",
        "environment": {
            "python_version": sys.version,
            "virtual_env": os.environ.get("VIRTUAL_ENV"),
            "postgres_dsn_set": bool(os.environ.get("POSTGRES_DSN")),
        },
        "results": results,
        "summary": {
            "ops_smoke_status": results.get("ops_smoke", {}).get("status", "not_run"),
            "repo_gold_status": results.get("repo_gold", {}).get("status", "not_run"),
            "leakage_validation_passed": results.get("leakage_validation", False),
            "datasets_validated": results.get("datasets_validated", False),
        },
    }

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"📊 CI report saved: {report_file}")
    return report


def main():
    """Main CI evaluation pipeline."""
    parser = argparse.ArgumentParser(description="CI Evaluation Pipeline")
    parser.add_argument("--ops-smoke-only", action="store_true", help="Run only ops smoke evaluation")
    parser.add_argument("--repo-gold-only", action="store_true", help="Run only repo-gold evaluation")
    parser.add_argument("--skip-validation", action="store_true", help="Skip dataset and leakage validation")

    args = parser.parse_args()

    print("🎯 CI EVALUATION PIPELINE")
    print("=" * 60)

    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed")
        sys.exit(1)

    results = {}

    # Validate datasets unless skipped
    if not args.skip_validation:
        if not validate_datasets():
            print("❌ Dataset validation failed")
            sys.exit(1)
        results["datasets_validated"] = True

    # Run leakage validation for repo-gold
    if not args.ops_smoke_only and not args.skip_validation:
        if not run_leakage_validation():
            print("❌ Leakage validation failed")
            sys.exit(1)
        results["leakage_validation"] = True

    # Run evaluations
    if args.ops_smoke_only:
        results["ops_smoke"] = run_ops_smoke_evaluation()
    elif args.repo_gold_only:
        results["repo_gold"] = run_repo_gold_evaluation()
    else:
        # Run both evaluations
        results["ops_smoke"] = run_ops_smoke_evaluation()
        results["repo_gold"] = run_repo_gold_evaluation()

    # Generate report
    report = generate_ci_report(results)

    # Determine exit code
    exit_code = 0
    if results.get("ops_smoke", {}).get("status") == "failed":
        exit_code = 1
    if results.get("repo_gold", {}).get("status") == "failed":
        exit_code = 2

    print("\n📊 CI EVALUATION SUMMARY")
    print("=" * 50)
    print(f"🔧 Environment: {'✅' if report['environment']['virtual_env'] else '❌'}")
    print(f"📁 Datasets: {'✅' if report['summary']['datasets_validated'] else '❌'}")
    print(f"🔒 Leakage: {'✅' if report['summary']['leakage_validation_passed'] else '❌'}")
    print(f"🚀 Ops Smoke: {report['summary']['ops_smoke_status']}")
    print(f"🎯 Repo-Gold: {report['summary']['repo_gold_status']}")
    print(f"📊 Report: {report['ci_run_id']}")

    if exit_code == 0:
        print("✅ CI evaluation pipeline completed successfully")
    else:
        print(f"❌ CI evaluation pipeline failed with exit code {exit_code}")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
