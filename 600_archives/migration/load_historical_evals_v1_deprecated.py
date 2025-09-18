#!/usr/bin/env python3
"""
DEPRECATED: Historical Evaluation Data Migration Script

This file has been moved to 600_archives and is deprecated.
Use scripts/migration/load_historical_evals.py instead.

Loads all historical evaluation JSON files into TimescaleDB for analysis and monitoring.
Handles different evaluation formats and normalizes them into the standard schema.

DEPRECATED: This version has JSONB serialization issues. Use the complete version instead.
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


class HistoricalEvalMigrator:
    """Migrates historical evaluation data to TimescaleDB."""

    def __init__(self, dsn: str | None = None, dry_run: bool = False):
        self.dsn: str = dsn or resolve_dsn(strict=False)
        self.dry_run: bool = dry_run
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

    def __enter__(self) -> HistoricalEvalMigrator:
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

    def find_evaluation_files(self, base_dir: str = "300_evals/metrics") -> list[Path]:
        """Find all evaluation JSON files."""
        base_path = Path(base_dir)
        json_files = []

        for file_path in base_path.rglob("*.json"):
            # Skip certain directories and files
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

    def parse_timestamp_from_filename(self, filename: str) -> datetime | None:
        """Extract timestamp from filename patterns."""
        import re

        # Pattern 1: ragchecker_clean_evaluation_20250907_070000.json
        match = re.search(r"(\d{8})_(\d{6})", filename)
        if match:
            date_str, time_str = match.groups()
            try:
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        # Pattern 2: baseline_ragchecker_v1.0_20250830_141742.json
        match = re.search(r"(\d{10})", filename)
        if match:
            try:
                return datetime.fromtimestamp(float(match.group(1)))
            except ValueError:
                pass

        # Pattern 3: evaluation_suite_20250907_070001.json
        match = re.search(r"(\d{8})_(\d{6})", filename)
        if match:
            date_str, time_str = match.groups()
            try:
                return datetime.strptime(f"{date_str}_{time_str}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        return None

    def extract_run_id(self, file_path: Path, data: dict[str, Any]) -> str:
        """Extract or generate run ID for the evaluation."""
        # Try to get run_id from data
        if "run_id" in data:
            return data["run_id"]

        # Try to get from config
        if "config" in data and "run_id" in data["config"]:
            return data["config"]["run_id"]

        # Generate from filename and timestamp
        timestamp = self.parse_timestamp_from_filename(file_path.name)
        if timestamp:
            return f"historical-{timestamp.strftime('%Y%m%d_%H%M%S')}-{file_path.stem[:20]}"

        # Fallback to filename
        return f"historical-{file_path.stem}"

    def extract_evaluation_type(self, data: dict[str, Any]) -> str:
        """Extract evaluation type from data."""
        if "evaluation_type" in data:
            return data["evaluation_type"]

        # Infer from filename
        filename = data.get("filename", "")
        if "ragchecker" in filename.lower():
            return "ragchecker_evaluation"
        elif "baseline" in filename.lower():
            return "baseline_evaluation"
        elif "synthetic" in filename.lower():
            return "synthetic_evaluation"
        elif "smoke" in filename.lower():
            return "smoke_test"
        else:
            return "unknown_evaluation"

    def extract_model_info(self, data: dict[str, Any]) -> tuple[str, str]:
        """Extract model and tag information."""
        model = "unknown"
        tag = "historical"

        # Try to get from config
        if "config" in data:
            config = data["config"]
            if "dspy_model" in config:
                model = config["dspy_model"]
            elif "model" in config:
                model = config["model"]

        # Try to get from environment
        if "environment" in data:
            env = data["environment"]
            if "DSPY_MODEL" in env:
                model = env["DSPY_MODEL"]
            elif "MODEL" in env:
                model = env["MODEL"]

        # Infer tag from evaluation type
        eval_type = self.extract_evaluation_type(data)
        if "ragchecker" in eval_type:
            tag = "ragchecker"
        elif "baseline" in eval_type:
            tag = "baseline"
        elif "synthetic" in eval_type:
            tag = "synthetic"
        elif "smoke" in eval_type:
            tag = "smoke_test"

        return model, tag

    def migrate_clean_harness_evaluation(self, file_path: Path, data: dict[str, Any]) -> bool:
        """Migrate clean harness evaluation format."""
        try:
            run_id = self.extract_run_id(file_path, data)
            model, tag = self.extract_model_info(data)

            # Extract overall metrics
            overall_metrics = data.get("overall_metrics", {})
            precision = overall_metrics.get("precision", 0.0)
            recall = overall_metrics.get("recall", 0.0)
            f1_score = overall_metrics.get("f1_score", 0.0)
            faithfulness = overall_metrics.get("faithfulness", 0.0)

            # Create evaluation run
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
                        datetime.now(),
                        datetime.now(),
                        model,
                        json.dumps(
                            {
                                "evaluation_type": self.extract_evaluation_type(data),
                                "file_path": str(file_path),
                                "overall_metrics": overall_metrics,
                                "config": data.get("config", {}),
                                "environment": data.get("environment", {}),
                            }
                        ),
                    ),
                )
                self.stats["runs_created"] += 1

            # Log overall metrics as events
            for metric_name, metric_value in [
                ("precision", precision),
                ("recall", recall),
                ("f1_score", f1_score),
                ("faithfulness", faithfulness),
            ]:
                if not self.dry_run:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            datetime.now(),
                            run_id,
                            "overall",
                            "evaluation",
                            metric_name,
                            metric_value,
                            model,
                            tag,
                            True,
                            json.dumps({"type": "overall_metrics"}),
                        ),
                    )
                    self.stats["events_created"] += 1

            # Process case results
            case_results = data.get("case_results", [])
            for i, case in enumerate(case_results):
                case_id = case.get("query_id", f"case_{i}")
                query = case.get("query", "")

                # Extract case metrics
                case_precision = case.get("precision", 0.0)
                case_recall = case.get("recall", 0.0)
                case_f1 = case.get("f1_score", 0.0)
                case_faithfulness = case.get("faithfulness", 0.0)
                latency_ms = case.get("latency_sec", 0.0) * 1000 if case.get("latency_sec") else 0.0

                # Log case result
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
                            True,
                            json.dumps(
                                {
                                    "query": query,
                                    "gt_answer": case.get("gt_answer", ""),
                                    "faithfulness": case_faithfulness,
                                    "retrieved_context_count": len(case.get("retrieved_context", [])),
                                    "tags": case.get("tags", []),
                                    "mode": case.get("mode", "reader"),
                                }
                            ),
                        ),
                    )
                    self.stats["case_results_created"] += 1

                # Log individual case events
                for metric_name, metric_value in [
                    ("precision", case_precision),
                    ("recall", case_recall),
                    ("f1_score", case_f1),
                    ("faithfulness", case_faithfulness),
                ]:
                    if not self.dry_run:
                        self.cursor.execute(
                            """
                            INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                datetime.now(),
                                run_id,
                                case_id,
                                "score",
                                metric_name,
                                metric_value,
                                model,
                                tag,
                                True,
                                json.dumps({"query": query[:200]}),
                            ),
                        )
                        self.stats["events_created"] += 1

            return True

        except Exception as e:
            self.stats["errors"].append(f"Error processing {file_path}: {e}")
            return False

    def migrate_baseline_evaluation(self, file_path: Path, data: dict[str, Any]) -> bool:
        """Migrate baseline evaluation format."""
        try:
            run_id = self.extract_run_id(file_path, data)
            model, tag = self.extract_model_info(data)

            # Extract overall metrics
            total_cases = data.get("total_cases", 0)
            passed_cases = data.get("passed_cases", 0)
            failed_cases = data.get("failed_cases", 0)
            total_score = data.get("total_score", 0.0)
            avg_score = total_score / total_cases if total_cases > 0 else 0.0

            # Create evaluation run
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
                        datetime.now(),
                        datetime.now(),
                        model,
                        json.dumps(
                            {
                                "evaluation_type": self.extract_evaluation_type(data),
                                "file_path": str(file_path),
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

            # Log overall metrics as events
            if not self.dry_run:
                self.cursor.execute(
                    """
                    INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                    (
                        datetime.now(),
                        run_id,
                        "overall",
                        "evaluation",
                        "average_score",
                        avg_score,
                        model,
                        tag,
                        True,
                        json.dumps({"type": "overall_metrics"}),
                    ),
                )
                self.stats["events_created"] += 1

            # Process case results
            case_results = data.get("case_results", [])
            for i, case in enumerate(case_results):
                case_id = case.get("name", f"case_{i}").replace(" ", "_").lower()
                query = case.get("query", "")
                score = case.get("score", 0.0)
                passed = case.get("passed", False)

                # Log case result
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
                                    "role": case.get("role", ""),
                                    "category": case.get("category", ""),
                                    "response_length": case.get("response_length", 0),
                                    "details": case.get("details", []),
                                    "errors": case.get("errors", []),
                                }
                            ),
                        ),
                    )
                    self.stats["case_results_created"] += 1

                # Log individual case events
                if not self.dry_run:
                    self.cursor.execute(
                        """
                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                        (
                            datetime.now(),
                            run_id,
                            case_id,
                            "score",
                            "score",
                            score,
                            model,
                            tag,
                            passed,
                            json.dumps({"query": query[:200]}),
                        ),
                    )
                    self.stats["events_created"] += 1

            return True

        except Exception as e:
            self.stats["errors"].append(f"Error processing {file_path}: {e}")
            return False

    def migrate_evaluation_suite(self, file_path: Path, data: dict[str, Any]) -> bool:
        """Migrate evaluation suite format (contains multiple evaluations)."""
        try:
            evaluations = data.get("evaluations", {})
            success_count = 0

            for eval_name, eval_data in evaluations.items():
                if "results" in eval_data:
                    # Create a temporary data structure for the nested evaluation
                    nested_data = eval_data["results"]
                    nested_data["filename"] = f"{file_path.name}#{eval_name}"
                    nested_data["evaluation_type"] = eval_data.get("eval_type", "unknown")

                    # Migrate the nested evaluation
                    if "overall_metrics" in nested_data and "case_results" in nested_data:
                        if self.migrate_clean_harness_evaluation(file_path, nested_data):
                            success_count += 1
                    elif "total_cases" in nested_data and "case_results" in nested_data:
                        if self.migrate_baseline_evaluation(file_path, nested_data):
                            success_count += 1

            return success_count > 0

        except Exception as e:
            self.stats["errors"].append(f"Error processing evaluation suite {file_path}: {e}")
            return False

    def migrate_metrics_file(self, file_path: Path, data: dict[str, Any]) -> bool:
        """Migrate metrics file format (system performance metrics)."""
        try:
            run_id = self.extract_run_id(file_path, data)
            model, tag = self.extract_model_info(data)

            # Create evaluation run
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
                        datetime.now(),
                        datetime.now(),
                        model,
                        json.dumps(
                            {
                                "evaluation_type": "system_metrics",
                                "file_path": str(file_path),
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

            # Log latency metrics
            latency = data.get("latency", {})
            for metric_name, metric_value in latency.items():
                if isinstance(metric_value, (int, float)):
                    if not self.dry_run:
                        self.cursor.execute(
                            """
                            INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                datetime.now(),
                                run_id,
                                "system",
                                "latency",
                                metric_name,
                                metric_value,
                                model,
                                tag,
                                True,
                                json.dumps({"type": "system_metrics"}),
                            ),
                        )
                        self.stats["events_created"] += 1

            # Log reranker metrics
            reranker = data.get("reranker", {})
            for metric_name, metric_value in reranker.items():
                if isinstance(metric_value, (int, float)):
                    if not self.dry_run:
                        self.cursor.execute(
                            """
                            INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                datetime.now(),
                                run_id,
                                "system",
                                "reranker",
                                metric_name,
                                metric_value,
                                model,
                                tag,
                                True,
                                json.dumps({"type": "system_metrics"}),
                            ),
                        )
                        self.stats["events_created"] += 1

            # Log health metrics
            health = data.get("health", {})
            for metric_name, metric_value in health.items():
                if isinstance(metric_value, (int, float, bool)):
                    if not self.dry_run:
                        self.cursor.execute(
                            """
                            INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                            (
                                datetime.now(),
                                run_id,
                                "system",
                                "health",
                                metric_name,
                                (float(metric_value) if isinstance(metric_value, bool) else metric_value),
                                model,
                                tag,
                                True,
                                json.dumps({"type": "system_metrics"}),
                            ),
                        )
                        self.stats["events_created"] += 1

            return True

        except Exception as e:
            self.stats["errors"].append(f"Error processing metrics file {file_path}: {e}")
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
                return self.migrate_evaluation_suite(file_path, data)
            elif "overall_metrics" in data and "case_results" in data:
                # Clean harness evaluation format
                return self.migrate_clean_harness_evaluation(file_path, data)
            elif "total_cases" in data and "case_results" in data:
                # Baseline evaluation format
                return self.migrate_baseline_evaluation(file_path, data)
            elif "latency" in data or "health" in data or "overall_score" in data:
                # Metrics file format
                return self.migrate_metrics_file(file_path, data)
            else:
                print(f"⚠️  Unknown evaluation format: {file_path}")
                self.stats["files_skipped"] += 1
                return False

        except Exception as e:
            self.stats["errors"].append(f"Error reading {file_path}: {e}")
            return False

    def migrate_all_evaluations(self, base_dir: str = "300_evals/metrics") -> Stats:
        """Migrate all historical evaluation files."""
        print(f"🔍 Finding evaluation files in {base_dir}...")
        json_files = self.find_evaluation_files(base_dir)
        print(f"📁 Found {len(json_files)} evaluation files")

        if self.dry_run:
            print("🧪 DRY RUN MODE - No data will be written to database")

        print("\n🚀 Starting migration...")

        for i, file_path in enumerate(json_files):
            if i % 100 == 0:
                print(f"📊 Progress: {i}/{len(json_files)} files processed")

            try:
                success = self.migrate_evaluation_file(file_path)
                if success:
                    self.stats["files_processed"] += 1
                else:
                    self.stats["files_skipped"] += 1
            except Exception as e:
                self.stats["errors"].append(f"Unexpected error processing {file_path}: {e}")
                self.stats["files_skipped"] += 1

        # Commit all changes
        if not self.dry_run and self.connection:
            self.connection.commit()

        print("\n✅ Migration completed!")
        print(f"📊 Files processed: {self.stats['files_processed']}")
        print(f"📊 Files skipped: {self.stats['files_skipped']}")
        print(f"📊 Runs created: {self.stats['runs_created']}")
        print(f"📊 Events created: {self.stats['events_created']}")
        print(f"📊 Case results created: {self.stats['case_results_created']}")

        if self.stats["errors"]:
            print(f"\n⚠️  Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"][:10]:  # Show first 10 errors
                print(f"   {error}")
            if len(self.stats["errors"]) > 10:
                print(f"   ... and {len(self.stats['errors']) - 10} more errors")

        return self.stats


def main():
    """Main migration function."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate historical evaluation data to TimescaleDB")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no database writes)",
    )
    parser.add_argument(
        "--base-dir",
        default="300_evals/metrics",
        help="Base directory to search for evaluation files",
    )
    parser.add_argument("--dsn", help="Database DSN (overrides environment)")

    args = parser.parse_args()

    print("🔄 Historical Evaluation Data Migration")
    print("=" * 50)

    try:
        with HistoricalEvalMigrator(dsn=args.dsn, dry_run=args.dry_run) as migrator:
            stats = migrator.migrate_all_evaluations(args.base_dir)

            if not args.dry_run:
                _ = print("\n🎯 Migration successful!")
                _ = print(f"📈 Total data points: {stats['events_created'] + stats['case_results_created']}")
            else:
                _ = print("\n🧪 Dry run completed - no data written to database")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
