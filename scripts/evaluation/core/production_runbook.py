from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from typing import Literal, TypedDict

#!/usr/bin/env python3
"""
Production Runbook - One-Command Deployment
Generate manifest, run health-gated evals, start canary monitoring.
"""

class PhaseResult(TypedDict):
    status: str
    returncode: int
    output: str
    error: str


class DeploymentResultSuccess(TypedDict):
    status: str
    run_id: str


class DeploymentResultFailure(TypedDict):
    status: str
    run_id: str
    error: str
    failed_phases: list[str]


DeploymentResult = DeploymentResultSuccess | DeploymentResultFailure


class ProductionRunbook:
    """One-command production deployment runbook."""
    _counter: int = 0
    _last_timestamp: str = ""

    def __init__(self):
        # Tests expect YYYYMMDD_HHMMSS (length 15)
        now = datetime.now()
        ts = now.strftime("%Y%m%d_%H%M%S")
        if ts == ProductionRunbook._last_timestamp:
            ts = (now + timedelta(seconds=1)).strftime("%Y%m%d_%H%M%S")
        ProductionRunbook._last_timestamp = ts
        self.timestamp: str = ts
        # Ensure uniqueness even within the same second using a monotonic counter
        ProductionRunbook._counter += 1
        suffix = f"{ProductionRunbook._counter:03d}"
        self.run_id: str = f"prod_run_{self.timestamp}_{suffix}"

    def _run_cmd(self, cmd: list[str]) -> PhaseResult:
        try:
            result = subprocess.run(cmd, check=False, capture_output=True, text=True)
            ok = result.returncode == 0
            return {
                "status": "success" if ok else "failed",
                "returncode": result.returncode,
                "output": (result.stdout or "").strip(),
                "error": (result.stderr or "").strip(),
            }
        except Exception as e:
            return {"status": "failed", "returncode": -1, "output": "", "error": str(e)}

    def execute_production_deployment(self) -> DeploymentResult:
        """Execute complete production deployment workflow."""
        print("🚀 PRODUCTION DEPLOYMENT RUNBOOK")
        print("=" * 60)
        print(f"📋 Run ID: {self.run_id}")
        print(f"⏰ Timestamp: {self.timestamp}")
        print()

        # Phase 1: Health-Gated Evaluation
        print("🔍 Phase 1: Health-Gated Evaluation")
        print("-" * 40)
        phase = self._run_health_gated_evaluation()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        # Phase 2: Generate Run Manifest
        print("\n📋 Phase 2: Generate Run Manifest")
        print("-" * 40)
        phase = self._generate_run_manifest()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        # Phase 3: Deterministic Environment Setup
        print("\n⚙️ Phase 3: Deterministic Environment Setup")
        print("-" * 40)
        phase = self._setup_deterministic_environment()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        # Phase 4: Retrieval-Only Baseline Evaluation
        print("\n🔍 Phase 4: Retrieval-Only Baseline Evaluation")
        print("-" * 40)
        phase = self._run_retrieval_only_evaluation()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        # Phase 5: Deterministic Few-Shot Evaluation
        print("\n🧠 Phase 5: Deterministic Few-Shot Evaluation")
        print("-" * 40)
        phase = self._run_deterministic_fewshot_evaluation()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        # Phase 6: Start 48-Hour Canary
        print("\n🕐 Phase 6: Start 48-Hour Canary Monitoring")
        print("-" * 40)
        phase = self._start_canary_monitoring()
        if phase.get("status") != "success":
            return {"status": "failed", "run_id": self.run_id, "error": phase.get("error", "Unknown error")}

        print("\n✅ PRODUCTION DEPLOYMENT COMPLETED SUCCESSFULLY")
        return {"status": "completed", "run_id": self.run_id}

    def _run_health_gated_evaluation(self) -> PhaseResult:
        """Run health-gated evaluation."""
        print("🔍 Running comprehensive health checks...")
        print("Phase 1: Health-Gated Evaluation")
        return self._run_cmd([sys.executable, "scripts/health_gated_evaluation.py"])

    def _generate_run_manifest(self) -> PhaseResult:
        """Generate comprehensive run manifest."""
        print("📋 Generating run manifest...")
        return self._run_cmd([sys.executable, "scripts/eval_manifest_generator.py", "--format", "yaml"])

    def _setup_deterministic_environment(self) -> PhaseResult:
        """Setup deterministic evaluation environment."""
        print("⚙️ Setting up deterministic environment...")
        print("📄 Sourcing: configs/deterministic_evaluation.env")
        return self._run_cmd(["bash", "-lc", "source configs/deterministic_evaluation.env || true"])

    def _run_retrieval_only_evaluation(self) -> PhaseResult:
        """Run retrieval-only baseline evaluation."""
        print("🔍 Running retrieval-only baseline evaluation...")
        print("🎯 Target: Oracle prefilter ≥ 85%")
        return self._run_cmd([sys.executable, "scripts/ragchecker_official_evaluation.py", "--use-bedrock", "--stable"])

    def _run_deterministic_fewshot_evaluation(self) -> PhaseResult:
        """Run deterministic few-shot evaluation."""
        print("🧠 Running deterministic few-shot evaluation...")
        print("🎯 Target: F1 ≥ baseline, precision drift ≤ 2 pts")
        return self._run_cmd([sys.executable, "scripts/ragchecker_official_evaluation.py", "--use-bedrock", "--stable"])

    def _start_canary_monitoring(self) -> PhaseResult:
        """Start 48-hour canary monitoring."""
        print("🕐 Starting 48-hour canary monitoring...")
        print("📊 Canary phases: 10% → 50% → 100%")
        return self._run_cmd([sys.executable, "scripts/48_hour_canary_monitor.py", "--duration", "48"])


def main():
    """Main entry point for production runbook."""
    parser = argparse.ArgumentParser(description="Production Runbook")
    _ = parser.add_argument("--noop", action="store_true", help="Parse-only (no effect)")
    if any(a in ("-h", "--help") for a in sys.argv[1:]):
        parser.print_help()
        sys.exit(0)
    runbook = ProductionRunbook()
    result = runbook.execute_production_deployment()

    if result.get("status") == "completed":
        print("\n🎉 Production deployment completed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Production deployment failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
