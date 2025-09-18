#!/usr/bin/env python3
"""
Enhanced Evaluation Example

This script demonstrates how to use the enhanced observability features
with our clean DSPy evaluator for maximum insights and monitoring.
"""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.monitoring.enhanced_observability import get_enhanced_logger
from scripts.monitoring.observability import init_observability


def run_enhanced_evaluation(profile: str = "gold", limit: int = 5):
    """Run evaluation with enhanced observability."""

    # Initialize observability
    init_observability(service="ai-dev-tasks")

    # Get enhanced logger
    logger = get_enhanced_logger(f"enhanced_{profile}_{limit}")

    # Log evaluation start
    logger.log_evaluation_start(
        profile=profile,
        total_cases=limit,
        environment=os.getenv("APP_ENV", "dev"),
        python_version=sys.version,
        platform=os.getenv("PLATFORM", "unknown"),
    )

    try:
        # Import and run the clean DSPy evaluator
        # from 300_evals.scripts.evaluation.clean_dspy_evaluator import CleanDSPyEvaluator
        # CleanDSPyEvaluator = None  # Placeholder

        # Create evaluator with enhanced logging
        # evaluator = CleanDSPyEvaluator(profile=profile)
        evaluator = None  # Placeholder

        # Run evaluation with enhanced tracing
        with logger.tracer.trace_evaluation_phase("evaluation_execution", profile=profile):
            results = evaluator.run_evaluation(limit=limit)

        # Log evaluation completion with enhanced metrics
        overall_metrics = {
            "precision": result.get("key", "")
            "recall": result.get("key", "")
            "f1_score": result.get("key", "")
            "faithfulness": result.get("key", "")
            "oracle_retrieval_hit_rate": result.get("key", "")
            "oracle_reader_hit_rate": result.get("key", "")
            "successful_cases": result.get("key", "")
            "total_cases": result.get("key", "")
        }

        logger.log_evaluation_complete(
            overall_metrics=overall_metrics, results_file=result.get("key", "")
        )

        print("✅ Enhanced evaluation completed successfully!")
        print(f"📊 Results: {overall_metrics}")

        return results

    except Exception as e:
        logger.log_error(error=e, context={"profile": profile, "limit": limit})
        print(f"❌ Enhanced evaluation failed: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Evaluation with Advanced Observability")
    parser.add_argument("--profile", choices=["gold", "real", "mock"], default="gold", help="Evaluation profile")
    parser.add_argument("--limit", type=int, default=5, help="Number of cases to evaluate")
    parser.add_argument("--apply-timescale", action="store_true", help="Apply TimescaleDB optimizations first")

    args = parser.parse_args()

    print("🚀 Enhanced Evaluation System")
    print("=" * 50)

    # Apply TimescaleDB optimizations if requested
    if args.apply_timescale:
        print("🔧 Applying TimescaleDB optimizations...")
        from scripts.database.apply_timescale_optimizations import apply_optimizations

        if not apply_optimizations():
            print("❌ Failed to apply TimescaleDB optimizations")
            sys.exit(1)
        print("✅ TimescaleDB optimizations applied")
        print()

    # Run enhanced evaluation
    try:
        results = run_enhanced_evaluation(profile=args.profile, limit=args.limit)
        print(f"\n🎯 Evaluation completed with profile: {args.profile}")
        print("📈 Enhanced observability data captured in Logfire and TimescaleDB")

    except Exception as e:
        print(f"\n❌ Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
