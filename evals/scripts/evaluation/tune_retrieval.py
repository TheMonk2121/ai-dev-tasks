from __future__ import annotations

import argparse
import itertools
import json
import os
import pathlib
import random
import sys
import time
from pathlib import Path
from typing import Any, Optional, Union

import yaml  # type: ignore[import-untyped]

from retrieval.quality_gates import validate_evaluation_results

#!/usr/bin/env python3
"""
Retrieval Tuning Utility

Performs hyperparameter search over retrieval configuration space
to optimize RAGChecker evaluation metrics.
"""

# Add src to path for retrieval modules
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

def load_config(config_path: str = "config/retrieval.yaml") -> dict[str, Any]:
    """Load retrieval configuration."""
    return yaml.safe_load(pathlib.Path(config_path).read_text())

def generate_search_configs(config: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate all combinations from search spaces."""
    search_spaces = config.get("tuning", {}).get("search_spaces", {})

    if not search_spaces:
        print("⚠️ No search spaces defined in config")
        return []

    # Extract parameter grids
    fusion_params = search_spaces.get("fusion", {})
    rerank_params = search_spaces.get("rerank", {})
    prefilter_params = search_spaces.get("prefilter", {})

    # Generate all combinations
    combinations = []

    # Fusion parameters
    lambda_lex_values = fusion_params.get("lambda_lex", [0.6])
    lambda_sem_values = fusion_params.get("lambda_sem", [0.4])
    k_values = fusion_params.get("k", [60])

    # Rerank parameters
    alpha_values = rerank_params.get("alpha", [0.7])
    final_top_n_values = rerank_params.get("final_top_n", [8])

    # Prefilter parameters
    min_bm25_values = prefilter_params.get("min_bm25_score", [0.1])
    min_vector_values = prefilter_params.get("min_vector_score", [0.7])
    diversity_values = prefilter_params.get("diversity_threshold", [0.9])

    # Generate Cartesian product
    for combo in itertools.product(
        lambda_lex_values,
        lambda_sem_values,
        k_values,
        alpha_values,
        final_top_n_values,
        min_bm25_values,
        min_vector_values,
        diversity_values,
    ):
        (lambda_lex, lambda_sem, k, alpha, final_top_n, min_bm25, min_vector, diversity) = combo

        # Ensure lambdas sum to 1.0
        total = lambda_lex + lambda_sem
        if total > 0:
            lambda_lex = lambda_lex / total
            lambda_sem = lambda_sem / total

        combinations.append(
            {
                "fusion": {"lambda_lex": lambda_lex, "lambda_sem": lambda_sem, "k": k},
                "rerank": {"alpha": alpha, "final_top_n": final_top_n},
                "prefilter": {
                    "min_bm25_score": min_bm25,
                    "min_vector_score": min_vector,
                    "diversity_threshold": diversity,
                },
            }
        )

    return combinations

def simulate_evaluation(config_variant: dict[str, Any]) -> dict[str, float]:
    """Simulate evaluation metrics for a config variant.

    In practice, this would run actual RAGChecker evaluation.
    For now, we simulate based on parameter combinations.
    """
    fusion = config_variant["fusion"]
    rerank = config_variant["rerank"]
    prefilter = config_variant["prefilter"]

    # Simulate metrics based on parameter values
    # Higher lambda_lex typically helps precision for config queries
    # Higher lambda_sem helps recall for conceptual queries
    # Higher alpha gives more weight to reranker

    base_recall = 0.15
    base_precision = 0.08
    base_faithfulness = 0.65

    # Fusion impact
    recall_boost = (fusion["lambda_sem"] - 0.4) * 0.3  # semantic helps recall
    precision_boost = (fusion["lambda_lex"] - 0.6) * 0.2  # lexical helps precision

    # Rerank impact
    recall_boost += (rerank["alpha"] - 0.7) * 0.15  # reranker helps both
    precision_boost += (rerank["alpha"] - 0.7) * 0.20

    # Prefilter impact (conservative thresholds help precision)
    precision_boost += (prefilter["min_vector_score"] - 0.7) * 0.10

    # Calculate final metrics with noise

    random.seed(hash(str(config_variant)) % 1000)

    recall = max(0.05, base_recall + recall_boost + random.uniform(-0.02, 0.02))
    precision = max(0.01, base_precision + precision_boost + random.uniform(-0.02, 0.02))
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.01
    faithfulness = max(0.3, base_faithfulness + random.uniform(-0.05, 0.05))

    return {"recall_at_20": recall, "precision_at_k": precision, "f1_score": f1, "faithfulness": faithfulness}

def tune_retrieval(config_path: str, max_evals: int = 50, output_path: str = "tuning_results.json") -> None:
    """Perform hyperparameter tuning."""
    print(f"🔧 Starting retrieval tuning with max {max_evals} evaluations")

    # Load base config
    config = load_config(config_path)

    # Generate search configurations
    search_configs = generate_search_configs(config)
    if not search_configs:
        print("❌ No search configurations generated")
        return

    print(f"📊 Generated {len(search_configs)} parameter combinations")

    # Limit evaluations
    if len(search_configs) > max_evals:

        search_configs = random.sample(search_configs, max_evals)
        print(f"🎲 Randomly sampled {max_evals} configurations")

    # Evaluate each configuration
    results = []
    best_score = 0.0
    best_config = None

    for i, config_variant in enumerate(search_configs):
        print(f"⚡ Evaluating configuration {i+1}/{len(search_configs)}")

        start_time = time.time()
        metrics = simulate_evaluation(config_variant)
        eval_time = time.time() - start_time

        # Calculate composite score (weighted F1 + recall)
        score = 0.6 * metrics["f1_score"] + 0.4 * metrics["recall_at_20"]

        result = {"config": config_variant, "metrics": metrics, "score": score, "eval_time": eval_time}
        results.append(result)

        # Track best
        if score > best_score:
            best_score = score
            best_config = config_variant

        # Validate against quality gates
        gate_result = validate_evaluation_results(metrics)
        gate_status = "✅ PASS" if gate_result.passed else "⚠️ SOFT_FAIL"

        print(
            f"  Score: {score:.3f}, F1: {metrics['f1_score']:.3f}, "
            f"Recall@20: {metrics['recall_at_20']:.3f}, Gates: {gate_status}"
        )

    # Sort results by score
    results.sort(key=lambda x: x["score"], reverse=True)

    # Save results
    output_data = {
        "tuning_summary": {
            "total_configs": len(results),
            "best_score": best_score,
            "best_config": best_config,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "results": results,
    }

    pathlib.Path(output_path).write_text(json.dumps(output_data, indent=2))
    print(f"💾 Results saved to {output_path}")

    # Print summary
    print("\n🏆 Tuning Results Summary:")
    print(f"   Best Score: {best_score:.3f}")
    print(f"   Best F1: {results[0]['metrics']['f1_score']:.3f}")
    print(f"   Best Recall@20: {results[0]['metrics']['recall_at_20']:.3f}")
    print("\n🔧 Best Configuration:")
    for section, params in best_config.items():
        print(f"   {section}:")
        for key, value in params.items():
            print(f"     {key}: {value}")

    # Show top 5 configurations
    print("\n📊 Top 5 Configurations:")
    for i, result in enumerate(results[:5]):
        metrics = result["metrics"]
        print(
            f"   {i+1}. Score: {result['score']:.3f}, "
            f"F1: {metrics['f1_score']:.3f}, "
            f"Recall: {metrics['recall_at_20']:.3f}"
        )

def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Retrieval hyperparameter tuning")
    parser.add_argument("--config", default="config/retrieval.yaml", help="Path to retrieval config file")
    parser.add_argument("--max-evals", type=int, default=50, help="Maximum number of evaluations to run")
    parser.add_argument("--output", default="tuning_results.json", help="Output file for results")

    args = parser.parse_args()

    tune_retrieval(args.config, args.max_evals, args.output)

if __name__ == "__main__":
    main()
