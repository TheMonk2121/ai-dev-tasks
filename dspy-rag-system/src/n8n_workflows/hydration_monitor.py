#!/usr/bin/env python3
"""
Hydration System Monitor - n8n Workflow
Monitors hydration system health, performance, and quality metrics
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.logger import get_logger
from src.utils.memory_rehydrator import build_hydration_bundle

logger = get_logger(__name__)


class HydrationMonitor:
    """Monitors hydration system health and performance"""

    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.last_check = None

    def check_system_health(self) -> dict[str, Any]:
        """Check overall system health"""
        logger.info("Checking hydration system health")

        health_checks = {
            "database_connection": self._check_database_connection(),
            "memory_rehydrator": self._check_memory_rehydrator(),
            "anchor_metadata": self._check_anchor_metadata(),
            "performance": self._check_performance_metrics(),
            "quality": self._check_quality_metrics(),
        }

        overall_health = all(health_checks.values())

        return {
            "timestamp": time.time(),
            "overall_health": overall_health,
            "health_checks": health_checks,
            "alerts": self.alerts,
        }

    def _check_database_connection(self) -> bool:
        """Check database connectivity"""
        try:
            # Get database connection string from environment
            connection_string = os.getenv("POSTGRES_DSN")
            if not connection_string:
                raise ValueError("POSTGRES_DSN environment variable not set")

            # Use direct connection for health check
            import psycopg2

            conn = psycopg2.connect(connection_string)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM document_chunks")
            result = cursor.fetchone()
            count = result[0] if result else 0
            cursor.close()
            conn.close()

            logger.info(f"Database health check successful: {count} chunks found")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            self.alerts.append(f"Database connection error: {e}")
            return False

    def _check_memory_rehydrator(self) -> bool:
        """Check memory rehydrator functionality"""
        try:
            # Test basic bundle creation
            bundle = build_hydration_bundle(role="planner", task="health check", token_budget=500)

            # Validate bundle structure
            if not hasattr(bundle, "text") or not hasattr(bundle, "meta"):
                raise ValueError("Invalid bundle structure")

            if bundle.meta.get("sections", 0) == 0:
                raise ValueError("Bundle has no sections")

            return True
        except Exception as e:
            logger.error(f"Memory rehydrator check failed: {e}")
            self.alerts.append(f"Memory rehydrator error: {e}")
            return False

    def _check_anchor_metadata(self) -> bool:
        """Check anchor metadata availability"""
        try:
            # Test anchor metadata extraction
            from src.utils.anchor_metadata_parser import extract_anchor_metadata

            # Test with a known file
            test_content = """
            <!-- ANCHOR_KEY: test -->
            <!-- ANCHOR_PRIORITY: 10 -->
            <!-- ROLE_PINS: ["planner"] -->

            # Test Content
            """

            metadata = extract_anchor_metadata(test_content)

            if not metadata.anchor_key or metadata.anchor_key != "test":
                raise ValueError("Anchor metadata extraction failed")

            return True
        except Exception as e:
            logger.error(f"Anchor metadata check failed: {e}")
            self.alerts.append(f"Anchor metadata error: {e}")
            return False

    def _check_performance_metrics(self) -> bool:
        """Check performance metrics"""
        try:
            start_time = time.time()

            # Create multiple bundles to test performance
            bundles = []
            for i in range(3):
                bundle = build_hydration_bundle(
                    role="planner" if i % 2 == 0 else "implementer", task=f"performance test {i}", token_budget=1000
                )
                bundles.append(bundle)

            total_time = time.time() - start_time
            avg_time = total_time / len(bundles)

            # Performance threshold: 5 seconds average
            performance_ok = avg_time < 5.0

            if not performance_ok:
                self.alerts.append(f"Performance degradation: {avg_time:.2f}s average")

            self.metrics["avg_creation_time"] = avg_time
            self.metrics["total_bundles_created"] = len(bundles)

            return performance_ok
        except Exception as e:
            logger.error(f"Performance check failed: {e}")
            self.alerts.append(f"Performance check error: {e}")
            return False

    def _check_quality_metrics(self) -> bool:
        """Check quality metrics"""
        try:
            # Test role-specific quality
            planner_bundle = build_hydration_bundle(role="planner", task="quality assessment", token_budget=1200)

            implementer_bundle = build_hydration_bundle(
                role="implementer", task="quality assessment", token_budget=1200
            )

            # Check for essential content
            planner_text = planner_bundle.text.lower()
            implementer_text = implementer_bundle.text.lower()

            # Quality checks
            planner_quality = any(keyword in planner_text for keyword in ["backlog", "priority", "system"])
            implementer_quality = any(keyword in implementer_text for keyword in ["dspy", "development", "technical"])

            quality_ok = planner_quality and implementer_quality

            if not quality_ok:
                self.alerts.append("Quality degradation detected")

            self.metrics["planner_quality"] = planner_quality
            self.metrics["implementer_quality"] = implementer_quality

            return quality_ok
        except Exception as e:
            logger.error(f"Quality check failed: {e}")
            self.alerts.append(f"Quality check error: {e}")
            return False

    def generate_health_report(self) -> dict[str, Any]:
        """Generate comprehensive health report"""
        health_status = self.check_system_health()

        report = {
            "timestamp": time.time(),
            "system": "hydration_monitor",
            "status": "healthy" if health_status["overall_health"] else "unhealthy",
            "health_checks": health_status["health_checks"],
            "metrics": self.metrics,
            "alerts": self.alerts,
            "recommendations": self._generate_recommendations(health_status),
        }

        return report

    def _generate_recommendations(self, health_status: dict[str, Any]) -> list[str]:
        """Generate recommendations based on health status"""
        recommendations = []

        if not health_status["overall_health"]:
            recommendations.append("System health check failed - investigate immediately")

        if not health_status["health_checks"]["database_connection"]:
            recommendations.append("Check database connectivity and connection pool settings")

        if not health_status["health_checks"]["performance"]:
            recommendations.append("Performance degradation detected - consider optimization")

        if not health_status["health_checks"]["quality"]:
            recommendations.append("Quality metrics below threshold - review content relevance")

        if self.metrics.get("avg_creation_time", 0) > 2.0:
            recommendations.append("Bundle creation time high - consider caching or optimization")

        return recommendations


def create_n8n_webhook_payload(health_report: dict[str, Any]) -> dict[str, Any]:
    """Create n8n webhook payload format"""
    return {
        "webhook_type": "hydration_health_check",
        "timestamp": health_report["timestamp"],
        "status": health_report["status"],
        "summary": {
            "overall_health": health_report["health_checks"],
            "alerts_count": len(health_report["alerts"]),
            "recommendations_count": len(health_report["recommendations"]),
        },
        "details": health_report,
        "action_required": health_report["status"] == "unhealthy",
    }


def main():
    """Main monitoring function for n8n integration"""
    logger.info("Starting hydration system monitoring")

    monitor = HydrationMonitor()
    health_report = monitor.generate_health_report()

    # Create n8n webhook payload
    webhook_payload = create_n8n_webhook_payload(health_report)

    # Output for n8n
    print(json.dumps(webhook_payload, indent=2))

    # Log results
    if health_report["status"] == "healthy":
        logger.info("Hydration system health check passed")
    else:
        logger.warning("Hydration system health check failed")
        logger.warning(f"Alerts: {health_report['alerts']}")

    return 0 if health_report["status"] == "healthy" else 1


if __name__ == "__main__":
    exit(main())
