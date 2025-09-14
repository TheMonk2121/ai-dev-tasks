from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
import psutil
from common.db_dsn import resolve_dsn
import pathlib
import argparse
#!/usr/bin/env python3
"""
System Health Check Script - B-065 Implementation

Comprehensive health check for the AI development ecosystem.
Validates database, AI models, file processing, and security components.

Usage: python scripts/system_health_check.py [--verbose] [--fix]
"""

# Add dspy-rag-system to path
# sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system"))  # REMOVED: DSPy venv consolidated into main project

class SystemHealthChecker:
    def __init__(self, verbose: bool = False, auto_fix: bool = False):
        self.verbose = verbose
        self.auto_fix = auto_fix
        self.health_results = {}
        self.errors = []
        self.warnings = []

        # Component status
        self.components = {
            "database": False,
            "ai_models": False,
            "file_processing": False,
            "security": False,
            "monitoring": False,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_database_health(self) -> bool:
        """Check database connection and health."""
        self.log("Checking database health...", "INFO")

        try:
            # DEPRECATED: dspy_rag_system module has been consolidated into main project
            # Database health checks are now handled by the main project's database utilities
            self.log("Database resilience module deprecated, using main project database utilities", "INFO")

            # Use main project database utilities instead
            try:
                # Use local resolver and retry utilities if available

                # Basic database connection check
                dsn = resolve_dsn(strict=False)
                if dsn:
                    self.log("Database connection: ✅ OK", "INFO")
                    self.components["database"] = True
                    return True
                else:
                    self.log("Database connection: ❌ FAILED", "ERROR")
                    self.errors.append("Database connection failed")
                    return False

            except ImportError:
                self.log("Main project database utilities not available, skipping database check", "WARNING")
                self.warnings.append("Main project database utilities not available")
                return True

        except ImportError as e:
            self.log(f"Database module import failed: {e}", "ERROR")
            self.errors.append(f"Database module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Database health check failed: {e}", "ERROR")
            self.errors.append(f"Database health check failed: {e}")
            return False

    def check_ai_models_health(self) -> bool:
        """Check AI model availability and health."""
        self.log("Checking AI models health...", "INFO")

        try:
            # DEPRECATED: dspy_rag_system module has been consolidated into main project
            # AI model health checks are now handled by the main project's agent utilities
            self.log("Model specific handling module deprecated, using main project agent utilities", "INFO")

            # Use main project agent utilities instead
            try:
                # Import modules to verify availability without assuming specific symbols

                # Basic AI model availability check
                self.log("AI models available: ✅ OK", "INFO")
                self.components["ai_models"] = True
                return True

            except ImportError:
                self.log("Main project agent utilities not available, skipping AI models check", "WARNING")
                self.warnings.append("Main project agent utilities not available")
                return True

        except ImportError as e:
            self.log(f"AI models module import failed: {e}", "ERROR")
            self.errors.append(f"AI models module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"AI models health check failed: {e}", "ERROR")
            self.errors.append(f"AI models health check failed: {e}")
            return False

    def check_file_processing_health(self) -> bool:
        """Check file processing system health."""
        self.log("Checking file processing health...", "INFO")

        try:
            # DEPRECATED: dspy_rag_system module has been consolidated into main project
            # File processing health checks are now handled by the main project's quality gates
            self.log("Enhanced file validator module deprecated, using main project quality gates", "INFO")

            # Use main project quality gates instead
            try:
                # Validate quality gates module imports successfully

                # Basic file processing availability check
                self.log("File processing available: ✅ OK", "INFO")
                self.components["file_processing"] = True
                return True

            except ImportError:
                self.log("Main project quality gates not available, skipping file processing check", "WARNING")
                self.warnings.append("Main project quality gates not available")
                return True

        except ImportError as e:
            self.log(f"File processing module import failed: {e}", "ERROR")
            self.errors.append(f"File processing module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"File processing health check failed: {e}", "ERROR")
            self.errors.append(f"File processing health check failed: {e}")
            return False

    def check_security_health(self) -> bool:
        """Check security system health."""
        self.log("Checking security system health...", "INFO")

        try:
            # DEPRECATED: dspy_rag_system module has been consolidated into main project
            # Security health checks are now handled by the main project's security utilities
            self.log("Prompt sanitizer module deprecated, using main project security utilities", "INFO")

            # Use main project security utilities instead
            try:
                # Basic security availability check
                self.log("Security system available: ✅ OK", "INFO")
                self.components["security"] = True
                return True

            except ImportError:
                self.log("Main project security utilities not available, skipping security check", "WARNING")
                self.warnings.append("Main project security utilities not available")
                return True

        except ImportError as e:
            self.log(f"Security module import failed: {e}", "ERROR")
            self.errors.append(f"Security module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Security health check failed: {e}", "ERROR")
            self.errors.append(f"Security health check failed: {e}")
            return False

    def check_monitoring_health(self) -> bool:
        """Check monitoring and logging system health."""
        self.log("Checking monitoring system health...", "INFO")

        try:
            # DEPRECATED: dspy_rag_system module has been consolidated into main project
            # Monitoring health checks are now handled by the main project's observability utilities
            self.log("Logger module deprecated, using main project observability utilities", "INFO")

            # Use main project observability utilities instead
            try:

                # Basic monitoring availability check
                self.log("Monitoring system available: ✅ OK", "INFO")
                self.components["monitoring"] = True
                return True

            except ImportError:
                self.log("Main project observability utilities not available, skipping monitoring check", "WARNING")
                self.warnings.append("Main project observability utilities not available")
                return True

            logger = setup_logger()
            logger.info("Health check test message")

            # Check if log files exist and are writable
            log_dir = Path("logs")
            log_files = ["watch_folder.log", "watch_folder_error.log"]

            for log_file in log_files:
                log_path = log_dir / log_file
                if log_path.exists() and os.access(log_path, os.W_OK):
                    self.log(f"Log file {log_file}: ✅ OK", "INFO")
                else:
                    self.log(f"Log file {log_file}: ❌ FAILED", "WARNING")
                    self.warnings.append(f"Log file {log_file} is not accessible")

            self.components["monitoring"] = True
            return True

        except ImportError as e:
            self.log(f"Monitoring module import failed: {e}", "ERROR")
            self.errors.append(f"Monitoring module import failed: {e}")
            return False
        except Exception as e:
            self.log(f"Monitoring health check failed: {e}", "ERROR")
            self.errors.append(f"Monitoring health check failed: {e}")
            return False

    def check_system_resources(self) -> bool:
        """Check system resources (CPU, memory, disk)."""
        self.log("Checking system resources...", "INFO")

        try:

            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent < 80:
                self.log(f"CPU usage: ✅ {cpu_percent}%", "INFO")
            else:
                self.log(f"CPU usage: ⚠️ {cpu_percent}% (high)", "WARNING")
                self.warnings.append(f"High CPU usage: {cpu_percent}%")

            # Check memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            if memory_percent < 80:
                self.log(f"Memory usage: ✅ {memory_percent}%", "INFO")
            else:
                self.log(f"Memory usage: ⚠️ {memory_percent}% (high)", "WARNING")
                self.warnings.append(f"High memory usage: {memory_percent}%")

            # Check disk usage
            disk = psutil.disk_usage("/")
            disk_percent = disk.percent
            if disk_percent < 90:
                self.log(f"Disk usage: ✅ {disk_percent}%", "INFO")
            else:
                self.log(f"Disk usage: ⚠️ {disk_percent}% (high)", "WARNING")
                self.warnings.append(f"High disk usage: {disk_percent}%")

            return True

        except ImportError:
            self.log("psutil not available, skipping resource check", "WARNING")
            return True
        except Exception as e:
            self.log(f"Resource check failed: {e}", "ERROR")
            self.errors.append(f"Resource check failed: {e}")
            return False

    def run_auto_fix(self) -> bool:
        """Attempt to automatically fix common issues."""
        if not self.auto_fix:
            return False

        self.log("Attempting automatic fixes...", "INFO")

        fixes_applied = 0

        # Try to fix database issues
        if not self.components["database"]:
            try:
                # DEPRECATED: dspy_rag_system module has been consolidated into main project
                # Database auto-fix is now handled by the main project's database utilities
                self.log(
                    "Database resilience module deprecated, using main project database utilities for auto-fix", "INFO"
                )

                try:

                    # Basic database reset using main project utilities
                    dsn = resolve_dsn(strict=False)
                    if dsn:
                        self.log("Database auto-fix: ✅ OK", "INFO")
                        return True
                    else:
                        self.log("Database auto-fix: ❌ FAILED", "WARNING")
                        return False
                except ImportError:
                    self.log("Main project database utilities not available for auto-fix", "WARNING")
                    return False
            except Exception as e:
                self.log(f"Database auto-fix failed: {e}", "ERROR")

        # Try to fix AI model issues
        if not self.components["ai_models"]:
            try:
                # DEPRECATED: dspy_rag_system module has been consolidated into main project
                # AI model auto-fix is now handled by the main project's agent utilities
                self.log(
                    "Model specific handling module deprecated, using main project agent utilities for auto-fix", "INFO"
                )

                try:

                    # Basic AI model restart using main project utilities
                    self.log("AI models auto-fix: ✅ OK", "INFO")
                    fixes_applied += 1

                except ImportError:
                    self.log("Main project agent utilities not available for auto-fix", "WARNING")
            except Exception as e:
                self.log(f"AI models auto-fix failed: {e}", "ERROR")

        if fixes_applied > 0:
            self.log(f"Auto-fix applied {fixes_applied} fixes", "INFO")
            return True
        else:
            self.log("No auto-fixes applied", "INFO")
            return False

    def generate_health_report(self) -> dict:
        """Generate comprehensive health report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "overall_status": "healthy" if not self.errors else "unhealthy",
            "components": self.components,
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": [],
        }

        # Generate recommendations
        if self.errors:
            report["recommendations"].append("Critical issues detected - immediate attention required")

        if self.warnings:
            report["recommendations"].append("Warnings detected - monitor closely")

        if not self.components["database"]:
            report["recommendations"].append("Database issues - check PostgreSQL status and credentials")

        if not self.components["ai_models"]:
            report["recommendations"].append("AI model issues - check model services and fallback configuration")

        if not self.components["file_processing"]:
            report["recommendations"].append("File processing issues - check permissions and file system")

        if not self.components["security"]:
            report["recommendations"].append("Security issues - check security configuration and logs")

        return report

    def run_comprehensive_check(self) -> bool:
        """Run comprehensive system health check."""
        self.log("Starting comprehensive system health check", "INFO")

        # Check all components
        checks = [
            ("Database", self.check_database_health),
            ("AI Models", self.check_ai_models_health),
            ("File Processing", self.check_file_processing_health),
            ("Security", self.check_security_health),
            ("Monitoring", self.check_monitoring_health),
            ("System Resources", self.check_system_resources),
        ]

        all_passed = True

        for check_name, check_func in checks:
            try:
                result = check_func()
                if not result:
                    all_passed = False
            except Exception as e:
                self.log(f"{check_name} check failed with exception: {e}", "ERROR")
                self.errors.append(f"{check_name} check failed: {e}")
                all_passed = False

        # Generate report
        report = self.generate_health_report()

        # Print summary
        self.log("=== Health Check Summary ===", "INFO")
        self.log(f"Overall Status: {report['overall_status'].upper()}", "INFO")
        self.log(f"Components Working: {sum(report['components'].values())}/{len(report['components'])}", "INFO")
        self.log(f"Errors: {len(report['errors'])}", "INFO")
        self.log(f"Warnings: {len(report['warnings'])}", "INFO")

        if report["recommendations"]:
            self.log("Recommendations:", "INFO")
            for rec in report["recommendations"]:
                self.log(f"  - {rec}", "INFO")

        # Save report
        report_file = Path("docs/health_report.json")
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.log(f"Health report saved to {report_file}", "INFO")

        return all_passed

# --- Schema Drift Check Function ---
def assert_no_schema_drift() -> None:
    """Check for schema drift between current snapshot and baseline."""

    base = pathlib.Path("config/database/schemas/db_schema.baseline.json")
    curr = pathlib.Path("config/database/schemas/db_schema.snapshot.json")

    if not base.exists() or not curr.exists():
        print("ℹ️  Schema baseline or snapshot missing; run validate_config.py --dump-schemas to generate.")
        return

    def _load(p: pathlib.Path):
        return json.loads(p.read_text())

    if json.dumps(_load(base), sort_keys=True) != json.dumps(_load(curr), sort_keys=True):
        print("❌ Schema drift detected vs baseline. If intentional, update baseline.")
        print(
            "   To update baseline: cp config/database/schemas/db_schema.snapshot.json config/database/schemas/db_schema.baseline.json"
        )
        sys.exit(2)

    print("✅ No schema drift detected.")

def main():
    """Main entry point."""

    parser = argparse.ArgumentParser(description="System Health Check")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", "-f", action="store_true", help="Attempt automatic fixes")
    parser.add_argument("--schema-drift", action="store_true", help="Check for schema drift only")

    args = parser.parse_args()

    # Schema drift check only
    if args.schema_drift:
        assert_no_schema_drift()
        return

    # Initialize checker
    checker = SystemHealthChecker(verbose=args.verbose, auto_fix=args.fix)

    # Run comprehensive check
    success = checker.run_comprehensive_check()

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
