#!/usr/bin/env python3
"""
Complete Historical Evaluation Data Migration Script

This script combines the best features from all versions:
- Comprehensive format support from v1 (clean harness, baseline, evaluation suite, metrics)
- Batch processing and transaction management from v2
- Proper JSONB serialization fixes from v3
- Enhanced error handling and progress tracking
- Type safety and modern Python patterns
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict

import psycopg
from psycopg.rows import dict_row

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn


class Stats(TypedDict):
    files_processed: int
    files_skipped: int
    runs_created: int
    events_created: int
    case_results_created: int
    errors: list[str]


class CompleteHistoricalEvalMigrator:
    """Complete migrator with all features and proper JSONB serialization."""

    def __init__(self, batch_size: int = 100, dry_run: bool = False, dsn: str | None = None) -> None:
        self.batch_size: int = batch_size
        self.dry_run: bool = dry_run
        self.dsn: str = dsn or resolve_dsn(strict=False)
        self.connection: Any | None = None
        self.cursor: Any | None = None
        self.stats: Stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "runs_created": 0,
            "events_created": 0,
            "case_results_created": 0,
            "errors": [],
        }

    def __enter__(self) -> CompleteHistoricalEvalMigrator:
        """Context manager entry."""
        if not self.dry_run:
            try:
                self.connection = psycopg.connect(self.dsn)
                try:
                    self.connection.row_factory = dict_row  # type: ignore[attr-defined]
                except Exception:
                    pass
                self.cursor = self.connection.cursor()
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                raise
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        """Context manager exit."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def find_evaluation_files(self, base_dir: str = "evals/metrics") -> list[Path]:
        """Find all evaluation JSON files with comprehensive filtering."""
        base_path = Path(base_dir)
        json_files = []

        # Skip certain directories and file patterns
        skip_dirs = {
            "node_modules",
            ".git",
            "__pycache__",
            ".pytest_cache",
            "venv",
            ".venv",
            "logs",
            "traces",
        }

        skip_patterns = {
            "package.json",
            "package-lock.json",
            "tsconfig.json",
            "*.log",
            "*.out",
            "*.txt",
            "*.md",
            "*.sql",
            "*.py",
            "*.sh",
        }

        for file_path in base_path.rglob("*.json"):
            # Skip if in excluded directory
            if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                continue

            # Skip if matches excluded pattern
            if any(file_path.name.endswith(pattern.replace("*", "")) for pattern in skip_patterns):
                continue

            # Skip very small files (likely not evaluation data)
            if file_path.stat().st_size < 100:
                continue

            # Skip certain evaluation directories
            if any(
                skip in str(file_path)
                for skip in [
                    "/_invalid/",
                    "/logs/",
                    "/derived_configs/",
                    "/vector_store/",
                    "/visualizations/",
                    "/system_diagnostics/",
                    "/cost_reports/",
                    "/calibration/",
                    "/integration_test/",
                    "/test_eval/",
                    "/test_off/",
                    "/test_on/",
                    "/test_real_eval/",
                    "/nightly_smoke/",
                    "/phase3_test/",
                    "/phase4/",
                    "/reranker_ablation/",
                    "/reranker_comparison_mock/",
                ]
            ):
                continue

            # Skip non-evaluation files
            if any(
                skip in file_path.name
                for skip in [
                    "bedrock_usage",
                    "circular_dependencies",
                    "complexity",
                    "coverage",
                    "dependency_analysis",
                    "fusion_head_report",
                    "import_conflicts",
                    "junit_latest",
                    "retirement_queue",
                    "tests_signal",
                    "validator_counts",
                    "enhanced_bedrock_usage",
                    "dsn_audit",
                    "progress_memory",
                    "progress_test",
                ]
            ):
                continue

            json_files.append(file_path)

        return sorted(json_files)

    def parse_timestamp_from_filename(self, file_path: Path) -> datetime | None:
        """Extract timestamp from filename patterns."""
        filename = file_path.name
        import re

        # Pattern 1: YYYYMMDD_HHMMSS
        if "_" in filename and len(filename.split("_")) >= 2:
            try:
                date_part = filename.split("_")[0]
                time_part = filename.split("_")[1].split(".")[0]
                if len(date_part) == 8 and len(time_part) == 6:
                    return datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        # Pattern 2: ragchecker_clean_evaluation_20250907_070000.json
        match = re.search(r"(\d{8})_(\d{6})", filename)
        if match:
            date_str, time_str = match.groups()
            try:
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        # Pattern 3: timestamp numbers
        try:
            numbers = re.findall(r"\d+", filename)
            if numbers:
                # Try the largest number as timestamp
                largest_num = max(numbers, key=len)
                if len(largest_num) >= 10:  # Unix timestamp
                    return datetime.fromtimestamp(int(largest_num))
        except (ValueError, OSError):
            pass

        return None

    def extract_run_id(self, data: dict[str, Any], file_path: Path) -> str:
        """Extract or generate run ID for the evaluation."""
        # Try to get run_id from data
        if "run_id" in data:
            return str(data.get("run_id", ""))
        if "evaluation_id" in data:
            return str(data.get("evaluation_id", ""))

        # Try to get from config
        if "config" in data and "run_id" in data.get("config", {}):
            return str(data.get("config", {}).get("run_id", ""))

        # Generate from filename and timestamp
        timestamp = self.parse_timestamp_from_filename(file_path)
        if timestamp:
            return f"historical-{timestamp.strftime('%Y%m%d_%H%M%S')}-{file_path.stem[:20]}"

        # Fallback to filename
        return f"historical-{file_path.stem}"

    def extract_evaluation_type(self, data: dict[str, Any], file_path: Path) -> str:
        """Extract evaluation type from data or filename."""
        if "evaluation_type" in data:
            return str(data.get("evaluation_type", ""))

        filename = file_path.name.lower()
        if "ragchecker" in filename:
            return "ragchecker_evaluation"
        elif "baseline" in filename:
            return "baseline_evaluation"
        elif "synthetic" in filename:
            return "synthetic_evaluation"
        elif "smoke" in filename:
            return "smoke_test"
        elif "clean" in filename:
            return "clean_harness"
        else:
            return "unknown_evaluation"

    def extract_model_info(self, data: dict[str, Any]) -> tuple[str, str]:
        """Extract model and tag information."""
        model = "unknown"
        tag = "historical"

        # Try to get from config
        if "config" in data:
            config = data.get("config", {})
            model_keys = ["dspy_model", "model", "llm_model", "provider"]
            for key in model_keys:
                if key in config:
                    model = str(config[key])
                    break

        # Try to get from environment
        if "environment" in data:
            env = data.get("environment", {})
            if "DSPY_MODEL" in env:
                model = str(env.get("DSPY_MODEL", ""))
            elif "MODEL" in env:
                model = str(env.get("MODEL", ""))

        # Try to get model from various possible keys
        model_keys = ["model", "dspy_model", "llm_model", "provider"]
        for key in model_keys:
            if key in data:
                model = str(data[key])
                break

        # Infer tag from evaluation type
        eval_type = self.extract_evaluation_type(data, Path(""))
        if "ragchecker" in eval_type:
            tag = "ragchecker"
        elif "baseline" in eval_type:
            tag = "baseline"
        elif "synthetic" in eval_type:
            tag = "synthetic"
        elif "smoke" in eval_type:
            tag = "smoke_test"
        elif "clean" in eval_type:
            tag = "clean_harness"

        return model, tag

    def convert_metric_value(self, value: Any) -> float:
        """Convert metric value to float, handling various types."""
        if value is None:
            return 0.0
        if isinstance(value, bool):
            return 1.0 if value else 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                return 0.0
        return 0.0

    def migrate_clean_harness_evaluation(self, data: dict[str, Any], file_path: Path) -> bool:
        """Migrate clean harness evaluation format with proper JSONB serialization."""
        try:
            run_id = self.extract_run_id(data, file_path)
            model, tag = self.extract_model_info(data)

            # Extract timestamp
            timestamp = self.parse_timestamp_from_filename(file_path)
            if not timestamp:
                timestamp = datetime.now()

            # Insert evaluation run with proper JSONB serialization
            if not self.dry_run:
                self.cursor.execute(
                    """
                    INSERT INTO eval_run (run_id, tag, started_at, finished_at, model, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        tag = EXCLUDED.tag,
                        started_at = EXCLUDED.started_at,
                        finished_at = EXCLUDED.finished_at,
                        model = EXCLUDED.model,
                        meta = EXCLUDED.meta
                    """,
                    (
                        run_id,
                        tag,
                        timestamp,
                        timestamp,
                        model,
                        json.dumps(
                            {
                                "evaluation_type": self.extract_evaluation_type(data, file_path),
                                "filename": str(file_path.name),
                                "source_file": str(file_path),
                                "overall_metrics": data.get("overall_metrics", {}),
                                "config": data.get("config", {}),
                                "environment": data.get("environment", {}),
                            }
                        ),
                    ),
                )

            # Process overall metrics
            overall_metrics = data.get("overall_metrics", {})
            events = []

            for metric_name, metric_value in [
                ("precision", overall_metrics.get("precision", 0.0)),
                ("recall", overall_metrics.get("recall", 0.0)),
                ("f1_score", overall_metrics.get("f1_score", 0.0)),
                ("faithfulness", overall_metrics.get("faithfulness", 0.0)),
            ]:
                events.append(
                    (
                        timestamp,
                        run_id,
                        "overall",
                        "evaluation",
                        metric_name,
                        self.convert_metric_value(metric_value),
                        model,
                        tag,
                        True,
                        json.dumps({"type": "overall_metrics"}),
                    )
                )

            # Process case results
            case_results = data.get("case_results", [])
            for i, case in enumerate(case_results):
                case_id = case.get("case_id", f"case_{i}")
                query = case.get("query", "")

                # Extract case metrics
                case_precision = self.convert_metric_value(case.get("precision", 0.0))
                case_recall = self.convert_metric_value(case.get("recall", 0.0))
                case_f1 = self.convert_metric_value(case.get("f1", 0.0))
                case_faithfulness = self.convert_metric_value(case.get("faithfulness", 0.0))
                latency_ms = self.convert_metric_value(case.get("latency_ms", 0.0))

                # Insert case result with proper JSONB serialization
                if not self.dry_run:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_case_result (run_id, case_id, f1, precision, recall, latency_ms, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (run_id, case_id) DO UPDATE SET
                            f1 = EXCLUDED.f1,
                            precision = EXCLUDED.precision,
                            recall = EXCLUDED.recall,
                            latency_ms = EXCLUDED.latency_ms,
                            ok = EXCLUDED.ok,
                            meta = EXCLUDED.meta
                        """,
                        (
                            run_id,
                            case_id,
                            case_f1,
                            case_precision,
                            case_recall,
                            latency_ms,
                            "error" not in case,
                            json.dumps(
                                {
                                    "query": query,
                                    "gt_answer": case.get("gt_answer", ""),
                                    "faithfulness": case_faithfulness,
                                    "retrieved_context_count": len(case.get("retrieved_context", [])),
                                    "tags": case.get("tags", []),
                                    "mode": case.get("mode", "unknown"),
                                    "response": case.get("response", ""),
                                }
                            ),
                        ),
                    )

                self.stats["case_results_created"] += 1

                # Create events for each metric
                for metric_name, metric_value in [
                    ("precision", case_precision),
                    ("recall", case_recall),
                    ("f1_score", case_f1),
                    ("faithfulness", case_faithfulness),
                ]:
                    events.append(
                        (
                            timestamp,
                            run_id,
                            case_id,
                            "score",
                            metric_name,
                            metric_value,
                            model,
                            tag,
                            True,
                            json.dumps({"query": query[:200], "case_index": i}),
                        )
                    )

            # Batch insert events
            if events and not self.dry_run:
                for event in events:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        event,
                    )
                self.stats["events_created"] += len(events)

            self.stats["runs_created"] += 1
            return True

        except Exception as e:
            error_msg = f"Error processing clean harness evaluation {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["files_skipped"] += 1
            self.stats["errors"].append(error_msg)
            return False

    def migrate_baseline_evaluation(self, data: dict[str, Any], file_path: Path) -> bool:
        """Migrate baseline evaluation format with proper JSONB serialization."""
        try:
            run_id = self.extract_run_id(data, file_path)
            model, tag = self.extract_model_info(data)

            # Extract timestamp
            timestamp = self.parse_timestamp_from_filename(file_path)
            if not timestamp:
                timestamp = datetime.now()

            # Extract overall metrics
            total_cases = len(data.get("case_results", []))
            passed_cases = sum(1 for case in data.get("case_results", []) if case.get("passed", False))
            failed_cases = total_cases - passed_cases
            total_score = sum(case.get("score", 0.0) for case in data.get("case_results", []))
            avg_score = total_score / total_cases if total_cases > 0 else 0.0

            # Insert evaluation run with proper JSONB serialization
            if not self.dry_run:
                self.cursor.execute(
                    """
                    INSERT INTO eval_run (run_id, tag, started_at, finished_at, model, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        tag = EXCLUDED.tag,
                        started_at = EXCLUDED.started_at,
                        finished_at = EXCLUDED.finished_at,
                        model = EXCLUDED.model,
                        meta = EXCLUDED.meta
                    """,
                    (
                        run_id,
                        tag,
                        timestamp,
                        timestamp,
                        model,
                        json.dumps(
                            {
                                "evaluation_type": self.extract_evaluation_type(data, file_path),
                                "filename": str(file_path.name),
                                "source_file": str(file_path),
                                "total_cases": total_cases,
                                "passed_cases": passed_cases,
                                "failed_cases": failed_cases,
                                "total_score": total_score,
                                "category_scores": data.get("category_scores", {}),
                            }
                        ),
                    ),
                )

            self.stats["runs_created"] += 1

            # Process overall metrics
            events = []
            events.append(
                (
                    timestamp,
                    run_id,
                    "overall",
                    "evaluation",
                    "average_score",
                    avg_score,
                    model,
                    tag,
                    True,
                    json.dumps({"type": "overall_metrics"}),
                )
            )

            # Process case results
            case_results = data.get("case_results", [])
            for i, case in enumerate(case_results):
                case_id = case.get("case_id", f"case_{i}")
                query = case.get("query", "")
                score = self.convert_metric_value(case.get("score", 0.0))
                passed = case.get("passed", False)

                # Insert case result with proper JSONB serialization
                if not self.dry_run:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_case_result (run_id, case_id, f1, precision, recall, latency_ms, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (run_id, case_id) DO UPDATE SET
                            f1 = EXCLUDED.f1,
                            precision = EXCLUDED.precision,
                            recall = EXCLUDED.recall,
                            latency_ms = EXCLUDED.latency_ms,
                            ok = EXCLUDED.ok,
                            meta = EXCLUDED.meta
                        """,
                        (
                            run_id,
                            case_id,
                            score / 100.0,  # Convert to 0-1 scale
                            score / 100.0,
                            score / 100.0,
                            0.0,  # No latency data
                            passed,
                            json.dumps(
                                {
                                    "query": query,
                                    "role": case.get("role", "unknown"),
                                    "category": case.get("category", "unknown"),
                                    "response_length": len(case.get("response", "")),
                                    "details": case.get("details", {}),
                                    "errors": case.get("errors", []),
                                }
                            ),
                        ),
                    )

                self.stats["case_results_created"] += 1

                # Create event for case score
                events.append(
                    (
                        timestamp,
                        run_id,
                        case_id,
                        "score",
                        "score",
                        score,
                        model,
                        tag,
                        passed,
                        json.dumps({"query": query[:200]}),
                    )
                )

            # Batch insert events
            if events and not self.dry_run:
                for event in events:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        event,
                    )
                self.stats["events_created"] += len(events)

            self.stats["runs_created"] += 1
            return True

        except Exception as e:
            error_msg = f"Error processing baseline evaluation {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["files_skipped"] += 1
            self.stats["errors"].append(error_msg)
            return False

    def migrate_evaluation_suite(self, data: dict[str, Any], file_path: Path) -> bool:
        """Migrate evaluation suite format (contains multiple evaluations)."""
        try:
            success_count = 0

            for eval_name, eval_data in data.items():
                if "results" in eval_data:
                    # Create a temporary data structure for the nested evaluation
                    nested_data = eval_data["results"]
                    nested_data["evaluation_type"] = eval_name
                    nested_data["config"] = eval_data.get("config", {})

                    # Migrate the nested evaluation
                    if "overall_metrics" in nested_data and "case_results" in nested_data:
                        if self.migrate_clean_harness_evaluation(nested_data, file_path):
                            success_count += 1
                    elif "total_cases" in nested_data and "case_results" in nested_data:
                        if self.migrate_baseline_evaluation(nested_data, file_path):
                            success_count += 1

            return success_count > 0

        except Exception as e:
            error_msg = f"Error processing evaluation suite {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["files_skipped"] += 1
            self.stats["errors"].append(error_msg)
            return False

    def migrate_metrics_file(self, data: dict[str, Any], file_path: Path) -> bool:
        """Migrate metrics file format (system performance metrics)."""
        try:
            run_id = self.extract_run_id(data, file_path)
            model, tag = self.extract_model_info(data)

            # Extract timestamp
            timestamp = self.parse_timestamp_from_filename(file_path)
            if not timestamp:
                timestamp = datetime.now()

            # Insert evaluation run with proper JSONB serialization
            if not self.dry_run:
                self.cursor.execute(
                    """
                    INSERT INTO eval_run (run_id, tag, started_at, finished_at, model, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO UPDATE SET
                        tag = EXCLUDED.tag,
                        started_at = EXCLUDED.started_at,
                        finished_at = EXCLUDED.finished_at,
                        model = EXCLUDED.model,
                        meta = EXCLUDED.meta
                    """,
                    (
                        run_id,
                        tag,
                        timestamp,
                        timestamp,
                        model,
                        json.dumps(
                            {
                                "evaluation_type": "system_metrics",
                                "filename": str(file_path.name),
                                "source_file": str(file_path),
                                "overall_score": data.get("overall_score", 0.0),
                                "status": data.get("status", "unknown"),
                                "latency": data.get("latency", {}),
                                "reranker": data.get("reranker", {}),
                                "health": data.get("health", {}),
                            }
                        ),
                    ),
                )

            self.stats["runs_created"] += 1

            # Process metrics
            events = []

            # Log latency metrics
            latency = data.get("latency", {})
            for metric_name, metric_value in latency.items():
                if isinstance(metric_value, (int, float)):
                    events.append(
                        (
                            timestamp,
                            run_id,
                            "system",
                            "latency",
                            metric_name,
                            self.convert_metric_value(metric_value),
                            model,
                            tag,
                            True,
                            json.dumps({"type": "system_metrics"}),
                        )
                    )

            # Log reranker metrics
            reranker = data.get("reranker", {})
            for metric_name, metric_value in reranker.items():
                if isinstance(metric_value, (int, float)):
                    events.append(
                        (
                            timestamp,
                            run_id,
                            "system",
                            "reranker",
                            metric_name,
                            self.convert_metric_value(metric_value),
                            model,
                            tag,
                            True,
                            json.dumps({"type": "system_metrics"}),
                        )
                    )

            # Log health metrics
            health = data.get("health", {})
            for metric_name, metric_value in health.items():
                if isinstance(metric_value, (int, float, bool)):
                    events.append(
                        (
                            timestamp,
                            run_id,
                            "system",
                            "health",
                            metric_name,
                            (
                                float(metric_value)
                                if isinstance(metric_value, bool)
                                else self.convert_metric_value(metric_value)
                            ),
                            model,
                            tag,
                            True,
                            json.dumps({"type": "system_metrics"}),
                        )
                    )

            # Batch insert events
            if events and not self.dry_run:
                for event in events:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT DO NOTHING
                        """,
                        event,
                    )
                self.stats["events_created"] += len(events)

            self.stats["runs_created"] += 1
            return True

        except Exception as e:
            error_msg = f"Error processing metrics file {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["files_skipped"] += 1
            self.stats["errors"].append(error_msg)
            return False

    def migrate_evaluation_file(self, file_path: Path) -> bool:
        """Migrate a single evaluation file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Add filename to data for reference
            data["filename"] = str(file_path.name)

            # Determine evaluation format and migrate
            if "evaluations" in data:
                # Evaluation suite format
                return self.migrate_evaluation_suite(data, file_path)
            elif "overall_metrics" in data and "case_results" in data:
                # Clean harness evaluation format
                return self.migrate_clean_harness_evaluation(data, file_path)
            elif "total_cases" in data and "case_results" in data:
                # Baseline evaluation format
                return self.migrate_baseline_evaluation(data, file_path)
            elif "latency" in data or "health" in data or "overall_score" in data:
                # Metrics file format
                return self.migrate_metrics_file(data, file_path)
            else:
                print(f"⚠️  Unknown evaluation format: {file_path}")
                self.stats["files_skipped"] += 1
                return False

        except Exception as e:
            error_msg = f"Error reading {file_path}: {e}"
            print(f"❌ {error_msg}")
            self.stats["files_skipped"] += 1
            self.stats["errors"].append(error_msg)
            return False

    def migrate_all_evaluations(self, base_dir: str = "evals/metrics", limit: int | None = None) -> Stats:
        """Migrate all evaluation files with proper batch processing."""
        print("🚀 Starting complete migration of historical evaluation data...")
        print(f"📁 Base directory: {base_dir}")
        print(f"📊 Batch size: {self.batch_size}")
        print(f"🔍 Dry run: {self.dry_run}")
        print()

        # Find all evaluation files
        json_files = self.find_evaluation_files(base_dir)
        if limit:
            json_files = json_files[:limit]

        print(f"📋 Found {len(json_files)} evaluation files to process")
        print()

        if self.dry_run:
            print("🧪 DRY RUN MODE - No data will be written to database")
            print()

        # Process files in batches
        for i in range(0, len(json_files), self.batch_size):
            batch_files = json_files[i : i + self.batch_size]
            batch_num = (i // self.batch_size) + 1
            total_batches = (len(json_files) + self.batch_size - 1) // self.batch_size

            print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch_files)} files)")

            # Process each file in the batch
            for file_path in batch_files:
                try:
                    success = self.migrate_evaluation_file(file_path)
                    if success:
                        self.stats["files_processed"] += 1
                    else:
                        self.stats["files_skipped"] += 1
                except Exception as e:
                    error_msg = f"Unexpected error processing {file_path}: {e}"
                    print(f"❌ {error_msg}")
                    self.stats["files_skipped"] += 1
                    self.stats["errors"].append(error_msg)

            # Commit batch
            if not self.dry_run and self.connection:
                try:
                    self.connection.commit()
                    print(f"✅ Batch {batch_num} committed successfully")
                except Exception as e:
                    print(f"❌ Error committing batch {batch_num}: {e}")
                    self.connection.rollback()
                    self.stats["errors"].append(f"Batch commit error: {e}")

            # Progress update
            processed = min(i + self.batch_size, len(json_files))
            print(f"📊 Progress: {processed}/{len(json_files)} files processed")
            print()

        print("=" * 60)
        print("🎯 Migration completed!")
        print("=" * 60)
        print(f"📊 Files processed: {self.stats['files_processed']}")
        print(f"📊 Files skipped: {self.stats['files_skipped']}")
        print(f"📊 Runs created: {self.stats['runs_created']}")
        print(f"📊 Events created: {self.stats['events_created']}")
        print(f"📊 Case results created: {self.stats['case_results_created']}")

        if self.stats["errors"]:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"   {error}")
            if len(self.stats["errors"]) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more errors")

        return self.stats


def main():
    """Main migration function."""
    import argparse

    parser = argparse.ArgumentParser(description="Complete migration of historical evaluation data to TimescaleDB")
    _ = parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no database writes)",
    )
    _ = parser.add_argument(
        "--base-dir",
        default="evals/metrics",
        help="Base directory to search for evaluation files",
    )
    _ = parser.add_argument("--dsn", help="Database DSN (overrides environment)")
    _ = parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    _ = parser.add_argument("--limit", type=int, help="Limit number of files to process")

    args = parser.parse_args()

    print("🔄 Complete Historical Evaluation Data Migration")
    print("=" * 60)

    try:
        with CompleteHistoricalEvalMigrator(batch_size=args.batch_size, dry_run=args.dry_run, dsn=args.dsn) as migrator:
            _ = migrator.migrate_all_evaluations(args.base_dir, args.limit)

            if not args.dry_run:
                print("\n🎯 Migration successful!")
                print(f"📈 Total data points: {migrator.stats['events_created']}")
            else:
                print("\n🧪 Dry run completed - no data written to database")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
