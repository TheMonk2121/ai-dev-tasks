#!/usr/bin/env python3
"""
Sample Historical Evaluation Data Migration Script

Loads a sample of historical evaluation JSON files into TimescaleDB for testing.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn


def load_sample_evaluations():
    """Load a sample of evaluation files into TimescaleDB."""

    # Sample files to migrate
    sample_files = [
        "300_evals/metrics/baseline_evaluations/ragchecker_clean_evaluation_20250907_070000.json",
        "300_evals/metrics/baseline_evaluations/baseline_ragchecker_v1.0_20250830_141742.json",
        "300_evals/metrics/baseline_evaluations/evaluation_suite_20250907_070001.json",
        "300_evals/metrics/baseline_evaluations/baseline_metrics_1756702701.json",
    ]

    dsn = resolve_dsn(strict=False)

    try:
        conn = psycopg2.connect(dsn, cursor_factory=RealDictCursor)
        cur = conn.cursor()

        print("🔄 Loading Sample Historical Evaluations")
        print("=" * 50)

        stats = {"files_processed": 0, "runs_created": 0, "events_created": 0, "case_results_created": 0, "errors": []}

        for file_path in sample_files:
            try:
                print(f"📁 Processing: {file_path}")

                with open(file_path, encoding="utf-8") as f:
                    data = json.load(f)

                # Generate run ID
                run_id = f"historical-{datetime.now().strftime('%Y%m%d_%H%M%S')}-{Path(file_path).stem[:20]}"

                # Determine evaluation type
                if "overall_metrics" in data and "case_results" in data:
                    # Clean harness format
                    overall_metrics = data.get("overall_metrics", {})

                    # Create run
                    cur.execute(
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
                            "ragchecker",
                            datetime.now(),
                            datetime.now(),
                            "claude-3-haiku",
                            json.dumps(
                                {
                                    "evaluation_type": "clean_harness_real_rag",
                                    "file_path": file_path,
                                    "overall_metrics": overall_metrics,
                                }
                            ),
                        ),
                    )
                    stats["runs_created"] += 1

                    # Log overall metrics
                    for metric_name, metric_value in overall_metrics.items():
                        cur.execute(
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
                                "claude-3-haiku",
                                "ragchecker",
                                True,
                                json.dumps({"type": "overall_metrics"}),
                            ),
                        )
                        stats["events_created"] += 1

                    # Process case results
                    case_results = data.get("case_results", [])
                    for i, case in enumerate(case_results[:10]):  # Limit to first 10 cases
                        case_id = case.get("query_id", f"case_{i}")

                        # Log case result
                        cur.execute(
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
                                case.get("f1_score", 0.0),
                                case.get("precision", 0.0),
                                case.get("recall", 0.0),
                                case.get("latency_sec", 0.0) * 1000 if case.get("latency_sec") else 0.0,
                                True,
                                json.dumps(
                                    {"query": case.get("query", "")[:200], "gt_answer": case.get("gt_answer", "")[:200]}
                                ),
                            ),
                        )
                        stats["case_results_created"] += 1

                        # Log case events
                        for metric_name in ["precision", "recall", "f1_score"]:
                            if metric_name in case:
                                cur.execute(
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
                                        case[metric_name],
                                        "claude-3-haiku",
                                        "ragchecker",
                                        True,
                                        json.dumps({"query": case.get("query", "")[:100]}),
                                    ),
                                )
                                stats["events_created"] += 1

                elif "total_cases" in data and "case_results" in data:
                    # Baseline format
                    total_cases = data.get("total_cases", 0)
                    total_score = data.get("total_score", 0.0)
                    avg_score = total_score / total_cases if total_cases > 0 else 0.0

                    # Create run
                    cur.execute(
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
                            "baseline",
                            datetime.now(),
                            datetime.now(),
                            "unknown",
                            json.dumps(
                                {
                                    "evaluation_type": "baseline_evaluation",
                                    "file_path": file_path,
                                    "total_cases": total_cases,
                                    "total_score": total_score,
                                    "category_scores": data.get("category_scores", {}),
                                }
                            ),
                        ),
                    )
                    stats["runs_created"] += 1

                    # Log overall score
                    cur.execute(
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
                            "unknown",
                            "baseline",
                            True,
                            json.dumps({"type": "overall_metrics"}),
                        ),
                    )
                    stats["events_created"] += 1

                    # Process case results
                    case_results = data.get("case_results", [])
                    for i, case in enumerate(case_results[:10]):  # Limit to first 10 cases
                        case_id = case.get("name", f"case_{i}").replace(" ", "_").lower()
                        score = case.get("score", 0.0)
                        passed = case.get("passed", False)

                        # Log case result
                        cur.execute(
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
                                        "query": case.get("query", "")[:200],
                                        "role": case.get("role", ""),
                                        "category": case.get("category", ""),
                                    }
                                ),
                            ),
                        )
                        stats["case_results_created"] += 1

                        # Log case event
                        cur.execute(
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
                                "unknown",
                                "baseline",
                                passed,
                                json.dumps({"query": case.get("query", "")[:100]}),
                            ),
                        )
                        stats["events_created"] += 1

                elif "latency" in data or "health" in data:
                    # Metrics format
                    cur.execute(
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
                            "system_metrics",
                            datetime.now(),
                            datetime.now(),
                            "system",
                            json.dumps(
                                {
                                    "evaluation_type": "system_metrics",
                                    "file_path": file_path,
                                    "overall_score": data.get("overall_score", 0.0),
                                    "status": data.get("status", "unknown"),
                                }
                            ),
                        ),
                    )
                    stats["runs_created"] += 1

                    # Log system metrics
                    for section in ["latency", "reranker", "health"]:
                        if section in data:
                            for metric_name, metric_value in data[section].items():
                                if isinstance(metric_value, (int, float, bool)):
                                    cur.execute(
                                        """
                                        INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    """,
                                        (
                                            datetime.now(),
                                            run_id,
                                            "system",
                                            section,
                                            metric_name,
                                            float(metric_value) if isinstance(metric_value, bool) else metric_value,
                                            "system",
                                            "system_metrics",
                                            True,
                                            json.dumps({"type": "system_metrics"}),
                                        ),
                                    )
                                    stats["events_created"] += 1

                stats["files_processed"] += 1
                print("  ✅ Processed successfully")

            except Exception as e:
                print(f"  ❌ Error: {e}")
                stats["errors"].append(f"Error processing {file_path}: {e}")

        # Commit all changes
        conn.commit()

        print("\n✅ Sample migration completed!")
        print(f"📊 Files processed: {stats['files_processed']}")
        print(f"📊 Runs created: {stats['runs_created']}")
        print(f"📊 Events created: {stats['events_created']}")
        print(f"📊 Case results created: {stats['case_results_created']}")

        if stats["errors"]:
            print(f"\n⚠️  Errors: {len(stats['errors'])}")
            for error in stats["errors"]:
                print(f"   {error}")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    load_sample_evaluations()
