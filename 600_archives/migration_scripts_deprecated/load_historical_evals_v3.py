#!/usr/bin/env python3
"""
Fixed historical evaluation data migration to TimescaleDB.

This script properly handles JSONB serialization and implements best practices:
- Proper JSON serialization for JSONB fields
- Batch processing with proper transaction management
- Data type validation and conversion
- Error handling and recovery
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.psycopg3_config import Psycopg3Config

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.common.db_dsn import resolve_dsn


class FixedHistoricalEvalMigrator:
    """Fixed migrator with proper JSONB serialization."""

    def __init__(self, batch_size: int = 100, dry_run: bool = False):
        self.batch_size = batch_size
        self.dry_run = dry_run
        self.conn = None
        self.cur = None
        self.stats = {
            "files_processed": 0,
            "files_skipped": 0,
            "runs_created": 0,
            "events_created": 0,
            "case_results_created": 0,
            "errors": 0,
        }

    def __enter__(self):
        """Context manager entry."""
        self.conn = psycopg2.connect(resolve_dsn(strict=False))
        self.cur = self.conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

    def find_evaluation_files(self, base_dir: str) -> list[Path]:
        """Find all evaluation JSON files recursively."""
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

            json_files.append(file_path)

        return sorted(json_files)

    def parse_timestamp_from_filename(self, file_path: Path) -> datetime | None:
        """Extract timestamp from filename patterns."""
        filename = file_path.name

        # Pattern 1: YYYYMMDD_HHMMSS
        if "_" in filename and len(filename.split("_")) >= 2:
            try:
                date_part = filename.split("_")[0]
                time_part = filename.split("_")[1].split(".")[0]
                if len(date_part) == 8 and len(time_part) == 6:
                    return datetime.strptime(f"{date_part}_{time_part}", "%Y%m%d_%H%M%S")
            except ValueError:
                pass

        # Pattern 2: timestamp numbers
        try:
            # Extract numbers from filename
            import re

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
        """Extract or generate run ID."""
        # Try to get from data
        if "run_id" in data:
            return str(data["run_id"])
        if "evaluation_id" in data:
            return str(data["evaluation_id"])

        # Generate from filename and timestamp
        timestamp = self.parse_timestamp_from_filename(file_path)
        if timestamp:
            return f"eval-{timestamp.strftime('%Y%m%d_%H%M%S')}"

        return f"eval-{file_path.stem}"

    def extract_evaluation_type(self, data: dict[str, Any], file_path: Path) -> str:
        """Extract evaluation type from data or filename."""
        if "evaluation_type" in data:
            return str(data["evaluation_type"])

        filename = file_path.name.lower()
        if "ragchecker" in filename:
            return "ragchecker"
        elif "baseline" in filename:
            return "baseline"
        elif "synthetic" in filename:
            return "synthetic"
        elif "clean" in filename:
            return "clean_harness"
        else:
            return "unknown"

    def extract_model_info(self, data: dict[str, Any]) -> tuple[str, str]:
        """Extract model and tag information."""
        model = "unknown"
        tag = "evaluation"

        # Try to get model from various possible keys
        model_keys = ["model", "dspy_model", "llm_model", "provider"]
        for key in model_keys:
            if key in data:
                model = str(data[key])
                break

        # Try to get tag from various possible keys
        tag_keys = ["tag", "profile", "eval_profile", "environment"]
        for key in tag_keys:
            if key in data:
                tag = str(data[key])
                break

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
        """Migrate clean harness evaluation format."""
        try:
            run_id = self.extract_run_id(data, file_path)
            model, tag = self.extract_model_info(data)

            # Extract timestamp
            timestamp = self.parse_timestamp_from_filename(file_path)
            if not timestamp:
                timestamp = datetime.now()

            # Insert evaluation run with proper JSONB serialization
            if not self.dry_run:
                self.cur.execute(
                    """
                    INSERT INTO eval_run (run_id, tag, started_at, finished_at, model, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                    """,
                    (
                        run_id,
                        tag,
                        timestamp,
                        timestamp,
                        model,
                        json.dumps(
                            {
                                "evaluation_type": "clean_harness",
                                "filename": str(file_path.name),
                                "source_file": str(file_path),
                            }
                        ),
                    ),
                )

            self.stats["runs_created"] += 1

            # Process case results
            case_results = data.get("case_results", [])
            events = []

            for i, case in enumerate(case_results):
                case_id = case.get("case_id", f"case_{i}")
                precision = self.convert_metric_value(case.get("precision", 0.0))
                recall = self.convert_metric_value(case.get("recall", 0.0))
                f1 = self.convert_metric_value(case.get("f1_score", 0.0))
                latency = self.convert_metric_value(case.get("latency_sec", 0.0)) * 1000  # Convert to ms

                # Insert case result with proper JSONB serialization
                if not self.dry_run:
                    self.cur.execute(
                        """
                        INSERT INTO eval_case_result (run_id, case_id, f1, precision, recall, latency_ms, ok, meta)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (run_id, case_id) DO NOTHING
                        """,
                        (
                            run_id,
                            case_id,
                            f1,
                            precision,
                            recall,
                            latency,
                            "error" not in case,
                            json.dumps(
                                {
                                    "query": case.get("query", "")[:200],
                                    "response": case.get("response", "")[:200],
                                    "tags": case.get("tags", []),
                                }
                            ),
                        ),
                    )

                self.stats["case_results_created"] += 1

                # Create events for each metric
                for metric_name, metric_value in [
                    ("f1", f1),
                    ("precision", precision),
                    ("recall", recall),
                    ("latency_ms", latency),
                ]:
                    events.append(
                        (
                            timestamp,
                            run_id,
                            case_id,
                            "evaluation",
                            metric_name,
                            metric_value,
                            model,
                            tag,
                            True,
                            json.dumps({"case_index": i}),
                        )
                    )

            # Batch insert events
            if events and not self.dry_run:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                    """,
                    events,
                )

            self.stats["events_created"] += len(events)
            return True

        except Exception as e:
            print(f"❌ Error processing clean harness evaluation {file_path}: {e}")
            self.stats["errors"] += 1
            return False

    def migrate_baseline_evaluation(self, data: dict[str, Any], file_path: Path) -> bool:
        """Migrate baseline evaluation format."""
        try:
            run_id = self.extract_run_id(data, file_path)
            model, tag = self.extract_model_info(data)

            # Extract timestamp
            timestamp = self.parse_timestamp_from_filename(file_path)
            if not timestamp:
                timestamp = datetime.now()

            # Insert evaluation run with proper JSONB serialization
            if not self.dry_run:
                self.cur.execute(
                    """
                    INSERT INTO eval_run (run_id, tag, started_at, finished_at, model, meta)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (run_id) DO NOTHING
                    """,
                    (
                        run_id,
                        tag,
                        timestamp,
                        timestamp,
                        model,
                        json.dumps(
                            {
                                "evaluation_type": "baseline",
                                "filename": str(file_path.name),
                                "source_file": str(file_path),
                            }
                        ),
                    ),
                )

            self.stats["runs_created"] += 1

            # Process overall metrics
            overall_metrics = data.get("overall_metrics", {})
            events = []

            for metric_name, metric_value in overall_metrics.items():
                if isinstance(metric_value, (int, float)):
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

            # Batch insert events
            if events and not self.dry_run:
                execute_values(
                    self.cur,
                    """
                    INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                    VALUES %s
                    ON CONFLICT DO NOTHING
                    """,
                    events,
                )

            self.stats["events_created"] += len(events)
            return True

        except Exception as e:
            print(f"❌ Error processing baseline evaluation {file_path}: {e}")
            self.stats["errors"] += 1
            return False

    def migrate_evaluation_file(self, file_path: Path) -> bool:
        """Migrate a single evaluation file."""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Determine format and migrate
            if "case_results" in data and "overall_metrics" in data:
                return self.migrate_clean_harness_evaluation(data, file_path)
            elif "overall_metrics" in data:
                return self.migrate_baseline_evaluation(data, file_path)
            else:
                print(f"⚠️  Unknown evaluation format: {file_path}")
                self.stats["files_skipped"] += 1
                return False

        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            self.stats["errors"] += 1
            return False

    def migrate_all_evaluations(self, base_dir: str, limit: int | None = None) -> dict[str, int]:
        """Migrate all evaluation files with proper batch processing."""
        print("🚀 Starting fixed migration of historical evaluation data...")
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
                    print(f"❌ Unexpected error processing {file_path}: {e}")
                    self.stats["errors"] += 1

            # Commit batch
            if not self.dry_run:
                try:
                    self.conn.commit()
                    print(f"✅ Batch {batch_num} committed successfully")
                except Exception as e:
                    print(f"❌ Error committing batch {batch_num}: {e}")
                    self.conn.rollback()
                    self.stats["errors"] += 1

            # Progress update
            processed = min(i + self.batch_size, len(json_files))
            print(f"📊 Progress: {processed}/{len(json_files)} files processed")

        return self.stats


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate historical evaluation data to TimescaleDB")
    parser.add_argument("--base-dir", default="300_evals/metrics", help="Base directory to search for JSON files")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch size for processing")
    parser.add_argument("--limit", type=int, help="Limit number of files to process")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without inserting data")

    args = parser.parse_args()

    with FixedHistoricalEvalMigrator(batch_size=args.batch_size, dry_run=args.dry_run) as migrator:
        stats = migrator.migrate_all_evaluations(args.base_dir, args.limit)

        print("\n" + "=" * 60)
        print("🎯 Migration completed!")
        print("=" * 60)
        print(f"📊 Files processed: {stats['files_processed']}")
        print(f"📊 Files skipped: {stats['files_skipped']}")
        print(f"📊 Runs created: {stats['runs_created']}")
        print(f"📊 Events created: {stats['events_created']}")
        print(f"📊 Case results created: {stats['case_results_created']}")
        print(f"❌ Errors encountered: {stats['errors']}")


if __name__ == "__main__":
    main()
