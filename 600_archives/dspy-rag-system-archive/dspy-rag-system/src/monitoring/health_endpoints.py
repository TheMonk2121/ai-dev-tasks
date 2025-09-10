#!/usr/bin/env python3
"""
Production Health Check Endpoints

Provides Kubernetes-ready health checks with dependency monitoring
for production deployment of the DSPy RAG system.
"""

import os
import sys
import time
from collections.abc import Callable
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from flask import jsonify

# Local imports
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from monitoring.production_monitor import ProductionMonitor
from utils.logger import get_logger
from utils.opentelemetry_config import add_span_attribute, trace_operation

logger = get_logger("health_endpoints")


@dataclass
class DependencyStatus:
    """Dependency health status"""

    name: str
    status: str  # healthy, degraded, unhealthy
    response_time: float
    last_check: datetime
    endpoint: str
    error_message: str | None = None
    metadata: dict[str, Any] | None = None


class HealthEndpointManager:
    """Manages health check endpoints for production deployment"""

    def __init__(self, production_monitor: ProductionMonitor | None = None):
        """
        Initialize the health endpoint manager.

        Args:
            production_monitor: Production monitor instance (optional)
        """
        self.production_monitor = production_monitor or ProductionMonitor()
        self.dependencies: dict[str, DependencyStatus] = {}
        self.health_check_callbacks: list[Callable] = []

        # Register default dependencies
        self._register_default_dependencies()

    def _register_default_dependencies(self) -> None:
        """Register default dependency health checks"""
        # Cursor models do not require a local inference service; remove legacy local model dependency
        # Use project-local DSN (no password required on local Postgres.app)
        self.register_dependency(
            "database",
            "postgresql://danieljacobs@localhost:5432/dspy_rag",
            self._check_database_dependency,
        )
        self.register_dependency("file_system", "/tmp", self._check_filesystem_dependency)

    def register_dependency(self, name: str, endpoint: str, check_func: Callable[[], DependencyStatus]) -> None:
        """Register a dependency health check"""
        self.dependencies[name] = DependencyStatus(
            name=name, status="unknown", response_time=0.0, last_check=datetime.now(), endpoint=endpoint
        )
        setattr(self, f"_check_{name}_dependency", check_func)

    def register_health_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for health check results"""
        self.health_check_callbacks.append(callback)

    # Removed legacy local model dependency check

    def _check_database_dependency(self) -> DependencyStatus:
        """Check database dependency by opening a short-lived connection."""
        try:
            import time as _time

            try:
                import psycopg2  # type: ignore
            except Exception as import_error:  # pragma: no cover
                return DependencyStatus(
                    name="database",
                    status="unhealthy",
                    response_time=0.0,
                    last_check=datetime.now(),
                    endpoint="postgresql://danieljacobs@localhost:5432/dspy_rag",
                    error_message=f"psycopg2 import failed: {import_error}",
                )

            start_time = _time.time()
            with psycopg2.connect(
                "postgresql://danieljacobs@localhost:5432/dspy_rag",
                connect_timeout=3,
            ) as _conn:
                with _conn.cursor() as _cur:
                    _cur.execute("SELECT 1")
                    _ = _cur.fetchone()
            response_time = _time.time() - start_time
            return DependencyStatus(
                name="database",
                status="healthy",
                response_time=response_time,
                last_check=datetime.now(),
                endpoint="postgresql://danieljacobs@localhost:5432/dspy_rag",
            )
        except Exception as e:
            return DependencyStatus(
                name="database",
                status="unhealthy",
                response_time=0.0,
                last_check=datetime.now(),
                endpoint="postgresql://danieljacobs@localhost:5432/dspy_rag",
                error_message=str(e),
            )

    def _check_filesystem_dependency(self) -> DependencyStatus:
        """Check filesystem dependency"""
        try:
            start_time = time.time()

            # Check if we can read and write to temp directory
            test_file = "/tmp/health_check_test"
            with open(test_file, "w") as f:
                f.write("health_check")

            with open(test_file) as f:
                content = f.read()

            os.remove(test_file)
            response_time = time.time() - start_time

            if content == "health_check":
                return DependencyStatus(
                    name="file_system",
                    status="healthy",
                    response_time=response_time,
                    last_check=datetime.now(),
                    endpoint="/tmp",
                )
            else:
                return DependencyStatus(
                    name="file_system",
                    status="degraded",
                    response_time=response_time,
                    last_check=datetime.now(),
                    endpoint="/tmp",
                    error_message="File content mismatch",
                )
        except Exception as e:
            return DependencyStatus(
                name="file_system",
                status="unhealthy",
                response_time=0.0,
                last_check=datetime.now(),
                endpoint="/tmp",
                error_message=str(e),
            )

    def run_dependency_checks(self) -> dict[str, DependencyStatus]:
        """Run all dependency health checks"""
        results = {}

        for name, dependency in self.dependencies.items():
            try:
                check_func = getattr(self, f"_check_{name}_dependency")
                result = check_func()

                # Update dependency status
                dependency.status = result.status
                dependency.response_time = result.response_time
                dependency.last_check = datetime.now()
                dependency.error_message = result.error_message
                dependency.metadata = result.metadata

                results[name] = dependency

                # Log dependency status
                if result.status != "healthy":
                    logger.warning(f"Dependency '{name}' status: {result.status}")

            except Exception as e:
                logger.error(f"Error checking dependency '{name}': {e}")
                dependency.status = "unhealthy"
                dependency.error_message = str(e)
                dependency.last_check = datetime.now()
                results[name] = dependency

        return results

    def get_health_status(self) -> dict[str, Any]:
        """Get comprehensive health status including dependencies"""
        with trace_operation("health_status_check"):
            # Get production monitor health
            monitor_health = self.production_monitor.get_health_status()

            # Run dependency checks
            dependency_results = self.run_dependency_checks()

            # Determine overall status
            unhealthy_deps = [dep for dep in dependency_results.values() if dep.status == "unhealthy"]
            degraded_deps = [dep for dep in dependency_results.values() if dep.status == "degraded"]

            overall_status = "healthy"
            if unhealthy_deps or monitor_health["status"] == "unhealthy":
                overall_status = "unhealthy"
            elif degraded_deps or monitor_health["status"] == "degraded":
                overall_status = "degraded"

            # Compile results
            health_status = {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "service": {
                    "name": "ai-dev-tasks",
                    "version": "0.3.1",
                    "environment": os.getenv("ENVIRONMENT", "production"),
                },
                "monitor_health": monitor_health,
                "dependencies": {name: asdict(dep) for name, dep in dependency_results.items()},
                "unhealthy_dependencies": len(unhealthy_deps),
                "degraded_dependencies": len(degraded_deps),
                "total_dependencies": len(dependency_results),
            }

            # Add OpenTelemetry attributes
            add_span_attribute("health.overall_status", overall_status)
            add_span_attribute("health.unhealthy_deps", len(unhealthy_deps))
            add_span_attribute("health.degraded_deps", len(degraded_deps))

            # Trigger callbacks
            for callback in self.health_check_callbacks:
                try:
                    callback(health_status)
                except Exception as e:
                    logger.error(f"Error in health callback: {e}")

            return health_status

    def get_ready_status(self) -> dict[str, Any]:
        """Get readiness status for Kubernetes"""
        health_status = self.get_health_status()

        # Ready if overall status is healthy or degraded (but not unhealthy)
        is_ready = health_status["status"] != "unhealthy"

        ready_status = {
            "ready": is_ready,
            "status": health_status["status"],
            "timestamp": health_status["timestamp"],
            "details": {
                "unhealthy_dependencies": health_status["unhealthy_dependencies"],
                "degraded_dependencies": health_status["degraded_dependencies"],
            },
        }

        return ready_status


# Global instance
_health_manager: HealthEndpointManager | None = None


def get_health_manager() -> HealthEndpointManager:
    """Get the global health endpoint manager instance"""
    global _health_manager
    if _health_manager is None:
        _health_manager = HealthEndpointManager()
    return _health_manager


def initialize_health_endpoints(production_monitor: ProductionMonitor | None = None) -> HealthEndpointManager:
    """Initialize health endpoints"""
    global _health_manager
    _health_manager = HealthEndpointManager(production_monitor)
    return _health_manager


# Flask integration functions
def create_health_endpoints(app):
    """Create health check endpoints for Flask app"""

    @app.route("/health")
    def health_check():
        """Kubernetes health check endpoint"""
        try:
            health_manager = get_health_manager()
            health_status = health_manager.get_health_status()

            # Return appropriate HTTP status code
            if health_status["status"] == "unhealthy":
                return jsonify(health_status), 503
            elif health_status["status"] == "degraded":
                return jsonify(health_status), 200
            else:
                return jsonify(health_status), 200

        except Exception as e:
            logger.error(f"Health check error: {e}")
            return jsonify({"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}), 503

    @app.route("/ready")
    def ready_check():
        """Kubernetes readiness check endpoint"""
        try:
            health_manager = get_health_manager()
            ready_status = health_manager.get_ready_status()

            # Return appropriate HTTP status code
            if ready_status["ready"]:
                return jsonify(ready_status), 200
            else:
                return jsonify(ready_status), 503

        except Exception as e:
            logger.error(f"Ready check error: {e}")
            return jsonify({"ready": False, "error": str(e), "timestamp": datetime.now().isoformat()}), 503

    @app.route("/api/health/detailed")
    def detailed_health_check():
        """Detailed health check with all metrics"""
        try:
            health_manager = get_health_manager()
            production_monitor = health_manager.production_monitor

            detailed_status = {
                "health": health_manager.get_health_status(),
                "security_events": production_monitor.get_security_events(hours=1),
                "system_metrics": production_monitor.get_system_metrics(minutes=30),
                "timestamp": datetime.now().isoformat(),
            }

            return jsonify(detailed_status), 200

        except Exception as e:
            logger.error(f"Detailed health check error: {e}")
            return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 503

    @app.route("/api/health/dependencies")
    def dependencies_check():
        """Check only dependencies"""
        try:
            health_manager = get_health_manager()
            dependency_results = health_manager.run_dependency_checks()

            return (
                jsonify(
                    {
                        "dependencies": {name: asdict(dep) for name, dep in dependency_results.items()},
                        "timestamp": datetime.now().isoformat(),
                    }
                ),
                200,
            )

        except Exception as e:
            logger.error(f"Dependencies check error: {e}")
            return jsonify({"error": str(e), "timestamp": datetime.now().isoformat()}), 503

    return app
