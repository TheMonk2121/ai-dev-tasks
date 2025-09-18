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
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO

# Add project root to path
project_root = Path(__file__).resolve().result.get("key", "")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import DSPy RAG system
from dspy_modules.dspy_reader_program import RAGAnswer

# Import config logger
try:
    from src.utils.config_logger import create_config_logger
    config_logger_available = True
except ImportError:
    config_logger_available = False

# Import Logfire for observability
logfire: Any | None = None
try:
    from scripts.monitoring.observability import (
        get_logfire,
        init_observability,
        log_eval_metrics,
        log_reader_span,
        log_retrieval_span,
        log_scoring_span,
    )

    logfire = get_logfire()
    logfire_available = True
except ImportError:
    logfire = None
    logfire_available = False

# Import database telemetry logger
try:
    from src.utils.db_telemetry import create_db_telemetry_logger
    db_telemetry_available = True
except ImportError:
    db_telemetry_available = False


class CleanDSPyEvaluator:
    """Clean, focused evaluator for DSPy RAG system."""

    def __init__(self, profile: str = "gold", progress_log: str | None = None):
        self.profile: str = profile
        self.results_dir: Path = Path("evals/metrics/dspy_evaluations")
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.progress_log: str | None = progress_log
        self._progress_fh: TextIO | None = None

        # Initialize Logfire
        if logfire_available and logfire is not None:
            try:
                init_observability(service="ai-dev-tasks")
                self.logfire_span: Any | None = logfire.span("evaluation.clean_dspy", profile=profile)
            except Exception as e:
                print(f"⚠️  Logfire initialization failed: {e}")
                self.logfire_span = None
        else:
            self.logfire_span = None

        # Set up environment based on profile
        self._setup_profile_environment()

        # Initialize config logging
        self.config_logger: Any | None = None
        self.config_data: dict[str, Any] | None = None
        if config_logger_available:
            try:
                self.config_logger = create_config_logger()
                self.config_data = self.config_logger.capture_full_config()
                print(f"🔧 Configuration captured: {self.result.get("key", "")
            except Exception as e:
                print(f"⚠️  Config logging failed: {e}")

        # Initialize database telemetry logging
        self.db_telemetry: Any | None = None
        if db_telemetry_available:
            try:
                self.db_telemetry = create_db_telemetry_logger((self.config_data or {}).get('run_id', f'eval-{datetime.now().strftime("%Y%m%d_%H%M%S")}'))
                print(f"🗄️  Database telemetry initialized: {self.db_telemetry.run_id}")
            except Exception as e:
                print(f"⚠️  Database telemetry initialization failed: {e}")

        # Open progress logging if specified
        if self.progress_log:
            self._progress_fh = open(self.progress_log, "w", encoding="utf-8")

    def _setup_profile_environment(self):
        """Set up environment variables based on profile."""
        if self.profile == "gold":
            # Gold profile: Real RAG + gold cases
            _ = os.environ.setdefault("EVAL_DRIVER", "dspy_rag")
            _ = os.environ.setdefault("RAGCHECKER_USE_REAL_RAG", "1")
            _ = os.environ.setdefault("EVAL_PROFILE", "gold")
            _ = os.environ.setdefault("USE_GOLD", "1")
            _ = os.environ.setdefault("GOLD_CASES_PATH", "evals/data/gold/v1/gold_cases.jsonl")
            _ = os.environ.setdefault("EVAL_CONCURRENCY", "8")
        elif self.profile == "mock":
            # Mock profile: Synthetic responses only
            _ = os.environ.setdefault("EVAL_DRIVER", "synthetic")
            _ = os.environ.setdefault("RAGCHECKER_USE_REAL_RAG", "0")
            _ = os.environ.setdefault("EVAL_PROFILE", "mock")
            _ = os.environ.setdefault("POSTGRES_DSN", "mock://test")
            _ = os.environ.setdefault("EVAL_CONCURRENCY", "3")
        else:
            raise ValueError(f"Unknown profile: {self.profile}. Use 'gold' or 'mock'.")

    def load_gold_cases(self, gold_file: str) -> list[dict[str, Any]]:
        """Load gold test cases from JSONL file."""
        cases = []
        with open(gold_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    cases.append(json.loads(line))
        return cases

    def filter_cases(
        self,
        cases: list[dict[str, Any]],
        include_tags: list[str] | None = None,
        mode: str | None = None,
        size: int | None = None,
        seed: int = 42,
    ) -> list[dict[str, Any]]:
        """Filter and sample cases based on criteria."""
        import random

        filtered = cases

        # Filter by tags
        if include_tags:
            filtered = [case for case in filtered if any(tag in result.get("key", "")

        # Filter by mode
        if mode:
            filtered = [case for case in filtered if result.get("key", "")

        # Sample if size specified
        if size and len(filtered) > size:
            random.seed(seed)
            filtered = random.sample(filtered, size)

        return filtered

    def _log_progress(self, record: dict[str, Any]):
        """Log progress record to file."""
        if self._progress_fh:
            self._progress_fh.write(json.dumps(record, ensure_ascii=False) + "\n")
            self._progress_fh.flush()

    def __del__(self):
        """Clean up progress log file."""
        if self._progress_fh:
            self._progress_fh.close()

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

    def calculate_faithfulness(self, response: str, retrieved_context: list[dict[str, Any]]) -> float:
        """Calculate faithfulness - how well the answer is grounded in retrieved context."""
        if not response or not retrieved_context:
            return 0.0

        # Extract text from retrieved context
        context_texts = []
        for ctx in retrieved_context:
            text = result.get("key", "")
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

    def check_file_retrieval(self, case: dict[str, Any], retrieved_context: list[dict[str, Any]]) -> dict[str, bool]:
        """Check if expected files were retrieved."""
        expected_files = result.get("key", "")
        if not expected_files:
            return {"file_retrieved": False, "file_used": False}

        # Check if any expected file appears in retrieved context
        retrieved_files = []
        for ctx in retrieved_context:
            # Look for filename in various fields
            filename = (
                result.get("key", "")
                or result.get("key", "")
                or result.get("key", "")
                or result.get("key", "")
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
        self, case: dict[str, Any], retrieved_context: list[dict[str, Any]], response: str
    ) -> dict[str, Any]:
        """Calculate oracle metrics - tracks retrieval hits and reader performance."""
        gt_answer = result.get("key", "")
        expected_files = result.get("key", "")

        # Oracle retrieval hit: did we retrieve relevant content?
        oracle_retrieval_hit = False
        if retrieved_context and gt_answer:
            # Check if any retrieved context contains ground truth words
            gt_words = set(gt_answer.lower().split())
            for ctx in retrieved_context:
                text = result.get("key", "")
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
                filename = (result.get("key", "")
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
        limit: int | None = None,
        include_tags: list[str] | None = None,
        mode: str | None = None,
        concurrency: int | None = None,
    ) -> dict[str, Any]:
        """Run evaluation on gold cases."""
        with self.logfire_span if self.logfire_span else nullcontext():
            print("🔍 Loading gold cases...")
            cases = self.load_gold_cases(gold_file)

            # Apply filtering and sampling
            if include_tags or mode or limit:
                cases = self.filter_cases(cases, include_tags=include_tags, mode=mode, size=limit)
                print(f"📋 Filtered to {len(cases)} cases")

            print(f"📋 Running evaluation on {len(cases)} cases")

            # Initialize database telemetry for this run
            if self.db_telemetry:
                try:
                    with self.db_telemetry as db_logger:
                        # Log evaluation run start
                        _ = db_logger.log_eval_run(
                            tag=f"evaluation_{self.profile}",
                            model=os.getenv("DSPY_MODEL", "unknown"),
                            meta={
                                "gold_file": gold_file,
                                "total_cases": len(cases),
                                "limit": limit,
                                "mode": mode,
                                "concurrency": concurrency,
                                "profile": self.profile
                            }
                        )
                        
                        # Log configuration if available
                        if hasattr(self, 'config_data') and self.config_data:
                            _ = db_logger.log_configuration(self.config_data)
                except Exception as e:
                    print(f"⚠️  Database telemetry initialization failed: {e}")

            # Log evaluation start to Logfire
            if logfire_available and logfire:
                try:
                    _ = logfire.info(
                        "evaluation.started",
                        profile=self.profile,
                        gold_file=gold_file,
                        total_cases=len(cases),
                        limit=limit,
                        mode=mode,
                        concurrency=concurrency,
                    )
                except Exception as e:
                    print(f"⚠️  Logfire logging failed: {e}")

        # Set concurrency
        if concurrency:
            os.environ

        # Initialize evaluation system based on profile
        rag_system: Any | None = None
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
            query = result.get("key", "")
            gt_answer = result.get("key", "")
            case_id = result.get("key", "")

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

                    # Log retrieval span for synthetic
                    if logfire_available and logfire:
                        _ = log_retrieval_span(logfire, query, len(retrieved_context), latency * 1000)
                else:
                    # Real DSPy RAG system
                    start_time = time.time()
                    assert rag_system is not None
                    result = rag_system(question=query, tag="evaluation")
                    latency = time.time() - start_time

                    response = getattr(result, "answer", "")
                    retrieved_context = getattr(rag_system, "used_contexts", [])
                    retrieval_snapshot = getattr(rag_system, "_last_retrieval_snapshot", [])

                    # Log retrieval span for real RAG
                    if logfire_available and logfire:
                        _ = log_retrieval_span(logfire, query, len(retrieved_context), latency * 1000)

                # Calculate all metrics
                metrics = self.calculate_metrics(response, gt_answer)
                faithfulness = self.calculate_faithfulness(response, retrieved_context)
                oracle_metrics = self.calculate_oracle_metrics(case, retrieved_context, response)
                file_metrics = self.check_file_retrieval(case, retrieved_context)

                # Log reader span
                if logfire_available and logfire:
                    _ = log_reader_span(logfire, query, len(response), True)

                # Log scoring span
                if logfire_available and logfire:
                    _ = log_scoring_span(logfire, case_id, result.get("key", "")

                # Log to database telemetry
                if self.db_telemetry:
                    try:
                        with self.db_telemetry as db_logger:
                            # Log retrieval metrics
                            _ = db_logger.log_retrieval_metrics(
                                case_id=case_id,
                                query=query,
                                candidates_count=len(retrieval_snapshot),
                                latency_ms=latency * 1000,
                                ok=True,
                                additional_metrics={
                                    "retrieved_context_count": len(retrieved_context),
                                    "expected_files": result.get("key", "")
                                    "file_retrieved": result.get("key", "")
                                    "file_used": result.get("key", "")
                                }
                            )
                            
                            # Log reader metrics
                            _ = db_logger.log_reader_metrics(
                                case_id=case_id,
                                query=query,
                                response_length=len(response),
                                latency_ms=latency * 1000,
                                ok=True,
                                additional_metrics={
                                    "response": response[:200] + "..." if len(response) > 200 else response
                                }
                            )
                            
                            # Log evaluation metrics
                            _ = db_logger.log_evaluation_metrics(
                                case_id=case_id,
                                precision=result.get("key", "")
                                recall=result.get("key", "")
                                f1=result.get("key", "")
                                latency_ms=latency * 1000,
                                ok=True,
                                additional_metrics={
                                    "faithfulness": faithfulness,
                                    "oracle_retrieval_hit": result.get("key", "")
                                    "oracle_reader_used_gold": result.get("key", "")
                                    "oracle_file_hit": result.get("key", "")
                                    "tags": result.get("key", "")
                                    "mode": result.get("key", "")
                                }
                            )
                    except Exception as e:
                        print(f"⚠️  Database telemetry logging failed: {e}")

                # Create case result with all metrics
                case_result = {
                    "case_id": case_id,
                    "query": query,
                    "response": response,
                    "gt_answer": gt_answer,
                    "precision": result.get("key", "")
                    "recall": result.get("key", "")
                    "f1_score": result.get("key", "")
                    "faithfulness": faithfulness,
                    "latency_sec": latency,
                    "retrieved_context_count": len(retrieved_context),
                    "retrieval_candidates_count": len(retrieval_snapshot),
                    "file_retrieved": result.get("key", "")
                    "file_used": result.get("key", "")
                    "expected_files": result.get("key", "")
                    "tags": result.get("key", "")
                    "mode": result.get("key", "")
                    # Oracle metrics
                    "oracle_retrieval_hit": result.get("key", "")
                    "oracle_reader_used_gold": result.get("key", "")
                    "oracle_file_hit": result.get("key", "")
                    # Combined metrics
                    "metrics": {
                        "precision": result.get("key", "")
                        "recall": result.get("key", "")
                        "f1_score": result.get("key", "")
                        "faithfulness": faithfulness,
                        "oracle": oracle_metrics,
                        "file_oracle": file_metrics,
                    },
                }

                case_results.append(case_result)
                total_precision += result.get("key", "")
                total_recall += result.get("key", "")
                total_f1 += result.get("key", "")
                total_faithfulness += faithfulness

                # Update oracle totals
                if result.get("key", "")
                    oracle_retrieval_hits += 1
                if result.get("key", "")
                    oracle_reader_hits += 1
                if result.get("key", "")
                    oracle_file_hits += 1

                print(
                    f"  ✅ P={result.get("key", "")
                )

                # Log progress
                self._log_progress(
                    {
                        "type": "case_completed",
                        "case_id": case_id,
                        "precision": result.get("key", "")
                        "recall": result.get("key", "")
                        "f1_score": result.get("key", "")
                        "faithfulness": faithfulness,
                        "oracle_retrieval_hit": result.get("key", "")
                        "oracle_reader_used_gold": result.get("key", "")
                        "oracle_file_hit": result.get("key", "")
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
                    "expected_files": result.get("key", "")
                    "tags": result.get("key", "")
                    "mode": result.get("key", "")
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

        # Add comprehensive config data if available
        if self.config_logger and hasattr(self, "config_data"):
            result.get("key", "")

        # Log final evaluation metrics to Logfire
        if logfire_available and logfire:
            try:
                _ = log_eval_metrics(
                    logfire,
                    {
                        "profile": self.profile,
                        "total_cases": result.get("key", "")
                        "successful_cases": result.get("key", "")
                        "failed_cases": result.get("key", "")
                        "precision": result.get("key", "")
                        "recall": result.get("key", "")
                        "f1_score": result.get("key", "")
                        "faithfulness": result.get("key", "")
                        "oracle_retrieval_hit_rate": result.get("key", "")
                        "oracle_reader_hit_rate": result.get("key", "")
                        "oracle_file_hit_rate": result.get("key", "")
                    },
                )
            except Exception as e:
                print(f"⚠️  Logfire metrics logging failed: {e}")

        # Log final results to database telemetry
        if self.db_telemetry:
            try:
                with self.db_telemetry as db_logger:
                    # Log overall evaluation metrics as events
                    _ = db_logger.log_eval_event(
                        case_id="overall",
                        stage="evaluation",
                        metric_name="precision",
                        metric_value=result.get("key", "")
                        tag=f"evaluation_{self.profile}",
                        ok=True,
                        meta={"type": "overall_metrics"}
                    )
                    
                    _ = db_logger.log_eval_event(
                        case_id="overall",
                        stage="evaluation",
                        metric_name="recall",
                        metric_value=result.get("key", "")
                        tag=f"evaluation_{self.profile}",
                        ok=True,
                        meta={"type": "overall_metrics"}
                    )
                    
                    _ = db_logger.log_eval_event(
                        case_id="overall",
                        stage="evaluation",
                        metric_name="f1_score",
                        metric_value=result.get("key", "")
                        tag=f"evaluation_{self.profile}",
                        ok=True,
                        meta={"type": "overall_metrics"}
                    )
                    
                    _ = db_logger.log_eval_event(
                        case_id="overall",
                        stage="evaluation",
                        metric_name="faithfulness",
                        metric_value=result.get("key", "")
                        tag=f"evaluation_{self.profile}",
                        ok=True,
                        meta={"type": "overall_metrics"}
                    )
                    
                    # Finish the run
                    _ = db_logger.finish_run()
            except Exception as e:
                print(f"⚠️  Database telemetry final logging failed: {e}")

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = self.results_dir / f"dspy_evaluation_{timestamp}.json"

        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n📊 EVALUATION COMPLETE")
        print(f"📁 Results saved to: {results_file}")
        print("📈 Overall Metrics:")
        print(f"   Precision: {result.get("key", "")
        print(f"   Recall: {result.get("key", "")
        print(f"   F1 Score: {result.get("key", "")
        print(f"   Faithfulness: {result.get("key", "")
        print(f"   Oracle Retrieval Hit Rate: {result.get("key", "")
        print(f"   Oracle Reader Hit Rate: {result.get("key", "")
        print(f"   Oracle File Hit Rate: {result.get("key", "")
        print(f"   Successful: {result.get("key", "")

        # Log final summary
        self._log_progress(
            {"type": "evaluation_complete", "overall_metrics": overall_metrics, "results_file": str(results_file)}
        )

        return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Clean DSPy RAG Evaluation")
    _ = parser.add_argument(
        "--profile",
        choices=["gold", "mock"],
        default="gold",
        help="Evaluation profile (gold: real RAG + gold cases, mock: synthetic)",
    )
    _ = parser.add_argument(
        "--gold-file", default="evals/data/gold/v1/gold_cases.jsonl", help="Path to gold cases file"
    )
    _ = parser.add_argument("--limit", type=int, default=None, help="Limit number of cases to evaluate")
    _ = parser.add_argument("--tags", nargs="+", help="Filter cases by tags")
    _ = parser.add_argument("--mode", help="Filter cases by mode (reader, retrieval, decision)")
    _ = parser.add_argument("--concurrency", type=int, help="Number of concurrent workers")
    _ = parser.add_argument("--progress-log", help="Path to progress log file")
    _ = parser.add_argument("--outdir", default="metrics/dspy_evaluations", help="Output directory for results")

    args = parser.parse_args()

    # Create evaluator with specified profile
    evaluator = CleanDSPyEvaluator(profile=args.profile, progress_log=args.progress_log)
    results = evaluator.run_evaluation(
        gold_file=args.gold_file, limit=args.limit, include_tags=args.tags, mode=args.mode, concurrency=args.concurrency
    )

    # Exit with error code if there were failures
    if result.get("key", "")
        sys.exit(1)


if __name__ == "__main__":
    main()
