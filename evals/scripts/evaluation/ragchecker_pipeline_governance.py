#!/usr/bin/env python3
"""
RAGChecker Pipeline Governance Integration
Integrates semantic process augmentation with existing RAGChecker evaluation system
"""

from __future__ import annotations

import copy
import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).resolve().parents[3]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from scripts.evaluation.ragchecker_official_evaluation import (
    OfficialRAGCheckerEvaluator,
)

# Add src to path for imports
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))  # REMOVED: DSPy venv consolidated into main project

# Import the RAG Pipeline Governance system
def _load_rag_pipeline_governance_module() -> tuple[Any, Any]:
    """Locate and import the rag pipeline governance module from known paths."""

    candidate_files = [
        Path(__file__).parent.parent / "testing" / "300_rag_pipeline_governance.py",
        Path(__file__).resolve().parents[2] / "stable_build" / "modules" / "300_rag_pipeline_governance.py",
        project_root / "evals" / "stable_build" / "modules" / "300_rag_pipeline_governance.py",
    ]

    for candidate in candidate_files:
        if candidate.exists():
            module_name = f"rag_pipeline_governance_{candidate.stem}"
            spec = importlib.util.spec_from_file_location(module_name, str(candidate))
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                return module.RAGPipelineGovernance, module.PipelineStage

    raise ImportError("Could not locate 300_rag_pipeline_governance.py in known locations")


RAGPipelineGovernance, PipelineStage = _load_rag_pipeline_governance_module()

# Import after path modification

logger = logging.getLogger(__name__)


class RAGCheckerPipelineGovernance:
    """
    RAGChecker Pipeline Governance with semantic process augmentation
    Integrates with existing RAGChecker evaluation system
    """

    def __init__(self):
        # Initialize the governance system
        self.governance: RAGPipelineGovernance = RAGPipelineGovernance()

        # Initialize RAGChecker evaluator
        self.ragchecker: OfficialRAGCheckerEvaluator = OfficialRAGCheckerEvaluator()

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
        validation_results["unusual_pattern"] = bool(is_unusual)

        # Suggest improvements
        if is_unusual:
            suggested_variant = self.governance.suggest_pipeline_variant(pipeline_id)
            if suggested_variant:
                validation_results["suggested_variant"] = suggested_variant

        # Clean up temporary pipeline
        if temp_id in self.governance.pipeline_graphs:
            del self.governance.pipeline_graphs[temp_id]
        if temp_id in self.governance.pipeline_metadata:
            del self.governance.pipeline_metadata[temp_id]

        return validation_results

    def optimize_ragchecker_pipeline(self, current_config: dict[str, Any]) -> dict[str, Any]:
        """Optimize a RAGChecker pipeline configuration using governance insights"""

        validation = self.validate_ragchecker_pipeline(current_config)
        optimized_config = copy.deepcopy(current_config)
        adjustments: list[str] = []

        temp_id = f"temp_optimization_{int(time.time())}"
        pipeline_id = self.governance.create_pipeline_graph(optimized_config, temp_id)

        try:
            if validation.get("errors"):
                logger.info("Pipeline validation reported errors; attempting to auto-fill missing stages")
                _ = self.governance.auto_fill_missing_steps(pipeline_id)
                optimized_config = copy.deepcopy(self.governance.pipeline_metadata[pipeline_id]["config"])
                adjustments.append("auto_fill_missing_steps")

            best_match = self.governance.suggest_pipeline_variant(pipeline_id)
            if best_match:
                reference_config = copy.deepcopy(self.governance.pipeline_metadata[best_match]["config"])
                merged_config = self._merge_pipeline_configs(reference_config, optimized_config)
                if merged_config != optimized_config:
                    optimized_config = merged_config
                    adjustments.append(f"merged_with_variant:{best_match}")

            revalidation = self.validate_ragchecker_pipeline(optimized_config)
            if not revalidation.get("valid", True) and best_match:
                logger.info("Optimized pipeline still invalid; falling back to known-good configuration")
                optimized_config = copy.deepcopy(self.governance.pipeline_metadata[best_match]["config"])
                adjustments.append("fallback_to_known_variant")
        finally:
            # Clean up temporary artifacts
            if temp_id in self.governance.pipeline_graphs:
                del self.governance.pipeline_graphs[temp_id]
            if temp_id in self.governance.pipeline_metadata:
                del self.governance.pipeline_metadata[temp_id]

        if adjustments:
            logger.info(f"Pipeline optimization adjustments applied: {', '.join(adjustments)}")
        else:
            logger.info("Pipeline configuration already aligned with known-good patterns")

        return optimized_config

    def _merge_pipeline_configs(
        self, reference_config: dict[str, Any], candidate_config: dict[str, Any]
    ) -> dict[str, Any]:
        """Merge pipeline configurations, giving precedence to candidate overrides."""

        merged = copy.deepcopy(reference_config)

        for stage_name, stage_config in candidate_config.items():
            if not isinstance(stage_config, dict):
                merged[stage_name] = stage_config
                continue

            stage_entry = merged.setdefault(stage_name, {"parameters": {}})
            if "parameters" not in stage_entry or not isinstance(stage_entry["parameters"], dict):
                stage_entry["parameters"] = {}

            candidate_params = stage_config.get("parameters", {})
            if isinstance(candidate_params, dict):
                stage_entry["parameters"].update(candidate_params)

            for key, value in stage_config.items():
                if key == "parameters":
                    continue
                stage_entry[key] = value

        return merged

    def generate_pipeline_variants(self, base_config: dict[str, Any], num_variants: int = 5) -> list[dict[str, Any]]:
        """Generate augmented pipeline variants for training and optimization"""

        # Create base pipeline
        base_id = self.governance.create_pipeline_graph(base_config, "base_pipeline")

        variants = []

        # Generate syntactic variants (Cat-2)
        for _ in range(num_variants // 2):
            variant_id = self.governance.augment_pipeline(base_id, "syntactic")
            variant_config = self.governance.pipeline_metadata[variant_id]["config"]
            variants.append({"config": variant_config, "type": "syntactic", "base_pipeline": base_id})

        # Generate semantic variants (Cat-1)
        for _ in range(num_variants - len(variants)):
            variant_id = self.governance.augment_pipeline(base_id, "semantic")
            variant_config = self.governance.pipeline_metadata[variant_id]["config"]
            variants.append({"config": variant_config, "type": "semantic", "base_pipeline": base_id})

        return variants

    def evaluate_pipeline_performance(self, pipeline_config: dict[str, Any], test_queries: list[str]) -> dict[str, Any]:
        """Evaluate pipeline performance using RAGChecker metrics"""

        baseline_config = copy.deepcopy(pipeline_config)
        baseline_validation = self.validate_ragchecker_pipeline(baseline_config)

        baseline_eval = self._run_simulated_evaluation(baseline_config, test_queries)
        if baseline_eval is None:
            return {"error": "All evaluations failed", "pipeline_config": baseline_config}

        best_config = baseline_config
        best_validation = baseline_validation
        best_eval = baseline_eval
        best_score = self._select_score(baseline_eval["average_metrics"])

        optimization_attempted = False
        optimized_choice_details: dict[str, Any] | None = None
        optimized_used = False

        candidate_config = self.optimize_ragchecker_pipeline(copy.deepcopy(baseline_config))
        if candidate_config != baseline_config:
            optimization_attempted = True
            candidate_validation = self.validate_ragchecker_pipeline(candidate_config)
            candidate_eval = self._run_simulated_evaluation(candidate_config, test_queries)

            if candidate_eval is not None:
                candidate_score = self._select_score(candidate_eval["average_metrics"])
                # Prefer the optimized configuration when it is not worse than baseline
                if candidate_score >= best_score - 1e-6:
                    best_config = candidate_config
                    best_validation = candidate_validation
                    best_eval = candidate_eval
                    best_score = candidate_score
                    optimized_used = True
                optimized_choice_details = candidate_eval

        result_payload: dict[str, Any] = {
            "pipeline_config": best_config,
            "validation_results": best_validation,
            "evaluation_results": best_eval["results"],
            "average_metrics": best_eval["average_metrics"],
            "success_rate": best_eval["success_rate"],
            "optimized": optimized_used,
            "optimization_attempted": optimization_attempted,
            "baseline_metrics": baseline_eval["average_metrics"],
        }

        if optimization_attempted and optimized_choice_details is not None:
            result_payload["optimized_metrics"] = optimized_choice_details["average_metrics"]
            result_payload["optimized_success_rate"] = optimized_choice_details["success_rate"]
        else:
            result_payload["optimized_metrics"] = None
            result_payload["optimized_success_rate"] = None

        return result_payload

    def _select_score(self, avg_metrics: dict[str, float]) -> float:
        """Select the comparison score used to choose between pipeline variants."""

        for key in ("f1_score", "f1", "precision", "recall"):
            if key in avg_metrics and isinstance(avg_metrics[key], int | float):
                return float(avg_metrics[key])
        return 0.0

    def _run_simulated_evaluation(
        self, pipeline_config: dict[str, Any], test_queries: list[str]
    ) -> dict[str, Any] | None:
        """Run the simulated evaluation workflow and aggregate metrics."""

        results: list[dict[str, Any]] = []
        for query in test_queries:
            try:
                simulated = self._simulate_ragchecker_evaluation(query, pipeline_config)
                results.append(simulated)
            except Exception as exc:  # pragma: no cover - logging path
                logger.error("Evaluation failed for query: %s, error: %s", query, exc)
                results.append({"query": query, "error": str(exc)})

        successful_results = [r for r in results if "error" not in r]
        if not successful_results:
            return None

        avg_metrics: dict[str, float] = {}
        for metric in ("precision", "recall", "f1_score", "context_utilization"):
            values = [float(r.get(metric, 0.0)) for r in successful_results]
            avg_metrics[metric] = sum(values) / len(values) if values else 0.0

        return {
            "results": successful_results,
            "average_metrics": avg_metrics,
            "success_rate": len(successful_results) / len(test_queries),
        }

    def _simulate_ragchecker_evaluation(self, query: str, pipeline_config: dict[str, Any]) -> dict[str, Any]:
        """Simulate RAGChecker evaluation (placeholder for actual integration)"""

        # This would integrate with your actual RAGChecker evaluation
        # For now, return simulated metrics based on pipeline configuration

        # Extract key parameters
        chunk_size = int(pipeline_config.get("chunk", {}).get("parameters", {}).get("chunk_size", 512))
        top_k = int(pipeline_config.get("retrieve", {}).get("parameters", {}).get("top_k", 5))
        temperature = float(pipeline_config.get("generate", {}).get("parameters", {}).get("temperature", 0.7))

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
                            "config": metadata.get("config", {}),
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
            chunk_size = int(config.get("chunk", {}).get("parameters", {}).get("chunk_size", 0))
            if chunk_size >= 500:  # Larger chunks often improve precision
                match_score += 0.3

        if "high_recall" in requirements and requirements["high_recall"]:
            # Check if pipeline has recall-optimized parameters
            config = metadata.get("config", {})
            top_k = int(config.get("retrieve", {}).get("parameters", {}).get("top_k", 0))
            if top_k >= 8:  # Higher top_k often improves recall
                match_score += 0.3

        if "fast_processing" in requirements and requirements["fast_processing"]:
            # Check if pipeline has speed-optimized parameters
            config = metadata.get("config", {})
            chunk_size = int(config.get("chunk", {}).get("parameters", {}).get("chunk_size", 9999))
            if chunk_size <= 400:  # Smaller chunks often process faster
                match_score += 0.2

        # Match on complexity
        node_count = len(metadata.get("graph", {}).get("nodes", [])) if "graph" in metadata else 0
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
    print(f"Governance report: {report}")
