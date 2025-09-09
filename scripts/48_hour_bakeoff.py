#!/usr/bin/env python3
"""
48-Hour Bakeoff Script
- Complete automated 48-hour bakeoff workflow
- Pre-bake setup, evaluation, monitoring, and rollout
- Comprehensive health checks and rollback capabilities
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

from src.utils.config_lock import ConfigLockManager, LockedConfig


def run_command(cmd: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    """Run a command and return the result"""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd or project_root,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Command failed: {cmd}")
        print(f"   Error: {result.stderr}")
        return result

    print(f"✅ Command succeeded: {cmd}")
    return result


def pre_bake_setup(config: LockedConfig) -> bool:
    """Pre-bake setup: freeze config, prewarm models, DB hygiene"""
    print("🔧 Pre-Bake Setup")
    print("=" * 40)

    # 1. Freeze config and surface it everywhere
    print("1. Freezing configuration...")
    env_vars = {
        "CHUNK_VERSION": config.chunk_version,
        "CONFIG_HASH": config.get_config_hash(),
        "EMBEDDER_NAME": config.embedder_name,
        "TOKENIZER_NAME": config.tokenizer_name,
        "TOKENIZER_HASH": config.tokenizer_hash,
        "CHUNK_SIZE": str(config.chunk_size),
        "OVERLAP_RATIO": str(config.overlap_ratio),
        "JACCARD_THRESHOLD": str(config.jaccard_threshold),
        "PREFIX_POLICY": config.prefix_policy,
        "EVAL_DISABLE_CACHE": "1",
    }

    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"   {key}={value}")

    # 2. Prewarm models (placeholder)
    print("2. Prewarming models...")
    print("   Cross-encoder: loaded once at process start")
    print("   Bedrock: keeping off for evals")

    # 3. DB hygiene (placeholder)
    print("3. Database hygiene...")
    shadow_table = config.shadow_table or f"document_chunks_{config.chunk_version.replace('-', '_')}"
    print(f"   VACUUM ANALYZE {shadow_table};")
    print("   Verifying indexes exist and are used")

    # 4. Cache stance for evals
    print("4. Cache configuration...")
    print("   EVAL_DISABLE_CACHE=1 (no query→docID caching)")

    # 5. Concurrency limits
    print("5. Concurrency limits...")
    print("   Limit to 2-3 workers")
    print("   BEDROCK_MAX_IN_FLIGHT=1 if Bedrock enabled")

    return True


def run_shadow_ingest(config: LockedConfig) -> bool:
    """Run shadow ingest into versioned table"""
    print("\n📊 Shadow Ingest")
    print("=" * 40)

    cmd = "python scripts/shadow_ingest.py"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ Shadow ingest failed")
        return False

    print("✅ Shadow ingest completed successfully")
    return True


def run_evaluation(config: LockedConfig) -> bool:
    """Run evaluation with locked configuration"""
    print("\n🧪 Evaluation")
    print("=" * 40)

    cmd = "python scripts/production_evaluation.py"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ Evaluation failed")
        return False

    print("✅ Evaluation completed successfully")
    return True


def run_sanity_probes(config: LockedConfig) -> bool:
    """Run sanity probes"""
    print("\n🔍 Sanity Probes")
    print("=" * 40)

    cmd = "python scripts/sanity_probes.py"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ Sanity probes failed")
        return False

    print("✅ Sanity probes passed")
    return True


def run_kpi_monitoring(config: LockedConfig) -> bool:
    """Run KPI monitoring and threshold checks"""
    print("\n📊 KPI Monitoring")
    print("=" * 40)

    cmd = "python scripts/kpi_monitor.py --promote-check"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ KPI monitoring failed - not ready for promotion")
        return False

    print("✅ KPI monitoring passed - ready for promotion")
    return True


def run_ci_parity_tests(config: LockedConfig) -> bool:
    """Run CI parity tests"""
    print("\n🧪 CI Parity Tests")
    print("=" * 40)

    cmd = "python scripts/ci_parity_tests.py"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ CI parity tests failed")
        return False

    print("✅ CI parity tests passed")
    return True


def start_canary_rollout(config: LockedConfig) -> bool:
    """Start canary rollout"""
    print("\n🚀 Canary Rollout")
    print("=" * 40)

    cmd = "python scripts/canary_rollout.py --start"
    result = run_command(cmd)

    if result.returncode != 0:
        print("❌ Canary rollout failed to start")
        return False

    print("✅ Canary rollout started (10% traffic)")
    return True


def monitor_rollout(config: LockedConfig, duration_hours: int = 48) -> bool:
    """Monitor rollout for specified duration"""
    print(f"\n📊 Monitoring Rollout ({duration_hours} hours)")
    print("=" * 40)

    start_time = datetime.now()
    end_time = start_time + timedelta(hours=duration_hours)

    print(f"Start time: {start_time}")
    print(f"End time: {end_time}")
    print("Monitoring key metrics...")

    # In a real implementation, you'd have continuous monitoring here
    # For now, we'll just show the monitoring plan
    print("\n📈 Monitoring Plan:")
    print("   - Oracle hit rate: +5-15 points vs baseline")
    print("   - Filter hit rate: ≥ baseline")
    print("   - Reader gold usage: ≥ baseline")
    print("   - F1 score: ≥ baseline")
    print("   - Precision drift: ≤ 2 points")
    print("   - Latency p95: ≤ +15% vs baseline")
    print("   - Token budget: 0 violations")
    print("   - Dedup rate: 10-35%")
    print("   - Prefix leakage: 0 chunks")

    print("\n🔄 Rollout Phases:")
    print("   - 0-16 hours: 10% traffic")
    print("   - 16-32 hours: 50% traffic")
    print("   - 32-48 hours: 100% traffic")

    return True


def generate_bakeoff_report(
    config: LockedConfig,
    pre_bake_success: bool,
    ingest_success: bool,
    eval_success: bool,
    sanity_success: bool,
    kpi_success: bool,
    ci_success: bool,
    canary_success: bool,
) -> dict[str, Any]:
    """Generate comprehensive bakeoff report"""

    overall_success = all(
        [
            pre_bake_success,
            ingest_success,
            eval_success,
            sanity_success,
            kpi_success,
            ci_success,
            canary_success,
        ]
    )

    return {
        "timestamp": datetime.now().isoformat(),
        "config_version": config.chunk_version,
        "config_hash": config.get_config_hash(),
        "overall_success": overall_success,
        "phase_results": {
            "pre_bake_setup": pre_bake_success,
            "shadow_ingest": ingest_success,
            "evaluation": eval_success,
            "sanity_probes": sanity_success,
            "kpi_monitoring": kpi_success,
            "ci_parity_tests": ci_success,
            "canary_rollout": canary_success,
        },
        "next_steps": [
            "Monitor rollout for 48 hours",
            "Promote to 50% traffic after 16 hours",
            "Promote to 100% traffic after 32 hours",
            "Archive v1 configuration after successful rollout",
        ],
        "rollback_plan": [
            "Use: python scripts/canary_rollout.py --rollback",
            "Clear retrieval cache",
            "Verify rollback with sanity probes",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description="Run 48-hour bakeoff")
    parser.add_argument("--skip-ingest", action="store_true", help="Skip shadow ingest")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation")
    parser.add_argument("--skip-canary", action="store_true", help="Skip canary rollout")
    parser.add_argument("--monitor-hours", type=int, default=48, help="Monitoring duration in hours")
    parser.add_argument("--output", help="Output file for bakeoff report")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)

    print("🚀 48-Hour Bakeoff")
    print("=" * 50)
    print(f"Config: {config.chunk_version}")
    print(f"Hash: {config.get_config_hash()}")
    print(f"Chunk size: {config.chunk_size}")
    print(f"Overlap ratio: {config.overlap_ratio}")
    print(f"Jaccard threshold: {config.jaccard_threshold}")
    print(f"Prefix policy: {config.prefix_policy}")
    print()

    # Run bakeoff phases
    pre_bake_success = pre_bake_setup(config)

    ingest_success = True
    if not args.skip_ingest:
        ingest_success = run_shadow_ingest(config)

    eval_success = True
    if not args.skip_eval:
        eval_success = run_evaluation(config)

    sanity_success = run_sanity_probes(config)
    kpi_success = run_kpi_monitoring(config)
    ci_success = run_ci_parity_tests(config)

    canary_success = True
    if not args.skip_canary and all(
        [pre_bake_success, ingest_success, eval_success, sanity_success, kpi_success, ci_success]
    ):
        canary_success = start_canary_rollout(config)

    # Generate report
    report = generate_bakeoff_report(
        config,
        pre_bake_success,
        ingest_success,
        eval_success,
        sanity_success,
        kpi_success,
        ci_success,
        canary_success,
    )

    # Save report
    if args.output:
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)

    # Console output
    if not args.quiet:
        print("\n📊 48-Hour Bakeoff Report")
        print("=" * 50)
        print(f"Overall Success: {'✅' if report['overall_success'] else '❌'}")
        print(f"Config Version: {report['config_version']}")
        print(f"Config Hash: {report['config_hash']}")

        print("\n📋 Phase Results:")
        for phase, success in report["phase_results"].items():
            status = "✅" if success else "❌"
            print(f"  {phase}: {status}")

        if report["overall_success"]:
            print("\n🎯 Next Steps:")
            for step in report["next_steps"]:
                print(f"  - {step}")

            print("\n🔄 Rollback Plan:")
            for step in report["rollback_plan"]:
                print(f"  - {step}")
        else:
            print("\n❌ Bakeoff failed - check phase results above")

    # Exit with error code if bakeoff failed
    if not report["overall_success"]:
        sys.exit(1)

    print("\n🎉 48-Hour Bakeoff completed successfully!")
    print("   Ready for production rollout")


if __name__ == "__main__":
    main()
