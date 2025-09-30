#!/usr/bin/env python3
"""Clean production evaluation entrypoint.

This script delegates the heavy lifting to ``production_eval_helpers`` so that
other environments (for example notebooks) can reuse the exact same
configuration and execution semantics.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

from evals.scripts.evaluation.core.production_eval_helpers import (
    DEFAULT_PRODUCTION_PASSES,
    DEFAULT_RESULTS_DIR,
    ProductionEvaluationSummary,
    run_production_evaluation,
)

# Add project paths - use absolute paths and check for duplicates
PROJECT_ROOT = Path(__file__).parent.parent.resolve()
DSPY_RAG_PATH = PROJECT_ROOT / "dspy-rag-system"

for candidate in (PROJECT_ROOT, DSPY_RAG_PATH):
    candidate_str = str(candidate)
    if candidate_str not in sys.path:
        sys.path.insert(0, candidate_str)

# Import settings to validate configuration early
from src.config import get_settings  # noqa: E402


def _print_summary(summary: ProductionEvaluationSummary) -> None:
    """Emit a human-readable summary for CLI usage."""

    print("\n📊 Analysis Results")
    print("=" * 60)
    for result in summary.results:
        name = result.config.name
        if not result.executed:
            print(f"⏭️  {name} skipped (dry-run)")
            continue
        if result.succeeded:
            print(f"✅ {name} completed successfully")
        else:
            print(f"❌ {name} failed")
            if result.error:
                print(f"   Error: {result.error}")
            elif result.stderr:
                print("   STDERR captured; inspect result payload for details.")

    if summary.overall_status == "success":
        print("🎉 ALL PASSES SUCCESSFUL - Ready for production!")
    elif summary.overall_status == "dry-run":
        print("ℹ️  Dry-run completed; no passes executed.")
    elif summary.overall_status == "partial":
        print("⚠️  PARTIAL SUCCESS - Review failed or skipped passes")
    else:
        print("❌ ALL EXECUTED PASSES FAILED - Fix issues before proceeding")


def _write_analysis(summary: ProductionEvaluationSummary, results_dir: Path) -> Path:
    """Persist aggregate analysis to disk."""

    analysis_payload: dict[str, object] = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_passes": summary.total_passes,
            "successful_passes": summary.successful_passes,
            "failed_passes": summary.failed_passes,
            "skipped_passes": summary.skipped_passes,
            "overall_status": summary.overall_status,
        },
        "pass_criteria": {
            "oracle_retrieval_hit_prefilter": "≥ +5-15 pts vs baseline",
            "reader_used_gold": "≥ baseline",
            "f1_score": "≥ baseline",
            "precision_drift": "≤ 2 pts",
            "p95_latency": "≤ +15%",
        },
        "passes": [],
    }

    for result in summary.results:
        pass_entry = {
            "name": result.config.name,
            "description": result.config.description,
            "env": dict(result.config.env),
            "cases_file": result.config.cases_file,
            "output_file": str(result.output_file),
            "return_code": result.return_code,
            "duration_seconds": result.duration_seconds,
            "error": result.error,
            "executed": result.executed,
        }
        analysis_payload["passes"].append(pass_entry)

    results_dir.mkdir(parents=True, exist_ok=True)
    analysis_file = results_dir / f"analysis_{int(time.time())}.json"
    analysis_file.write_text(json.dumps(analysis_payload, indent=2), encoding="utf-8")
    return analysis_file


def main() -> None:
    """Run production evaluation with the canonical pass set."""

    print("🚀 PRODUCTION EVALUATION - Clean & Reproducible")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Validate configuration early; exit fast on misconfiguration
    try:
        settings = get_settings()
        print(f"✅ Configuration loaded successfully for environment: {settings.env}")
    except Exception as exc:  # pragma: no cover - configuration failure path
        print(f"❌ Configuration validation failed: {exc}")
        sys.exit(1)

    results_root = DEFAULT_RESULTS_DIR
    run_id = time.strftime("%Y%m%d_%H%M%S")

    summary = run_production_evaluation(
        DEFAULT_PRODUCTION_PASSES,
        project_root=PROJECT_ROOT,
        results_dir=results_root,
        execute=True,
        capture_output=True,
        logger=print,
        base_env=os.environ,
        run_id=run_id,
    )

    _print_summary(summary)
    analysis_file = _write_analysis(summary, summary.run_dir)

    print(f"\n📁 Results root: {results_root}")
    print(f"📁 Run directory: {summary.run_dir}")
    print(f"📊 Analysis saved to: {analysis_file}")

    if summary.overall_status == "success":
        print("\n🎯 NEXT STEPS:")
        print("   1. Review evaluation results")
        print("   2. Proceed with canary rollout")
        print("   3. Monitor production metrics")
        print(json.dumps({
            "run_id": summary.run_id,
            "run_dir": str(summary.run_dir),
            "manifest": str(summary.manifest_path),
            "analysis_file": str(analysis_file),
            "overall_status": summary.overall_status,
        }))
        sys.exit(0)

    print("\n🔧 NEXT STEPS:")
    print("   1. Fix failed evaluation passes")
    print("   2. Re-run production evaluation")
    print("   3. Address any issues before production")
    print(json.dumps({
        "run_id": summary.run_id,
        "run_dir": str(summary.run_dir),
        "manifest": str(summary.manifest_path),
        "analysis_file": str(analysis_file),
        "overall_status": summary.overall_status,
    }))
    sys.exit(1)


if __name__ == "__main__":
    main()
