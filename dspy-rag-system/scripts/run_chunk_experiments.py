#!/usr/bin/env python3
"""
Chunking Experiments Script
- Chunk size sweep (300/450/700/900)
- Prefix policy A/B test
- Dedup threshold experiment (0.7/0.8/0.9)
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


def run_evaluation() -> dict[str, Any]:
    """Run RAGChecker evaluation and return results"""
    print("Running RAGChecker evaluation...")

    # Set environment variables
    env = os.environ.copy()
    env["AWS_REGION"] = "us-east-1"

    try:
        result = subprocess.run(
            ["python3", "scripts/ragchecker_official_evaluation.py", "--use-bedrock", "--bypass-cli"],
            capture_output=True,
            text=True,
            env=env,
            cwd="/Users/danieljacobs/Code/ai-dev-tasks",
        )

        if result.returncode != 0:
            print(f"Evaluation failed: {result.stderr}")
            return {}

        # Parse results from stdout or find latest results file
        results_dir = Path("/Users/danieljacobs/Code/ai-dev-tasks/metrics/baseline_evaluations")
        if results_dir.exists():
            latest_file = max(results_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, default=None)
            if latest_file:
                with open(latest_file) as f:
                    return json.load(f)

        return {}

    except Exception as e:
        print(f"Error running evaluation: {e}")
        return {}


def run_ingestion(chunk_size: int, embedder: str = "sentence-transformers/all-MiniLM-L6-v2") -> bool:
    """Run ingestion with specific chunk size"""
    print(f"Running ingestion with chunk size {chunk_size}...")

    try:
        result = subprocess.run(
            [
                "python3",
                "dspy-rag-system/scripts/ingest_enhanced.py",
                "--glob",
                "000_core/**/*.md,100_memory/**/*.md,400_guides/**/*.md",
                "--embedder",
                embedder,
                "--chunk-size",
                str(chunk_size),
                "--use-enhanced-chunking",
                "--force",
                "--rebuild",
            ],
            capture_output=True,
            text=True,
            cwd="/Users/danieljacobs/Code/ai-dev-tasks",
        )

        if result.returncode != 0:
            print(f"Ingestion failed: {result.stderr}")
            return False

        return True

    except Exception as e:
        print(f"Error running ingestion: {e}")
        return False


def experiment_chunk_size_sweep():
    """Experiment 1: Chunk size sweep (300/450/700/900)"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 1: Chunk Size Sweep")
    print("=" * 60)

    chunk_sizes = [300, 450, 700, 900]
    results = {}

    for chunk_size in chunk_sizes:
        print(f"\n--- Testing chunk size: {chunk_size} ---")

        # Run ingestion
        if not run_ingestion(chunk_size):
            print(f"Failed to ingest with chunk size {chunk_size}")
            continue

        # Wait a moment for database to settle
        time.sleep(2)

        # Run evaluation
        eval_results = run_evaluation()

        if eval_results:
            results[chunk_size] = {
                "precision": eval_results.get("summary", {}).get("precision", 0),
                "recall": eval_results.get("summary", {}).get("recall", 0),
                "f1": eval_results.get("summary", {}).get("f1", 0),
                "oracle_retrieval_hit": eval_results.get("summary", {}).get("oracle_retrieval_hit_prefilter", 0),
                "oracle_filter_hit": eval_results.get("summary", {}).get("oracle_filter_hit_postfilter", 0),
                "reader_used_gold": eval_results.get("summary", {}).get("reader_used_gold", 0),
            }
            print(
                f"Results: P={results[chunk_size]['precision']:.3f}, R={results[chunk_size]['recall']:.3f}, F1={results[chunk_size]['f1']:.3f}"
            )
        else:
            print("No evaluation results")

    # Save results
    with open("experiment_chunk_size_sweep.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\nChunk Size Sweep Results:")
    print("Chunk Size | Precision | Recall | F1     | Oracle Retrieval | Oracle Filter | Reader Gold")
    print("-" * 80)
    for chunk_size, metrics in results.items():
        print(
            f"{chunk_size:10} | {metrics['precision']:8.3f} | {metrics['recall']:6.3f} | {metrics['f1']:6.3f} | {metrics['oracle_retrieval_hit']:15.3f} | {metrics['oracle_filter_hit']:12.3f} | {metrics['reader_used_gold']:10.3f}"
        )

    return results


def experiment_prefix_policy_ab():
    """Experiment 2: Prefix policy A/B test"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 2: Prefix Policy A/B Test")
    print("=" * 60)

    # This would require modifying the chunking config
    # For now, we'll just document the approach
    print("Prefix Policy A/B Test:")
    print("A: prefix in embeddings only (current implementation)")
    print("B: prefix in both embeddings & sparse titles only")
    print("\nTo implement this experiment:")
    print("1. Modify create_contextual_prefix() to have two modes")
    print("2. Run ingestion with each mode")
    print("3. Compare oracle metrics")
    print("\nCurrent implementation uses mode A (prefix in embeddings only)")

    return {}


def experiment_dedup_threshold():
    """Experiment 3: Dedup threshold experiment (0.7/0.8/0.9)"""
    print("\n" + "=" * 60)
    print("EXPERIMENT 3: Dedup Threshold Test")
    print("=" * 60)

    # This would require modifying the chunking config
    # For now, we'll just document the approach
    print("Dedup Threshold Test:")
    print("Testing Jaccard thresholds: 0.7, 0.8, 0.9")
    print("\nTo implement this experiment:")
    print("1. Modify ChunkingConfig to accept jaccard_threshold")
    print("2. Run ingestion with each threshold")
    print("3. Compare oracle_retrieval_hit_prefilter (watch for too aggressive dedup)")
    print("\nCurrent implementation uses threshold 0.8")

    return {}


def main():
    """Run all experiments"""
    load_dotenv()

    parser = argparse.ArgumentParser("Chunking Experiments")
    parser.add_argument(
        "--experiment", choices=["chunk_size", "prefix", "dedup", "all"], default="all", help="Which experiment to run"
    )
    parser.add_argument("--quick", action="store_true", help="Run quick test with smaller dataset")
    args = parser.parse_args()

    if not os.getenv("DATABASE_URL"):
        print("DATABASE_URL not set")
        sys.exit(1)

    print("Starting Chunking Experiments")
    print("=" * 60)

    results = {}

    if args.experiment in ["chunk_size", "all"]:
        results["chunk_size_sweep"] = experiment_chunk_size_sweep()

    if args.experiment in ["prefix", "all"]:
        results["prefix_policy"] = experiment_prefix_policy_ab()

    if args.experiment in ["dedup", "all"]:
        results["dedup_threshold"] = experiment_dedup_threshold()

    # Save all results
    with open("experiment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print("EXPERIMENT SUMMARY")
    print("=" * 60)

    if "chunk_size_sweep" in results and results["chunk_size_sweep"]:
        best_chunk_size = max(results["chunk_size_sweep"].items(), key=lambda x: x[1]["f1"])
        print(f"Best chunk size: {best_chunk_size[0]} (F1: {best_chunk_size[1]['f1']:.3f})")

    print("\nAll results saved to experiment_results.json")
    print("Next steps:")
    print("1. Analyze results to find optimal chunk size")
    print("2. Implement prefix policy A/B test")
    print("3. Implement dedup threshold experiment")
    print("4. Run full evaluation with best settings")


if __name__ == "__main__":
    main()
