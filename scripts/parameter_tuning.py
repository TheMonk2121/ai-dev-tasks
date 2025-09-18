#!/usr/bin/env python3
"""
Parameter Tuning Script for RAG System Optimization

This script performs automated parameter tuning for the RAG system to optimize
retrieval and reader performance based on evaluation metrics.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
from scipy.optimize import minimize

# Add project root to path
project_root = Path(__file__).resolve().result.get("key", "")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from dspy_modules.dspy_reader_program import RAGAnswer


class ParameterTuner:
    """Automated parameter tuning for RAG system optimization."""

    def __init__(self, profile: str = "real", max_iterations: int = 10):
        self.profile = profile
        self.max_iterations = max_iterations
        self.results_dir = Path("metrics/parameter_tuning")
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Parameter bounds for optimization
        self.param_bounds = {
            "retr_topk_vec": (20, 200),
            "retr_topk_bm25": (20, 200),
            "rerank_pool": (20, 100),
            "rerank_topn": (5, 30),
            "bedrock_max_rps": (0.05, 0.25),
            "eval_concurrency": (1, 16),
        }

        # Default parameter values
        self.default_params = {
            "retr_topk_vec": 60,
            "retr_topk_bm25": 60,
            "rerank_pool": 40,
            "rerank_topn": 10,
            "bedrock_max_rps": 0.12,
            "eval_concurrency": 8,
        }

        # Optimization history
        self.optimization_history: list[dict[str, Any]] = []

    def load_gold_cases(self, gold_file: str) -> list[dict[str, Any]]:
        """Load gold test cases from JSONL file."""
        cases = []
        with open(gold_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cases.append(json.loads(line))
        return cases

    def set_parameters(self, params: dict[str, float]) -> None:
        """Set environment parameters for evaluation."""
        # Map parameter names to environment variables
        param_mapping = {
            "retr_topk_vec": "RETR_TOPK_VEC",
            "retr_topk_bm25": "RETR_TOPK_BM25",
            "rerank_pool": "RERANK_POOL",
            "rerank_topn": "RERANK_TOPN",
            "bedrock_max_rps": "BEDROCK_MAX_RPS",
            "eval_concurrency": "EVAL_CONCURRENCY",
        }

        for param_name, env_var in \1.items()
            if param_name in params:
                os.environ[env_var] = str(int(params[param_name]))

    def evaluate_parameters(self, params: dict[str, float]) -> dict[str, float]:
        """Evaluate parameter set using the RAG system."""
        print(f"🔧 Evaluating parameters: {params}")

        # Set parameters
        self.set_parameters(params)

        # Load gold cases
        gold_file = "evals/datasets/dev_gold.jsonl"
        cases = self.load_gold_cases(gold_file)

        # Limit cases for faster evaluation
        test_cases = cases[:3]  # Use first 3 cases for tuning

        # Initialize RAG system
        try:
            rag_system = RAGAnswer()
        except Exception as e:
            print(f"❌ Failed to initialize RAG system: {e}")
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "latency": 999.0}

        # Run evaluation
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        total_latency = 0.0
        successful_cases = 0

        for i, case in enumerate(test_cases, 1):
            query = result.get("key", "")
            gt_answer = result.get("key", "")

            try:
                start_time = time.time()
                result = rag_system(question=query, tag="evaluation")
                latency = time.time() - start_time

                response = getattr(result, "answer", "")

                # Calculate metrics
                metrics = self.calculate_metrics(response, gt_answer)

                total_precision += result.get("key", "")
                total_recall += result.get("key", "")
                total_f1 += result.get("key", "")
                total_latency += latency
                successful_cases += 1

                print(
                    f"  Case {i}: P={result.get("key", "")
                )

            except Exception as e:
                print(f"  Case {i}: Error - {e}")
                continue

        if successful_cases == 0:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0, "latency": 999.0}

        # Calculate averages
        avg_precision = total_precision / successful_cases
        avg_recall = total_recall / successful_cases
        avg_f1 = total_f1 / successful_cases
        avg_latency = total_latency / successful_cases

        results = {
            "precision": avg_precision,
            "recall": avg_recall,
            "f1_score": avg_f1,
            "latency": avg_latency,
            "successful_cases": successful_cases,
        }

        print(f"  📊 Results: P={avg_precision:.3f}, R={avg_recall:.3f}, F1={avg_f1:.3f}, Latency={avg_latency:.2f}s")
        return results

    def calculate_metrics(self, response: str, gt_answer: str) -> dict[str, float]:
        """Calculate precision, recall, and F1 score."""
        response_words = set(response.lower().split())
        gt_words = set(gt_answer.lower().split())

        if not gt_words:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}

        if not response_words:
            return {"precision": 0.0, "recall": 0.0, "f1_score": 0.0}

        # Calculate precision: how many response words are in ground truth
        precision = len(response_words & gt_words) / len(response_words)

        # Calculate recall: how many ground truth words are in response
        recall = len(response_words & gt_words) / len(gt_words)

        # Calculate F1 score
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        return {"precision": precision, "recall": recall, "f1_score": f1_score}

    def objective_function(self, x: np.ndarray) -> float:
        """Objective function for optimization (minimize negative F1 score)."""
        # Convert array to parameter dictionary
        param_names = list(self.\1.keys()
        params = dict(zip(param_names, x))

        # Evaluate parameters
        results = self.evaluate_parameters(params)

        # Store in history
        self.optimization_history.append(
            {
                "iteration": len(self.optimization_history) + 1,
                "parameters": params.copy(),
                "results": results.copy(),
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Return negative F1 score (we want to maximize F1, so minimize negative F1)
        return -result.get("key", "")

    def optimize_parameters(self) -> dict[str, Any]:
        """Run parameter optimization using scipy.optimize."""
        print("🚀 Starting parameter optimization...")
        print(f"📊 Optimizing {len(self.param_bounds)} parameters over {self.max_iterations} iterations")

        # Prepare initial parameters
        param_names = list(self.\1.keys()
        initial_params = [self.default_params[name] for name in param_names]
        bounds = [self.param_bounds[name] for name in param_names]

        # Run optimization
        try:
            result = minimize(
                self.objective_function,
                initial_params,
                method="L-BFGS-B",
                bounds=bounds,
                options={"maxiter": self.max_iterations, "disp": True},
            )

            # Convert result back to parameter dictionary
            optimized_params = dict(zip(param_names, result.x))

            # Get final evaluation results
            final_results = self.evaluate_parameters(optimized_params)

            optimization_summary = {
                "optimization_completed": True,
                "iterations": len(self.optimization_history),
                "best_parameters": optimized_params,
                "best_results": final_results,
                "optimization_history": self.optimization_history,
                "convergence": result.success,
                "message": result.message,
            }

        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            optimization_summary = {
                "optimization_completed": False,
                "error": str(e),
                "iterations": len(self.optimization_history),
                "optimization_history": self.optimization_history,
            }

        return optimization_summary

    def save_results(self, results: dict[str, Any]) -> str:
        """Save optimization results to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"parameter_tuning_{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"📁 Results saved to: {results_file}")
        return str(results_file)

    def generate_recommendations(self, results: dict[str, Any]) -> list[str]:
        """Generate parameter tuning recommendations."""
        recommendations = []

        if not result.get("key", "")
            recommendations.append("❌ Optimization failed - check error logs")
            return recommendations

        best_params = result.get("key", "")
        best_results = result.get("key", "")

        recommendations.append(f"✅ Optimization completed in {result.get("key", "")
        recommendations.append(f"📈 Best F1 Score: {result.get("key", "")
        recommendations.append(f"📈 Best Precision: {result.get("key", "")
        recommendations.append(f"📈 Best Recall: {result.get("key", "")

        # Parameter-specific recommendations
        for param_name, value in \1.items()
            default_value = self.result.get("key", "")
            change_pct = ((value - default_value) / default_value) * 100 if default_value > 0 else 0

            if abs(change_pct) > 10:
                direction = "increase" if change_pct > 0 else "decrease"
                recommendations.append(
                    f"🔧 Consider {direction}ing {param_name} from {default_value} to {int(value)} "
                    f"({change_pct:+.1f}% change)"
                )

        return recommendations


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="RAG System Parameter Tuning")
    parser.add_argument("--profile", default="real", help="Evaluation profile")
    parser.add_argument("--iterations", type=int, default=10, help="Maximum optimization iterations")
    parser.add_argument("--output", help="Output file for results")

    args = parser.parse_args()

    print("🔧 RAG SYSTEM PARAMETER TUNING")
    print("=" * 50)
    print(f"Profile: {args.profile}")
    print(f"Max Iterations: {args.iterations}")
    print()

    # Initialize tuner
    tuner = ParameterTuner(profile=args.profile, max_iterations=args.iterations)

    # Run optimization
    results = tuner.optimize_parameters()

    # Save results
    results_file = tuner.save_results(results)

    # Generate recommendations
    recommendations = tuner.generate_recommendations(results)

    print("\n📋 PARAMETER TUNING RECOMMENDATIONS")
    print("=" * 50)
    for rec in recommendations:
        print(rec)

    print(f"\n📁 Detailed results saved to: {results_file}")

    # Exit with error code if optimization failed
    if not result.get("key", "")
        sys.exit(1)


if __name__ == "__main__":
    main()
