#!/usr/bin/env python3
"""
Database Telemetry Logger for TimescaleDB

Handles structured logging to TimescaleDB tables for evaluation telemetry.
Designed to work with the existing TimescaleDB schema for optimal performance.
"""

from __future__ import annotations

import json
import os
import sys
from contextlib import nullcontext
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.common.db_dsn import resolve_dsn

# Import Logfire for observability
try:
    from scripts.monitoring.observability import get_logfire, init_observability

    logfire = get_logfire()
    LOGFIRE_AVAILABLE = True
except ImportError:
    logfire = None
    LOGFIRE_AVAILABLE = False


class DatabaseTelemetryLogger:
    """Handles structured logging to TimescaleDB for evaluation telemetry."""

    def __init__(self, run_id: str, dsn: str | None = None):
        self.run_id = run_id
        self.dsn = dsn or resolve_dsn(strict=False)
        self.connection = None
        self.cursor = None

        # Initialize Logfire if available
        if LOGFIRE_AVAILABLE:
            try:
                init_observability(service="ai-dev-tasks")
                self.logfire_span = logfire.span("db_telemetry", run_id=run_id)
            except Exception as e:
                print(f"⚠️  Logfire initialization failed: {e}")
                self.logfire_span = None
        else:
            self.logfire_span = None

    def __enter__(self):
        """Context manager entry."""
        try:
            self.connection = psycopg2.connect(self.dsn, cursor_factory=RealDictCursor)
            self.cursor = self.connection.cursor()
            return self
        except Exception as e:
            print(f"⚠️  Database connection failed: {e}")
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def log_eval_run(
        self,
        tag: str = "evaluation",
        model: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
        meta: dict[str, Any] | None = None,
    ) -> bool:
        """Log evaluation run metadata to eval_run table."""
        if not self.cursor:
            return False

        try:
            started_at = started_at or datetime.now()
            meta = meta or {}

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
                (self.run_id, tag, started_at, finished_at, model, json.dumps(meta, default=str)),
            )

            self.connection.commit()

            # Log to Logfire
            if LOGFIRE_AVAILABLE and logfire:
                logfire.info("db_telemetry.eval_run_logged", run_id=self.run_id, tag=tag, model=model)

            return True
        except Exception as e:
            print(f"⚠️  Failed to log eval_run: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def log_eval_event(
        self,
        case_id: str,
        stage: str,
        metric_name: str,
        metric_value: float,
        model: str | None = None,
        tag: str | None = None,
        ok: bool | None = None,
        meta: dict[str, Any] | None = None,
        timestamp: datetime | None = None,
    ) -> bool:
        """Log individual evaluation event to eval_event table."""
        if not self.cursor:
            return False

        try:
            timestamp = timestamp or datetime.now()
            meta = meta or {}

            self.cursor.execute(
                """
                INSERT INTO eval_event (ts, run_id, case_id, stage, metric_name, metric_value, model, tag, ok, meta)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
                (
                    timestamp,
                    self.run_id,
                    case_id,
                    stage,
                    metric_name,
                    metric_value,
                    model,
                    tag,
                    ok,
                    json.dumps(meta, default=str),
                ),
            )

            self.connection.commit()
            return True
        except Exception as e:
            print(f"⚠️  Failed to log eval_event: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def log_case_result(
        self,
        case_id: str,
        f1: float | None = None,
        precision: float | None = None,
        recall: float | None = None,
        latency_ms: float | None = None,
        ok: bool | None = None,
        meta: dict[str, Any] | None = None,
    ) -> bool:
        """Log case result to eval_case_result table."""
        if not self.cursor:
            return False

        try:
            meta = meta or {}

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
                (self.run_id, case_id, f1, precision, recall, latency_ms, ok, json.dumps(meta, default=str)),
            )

            self.connection.commit()
            return True
        except Exception as e:
            print(f"⚠️  Failed to log case_result: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def log_configuration(self, config_data: dict[str, Any]) -> bool:
        """Log configuration data to eval_run.meta."""
        if not self.cursor:
            return False

        try:
            self.cursor.execute(
                """
                UPDATE eval_run 
                SET meta = meta || %s
                WHERE run_id = %s
            """,
                (json.dumps({"config": config_data}, default=str), self.run_id),
            )

            self.connection.commit()

            # Log to Logfire
            if LOGFIRE_AVAILABLE and logfire:
                logfire.info("db_telemetry.config_logged", run_id=self.run_id, config_keys=list(config_data.keys()))

            return True
        except Exception as e:
            print(f"⚠️  Failed to log configuration: {e}")
            if self.connection:
                self.connection.rollback()
            return False

    def log_evaluation_metrics(
        self,
        case_id: str,
        precision: float,
        recall: float,
        f1: float,
        latency_ms: float,
        ok: bool = True,
        additional_metrics: dict[str, Any] | None = None,
    ) -> bool:
        """Log comprehensive evaluation metrics for a case."""
        if not self.cursor:
            return False

        try:
            # Log individual metrics as events
            metrics = [
                ("precision", precision),
                ("recall", recall),
                ("f1", f1),
                ("latency_ms", latency_ms),
            ]

            for metric_name, metric_value in metrics:
                self.log_eval_event(
                    case_id=case_id,
                    stage="score",
                    metric_name=metric_name,
                    metric_value=metric_value,
                    ok=ok,
                    meta=additional_metrics or {},
                )

            # Log case result summary
            self.log_case_result(
                case_id=case_id,
                f1=f1,
                precision=precision,
                recall=recall,
                latency_ms=latency_ms,
                ok=ok,
                meta=additional_metrics or {},
            )

            return True
        except Exception as e:
            print(f"⚠️  Failed to log evaluation metrics: {e}")
            return False

    def log_retrieval_metrics(
        self,
        case_id: str,
        query: str,
        candidates_count: int,
        latency_ms: float,
        ok: bool = True,
        additional_metrics: dict[str, Any] | None = None,
    ) -> bool:
        """Log retrieval-specific metrics."""
        if not self.cursor:
            return False

        try:
            meta = {"query": query, "candidates_count": candidates_count, **(additional_metrics or {})}

            # Log retrieval latency
            self.log_eval_event(
                case_id=case_id, stage="retrieve", metric_name="latency_ms", metric_value=latency_ms, ok=ok, meta=meta
            )

            # Log candidate count
            self.log_eval_event(
                case_id=case_id,
                stage="retrieve",
                metric_name="candidates_count",
                metric_value=float(candidates_count),
                ok=ok,
                meta=meta,
            )

            return True
        except Exception as e:
            print(f"⚠️  Failed to log retrieval metrics: {e}")
            return False

    def log_reader_metrics(
        self,
        case_id: str,
        query: str,
        response_length: int,
        latency_ms: float,
        ok: bool = True,
        additional_metrics: dict[str, Any] | None = None,
    ) -> bool:
        """Log reader-specific metrics."""
        if not self.cursor:
            return False

        try:
            meta = {"query": query, "response_length": response_length, **(additional_metrics or {})}

            # Log reader latency
            self.log_eval_event(
                case_id=case_id, stage="reader", metric_name="latency_ms", metric_value=latency_ms, ok=ok, meta=meta
            )

            # Log response length
            self.log_eval_event(
                case_id=case_id,
                stage="reader",
                metric_name="response_length",
                metric_value=float(response_length),
                ok=ok,
                meta=meta,
            )

            return True
        except Exception as e:
            print(f"⚠️  Failed to log reader metrics: {e}")
            return False

    def finish_run(self, finished_at: datetime | None = None) -> bool:
        """Mark evaluation run as finished."""
        if not self.cursor:
            return False

        try:
            finished_at = finished_at or datetime.now()

            self.cursor.execute(
                """
                UPDATE eval_run 
                SET finished_at = %s
                WHERE run_id = %s
            """,
                (finished_at, self.run_id),
            )

            self.connection.commit()

            # Log to Logfire
            if LOGFIRE_AVAILABLE and logfire:
                logfire.info("db_telemetry.run_finished", run_id=self.run_id, finished_at=finished_at.isoformat())

            return True
        except Exception as e:
            print(f"⚠️  Failed to finish run: {e}")
            if self.connection:
                self.connection.rollback()
            return False


def create_db_telemetry_logger(run_id: str, dsn: str | None = None) -> DatabaseTelemetryLogger:
    """Factory function to create a database telemetry logger."""
    return DatabaseTelemetryLogger(run_id, dsn)


if __name__ == "__main__":
    # Test the database telemetry logger
    logger = create_db_telemetry_logger("test-db-telemetry-001")

    with logger as db_logger:
        # Test eval run logging
        success = db_logger.log_eval_run(
            tag="test_evaluation", model="test-model", meta={"test": True, "version": "1.0"}
        )
        print(f"Eval run logged: {success}")

        # Test configuration logging
        config_data = {"profile": "test", "driver": "test_driver", "database_connected": True}
        success = db_logger.log_configuration(config_data)
        print(f"Configuration logged: {success}")

        # Test evaluation metrics
        success = db_logger.log_evaluation_metrics(
            case_id="test_case_001",
            precision=0.85,
            recall=0.78,
            f1=0.81,
            latency_ms=150.5,
            ok=True,
            additional_metrics={"test_metric": "test_value"},
        )
        print(f"Evaluation metrics logged: {success}")

        # Test retrieval metrics
        success = db_logger.log_retrieval_metrics(
            case_id="test_case_001", query="test query", candidates_count=10, latency_ms=50.2, ok=True
        )
        print(f"Retrieval metrics logged: {success}")

        # Test reader metrics
        success = db_logger.log_reader_metrics(
            case_id="test_case_001", query="test query", response_length=150, latency_ms=100.3, ok=True
        )
        print(f"Reader metrics logged: {success}")

        # Finish run
        success = db_logger.finish_run()
        print(f"Run finished: {success}")

    print("🎯 Database telemetry test completed!")
