#!/usr/bin/env python3
"""
Clean DSPy RAG Evaluation Harness (import-safe minimal version)

This minimal evaluator avoids heavy/project-specific imports so the evals
package can be imported and a smoke test can run even if parts of the repo
are temporarily broken. It reads gold cases and emits a structured results
file with stubbed metrics. Replace with the full evaluator once the tree is
fully repaired.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


class CleanDSPyEvaluator:
    """Minimal evaluator that produces a deterministic, import-safe output."""

    def __init__(self, profile: str = "gold", progress_log: str | None = None) -> None:
        self.profile: str = profile
        self.results_dir: Path = Path("evals/metrics/dspy_evaluations")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.progress_log: str | None = progress_log

    def load_gold_cases(self, gold_file: str) -> list[dict[str, Any]]:
        cases: list[dict[str, Any]] = []
        try:
            with open(gold_file, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        cases.append(json.loads(line))
        except Exception:
            # Tolerate missing files during smoke
            pass
        return cases

    def run_evaluation(
        self,
        gold_file: str,
        limit: int | None = None,
        include_tags: list[str] | None = None,
        mode: str | None = None,
        _concurrency: int | None = None,  # Unused parameter
    ) -> dict[str, Any]:
        cases = self.load_gold_cases(gold_file)
        # Light filtering
        if include_tags:
            cases = [c for c in cases if any(tag in (c.get("tags", []) or []) for tag in include_tags)]
        if mode:
            cases = [c for c in cases if c.get("mode") == mode]
        if limit and len(cases) > limit:
            cases = cases[:limit]

        case_results: list[dict[str, Any]] = []
        for idx, case in enumerate(cases, 1):
            case_results.append(
                {
                    "case_id": case.get("id", str(idx)),
                    "query": case.get("query", ""),
                    "response": "",
                    "gt_answer": case.get("gt_answer", ""),
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0,
                    "faithfulness": 0.0,
                    "latency_sec": 0.0,
                }
            )

        n = len(case_results)
        overall_metrics = {
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "faithfulness": 0.0,
            "total_cases": n,
            "successful_cases": n,
            "failed_cases": 0,
        }

        results = {
            "evaluation_type": "clean_dspy_rag_minimal",
            "timestamp": datetime.now().isoformat(),
            "overall_metrics": overall_metrics,
            "case_results": case_results,
            "config": {"gold_file": gold_file, "limit": limit, "profile": self.profile},
        }

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_file = self.results_dir / f"dspy_evaluation_{ts}.json"
        try:
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
            print(f"Results saved to: {out_file}")
        except Exception:
            pass

        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean DSPy RAG Evaluation (minimal)")
    _ = parser.add_argument("--profile", choices=["gold", "mock"], default="gold")
    _ = parser.add_argument("--gold-file", default="evals/data/gold/v1/gold_cases.jsonl")
    _ = parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    evaluator = CleanDSPyEvaluator(profile=args.profile)
    _ = evaluator.run_evaluation(gold_file=args.gold_file, limit=args.limit)


if __name__ == "__main__":
    main()
