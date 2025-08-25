#!/usr/bin/env python3
"""
Upgrade Validation Framework

This module provides comprehensive validation procedures for system upgrades,
including pre-upgrade health checks, post-upgrade validation, and rollback
validation procedures.

Author: AI Development Ecosystem
Version: 1.0
Last Updated: 2024-08-07
"""

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import psycopg2
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Validation result data structure."""

    component: str
    status: bool
    message: str
    details: Dict[str, Any]
    timestamp: datetime


@dataclass
class UpgradeMetrics:
    """Upgrade metrics tracking."""

    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "running"
    progress: float = 0.0
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


class UpgradeValidator:
    """Comprehensive upgrade validation framework."""

    def __init__(self):
        """Initialize the upgrade validator."""
        self.results: List[ValidationResult] = []
        self.metrics = UpgradeMetrics(start_time=datetime.now())

    def validate_database_health(self) -> ValidationResult:
        """
        Validate database connectivity and health.

        Returns:
            ValidationResult: Database health validation result
        """
        try:
            # Test database connectivity
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()

            # Test basic query
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            # Test table access
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables")
            result = cursor.fetchone()
            table_count = result[0] if result else 0

            # Test specific tables
            cursor.execute("SELECT COUNT(*) FROM episodic_logs")
            result = cursor.fetchone()
            episodic_count = result[0] if result else 0

            cursor.close()
            conn.close()

            details = {"table_count": table_count, "episodic_logs_count": episodic_count, "connection_successful": True}

            return ValidationResult(
                component="database",
                status=True,
                message="Database health check passed",
                details=details,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return ValidationResult(
                component="database",
                status=False,
                message=f"Database health check failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def validate_application_health(self) -> ValidationResult:
        """
        Validate application health and functionality.

        Returns:
            ValidationResult: Application health validation result
        """
        try:
            # Test application health endpoint
            response = requests.get("http://localhost:5000/health", timeout=5)

            if response.status_code == 200:
                health_data = response.json()

                details = {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "health_data": health_data,
                }

                return ValidationResult(
                    component="application",
                    status=True,
                    message="Application health check passed",
                    details=details,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    component="application",
                    status=False,
                    message=f"Application health check failed: HTTP {response.status_code}",
                    details={"status_code": response.status_code},
                    timestamp=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Application health check failed: {e}")
            return ValidationResult(
                component="application",
                status=False,
                message=f"Application health check failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def validate_ai_models_health(self) -> ValidationResult:
        """
        Validate AI model availability and functionality.

        Returns:
            ValidationResult: AI models health validation result
        """
        try:
            # Test Mistral 7B model
            mistral_url = os.getenv("MISTRAL_7B_URL")
            if mistral_url:
                mistral_response = requests.get(f"{mistral_url}/health", timeout=5)
                mistral_healthy = mistral_response.status_code == 200
            else:
                mistral_healthy = False

            # Test Yi-Coder model
            yi_coder_url = os.getenv("YI_CODER_URL")
            if yi_coder_url:
                yi_coder_response = requests.get(f"{yi_coder_url}/health", timeout=5)
                yi_coder_healthy = yi_coder_response.status_code == 200
            else:
                yi_coder_healthy = False

            details = {
                "mistral_7b_healthy": mistral_healthy,
                "yi_coder_healthy": yi_coder_healthy,
                "models_available": mistral_healthy or yi_coder_healthy,
            }

            if mistral_healthy and yi_coder_healthy:
                return ValidationResult(
                    component="ai_models",
                    status=True,
                    message="All AI models healthy",
                    details=details,
                    timestamp=datetime.now(),
                )
            elif mistral_healthy or yi_coder_healthy:
                return ValidationResult(
                    component="ai_models",
                    status=True,
                    message="Some AI models healthy",
                    details=details,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    component="ai_models",
                    status=False,
                    message="No AI models available",
                    details=details,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            logger.error(f"AI models health check failed: {e}")
            return ValidationResult(
                component="ai_models",
                status=False,
                message=f"AI models health check failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def validate_monitoring_health(self) -> ValidationResult:
        """
        Validate monitoring system health.

        Returns:
            ValidationResult: Monitoring health validation result
        """
        try:
            # Test metrics endpoint
            try:
                metrics_response = requests.get("http://localhost:5000/metrics", timeout=5)
                metrics_healthy = metrics_response.status_code == 200
            except Exception:
                metrics_healthy = False

            details = {
                "redis_healthy": False,  # Redis not available in this environment
                "metrics_healthy": metrics_healthy,
                "monitoring_available": metrics_healthy,
            }

            if metrics_healthy:
                return ValidationResult(
                    component="monitoring",
                    status=True,
                    message="Monitoring system healthy",
                    details=details,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    component="monitoring",
                    status=False,
                    message="No monitoring systems available",
                    details=details,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Monitoring health check failed: {e}")
            return ValidationResult(
                component="monitoring",
                status=False,
                message=f"Monitoring health check failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def validate_system_resources(self) -> ValidationResult:
        """
        Validate system resource availability.

        Returns:
            ValidationResult: System resources validation result
        """
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # Check disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent

            # Check available disk space
            available_gb = disk.free / (1024**3)

            details = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
                "available_disk_gb": round(available_gb, 2),
                "memory_available_gb": round(memory.available / (1024**3), 2),
            }

            # Determine if resources are adequate
            resource_adequate = cpu_percent < 80 and memory_percent < 80 and disk_percent < 90 and available_gb > 5.0

            return ValidationResult(
                component="system_resources",
                status=resource_adequate,
                message="System resources adequate" if resource_adequate else "System resources insufficient",
                details=details,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return ValidationResult(
                component="system_resources",
                status=False,
                message=f"System resources check failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def pre_upgrade_validation(self) -> Dict[str, Any]:
        """
        Perform comprehensive pre-upgrade validation.

        Returns:
            Dict containing validation results
        """
        logger.info("Starting pre-upgrade validation...")

        # Run all validation checks
        validations = [
            self.validate_database_health(),
            self.validate_application_health(),
            self.validate_ai_models_health(),
            self.validate_monitoring_health(),
            self.validate_system_resources(),
        ]

        # Store results
        self.results.extend(validations)

        # Calculate overall status
        overall_status = all(v.status for v in validations)

        # Generate report
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "validations": [asdict(v) for v in validations],
            "summary": {
                "total_checks": len(validations),
                "passed_checks": sum(1 for v in validations if v.status),
                "failed_checks": sum(1 for v in validations if not v.status),
            },
        }

        # Log results
        if overall_status:
            logger.info("Pre-upgrade validation PASSED")
        else:
            logger.error("Pre-upgrade validation FAILED")
            for validation in validations:
                if not validation.status:
                    logger.error(f"Failed: {validation.component} - {validation.message}")

        return report

    def post_upgrade_validation(self) -> Dict[str, Any]:
        """
        Perform comprehensive post-upgrade validation.

        Returns:
            Dict containing validation results
        """
        logger.info("Starting post-upgrade validation...")

        # Run all validation checks
        validations = [
            self.validate_database_health(),
            self.validate_application_health(),
            self.validate_ai_models_health(),
            self.validate_monitoring_health(),
            self.validate_system_resources(),
        ]

        # Additional post-upgrade specific checks
        validations.append(self.validate_upgrade_specific_features())

        # Store results
        self.results.extend(validations)

        # Calculate overall status
        overall_status = all(v.status for v in validations)

        # Generate report
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "validations": [asdict(v) for v in validations],
            "summary": {
                "total_checks": len(validations),
                "passed_checks": sum(1 for v in validations if v.status),
                "failed_checks": sum(1 for v in validations if not v.status),
            },
        }

        # Log results
        if overall_status:
            logger.info("Post-upgrade validation PASSED")
        else:
            logger.error("Post-upgrade validation FAILED")
            for validation in validations:
                if not validation.status:
                    logger.error(f"Failed: {validation.component} - {validation.message}")

        return report

    def validate_upgrade_specific_features(self) -> ValidationResult:
        """
        Validate features specific to the upgrade.

        Returns:
            ValidationResult: Upgrade-specific validation result
        """
        try:
            # Test new database columns if they were added
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()

            # Check for new columns
            cursor.execute(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'episodic_logs'
                AND column_name IN ('cache_hit', 'similarity_score', 'last_verified')
            """
            )
            new_columns = [row[0] for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            details = {
                "new_columns_found": new_columns,
                "expected_columns": ["cache_hit", "similarity_score", "last_verified"],
            }

            if len(new_columns) >= 1:  # At least one new column should be present
                return ValidationResult(
                    component="upgrade_features",
                    status=True,
                    message="Upgrade-specific features validated",
                    details=details,
                    timestamp=datetime.now(),
                )
            else:
                return ValidationResult(
                    component="upgrade_features",
                    status=False,
                    message="Upgrade-specific features not found",
                    details=details,
                    timestamp=datetime.now(),
                )

        except Exception as e:
            logger.error(f"Upgrade-specific validation failed: {e}")
            return ValidationResult(
                component="upgrade_features",
                status=False,
                message=f"Upgrade-specific validation failed: {e}",
                details={"error": str(e)},
                timestamp=datetime.now(),
            )

    def rollback_validation(self) -> Dict[str, Any]:
        """
        Perform rollback validation.

        Returns:
            Dict containing rollback validation results
        """
        logger.info("Starting rollback validation...")

        # Run basic health checks after rollback
        validations = [
            self.validate_database_health(),
            self.validate_application_health(),
            self.validate_ai_models_health(),
            self.validate_monitoring_health(),
        ]

        # Store results
        self.results.extend(validations)

        # Calculate overall status
        overall_status = all(v.status for v in validations)

        # Generate report
        report = {
            "overall_status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "validations": [asdict(v) for v in validations],
            "summary": {
                "total_checks": len(validations),
                "passed_checks": sum(1 for v in validations if v.status),
                "failed_checks": sum(1 for v in validations if not v.status),
            },
        }

        # Log results
        if overall_status:
            logger.info("Rollback validation PASSED")
        else:
            logger.error("Rollback validation FAILED")
            for validation in validations:
                if not validation.status:
                    logger.error(f"Failed: {validation.component} - {validation.message}")

        return report

    def save_validation_report(self, report: Dict[str, Any], filename: str) -> None:
        """
        Save validation report to file.

        Args:
            report: Validation report to save
            filename: Output filename
        """
        try:
            with open(filename, "w") as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"Validation report saved to {filename}")
        except Exception as e:
            logger.error(f"Failed to save validation report: {e}")

    def send_validation_alert(self, report: Dict[str, Any]) -> None:
        """
        Send validation alert to monitoring system.

        Args:
            report: Validation report to send
        """
        try:
            monitoring_url = os.getenv("MONITORING_URL")
            if monitoring_url:
                response = requests.post(f"{monitoring_url}/validation-alert", json=report, timeout=10)
                if response.status_code == 200:
                    logger.info("Validation alert sent successfully")
                else:
                    logger.warning(f"Failed to send validation alert: HTTP {response.status_code}")
            else:
                logger.warning("MONITORING_URL not configured, skipping alert")
        except Exception as e:
            logger.error(f"Failed to send validation alert: {e}")


def main():
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Upgrade Validation Framework")
    parser.add_argument(
        "--type", choices=["pre", "post", "rollback"], required=True, help="Type of validation to perform"
    )
    parser.add_argument("--output", default="validation_report.json", help="Output file for validation report")
    parser.add_argument("--alert", action="store_true", help="Send validation alert to monitoring system")

    args = parser.parse_args()

    # Initialize validator
    validator = UpgradeValidator()

    # Perform validation based on type
    if args.type == "pre":
        report = validator.pre_upgrade_validation()
    elif args.type == "post":
        report = validator.post_upgrade_validation()
    elif args.type == "rollback":
        report = validator.rollback_validation()

    # Save report
    validator.save_validation_report(report, args.output)

    # Send alert if requested
    if args.alert:
        validator.send_validation_alert(report)

    # Exit with appropriate code
    if report["overall_status"]:
        logger.info("Validation completed successfully")
        sys.exit(0)
    else:
        logger.error("Validation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
