"""
Health Endpoint Manager for AI Development Tasks

Manages health checks for various system components including:
- Database connectivity and performance
- Memory system status
- DSPy RAG system health
- External service dependencies
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Optional

import psycopg2
from psycopg2.extras import RealDictCursor


class HealthEndpointManager:
    """Manages health checks for system components"""

    def __init__(self) -> None:
        self.database_url = os.getenv("DATABASE_URL", "postgresql://localhost:5432/ai_agency")
        self.health_thresholds = {
            "database_response_time": 5.0,  # seconds
            "memory_usage_percent": 80.0,  # percentage
            "disk_usage_percent": 90.0,  # percentage
        }

    def get_health_status(self) -> dict[str, Any]:
        """Get overall system health status"""
        dependencies = []
        unhealthy_count = 0
        degraded_count = 0

        # Check database health
        db_health = self._check_database_health()
        dependencies.append(db_health)
        if db_health["status"] == "unhealthy":
            unhealthy_count += 1
        elif db_health["status"] == "degraded":
            degraded_count += 1

        # Check memory system health
        memory_health = self._check_memory_system_health()
        dependencies.append(memory_health)
        if memory_health["status"] == "unhealthy":
            unhealthy_count += 1
        elif memory_health["status"] == "degraded":
            degraded_count += 1

        # Check DSPy RAG system health
        rag_health = self._check_rag_system_health()
        dependencies.append(rag_health)
        if rag_health["status"] == "unhealthy":
            unhealthy_count += 1
        elif rag_health["status"] == "degraded":
            degraded_count += 1

        # Determine overall status
        if unhealthy_count > 0:
            overall_status = "unhealthy"
        elif degraded_count > 0:
            overall_status = "degraded"
        else:
            overall_status = "healthy"

        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "dependencies": dependencies,
            "unhealthy_dependencies": unhealthy_count,
            "degraded_dependencies": degraded_count,
        }

    def _check_database_health(self) -> dict[str, Any]:
        """Check database connectivity and performance"""
        try:
            start_time = datetime.now()
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            # Test basic connectivity
            cursor.execute("SELECT 1")
            cursor.fetchone()

            # Check if pg_stat_statements is enabled
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

            # Get database size
            cursor.execute(
                """
                SELECT pg_size_pretty(pg_database_size(current_database())) as size
            """
            )
            result = cursor.fetchone()
            db_size = result["size"] if result else "unknown"

            cursor.close()
            conn.close()

            response_time = (datetime.now() - start_time).total_seconds()

            status = "healthy"
            if response_time > self.health_thresholds["database_response_time"]:
                status = "degraded"

            return {
                "name": "database",
                "status": status,
                "response_time": response_time,
                "pg_stat_statements_enabled": pg_stat_enabled,
                "database_size": db_size,
                "details": f"Response time: {response_time:.3f}s",
            }

        except Exception as e:
            return {
                "name": "database",
                "status": "unhealthy",
                "error": str(e),
                "details": f"Database connection failed: {e}",
            }

    def _check_memory_system_health(self) -> dict[str, Any]:
        """Check memory system status"""
        try:
            # Check if memory system files exist
            memory_files = [
                "100_memory/100_cursor-memory-context.md",
                "100_memory/104_dspy-development-context.md",
            ]

            missing_files = []
            for file_path in memory_files:
                if not os.path.exists(file_path):
                    missing_files.append(file_path)

            if missing_files:
                return {
                    "name": "memory_system",
                    "status": "unhealthy",
                    "missing_files": missing_files,
                    "details": f"Missing critical memory files: {missing_files}",
                }

            # Check memory system scripts
            memory_scripts = [
                "scripts/unified_memory_orchestrator.py",
                "scripts/update_cursor_memory.py",
            ]

            missing_scripts = []
            for script_path in memory_scripts:
                if not os.path.exists(script_path):
                    missing_scripts.append(script_path)

            status = "healthy"
            if missing_scripts:
                status = "degraded"

            return {
                "name": "memory_system",
                "status": status,
                "missing_scripts": missing_scripts,
                "details": (
                    f"Memory system files present, missing scripts: {missing_scripts}"
                    if missing_scripts
                    else "All memory system components present"
                ),
            }

        except Exception as e:
            return {
                "name": "memory_system",
                "status": "unhealthy",
                "error": str(e),
                "details": f"Memory system check failed: {e}",
            }

    def _check_rag_system_health(self) -> dict[str, Any]:
        """Check DSPy RAG system health"""
        try:
            # Check if DSPy modules exist
            dspy_modules = [
                "src/dspy_modules/retriever/rerank.py",
                "src/dspy_modules/reader/program.py",
                "src/schemas/eval.py",
            ]

            missing_modules = []
            for module_path in dspy_modules:
                if not os.path.exists(module_path):
                    missing_modules.append(module_path)

            if missing_modules:
                return {
                    "name": "rag_system",
                    "status": "unhealthy",
                    "missing_modules": missing_modules,
                    "details": f"Missing critical RAG modules: {missing_modules}",
                }

            # Check if evaluation data exists
            eval_data_files = [
                "tests/data/edge_cases.jsonl",
                "metrics/baseline_evaluations/",
            ]

            missing_data = []
            for data_path in eval_data_files:
                if not os.path.exists(data_path):
                    missing_data.append(data_path)

            status = "healthy"
            if missing_data:
                status = "degraded"

            return {
                "name": "rag_system",
                "status": status,
                "missing_data": missing_data,
                "details": (
                    f"RAG system modules present, missing data: {missing_data}"
                    if missing_data
                    else "All RAG system components present"
                ),
            }

        except Exception as e:
            return {
                "name": "rag_system",
                "status": "unhealthy",
                "error": str(e),
                "details": f"RAG system check failed: {e}",
            }

    def get_detailed_health_report(self) -> dict[str, Any]:
        """Get detailed health report with metrics"""
        health_status = self.get_health_status()

        # Add system resource metrics
        try:
            import psutil

            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            health_status["system_resources"] = {
                "memory_usage_percent": memory.percent,
                "memory_available_gb": memory.available / (1024**3),
                "disk_usage_percent": disk.percent,
                "disk_free_gb": disk.free / (1024**3),
            }
        except ImportError:
            health_status["system_resources"] = {"error": "psutil not available for system metrics"}

        return health_status
