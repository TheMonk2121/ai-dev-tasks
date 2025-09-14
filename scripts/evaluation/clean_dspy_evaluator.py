#!/usr/bin/env python3
"""
Clean DSPy RAG Evaluation Harness

A focused, working evaluation system that properly tests the DSPy RAG system
with gold questions. Simple, reliable, and easy to understand.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import DSPy RAG system
from dspy_modules.dspy_reader_program import RAGAnswer


class CleanDSPyEvaluator:
    """Clean, focused evaluator for DSPy RAG system."""

    def __init__(self, profile: str = "gold", progress_log: str = None):
        self.profile = profile
        self.results_dir = Path("metrics/dspy_evaluations")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.progress_log = progress_log
        self._progress_fh = None

        # Set up environment based on profile
        self._setup_profile_environment()

        # Open progress logging if specified
        if self.progress_log:
            self._progress_fh = open(self.progress_log, "w", encoding="utf-8")

    def _setup_profile_environment(self):
        """Set up environment variables based on profile."""
        if self.profile == "gold":
            # Gold profile: Real RAG + gold cases
            os.environ.setdefault("EVAL_DRIVER", "dspy_rag")
            os.environ.setdefault("RAGCHECKER_USE_REAL_RAG", "1")
            os.environ.setdefault("EVAL_PROFILE", "gold")
            os.environ.setdefault("USE_GOLD", "1")
            os.environ.setdefault("GOLD_CASES_PATH", "300_evals/data/gold/v1/gold_cases.jsonl")
            os.environ.setdefault("EVAL_CONCURRENCY", "8")
        elif self.profile == "mock":
            # Mock profile: Synthetic responses only
            os.environ.setdefault("EVAL_DRIVER", "synthetic")
            os.environ.setdefault("RAGCHECKER_USE_REAL_RAG", "0")
            os.environ.setdefault("EVAL_PROFILE", "mock")
            os.environ.setdefault("POSTGRES_DSN", "mock://test")
            os.environ.setdefault("EVAL_CONCURRENCY", "3")
        else:
            raise ValueError(f"Unknown profile: {self.profile}. Use 'gold' or 'mock'.")

    def load_gold_cases(self, gold_file: str) -> List[Dict[str, Any]]:
        """Load gold test cases from JSONL file."""
        cases = []
        with open(gold_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cases.append(json.loads(line))
        return cases

    def filter_cases(
        self,
        cases: List[Dict[str, Any]],
        include_tags: List[str] = None,
        mode: str = None,
        size: int = None,
        seed: int = 42,
    ) -> List[Dict[str, Any]]:
        """Filter and sample cases based on criteria."""
        import random

        filtered = cases

        # Filter by tags
        if include_tags:
            filtered = [case for case in filtered if any(tag in case.get("tags", []) for tag in include_tags)]

        # Filter by mode
        if mode:
            filtered = [case for case in filtered if case.get("mode") == mode]

        # Sample if size specified
        if size and len(filtered) > size:
            random.seed(seed)
            filtered = random.sample(filtered, size)

        return filtered

    def _log_progress(self, record: Dict[str, Any]):
        """Log progress record to file."""
        if self._progress_fh:
            self._progress_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._progress_fh.flush()

    def __del__(self):
        """Clean up progress log file."""
        if self._progress_fh:
            self._progress_fh.close()

    def calculate_metrics(self, response: str, gt_answer: str) -> Dict[str, float]:
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

    def calculate_faithfulness(self, response: str, retrieved_context: List[Dict[str, Any]]) -> float:
        """Calculate faithfulness - how well the answer is grounded in retrieved context."""
        if not response or not retrieved_context:
            return 0.0

        # Extract text from retrieved context
        context_texts = []
        for ctx in retrieved_context:
            if isinstance(ctx, dict):
                text = ctx.get("text", "") or ctx.get("content", "")
                if text:
                    context_texts.append(text)

        if not context_texts:
            return 0.0

        # Simple faithfulness: check if response words appear in context
        response_words = set(response.lower().split())
        context_words = set()
        for text in context_texts:
            context_words.update(text.lower().split())

        if not response_words:
            return 0.0

        # Calculate overlap ratio
        overlap = len(response_words & context_words)
        faithfulness = overlap / len(response_words)

        return min(1.0, faithfulness)

    def check_file_retrieval(self, case: Dict[str, Any], retrieved_context: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Check if expected files were retrieved."""
        expected_files = case.get("expected_files", [])
        if not expected_files:
            return {"file_retrieved": False, "file_used": False}

        # Check if any expected file appears in retrieved context
        retrieved_files = []
        for ctx in retrieved_context:
            if isinstance(ctx, dict):
                # Look for filename in various fields
                filename = (
                    ctx.get("filename")
                    or ctx.get("src")
                    or ctx.get("source_document")
                    or ctx.get("document_path")
                    or ""
                )
                if filename:
                    retrieved_files.append(filename)

        # Check if any expected file was retrieved
        file_retrieved = any(any(exp_file in ret_file for exp_file in expected_files) for ret_file in retrieved_files)

        # For now, assume file was used if retrieved (could be enhanced)
        file_used = file_retrieved

        return {"file_retrieved": file_retrieved, "file_used": file_used}

    def calculate_oracle_metrics(
        self, case: Dict[str, Any], retrieved_context: List[Dict[str, Any]], response: str
    ) -> Dict[str, Any]:
        """Calculate oracle metrics - tracks retrieval hits and reader performance."""
        gt_answer = case.get("gt_answer", "")
        expected_files = case.get("expected_files", [])

        # Oracle retrieval hit: did we retrieve relevant content?
        oracle_retrieval_hit = False
        if retrieved_context and gt_answer:
            # Check if any retrieved context contains ground truth words
            gt_words = set(gt_answer.lower().split())
            for ctx in retrieved_context:
                if isinstance(ctx, dict):
                    text = ctx.get("text", "") or ctx.get("content", "")
                    if text:
                        ctx_words = set(text.lower().split())
                        overlap = len(gt_words & ctx_words)
                        if overlap > 0:
                            oracle_retrieval_hit = True
                            break

        # Oracle reader performance: did we use the right content in our answer?
        oracle_reader_used_gold = False
        if response and gt_answer:
            response_words = set(response.lower().split())
            gt_words = set(gt_answer.lower().split())
            overlap = len(response_words & gt_words)
            oracle_reader_used_gold = overlap > 0

        # File oracle: did we retrieve expected files?
        file_oracle_hit = False
        if expected_files and retrieved_context:
            for ctx in retrieved_context:
                if isinstance(ctx, dict):
                    filename = (ctx.get("filename") or ctx.get("src") or "").lower()
                    for exp_file in expected_files:
                        if exp_file.lower() in filename:
                            file_oracle_hit = True
                            break
                    if file_oracle_hit:
                        break

        return {
            "oracle_retrieval_hit": oracle_retrieval_hit,
            "oracle_reader_used_gold": oracle_reader_used_gold,
            "oracle_file_hit": file_oracle_hit,
            "retrieval_context_count": len(retrieved_context),
            "expected_files_count": len(expected_files),
        }

    def run_evaluation(
        self,
        gold_file: str,
        limit: int = None,
        include_tags: List[str] = None,
        mode: str = None,
        concurrency: int = None,
    ) -> Dict[str, Any]:
        """Run evaluation on gold cases."""
        print("🔍 Loading gold cases...")
        cases = self.load_gold_cases(gold_file)

        # Apply filtering and sampling
        if include_tags or mode or limit:
            cases = self.filter_cases(cases, include_tags=include_tags, mode=mode, size=limit)
            print(f"📋 Filtered to {len(cases)} cases")

        print(f"📋 Running evaluation on {len(cases)} cases")

        # Set concurrency
        if concurrency:
            os.environ["EVAL_CONCURRENCY"] = str(concurrency)

        # Initialize evaluation system based on profile
        if self.profile == "mock":
            print("🎭 Using synthetic evaluation (mock mode)")
            rag_system = None
        else:
            print("🤖 Initializing DSPy RAG system...")
            try:
                rag_system = RAGAnswer()
                print("✅ DSPy RAG system initialized")
            except Exception as e:
                print(f"❌ Failed to initialize DSPy RAG system: {e}")
                return {"error": str(e)}

        # Run evaluation
        case_results = []
        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        total_faithfulness = 0.0

        # Oracle metrics totals
        oracle_retrieval_hits = 0
        oracle_reader_hits = 0
        oracle_file_hits = 0

        for i, case in enumerate(cases, 1):
            query = case.get("query", "")
            gt_answer = case.get("gt_answer", "")
            case_id = case.get("id", f"case_{i}")

            print(f"🔍 Case {i}/{len(cases)}: {query[:60]}...")

            try:
                if self.profile == "mock":
                    # Synthetic evaluation
                    start_time = time.time()
                    response = f"Based on the available documentation, {query.lower()}. This is a synthetic response for testing infrastructure."
                    retrieved_context = [
                        {"text": f"Synthetic context about {query[:30]}...", "filename": "synthetic_doc.md"}
                    ]
                    retrieval_snapshot = retrieved_context
                    latency = time.time() - start_time
                else:
                    # Real DSPy RAG system
                    start_time = time.time()
                    result = rag_system(question=query, tag="evaluation")
                    latency = time.time() - start_time

                    response = getattr(result, "answer", "")
                    retrieved_context = getattr(rag_system, "used_contexts", [])
                    retrieval_snapshot = getattr(rag_system, "_last_retrieval_snapshot", [])

                # Calculate all metrics
                metrics = self.calculate_metrics(response, gt_answer)
                faithfulness = self.calculate_faithfulness(response, retrieved_context)
                oracle_metrics = self.calculate_oracle_metrics(case, retrieved_context, response)
                file_metrics = self.check_file_retrieval(case, retrieved_context)

                # Create case result with all metrics
                case_result = {
                    "case_id": case_id,
                    "query": query,
                    "response": response,
                    "gt_answer": gt_answer,
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1_score": metrics["f1_score"],
                    "faithfulness": faithfulness,
                    "latency_sec": latency,
                    "retrieved_context_count": len(retrieved_context),
                    "retrieval_candidates_count": len(retrieval_snapshot),
                    "file_retrieved": file_metrics["file_retrieved"],
                    "file_used": file_metrics["file_used"],
                    "expected_files": case.get("expected_files", []),
                    "tags": case.get("tags", []),
                    "mode": case.get("mode", "reader"),
                    # Oracle metrics
                    "oracle_retrieval_hit": oracle_metrics["oracle_retrieval_hit"],
                    "oracle_reader_used_gold": oracle_metrics["oracle_reader_used_gold"],
                    "oracle_file_hit": oracle_metrics["oracle_file_hit"],
                    # Combined metrics
                    "metrics": {
                        "precision": metrics["precision"],
                        "recall": metrics["recall"],
                        "f1_score": metrics["f1_score"],
                        "faithfulness": faithfulness,
                        "oracle": oracle_metrics,
                        "file_oracle": file_metrics,
                    },
                }

                case_results.append(case_result)
                total_precision += metrics["precision"]
                total_recall += metrics["recall"]
                total_f1 += metrics["f1_score"]
                total_faithfulness += faithfulness

                # Update oracle totals
                if oracle_metrics["oracle_retrieval_hit"]:
                    oracle_retrieval_hits += 1
                if oracle_metrics["oracle_reader_used_gold"]:
                    oracle_reader_hits += 1
                if oracle_metrics["oracle_file_hit"]:
                    oracle_file_hits += 1

                print(
                    f"  ✅ P={metrics['precision']:.3f}, R={metrics['recall']:.3f}, F1={metrics['f1_score']:.3f}, F={faithfulness:.3f}"
                )

                # Log progress
                self._log_progress(
                    {
                        "type": "case_completed",
                        "case_id": case_id,
                        "precision": metrics["precision"],
                        "recall": metrics["recall"],
                        "f1_score": metrics["f1_score"],
                        "faithfulness": faithfulness,
                        "oracle_retrieval_hit": oracle_metrics["oracle_retrieval_hit"],
                        "oracle_reader_used_gold": oracle_metrics["oracle_reader_used_gold"],
                        "oracle_file_hit": oracle_metrics["oracle_file_hit"],
                        "latency_sec": latency,
                    }
                )

            except Exception as e:
                print(f"  ❌ Error: {e}")
                case_result = {
                    "case_id": case_id,
                    "query": query,
                    "response": "",
                    "gt_answer": gt_answer,
                    "precision": 0.0,
                    "recall": 0.0,
                    "f1_score": 0.0,
                    "latency_sec": 0.0,
                    "error": str(e),
                    "retrieved_context_count": 0,
                    "retrieval_candidates_count": 0,
                    "file_retrieved": False,
                    "file_used": False,
                    "expected_files": case.get("expected_files", []),
                    "tags": case.get("tags", []),
                    "mode": case.get("mode", "reader"),
                }
                case_results.append(case_result)

        # Calculate overall metrics
        n_cases = len(case_results)
        overall_metrics = {
            "precision": total_precision / n_cases if n_cases > 0 else 0.0,
            "recall": total_recall / n_cases if n_cases > 0 else 0.0,
            "f1_score": total_f1 / n_cases if n_cases > 0 else 0.0,
            "faithfulness": total_faithfulness / n_cases if n_cases > 0 else 0.0,
            "total_cases": n_cases,
            "successful_cases": len([c for c in case_results if "error" not in c]),
            "failed_cases": len([c for c in case_results if "error" in c]),
            # Oracle metrics
            "oracle_retrieval_hit_rate": oracle_retrieval_hits / n_cases if n_cases > 0 else 0.0,
            "oracle_reader_hit_rate": oracle_reader_hits / n_cases if n_cases > 0 else 0.0,
            "oracle_file_hit_rate": oracle_file_hits / n_cases if n_cases > 0 else 0.0,
        }

        # Create results
        results = {
            "evaluation_type": "clean_dspy_rag",
            "timestamp": datetime.now().isoformat(),
            "overall_metrics": overall_metrics,
            "case_results": case_results,
            "config": {
                "gold_file": gold_file,
                "limit": limit,
                "dspy_model": os.getenv("DSPY_MODEL", "anthropic.claude-3-haiku-20240307-v1:0"),
                "postgres_dsn": os.getenv("POSTGRES_DSN", "<not_set>")[:20] + "...",
                "eval_driver": os.getenv("EVAL_DRIVER", "dspy_rag"),
            },
        }

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"dspy_evaluation_{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n📊 EVALUATION COMPLETE")
        print(f"📁 Results saved to: {results_file}")
        print(f"📈 Overall Metrics:")
        print(f"   Precision: {overall_metrics['precision']:.3f}")
        print(f"   Recall: {overall_metrics['recall']:.3f}")
        print(f"   F1 Score: {overall_metrics['f1_score']:.3f}")
        print(f"   Faithfulness: {overall_metrics['faithfulness']:.3f}")
        print(f"   Oracle Retrieval Hit Rate: {overall_metrics['oracle_retrieval_hit_rate']:.3f}")
        print(f"   Oracle Reader Hit Rate: {overall_metrics['oracle_reader_hit_rate']:.3f}")
        print(f"   Oracle File Hit Rate: {overall_metrics['oracle_file_hit_rate']:.3f}")
        print(f"   Successful: {overall_metrics['successful_cases']}/{overall_metrics['total_cases']}")

        # Log final summary
        self._log_progress(
            {"type": "evaluation_complete", "overall_metrics": overall_metrics, "results_file": str(results_file)}
        )

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Clean DSPy RAG Evaluation")
    parser.add_argument(
        "--profile",
        choices=["gold", "mock"],
        default="gold",
        help="Evaluation profile (gold: real RAG + gold cases, mock: synthetic)",
    )
    parser.add_argument(
        "--gold-file", default="300_evals/data/gold/v1/gold_cases.jsonl", help="Path to gold cases file"
    )
    parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to evaluate")
    parser.add_argument("--tags", nargs="+", help="Filter cases by tags")
    parser.add_argument("--mode", help="Filter cases by mode (reader, retrieval, decision)")
    parser.add_argument("--concurrency", type=int, help="Number of concurrent workers")
    parser.add_argument("--progress-log", help="Path to progress log file")
    parser.add_argument("--outdir", default="metrics/dspy_evaluations", help="Output directory for results")

    args = parser.parse_args()

    # Create evaluator with specified profile
    evaluator = CleanDSPyEvaluator(profile=args.profile, progress_log=args.progress_log)
    results = evaluator.run_evaluation(
        gold_file=args.gold_file, limit=args.limit, include_tags=args.tags, mode=args.mode, concurrency=args.concurrency
    )

    # Exit with error code if there were failures
    if results.get("overall_metrics", {}).get("failed_cases", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
