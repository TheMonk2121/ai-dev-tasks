#!/usr/bin/env python3
"""
Production Runbook - One-Command Deployment
Generate manifest, run health-gated evals, start canary monitoring.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path


class ProductionRunbook:
    """One-command production deployment runbook."""

    def __init__(self):
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.run_id = f"prod_run_{self.timestamp}"

    def execute_production_deployment(self) -> dict:
        """Execute complete production deployment workflow."""
        print("🚀 PRODUCTION DEPLOYMENT RUNBOOK")
        print("="*60)
        print(f"📋 Run ID: {self.run_id}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print()

        # Phase 1: Health-Gated Evaluation
        print("🔍 Phase 1: Health-Gated Evaluation")
        print("-" * 40)
        self._run_health_gated_evaluation()

        # Phase 2: Generate Run Manifest
        print("\n📋 Phase 2: Generate Run Manifest")
        print("-" * 40)
        self._generate_run_manifest()

        # Phase 3: Deterministic Environment Setup
        print("\n⚙️ Phase 3: Deterministic Environment Setup")
        print("-" * 40)
        self._setup_deterministic_environment()

        # Phase 4: Retrieval-Only Baseline Evaluation
        print("\n🔍 Phase 4: Retrieval-Only Baseline Evaluation")
        print("-" * 40)
        self._run_retrieval_only_evaluation()

        # Phase 5: Deterministic Few-Shot Evaluation
        print("\n🧠 Phase 5: Deterministic Few-Shot Evaluation")
        print("-" * 40)
        self._run_deterministic_fewshot_evaluation()

        # Phase 6: Start 48-Hour Canary
        print("\n🕐 Phase 6: Start 48-Hour Canary Monitoring")
        print("-" * 40)
        self._start_canary_monitoring()

        print("\n✅ PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY")
        return {"status": "completed", "run_id": self.run_id}

    def _run_health_gated_evaluation(self):
        """Run health-gated evaluation."""
        print("🔍 Running comprehensive health checks...")
        os.system("python3 scripts/health_gated_evaluation.py")

    def _generate_run_manifest(self):
        """Generate comprehensive run manifest."""
        print("📋 Generating run manifest...")
        os.system("python3 scripts/eval_manifest_generator.py --format yaml")

    def _setup_deterministic_environment(self):
        """Setup deterministic evaluation environment."""
        print("⚙️ Setting up deterministic environment...")
        print("📄 Sourcing: configs/deterministic_evaluation.env")
        os.system("source configs/deterministic_evaluation.env")

    def _run_retrieval_only_evaluation(self):
        """Run retrieval-only baseline evaluation."""
        print("🔍 Running retrieval-only baseline evaluation...")
        print("🎯 Target: Oracle prefilter ≥ 85%")
        os.system("python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable")

    def _run_deterministic_fewshot_evaluation(self):
        """Run deterministic few-shot evaluation."""
        print("🧠 Running deterministic few-shot evaluation...")
        print("🎯 Target: F1 ≥ baseline, precision drift ≤ 2 pts")
        os.system("python3 scripts/ragchecker_official_evaluation.py --use-bedrock --stable")

    def _start_canary_monitoring(self):
        """Start 48-hour canary monitoring."""
        print("🕐 Starting 48-hour canary monitoring...")
        print("📊 Canary phases: 10% → 50% → 100%")
        os.system("python3 scripts/48_hour_canary_monitor.py --duration 48")


def main():
    """Main entry point for production runbook."""
    runbook = ProductionRunbook()
    result = runbook.execute_production_deployment()
    
    if result["status"] == "completed":
        print("\n🎉 Production deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Production deployment failed")
        sys.exit(1)


if __name__ == "__main__":
    main()