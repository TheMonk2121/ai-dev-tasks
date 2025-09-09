#!/usr/bin/env python3
"""
Run RAGChecker Evaluation with Pipeline Governance
Integrates semantic process augmentation with RAGChecker evaluation
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from ragchecker_pipeline_governance import RAGCheckerPipelineGovernance

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_governance_config(config_path: str = "../config/rag_pipeline_governance.json") -> dict[str, Any]:
    """Load governance configuration"""
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Configuration file not found: {config_path}, using defaults")
        return {}


def run_governed_evaluation(
    governance: RAGCheckerPipelineGovernance, config: dict[str, Any], pipeline_config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Run RAGChecker evaluation with governance validation"""

    # Use default pipeline config if none provided
    if pipeline_config is None:
        pipeline_config = {
            "ingest": {"parameters": {"batch_size": 100}},
            "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
            "retrieve": {"parameters": {"top_k": 5}},
            "rerank": {"parameters": {"rerank_top_k": 3}},
            "generate": {"parameters": {"temperature": 0.7}},
            "validate": {"parameters": {"min_length": 10}},
        }

    logger.info("🔍 Validating pipeline configuration...")

    # Validate pipeline configuration
    validation_results = governance.validate_ragchecker_pipeline(pipeline_config)

    if not validation_results["valid"]:
        logger.error("❌ Pipeline validation failed:")
        for error in validation_results["errors"]:
            logger.error(f"  - {error}")

        # Try to optimize the pipeline
        logger.info("🔧 Attempting to optimize pipeline...")
        optimized_config = governance.optimize_ragchecker_pipeline(pipeline_config)

        # Re-validate optimized pipeline
        validation_results = governance.validate_ragchecker_pipeline(optimized_config)

        if validation_results["valid"]:
            logger.info("✅ Pipeline optimization successful")
            pipeline_config = optimized_config
        else:
            logger.error("❌ Pipeline optimization failed, using original config")

    if validation_results["unusual_patterns"]:
        logger.warning("⚠️ Unusual patterns detected in pipeline")
        if "suggested_variant" in validation_results:
            logger.info(f"💡 Suggested variant: {validation_results['suggested_variant']}")

    # Run evaluation with validated pipeline
    logger.info("🚀 Running RAGChecker evaluation with governed pipeline...")

    # Get test queries from config
    test_queries = config.get("evaluation_config", {}).get(
        "test_queries",
        ["What is the current project status?", "How do I create a PRD?", "What are the DSPy integration patterns?"],
    )

    # Evaluate pipeline performance
    evaluation_results = governance.evaluate_pipeline_performance(pipeline_config, test_queries)

    # Check performance against targets
    performance_targets = config.get("evaluation_config", {}).get("performance_targets", {})

    performance_summary = {
        "pipeline_config": pipeline_config,
        "validation_results": validation_results,
        "evaluation_results": evaluation_results,
        "performance_targets": performance_targets,
        "targets_met": {},
    }

    # Check if targets are met
    if "average_metrics" in evaluation_results:
        avg_metrics = evaluation_results["average_metrics"]
        for metric, target in performance_targets.items():
            actual = avg_metrics.get(metric, 0)
            performance_summary["targets_met"][metric] = actual >= target
            logger.info(f"📊 {metric}: {actual:.3f} (target: {target:.3f}) {'✅' if actual >= target else '❌'}")

    return performance_summary


def generate_pipeline_variants(
    governance: RAGCheckerPipelineGovernance, base_config: dict[str, Any], num_variants: int = 5
) -> list[dict[str, Any]]:
    """Generate and evaluate pipeline variants"""

    logger.info(f"🔄 Generating {num_variants} pipeline variants...")

    variants = governance.generate_pipeline_variants(base_config, num_variants)

    logger.info(f"✅ Generated {len(variants)} variants")

    # Evaluate each variant
    variant_results = []
    for i, variant in enumerate(variants):
        logger.info(f"🧪 Evaluating variant {i+1}/{len(variants)} ({variant['type']})")

        # Get test queries
        test_queries = ["What is the current project status?", "How do I create a PRD?"]

        # Evaluate variant
        results = governance.evaluate_pipeline_performance(variant["config"], test_queries)

        variant_results.append(
            {"variant_id": i + 1, "type": variant["type"], "config": variant["config"], "results": results}
        )

    return variant_results


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description="Run RAGChecker evaluation with pipeline governance")
    parser.add_argument(
        "--config", default="../config/rag_pipeline_governance.json", help="Governance configuration file"
    )
    parser.add_argument("--pipeline-config", help="Custom pipeline configuration file")
    parser.add_argument("--generate-variants", type=int, default=0, help="Generate N pipeline variants")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Load configuration
    config = load_governance_config(args.config)

    # Load custom pipeline config if provided
    pipeline_config = None
    if args.pipeline_config:
        try:
            with open(args.pipeline_config) as f:
                pipeline_config = json.load(f)
        except FileNotFoundError:
            logger.error(f"Pipeline configuration file not found: {args.pipeline_config}")
            return 1

    # Initialize governance system
    logger.info("🔧 Initializing RAGChecker Pipeline Governance...")
    governance = RAGCheckerPipelineGovernance()

    # Run governed evaluation
    results = run_governed_evaluation(governance, config, pipeline_config)

    # Generate variants if requested
    if args.generate_variants > 0:
        logger.info(f"🔄 Generating {args.generate_variants} pipeline variants...")
        base_config = pipeline_config or {
            "ingest": {"parameters": {"batch_size": 100}},
            "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
            "retrieve": {"parameters": {"top_k": 5}},
            "generate": {"parameters": {"temperature": 0.7}},
            "validate": {"parameters": {"min_length": 10}},
        }

        variant_results = generate_pipeline_variants(governance, base_config, args.generate_variants)
        results["variants"] = variant_results

    # Export governance report
    governance_report = governance.export_governance_report()
    results["governance_report"] = governance_report

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"📄 Results saved to: {args.output}")
    else:
        print(json.dumps(results, indent=2))

    # Summary
    logger.info("📊 Evaluation Summary:")
    if "evaluation_results" in results and "average_metrics" in results["evaluation_results"]:
        avg_metrics = results["evaluation_results"]["average_metrics"]
        logger.info(f"  - Average Precision: {avg_metrics.get('precision', 0):.3f}")
        logger.info(f"  - Average Recall: {avg_metrics.get('recall', 0):.3f}")
        logger.info(f"  - Average F1 Score: {avg_metrics.get('f1_score', 0):.3f}")
        logger.info(f"  - Success Rate: {results['evaluation_results'].get('success_rate', 0):.3f}")

    if "targets_met" in results:
        targets_met = sum(results["targets_met"].values())
        total_targets = len(results["targets_met"])
        logger.info(f"  - Performance Targets Met: {targets_met}/{total_targets}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
