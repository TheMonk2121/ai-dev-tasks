#!/usr/bin/env python3
"""
RAGChecker Pipeline Governance Integration
Integrates semantic process augmentation with existing RAGChecker evaluation system
"""

import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))

# Import the RAG Pipeline Governance system
sys.path.insert(0, str(Path(__file__).parent.parent / "300_experiments"))

spec = importlib.util.spec_from_file_location(
    "rag_pipeline_governance", str(Path(__file__).parent.parent / "300_experiments" / "300_rag_pipeline_governance.py")
)
if spec is None or spec.loader is None:
    raise ImportError("Could not load spec for 300_rag_pipeline_governance.py")
rag_governance_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rag_governance_module)
RAGPipelineGovernance = rag_governance_module.RAGPipelineGovernance
PipelineStage = rag_governance_module.PipelineStage

# Import after path modification
from ragchecker_official_evaluation import OfficialRAGCheckerEvaluator

logger = logging.getLogger(__name__)


class RAGCheckerPipelineGovernance:
    """
    RAGChecker Pipeline Governance with semantic process augmentation
    Integrates with existing RAGChecker evaluation system
    """

    def __init__(self):
        # Initialize the governance system
        self.governance = RAGPipelineGovernance()

        # Initialize RAGChecker evaluator
        self.ragchecker = OfficialRAGCheckerEvaluator()

        # Known good pipeline patterns from your system
        self._initialize_known_good_patterns()

        logger.info("RAGChecker Pipeline Governance initialized")

    def _initialize_known_good_patterns(self):
        """Initialize known good pipeline patterns from your RAGChecker system"""

        # Pattern 1: Standard RAGChecker evaluation pipeline
        standard_pipeline = {
            "ingest": {
                "parameters": {
                    "batch_size": 100,
                    "encoding": "utf-8",
                    "source_types": ["memory_system", "documentation"],
                }
            },
            "chunk": {
                "parameters": {"chunk_size": 512, "overlap": 50, "preserve_code_units": True, "enable_stitching": True}
            },
            "retrieve": {
                "parameters": {
                    "top_k": 5,
                    "similarity_threshold": 0.7,
                    "hybrid_weights": {"bm25": 0.55, "dense": 0.35, "metadata": 0.10},
                }
            },
            "rerank": {"parameters": {"rerank_top_k": 3, "model": "cross-encoder", "enable_reranking": True}},
            "generate": {
                "parameters": {"temperature": 0.7, "max_tokens": 1000, "min_citations": 2, "enable_abstention": True}
            },
            "validate": {"parameters": {"min_length": 10, "max_length": 5000, "enable_quality_gates": True}},
        }

        # Create and store the standard pipeline
        standard_id = self.governance.create_pipeline_graph(standard_pipeline, "ragchecker_standard")
        self.governance.known_good_patterns.add(standard_id)

        # Pattern 2: Enhanced evaluation pipeline (from your enhanced system)
        enhanced_pipeline = {
            "ingest": {
                "parameters": {
                    "batch_size": 100,
                    "encoding": "utf-8",
                    "source_types": ["memory_system", "documentation", "codebase"],
                }
            },
            "chunk": {
                "parameters": {"chunk_size": 300, "overlap": 64, "preserve_code_units": True, "enable_stitching": True}
            },
            "retrieve": {
                "parameters": {
                    "stage1_top_k": 24,
                    "stage2_top_k": 8,
                    "hybrid_weights": {"bm25": 0.55, "dense": 0.35, "metadata": 0.10},
                }
            },
            "rerank": {"parameters": {"rerank_top_k": 3, "model": "cross-encoder", "enable_reranking": True}},
            "generate": {
                "parameters": {
                    "temperature": 0.7,
                    "max_tokens": 500,
                    "min_citations": 2,
                    "enable_abstention": True,
                    "code_formatting": True,
                }
            },
            "validate": {
                "parameters": {
                    "min_length": 10,
                    "max_length": 5000,
                    "enable_quality_gates": True,
                    "comprehensive_metrics": True,
                }
            },
        }

        # Create and store the enhanced pipeline
        enhanced_id = self.governance.create_pipeline_graph(enhanced_pipeline, "ragchecker_enhanced")
        self.governance.known_good_patterns.add(enhanced_id)

        logger.info(f"Initialized {len(self.governance.known_good_patterns)} known good pipeline patterns")

    def validate_ragchecker_pipeline(self, pipeline_config: dict[str, Any]) -> dict[str, Any]:
        """Validate a RAGChecker pipeline configuration"""

        # Create a temporary pipeline ID for validation
        temp_id = f"temp_validation_{int(time.time())}"

        # Create pipeline graph
        pipeline_id = self.governance.create_pipeline_graph(pipeline_config, temp_id)

        # Validate the pipeline
        validation_results = self.governance.validate_pipeline(pipeline_id)

        # Check for unusual patterns
        is_unusual = self.governance.flag_unusual_plans(pipeline_id)
        validation_results["unusual_patterns"] = is_unusual

        # Suggest improvements
        if is_unusual or not validation_results["valid"]:
            suggested_variant = self.governance.suggest_pipeline_variant(pipeline_id)
            if suggested_variant:
                validation_results["suggested_variant"] = suggested_variant
                validation_results["suggestions"].append(f"Consider using known-good variant: {suggested_variant}")

        # Clean up temporary pipeline
        if temp_id in self.governance.pipeline_graphs:
            del self.governance.pipeline_graphs[temp_id]
        if temp_id in self.governance.pipeline_metadata:
            del self.governance.pipeline_metadata[temp_id]

        return validation_results

    def optimize_ragchecker_pipeline(self, current_config: dict[str, Any]) -> dict[str, Any]:
        """Optimize a RAGChecker pipeline configuration using governance insights"""

        # Validate current configuration
        validation = self.validate_ragchecker_pipeline(current_config)

        if validation["valid"] and not validation["unusual_patterns"]:
            logger.info("Pipeline is already optimal")
            return current_config

        # Find the best matching known-good pattern
        temp_id = f"temp_optimization_{int(time.time())}"
        pipeline_id = self.governance.create_pipeline_graph(current_config, temp_id)

        best_match = self.governance.suggest_pipeline_variant(pipeline_id)

        if best_match:
            # Get the known-good configuration
            best_config = self.governance.pipeline_metadata[best_match]["config"]
            logger.info(f"Optimized pipeline using variant: {best_match}")
            return best_config
        else:
            # Auto-fill missing steps
            optimized_id = self.governance.auto_fill_missing_steps(pipeline_id)
            optimized_config = self.governance.pipeline_metadata[optimized_id]["config"]
            logger.info("Optimized pipeline by auto-filling missing steps")
            return optimized_config

    def generate_pipeline_variants(self, base_config: dict[str, Any], num_variants: int = 5) -> list[dict[str, Any]]:
        """Generate augmented pipeline variants for training and optimization"""

        # Create base pipeline
        base_id = self.governance.create_pipeline_graph(base_config, "base_pipeline")

        variants = []

        # Generate syntactic variants (Cat-2)
        for i in range(num_variants // 2):
            variant_id = self.governance.augment_pipeline(base_id, "syntactic")
            variant_config = self.governance.pipeline_metadata[variant_id]["config"]
            variants.append({"config": variant_config, "type": "syntactic", "base_pipeline": base_id})

        # Generate semantic variants (Cat-1)
        for i in range(num_variants - len(variants)):
            variant_id = self.governance.augment_pipeline(base_id, "semantic")
            variant_config = self.governance.pipeline_metadata[variant_id]["config"]
            variants.append({"config": variant_config, "type": "semantic", "base_pipeline": base_id})

        return variants

    def evaluate_pipeline_performance(self, pipeline_config: dict[str, Any], test_queries: list[str]) -> dict[str, Any]:
        """Evaluate pipeline performance using RAGChecker metrics"""

        # Validate pipeline first
        validation = self.validate_ragchecker_pipeline(pipeline_config)

        if not validation["valid"]:
            # Try to optimize the pipeline first
            logger.info("Pipeline validation failed, attempting optimization...")
            optimized_config = self.optimize_ragchecker_pipeline(pipeline_config)

            # Re-validate optimized pipeline
            validation = self.validate_ragchecker_pipeline(optimized_config)

            if not validation["valid"]:
                return {
                    "error": "Invalid pipeline configuration even after optimization",
                    "validation_results": validation,
                }

            # Use optimized config for evaluation
            pipeline_config = optimized_config

        # Run evaluation with the pipeline configuration
        results = []

        for query in test_queries:
            try:
                # This would integrate with your actual RAGChecker evaluation
                # For now, we'll simulate the evaluation
                result = self._simulate_ragchecker_evaluation(query, pipeline_config)
                results.append(result)
            except Exception as e:
                logger.error(f"Evaluation failed for query: {query}, error: {e}")
                results.append({"query": query, "error": str(e)})

        # Calculate aggregate metrics
        successful_results = [r for r in results if "error" not in r]

        if not successful_results:
            return {"error": "All evaluations failed", "results": results}

        # Calculate average metrics
        avg_metrics = {}
        for metric in ["precision", "recall", "f1_score", "context_utilization"]:
            values = [r.get(metric, 0) for r in successful_results]
            avg_metrics[metric] = sum(values) / len(values) if values else 0

        return {
            "pipeline_config": pipeline_config,
            "validation_results": validation,
            "evaluation_results": results,
            "average_metrics": avg_metrics,
            "success_rate": len(successful_results) / len(test_queries),
        }

    def _simulate_ragchecker_evaluation(self, query: str, pipeline_config: dict[str, Any]) -> dict[str, Any]:
        """Simulate RAGChecker evaluation (placeholder for actual integration)"""

        # This would integrate with your actual RAGChecker evaluation
        # For now, return simulated metrics based on pipeline configuration

        # Extract key parameters
        chunk_size = pipeline_config.get("chunk", {}).get("parameters", {}).get("chunk_size", 512)
        top_k = pipeline_config.get("retrieve", {}).get("parameters", {}).get("top_k", 5)
        temperature = pipeline_config.get("generate", {}).get("parameters", {}).get("temperature", 0.7)

        # Simulate metrics based on parameter quality
        precision = min(0.9, 0.5 + (chunk_size / 1000) * 0.2 + (top_k / 10) * 0.1)
        recall = min(0.9, 0.4 + (chunk_size / 1000) * 0.3 + (top_k / 10) * 0.2)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        context_utilization = min(0.9, 0.6 + (temperature / 2) * 0.2)

        return {
            "query": query,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "context_utilization": context_utilization,
            "pipeline_params": {"chunk_size": chunk_size, "top_k": top_k, "temperature": temperature},
        }

    def get_pipeline_recommendations(self, requirements: dict[str, Any]) -> list[dict[str, Any]]:
        """Get pipeline recommendations based on requirements"""

        recommendations = []

        for pipeline_id in self.governance.known_good_patterns:
            if pipeline_id in self.governance.pipeline_metadata:
                metadata = self.governance.pipeline_metadata[pipeline_id]

                # Calculate match score
                match_score = self._calculate_requirement_match(requirements, metadata)

                if match_score > 0.3:  # Threshold for relevance
                    recommendations.append(
                        {
                            "pipeline_id": pipeline_id,
                            "config": metadata["config"],
                            "match_score": match_score,
                            "metadata": metadata,
                        }
                    )

        # Sort by match score
        recommendations.sort(key=lambda x: x["match_score"], reverse=True)

        return recommendations

    def _calculate_requirement_match(self, requirements: dict[str, Any], metadata: dict[str, Any]) -> float:
        """Calculate how well a pipeline matches given requirements"""

        match_score = 0.0

        # Match on performance requirements
        if "high_precision" in requirements and requirements["high_precision"]:
            # Check if pipeline has precision-optimized parameters
            config = metadata.get("config", {})
            chunk_size = config.get("chunk", {}).get("parameters", {}).get("chunk_size", 512)
            if chunk_size >= 500:  # Larger chunks often improve precision
                match_score += 0.3

        if "high_recall" in requirements and requirements["high_recall"]:
            # Check if pipeline has recall-optimized parameters
            config = metadata.get("config", {})
            top_k = config.get("retrieve", {}).get("parameters", {}).get("top_k", 5)
            if top_k >= 8:  # Higher top_k often improves recall
                match_score += 0.3

        if "fast_processing" in requirements and requirements["fast_processing"]:
            # Check if pipeline has speed-optimized parameters
            config = metadata.get("config", {})
            chunk_size = config.get("chunk", {}).get("parameters", {}).get("chunk_size", 512)
            if chunk_size <= 400:  # Smaller chunks often process faster
                match_score += 0.2

        # Match on complexity
        node_count = metadata.get("node_count", 0)
        if "complexity" in requirements:
            req_complexity = requirements["complexity"]
            if req_complexity == "simple" and node_count <= 6:
                match_score += 0.2
            elif req_complexity == "complex" and node_count > 6:
                match_score += 0.2

        return match_score

    def export_governance_report(self) -> dict[str, Any]:
        """Export comprehensive governance report"""

        return {
            "governance_system": {
                "total_pipelines": len(self.governance.pipeline_graphs),
                "known_good_patterns": len(self.governance.known_good_patterns),
                "pipeline_metadata": self.governance.pipeline_metadata,
            },
            "ragchecker_integration": {
                "evaluation_system": "RAGChecker Official Evaluation",
                "governance_enabled": True,
                "validation_active": True,
            },
            "recommendations": {
                "focus_areas": [
                    "Pipeline validation and optimization",
                    "Known-good pattern matching",
                    "Augmentation for training data generation",
                ],
                "next_steps": [
                    "Integrate with actual RAGChecker evaluation",
                    "Add performance monitoring",
                    "Implement automated optimization",
                ],
            },
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize governance system
    governance = RAGCheckerPipelineGovernance()

    # Test pipeline validation
    test_config = {
        "ingest": {"parameters": {"batch_size": 100}},
        "chunk": {"parameters": {"chunk_size": 512, "overlap": 50}},
        "retrieve": {"parameters": {"top_k": 5}},
        "generate": {"parameters": {"temperature": 0.7}},
        "validate": {"parameters": {"min_length": 10}},
    }

    # Validate pipeline
    validation = governance.validate_ragchecker_pipeline(test_config)
    print(f"Pipeline validation: {validation}")

    # Get recommendations
    requirements = {"high_precision": True, "fast_processing": True}
    recommendations = governance.get_pipeline_recommendations(requirements)
    print(f"Recommendations: {len(recommendations)} found")

    # Export report
    report = governance.export_governance_report()
    print(f"Governance report: {report['governance_system']['total_pipelines']} pipelines managed")
