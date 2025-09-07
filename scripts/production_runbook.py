#!/usr/bin/env python3
"""
Production Runbook - Single Command Deployment
Executes the complete production deployment pipeline with all fixes.
"""

import os
import subprocess
import sys
import time
from pathlib import Path


def run_command(cmd: str, description: str, check: bool = True) -> bool:
    """Run a command and return success status."""
    print(f"\n🔄 {description}")
    print(f"   Command: {cmd}")
    print("-" * 60)

    try:
        result = subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        if result.stderr and result.returncode != 0:
            print(f"STDERR: {result.stderr}")
        print(f"✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Return code: {e.returncode}")
        if e.stdout:
            print(f"STDOUT: {e.stdout}")
        if e.stderr:
            print(f"STDERR: {e.stderr}")
        return False


def main():
    """Execute the complete production runbook."""
    print("🚀 PRODUCTION RUNBOOK - Complete Deployment Pipeline")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Get project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)

    # Step 1: Preflight environment check
    print("\n📋 STEP 1: Environment Preflight Check")
    if not run_command("python3 -c 'import config.env_guard'", "Environment variables validation"):
        print("❌ Environment check failed. Please set required environment variables:")
        print("   export POSTGRES_DSN='postgresql://user:pass@host:5432/dbname'")
        print("   export OPENAI_API_KEY='sk-...'")
        print("   export AWS_REGION='us-east-1'")
        sys.exit(1)

    # Step 2: Apply SQL DDL fixes
    print("\n📋 STEP 2: Database Schema & Performance Fixes")
    if not run_command(
        'psql "$POSTGRES_DSN" -f scripts/sql/fix_sparse_vector_ddls.sql',
        "Apply SQL DDL fixes (vector types, indexes, active config)",
    ):
        print("⚠️  SQL fixes failed - continuing with existing schema")

    # Step 3: Set environment for evaluation
    print("\n📋 STEP 3: Configure Evaluation Environment")
    os.environ["EVAL_DISABLE_CACHE"] = "1"
    os.environ["DSPY_TELEPROMPT_CACHE"] = "false"

    # Step 4: Run production evaluation
    print("\n📋 STEP 4: Production Evaluation")
    if not run_command(
        "python3 scripts/production_evaluation.py", "Run production evaluation with locked configuration"
    ):
        print("❌ Production evaluation failed")
        sys.exit(1)

    # Step 5: Health check
    print("\n📋 STEP 5: System Health Check")
    if not run_command("python3 scripts/healthcheck_notebook.py", "Comprehensive system health check"):
        print("⚠️  Health check found issues - review output above")

    # Step 6: Production health monitor
    print("\n📋 STEP 6: Production Health Monitor")
    if not run_command("python3 scripts/production_health_monitor.py", "Production health monitoring"):
        print("⚠️  Production health monitor found issues")

    # Step 7: KPI monitoring
    print("\n📋 STEP 7: KPI Monitoring")
    if not run_command("python3 scripts/kpi_monitor.py", "KPI threshold monitoring"):
        print("⚠️  KPI monitoring found issues")

    # Step 8: Sanity probes
    print("\n📋 STEP 8: Sanity Probes")
    if not run_command("python3 scripts/sanity_probes.py", "Sanity checks and validation"):
        print("⚠️  Sanity probes found issues")

    # Summary
    print("\n🎉 PRODUCTION RUNBOOK COMPLETED")
    print("=" * 80)
    print("✅ All critical steps completed successfully")
    print("📊 Review the outputs above for any warnings or issues")
    print("🔍 Run individual health checks as needed:")
    print("   python3 scripts/healthcheck_notebook.py")
    print("   python3 scripts/production_health_monitor.py")
    print("   python3 scripts/kpi_monitor.py")


if __name__ == "__main__":
    main()
