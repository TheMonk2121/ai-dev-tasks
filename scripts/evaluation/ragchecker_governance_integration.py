from __future__ import annotations
import json
import logging
import sys
from pathlib import Path
from typing import Any
from ragchecker_official_evaluation import OfficialRAGCheckerEvaluator
from ragchecker_pipeline_governance import RAGCheckerPipelineGovernance
    import argparse
import os
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
RAGChecker Governance Integration with Real Evaluation
Integrates the governance system with actual RAGChecker evaluation
"""

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)

class RAGCheckerGovernanceIntegration:
    """
    Full integration of RAGChecker evaluation with pipeline governance
    """

    def __init__(self):
        # Initialize governance system
        self.governance = RAGCheckerPipelineGovernance()

        # Initialize RAGChecker evaluator
        self.ragchecker = OfficialRAGCheckerEvaluator()

        logger.info("RAGChecker Governance Integration initialized")

    def evaluate_with_governance(
        self, pipeline_config: dict[str, Any] | None = None, use_bedrock: bool = True, num_cases: int = 5
    ) -> dict[str, Any]:
        """
        Run full RAGChecker evaluation with pipeline governance
        """

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
        validation_results = self.governance.validate_ragchecker_pipeline(pipeline_config)

        if not validation_results["valid"]:
            logger.warning("⚠️ Pipeline validation failed, attempting optimization...")
            optimized_config = self.governance.optimize_ragchecker_pipeline(pipeline_config)

            # Re-validate optimized pipeline
            validation_results = self.governance.validate_ragchecker_pipeline(optimized_config)

            if validation_results["valid"]:
                logger.info("✅ Pipeline optimization successful")
                pipeline_config = optimized_config
            else:
                logger.error("❌ Pipeline optimization failed, using original config")

        # Check for unusual patterns
        if validation_results.get("unusual_patterns", False):
            logger.warning("⚠️ Unusual patterns detected in pipeline")
            if "suggested_variant" in validation_results:
                logger.info(f"💡 Suggested variant: {validation_results['suggested_variant']}")

        # Run actual RAGChecker evaluation
        logger.info("🚀 Running RAGChecker evaluation with governed pipeline...")

        try:
            # Run the actual RAGChecker evaluation
            evaluation_results = self.ragchecker.run_official_evaluation(use_local_llm=False, use_bedrock=use_bedrock)

            # Extract key metrics
            overall_metrics = evaluation_results.get("overall_metrics", {})

            # Check against performance targets
            performance_targets = {"precision": 0.20, "recall": 0.45, "f1_score": 0.22, "context_utilization": 0.60}

            targets_met = {}
            for metric, target in performance_targets.items():
                actual = overall_metrics.get(metric, 0)
                targets_met[metric] = actual >= target
                status = "✅" if actual >= target else "❌"
                logger.info(f"📊 {metric}: {actual:.3f} (target: {target:.3f}) {status}")

            # Generate governance report
            governance_report = self.governance.export_governance_report()

            return {
                "pipeline_config": pipeline_config,
                "validation_results": validation_results,
                "evaluation_results": evaluation_results,
                "performance_targets": performance_targets,
                "targets_met": targets_met,
                "governance_report": governance_report,
                "success": True,
            }

        except Exception as e:
            logger.error(f"❌ RAGChecker evaluation failed: {e}")
            return {
                "pipeline_config": pipeline_config,
                "validation_results": validation_results,
                "error": str(e),
                "success": False,
            }

    def evaluate_pipeline_variants(
        self, base_config: dict[str, Any], num_variants: int = 5, use_bedrock: bool = True, num_cases: int = 3
    ) -> list[dict[str, Any]]:
        """
        Evaluate multiple pipeline variants using real RAGChecker evaluation
        """

        logger.info(f"🔄 Generating {num_variants} pipeline variants...")

        # Generate variants
        variants = self.governance.generate_pipeline_variants(base_config, num_variants)

        logger.info(f"✅ Generated {len(variants)} variants")

        # Evaluate each variant
        variant_results = []
        for i, variant in enumerate(variants):
            logger.info(f"🧪 Evaluating variant {i+1}/{len(variants)} ({variant['type']})")

            try:
                # Run evaluation for this variant
                result = self.evaluate_with_governance(
                    pipeline_config=variant["config"], use_bedrock=use_bedrock, num_cases=num_cases
                )

                variant_results.append(
                    {"variant_id": i + 1, "type": variant["type"], "config": variant["config"], "result": result}
                )

            except Exception as e:
                logger.error(f"❌ Variant {i+1} evaluation failed: {e}")
                variant_results.append(
                    {"variant_id": i + 1, "type": variant["type"], "config": variant["config"], "error": str(e)}
                )

        return variant_results

    def get_pipeline_recommendations(self, requirements: dict[str, Any]) -> list[dict[str, Any]]:
        """Get pipeline recommendations based on requirements"""
        return self.governance.get_pipeline_recommendations(requirements)

    def export_comprehensive_report(self) -> dict[str, Any]:
        """Export comprehensive report including governance and evaluation data"""
        governance_report = self.governance.export_governance_report()

        return {
            "integration_status": "operational",
            "governance_system": governance_report,
            "ragchecker_integration": {
                "evaluation_system": "OfficialRAGCheckerEvaluator",
                "governance_enabled": True,
                "validation_active": True,
                "optimization_active": True,
            },
            "capabilities": [
                "Pipeline validation and optimization",
                "Real RAGChecker evaluation integration",
                "Pipeline variant generation and testing",
                "Performance target monitoring",
                "Governance reporting and analysis",
            ],
        }

def main():
    """Main execution function"""

    parser = argparse.ArgumentParser(description="RAGChecker Governance Integration")
    parser.add_argument("--variants", type=int, default=0, help="Generate and evaluate N pipeline variants")
    parser.add_argument("--use-bedrock", action="store_true", help="Use Bedrock for evaluation")
    parser.add_argument("--num-cases", type=int, default=5, help="Number of test cases")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Initialize integration
    integration = RAGCheckerGovernanceIntegration()

    if args.variants > 0:
        # Generate and evaluate variants
        logger.info(f"🔄 Generating and evaluating {args.variants} pipeline variants...")

        base_config = {
            "ingest": {"parameters": {"batch_size": 100}},
            "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
            "retrieve": {"parameters": {"top_k": 5}},
            "rerank": {"parameters": {"rerank_top_k": 3}},
            "generate": {"parameters": {"temperature": 0.7}},
            "validate": {"parameters": {"min_length": 10}},
        }

        variant_results = integration.evaluate_pipeline_variants(
            base_config=base_config, num_variants=args.variants, use_bedrock=args.use_bedrock, num_cases=args.num_cases
        )

        results = {
            "variant_evaluation": variant_results,
            "comprehensive_report": integration.export_comprehensive_report(),
        }

    else:
        # Single evaluation
        logger.info("🚀 Running single RAGChecker evaluation with governance...")

        results = integration.evaluate_with_governance(use_bedrock=args.use_bedrock, num_cases=args.num_cases)

        results["comprehensive_report"] = integration.export_comprehensive_report()

    # Output results
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        logger.info(f"📄 Results saved to: {args.output}")
    else:
        print(json.dumps(results, indent=2))

    # Summary
    if "evaluation_results" in results and results.get("success", False):
        eval_results = results["evaluation_results"]
        overall_metrics = eval_results.get("overall_metrics", {})

        logger.info("📊 Evaluation Summary:")
        logger.info(f"  - Precision: {overall_metrics.get('precision', 0):.3f}")
        logger.info(f"  - Recall: {overall_metrics.get('recall', 0):.3f}")
        logger.info(f"  - F1 Score: {overall_metrics.get('f1_score', 0):.3f}")
        logger.info(f"  - Total Cases: {eval_results.get('total_cases', 0)}")

        if "targets_met" in results:
            targets_met = sum(results["targets_met"].values())
            total_targets = len(results["targets_met"])
            logger.info(f"  - Performance Targets Met: {targets_met}/{total_targets}")

if __name__ == "__main__":
    main()
