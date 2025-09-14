"""
Metrics Collection for AI Development Tasks

Collects and analyzes system metrics including:
- Database performance metrics
- Memory system usage
- RAG system performance
- System resource utilization
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


def get_metrics() -> dict[str, Any]:
    """Get comprehensive system metrics"""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "database_metrics": get_database_metrics(),
        "memory_metrics": get_memory_metrics(),
        "rag_metrics": get_rag_metrics(),
        "system_metrics": get_system_metrics(),
    }
    return metrics


def get_database_metrics() -> dict[str, Any]:
    """Get database performance metrics"""
    try:
        database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_agency")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        metrics = {}

        # Get database size
        cursor.execute(
            """
            SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                   pg_database_size(current_database()) as size_bytes
        """
        )
        result = cursor.fetchone()
        if result:
            metrics["database_size"] = result["size"]
            metrics["database_size_bytes"] = result["size_bytes"]

        # Get table counts
        cursor.execute(
            """
            SELECT schemaname, tablename, n_tup_ins as inserts, n_tup_upd as updates, 
                   n_tup_del as deletes, n_live_tup as live_tuples
            FROM pg_stat_user_tables
            ORDER BY n_live_tup DESC
            LIMIT 10
        """
        )
        tables = cursor.fetchall()
        metrics["top_tables"] = [dict(row) for row in tables]

        # Check if pg_stat_statements is available
        cursor.execute(
            """
            SELECT EXISTS(
                SELECT 1 FROM pg_extension 
                WHERE extname = 'pg_stat_statements'
            ) as exists
        """
        )
        result = cursor.fetchone()
        pg_stat_enabled = result["exists"] if result else False
        metrics["pg_stat_statements_enabled"] = pg_stat_enabled

        if pg_stat_enabled:
            # Get slow queries
            cursor.execute(
                """
                SELECT query, calls, total_time, mean_time, rows
                FROM pg_stat_statements
                ORDER BY total_time DESC
                LIMIT 5
            """
            )
            slow_queries = cursor.fetchall()
            metrics["slow_queries"] = [dict(row) for row in slow_queries]

        cursor.close()
        conn.close()

        return metrics

    except Exception as e:
        return {"error": f"Database metrics collection failed: {e}"}


def get_memory_metrics() -> dict[str, Any]:
    """Get memory system metrics"""
    try:
        metrics: dict[str, Any] = {}

        # Check memory system file sizes
        memory_files = [
            "100_memory/100_cursor-memory-context.md",
            "100_memory/104_dspy-development-context.md",
        ]

        file_metrics: dict[str, int | None] = {}
        total_size = 0
        for file_path in memory_files:
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                file_metrics[file_path] = size
                total_size += size
            else:
                file_metrics[file_path] = None

        metrics["memory_files"] = file_metrics
        metrics["total_memory_files_size"] = total_size

        # Check memory system scripts
        memory_scripts = [
            "scripts/unified_memory_orchestrator.py",
            "scripts/update_cursor_memory.py",
        ]

        script_metrics: dict[str, int | None] = {}
        for script_path in memory_scripts:
            if os.path.exists(script_path):
                size = os.path.getsize(script_path)
                script_metrics[script_path] = size
            else:
                script_metrics[script_path] = None

        metrics["memory_scripts"] = script_metrics

        return metrics

    except Exception as e:
        return {"error": f"Memory metrics collection failed: {e}"}


def get_rag_metrics() -> dict[str, Any]:
    """Get RAG system metrics"""
    try:
        metrics: dict[str, Any] = {}

        # Check evaluation data
        eval_files = [
            "tests/data/edge_cases.jsonl",
            "metrics/baseline_evaluations/",
        ]

        eval_metrics: dict[str, int | str | None] = {}
        for file_path in eval_files:
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    size = os.path.getsize(file_path)
                    eval_metrics[file_path] = size
                else:
                    # Directory - count files
                    file_count = len([f for f in os.listdir(file_path) if os.path.isfile(os.path.join(file_path, f))])
                    eval_metrics[file_path] = f"{file_count} files"
            else:
                eval_metrics[file_path] = None

        metrics["evaluation_data"] = eval_metrics

        # Check property test results
        if os.path.exists("tests/data/edge_cases.jsonl"):
            try:
                with open("tests/data/edge_cases.jsonl") as f:
                    edge_cases = [line.strip() for line in f if line.strip()]
                metrics["edge_cases_count"] = len(edge_cases)
            except Exception:
                metrics["edge_cases_count"] = "error reading file"

        # Check Hypothesis cache
        if os.path.exists(".hypothesis/examples/"):
            try:
                example_files = []
                for root, dirs, files in os.walk(".hypothesis/examples/"):
                    example_files.extend(files)
                metrics["hypothesis_examples_count"] = len(example_files)
            except Exception:
                metrics["hypothesis_examples_count"] = "error counting files"

        return metrics

    except Exception as e:
        return {"error": f"RAG metrics collection failed: {e}"}


def get_system_metrics() -> dict[str, Any]:
    """Get system resource metrics"""
    try:
        import psutil

        # Memory metrics
        memory = psutil.virtual_memory()
        memory_metrics = {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3),
            "used_gb": memory.used / (1024**3),
            "percent_used": memory.percent,
        }

        # Disk metrics
        disk = psutil.disk_usage("/")
        disk_metrics = {
            "total_gb": disk.total / (1024**3),
            "used_gb": disk.used / (1024**3),
            "free_gb": disk.free / (1024**3),
            "percent_used": (disk.used / disk.total) * 100,
        }

        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_metrics = {
            "percent_used": cpu_percent,
            "count": psutil.cpu_count(),
        }

        return {
            "memory": memory_metrics,
            "disk": disk_metrics,
            "cpu": cpu_metrics,
            "timestamp": datetime.now().isoformat(),
        }

    except ImportError:
        return {"error": "psutil not available for system metrics"}
    except Exception as e:
        return {"error": f"System metrics collection failed: {e}"}


def get_performance_summary() -> dict[str, Any]:
    """Get performance summary for monitoring dashboard"""
    metrics = get_metrics()

    summary = {
        "timestamp": metrics["timestamp"],
        "status": "healthy",
        "alerts": [],
        "key_metrics": {},
    }

    # Check database health
    if "error" in metrics["database_metrics"]:
        summary["status"] = "unhealthy"
        summary["alerts"].append(f"Database error: {metrics['database_metrics']['error']}")
    else:
        summary["key_metrics"]["database_size"] = metrics["database_metrics"].get("database_size", "unknown")

    # Check system resources
    if "error" not in metrics["system_metrics"]:
        memory_percent = metrics["system_metrics"]["memory"]["percent_used"]
        disk_percent = metrics["system_metrics"]["disk"]["percent_used"]

        if memory_percent > 80:
            summary["alerts"].append(f"High memory usage: {memory_percent:.1f}%")
            if summary["status"] == "healthy":
                summary["status"] = "degraded"

        if disk_percent > 90:
            summary["alerts"].append(f"High disk usage: {disk_percent:.1f}%")
            if summary["status"] == "healthy":
                summary["status"] = "degraded"

        summary["key_metrics"]["memory_usage"] = f"{memory_percent:.1f}%"
        summary["key_metrics"]["disk_usage"] = f"{disk_percent:.1f}%"

    # Check RAG system
    if "error" in metrics["rag_metrics"]:
        summary["alerts"].append(f"RAG system error: {metrics['rag_metrics']['error']}")
        if summary["status"] == "healthy":
            summary["status"] = "degraded"
    else:
        edge_cases = metrics["rag_metrics"].get("edge_cases_count", 0)
        summary["key_metrics"]["edge_cases"] = edge_cases

    return summary
