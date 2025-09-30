from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import os
import pathlib
import random
import subprocess
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

PROVENANCE_ENV_KEYS = [
    "EVAL_PROFILE",
    "EVAL_PROVIDER",
    "EVAL_DRIVER",
    "DSPY_MODEL",
    "RERANKER_MODEL",
    "SEED",
    "EVAL_SEED",
    "FEW_SHOT_SELECTOR",
    "FEW_SHOT_SEED",
    "RETR_TOPK_VEC",
    "RETR_TOPK_BM25",
    "RERANK_POOL",
    "RERANK_TOPN",
    "RERANK_KEEP",
    "MIN_RERANK_SCORE",
    "READER_PRECHECK_MIN_OVERLAP",
    "READER_MIN_OVERLAP_RATIO",
    "READER_MIN_OVERLAP_RATIO_CONFIG",
    "RETRIEVAL_CONFIG_PATH",
]


def _resolve_git_sha() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL)
            .decode("utf-8")
            .strip()
        )
    except Exception:
        return "unknown"


def _dataset_hash(path: Path) -> str:
    try:
        digest = hashlib.md5()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(8192), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except Exception:
        return "unknown"


def _determine_base_config_path(config_path: str) -> Path:
    """Resolve the base retrieval YAML that includes full settings."""
    candidate = Path(config_path)
    if candidate.exists():
        try:
            data = yaml.safe_load(candidate.read_text())
        except Exception:
            data = None
        if isinstance(data, dict) and {"fusion", "prefilter", "rerank"} & set(data.keys()):
            return candidate
    return Path("evals/stable_build/config/retrieval.yaml")


def _run_gold_smoke_eval(
    limit: int,
    out_dir: Path,
    config_variant: dict[str, Any] | None = None,
    base_config_path: Path | None = None,
) -> tuple[dict[str, float], Path | None]:
    """
    Run a gold-profile smoke evaluation through the repo dispatcher so the
    profile controls dataset paths and settings. Returns overall metrics.
    """
    import subprocess

    out_dir.mkdir(parents=True, exist_ok=True)

    env = os.environ.copy()
    env.pop("INGEST_RUN_ID", None)
    env.pop("CHUNK_VARIANT", None)
    env["UV_PROJECT_ENVIRONMENT"] = ".venv"

    temp_config_path: Path | None = None
    if config_variant:
        source_path = base_config_path or Path("evals/stable_build/config/retrieval.yaml")
        try:
            base_config = yaml.safe_load(source_path.read_text())
        except Exception:
            base_config = {}
        if not isinstance(base_config, dict):
            base_config = {}

        merged_config = copy.deepcopy(base_config)
        for section, overrides in config_variant.items():
            if not isinstance(overrides, dict):
                merged_config[section] = overrides
                continue
            target = merged_config.get(section)
            if isinstance(target, dict):
                target.update(overrides)
            else:
                merged_config[section] = overrides

        temp_config_path = out_dir / "retrieval_config.yaml"
        temp_config_path.write_text(yaml.safe_dump(merged_config, sort_keys=False), encoding="utf-8")
        env["RETRIEVAL_CONFIG_PATH"] = str(temp_config_path)
    else:
        env.pop("RETRIEVAL_CONFIG_PATH", None)

    cmd = [
        "uv",
        "run",
        "python",
        "scripts/evaluation/ragchecker_official_evaluation.py",
        "--profile",
        "gold",
        "--limit",
        str(limit),
        "--outdir",
        str(out_dir),
    ]
    subprocess.run(cmd, check=True, env=env)

    json_candidates = sorted(out_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not json_candidates:
        return ({"recall_at_20": 0.0, "precision_at_k": 0.0, "f1_score": 0.0, "faithfulness": 0.0}, None)
    latest = json_candidates[0]
    try:
        data = json.loads(latest.read_text())
        overall = data.get("overall_metrics", data)
        return (
            {
                "recall_at_20": float(overall.get("recall", overall.get("recall_at_20", 0.0))),
                "precision_at_k": float(overall.get("precision", overall.get("precision_at_k", 0.0))),
                "f1_score": float(overall.get("f1_score", overall.get("f1", 0.0))),
                "faithfulness": float(overall.get("faithfulness", 0.0)),
            },
            latest,
        )
    except Exception:
        return ({"recall_at_20": 0.0, "precision_at_k": 0.0, "f1_score": 0.0, "faithfulness": 0.0}, latest)


def _collect_provenance(
    *,
    config_variant: dict[str, Any],
    metrics: dict[str, float],
    score: float,
    eval_time: float,
    metrics_path: Path | None,
    gold_limit: int,
    dry_run: bool,
    run_id: str,
    run_dir: Path,
) -> dict[str, Any]:
    env_overrides = {key: os.getenv(key) for key in PROVENANCE_ENV_KEYS if os.getenv(key) is not None}
    dataset_path = Path(os.getenv("GOLD_CASES_PATH", "evals/data/gold/v1/gold_cases_121.jsonl"))
    provider = os.getenv("EVAL_PROVIDER")
    model = os.getenv("DSPY_MODEL")
    reranker_model = os.getenv("RERANKER_MODEL")
    seed = (
        os.getenv("SEED")
        or os.getenv("EVAL_SEED")
        or os.getenv("FEW_SHOT_SEED")
    )

    entry = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "run_id": run_id,
        "git_sha": _resolve_git_sha(),
        "profile": "gold",
        "gold_limit": gold_limit,
        "dry_run": dry_run,
        "eval_time_seconds": eval_time,
        "env_overrides": env_overrides,
        "provider": provider,
        "model": model,
        "reranker_model": reranker_model,
        "seed": seed,
        "config": config_variant,
        "metrics": metrics,
        "score": score,
        "metrics_path": str(metrics_path) if metrics_path else None,
        "dataset_path": str(dataset_path),
        "dataset_hash": _dataset_hash(dataset_path),
        "run_dir": str(run_dir),
    }
    return entry

def tune_retrieval(
    config_path: str,
    max_evals: int = 50,
    output_path: str = "tuning_results.json",
    gold_limit: int = 5,
    dry_run: bool = False,
) -> None:
    """Perform hyperparameter tuning."""
    print(f"🔧 Starting retrieval tuning with max {max_evals} evaluations")

    # Load base config
    config = load_config(config_path)
    base_config_path = _determine_base_config_path(config_path)

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

    # Prepare output directories
    run_id = time.strftime("%Y%m%d_%H%M%S")
    run_dir = Path("metrics/tuning_runs") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # Evaluate each configuration
    results: list[dict[str, Any]] = []
    best_score: float | None = None
    best_config: dict[str, Any] | None = None
    best_metrics: dict[str, float] | None = None

    # Prepare manifest output
    manifest_path = Path("metrics/parameter_tuning/manifest.jsonl")
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    run_manifest_path = run_dir / "run_manifest.jsonl"

    for i, config_variant in enumerate(search_configs):
        print(f"⚡ Evaluating configuration {i+1}/{len(search_configs)}")

        start_time = time.time()
        trial_dir = run_dir / f"trial_{i+1:03d}"

        if dry_run:
            metrics, metrics_path = (
                {"recall_at_20": 0.0, "precision_at_k": 0.0, "f1_score": 0.0, "faithfulness": 0.0},
                None,
            )
        else:
            metrics, metrics_path = _run_gold_smoke_eval(
                gold_limit,
                trial_dir,
                config_variant=config_variant,
                base_config_path=base_config_path,
            )
        eval_time = time.time() - start_time

        # Calculate composite score (weighted F1 + recall)
        score = 0.6 * metrics["f1_score"] + 0.4 * metrics["recall_at_20"]

        result = {"config": config_variant, "metrics": metrics, "score": score, "eval_time": eval_time}
        results.append(result)

        # Append manifest entry (one JSON object per line)
        manifest_entry = _collect_provenance(
            config_variant=config_variant,
            metrics=metrics,
            score=score,
            eval_time=eval_time,
            metrics_path=metrics_path,
            gold_limit=gold_limit,
            dry_run=dry_run,
            run_id=run_id,
            run_dir=run_dir,
        )
        with manifest_path.open("a", encoding="utf-8") as mf:
            mf.write(json.dumps(manifest_entry) + "\n")
        with run_manifest_path.open("a", encoding="utf-8") as rm:
            rm.write(json.dumps(manifest_entry) + "\n")

    # Optionally write a simple before/after comparison artifact if baseline is known
    try:
        baseline_candidates = list((Path("metrics/baseline_evaluations")).glob("*.json"))
        if baseline_candidates and results:
            baseline_path = max(baseline_candidates, key=lambda p: p.stat().st_mtime)
            baseline = json.loads(baseline_path.read_text())
            baseline_overall = baseline.get("overall_metrics", baseline)
            best = max(results, key=lambda r: r["score"])
            comparison = {
                "baseline": {
                    "path": str(baseline_path),
                    "precision": float(baseline_overall.get("precision", baseline_overall.get("precision_at_k", 0.0))),
                    "recall": float(baseline_overall.get("recall", baseline_overall.get("recall_at_20", 0.0))),
                    "f1": float(baseline_overall.get("f1_score", baseline_overall.get("f1", 0.0))),
                },
                "candidate_best": {
                    "precision": float(best["metrics"].get("precision_at_k", 0.0)),
                    "recall": float(best["metrics"].get("recall_at_20", 0.0)),
                    "f1": float(best["metrics"].get("f1_score", 0.0)),
                    "config": best["config"],
                },
            }
            (run_dir / "comparison.json").write_text(json.dumps(comparison, indent=2))
    except Exception:
        pass

        # Track best (keep first-on-tie to preserve deterministic ordering)
        if best_score is None or score > best_score:
            best_score = score
            best_config = config_variant
            best_metrics = metrics

        # Validate against quality gates
        gate_result = validate_evaluation_results(metrics)
        gate_status = "✅ PASS" if gate_result.passed else "⚠️ SOFT_FAIL"

        print(
            f"  Score: {score:.3f}, F1: {metrics['f1_score']:.3f}, "
            f"Recall@20: {metrics['recall_at_20']:.3f}, Gates: {gate_status}"
        )

    if not results:
        print("❌ No tuning results captured; aborting summary.")
        return

    # Sort results by score
    results.sort(key=lambda x: x["score"], reverse=True)

    best_score_value = best_score if best_score is not None else results[0]["score"]
    best_config_value = best_config or results[0]["config"]
    best_metrics_value = best_metrics or results[0]["metrics"]

    score_set = {r["score"] for r in results}
    all_scores_tied = len(score_set) == 1

    # Save results
    output_data = {
        "tuning_summary": {
            "total_configs": len(results),
            "best_score": best_score_value,
            "best_config": best_config_value,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "all_scores_tied": all_scores_tied,
        },
        "results": results,
    }

    pathlib.Path(output_path).write_text(json.dumps(output_data, indent=2))
    print(f"💾 Results saved to {output_path}")
    # Final JSON line for downstream tooling
    final_payload = {
        **output_data,
        "run_id": run_id,
        "run_dir": str(run_dir),
        "manifest": str(run_manifest_path),
        "provider": os.getenv("EVAL_PROVIDER"),
        "model": os.getenv("DSPY_MODEL"),
        "reranker_model": os.getenv("RERANKER_MODEL"),
        "seed": os.getenv("SEED")
        or os.getenv("EVAL_SEED")
        or os.getenv("FEW_SHOT_SEED"),
    }
    print(json.dumps(final_payload))

    # Print summary
    print("\n🏆 Tuning Results Summary:")
    print(f"   Best Score: {best_score_value:.3f}")
    print(f"   Best F1: {best_metrics_value['f1_score']:.3f}")
    print(f"   Best Recall@20: {best_metrics_value['recall_at_20']:.3f}")
    if all_scores_tied:
        print("   ⚠️ All candidates produced identical scores; reporting first configuration.")
    print("\n🔧 Best Configuration:")
    for section, params in best_config_value.items():
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
    parser.add_argument("--gold-limit", type=int, default=5, help="Gold profile limit per trial")
    parser.add_argument("--dry-run", action="store_true", help="Skip real evals and emit zeroed metrics")

    args = parser.parse_args()

    tune_retrieval(args.config, args.max_evals, args.output, args.gold_limit, args.dry_run)

if __name__ == "__main__":
    main()
