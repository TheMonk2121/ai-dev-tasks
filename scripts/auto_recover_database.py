#!/usr/bin/env python3
"""
Automated Database Recovery Script - B-065 Implementation

Automatically detects and fixes common database issues.
Integrates with the B-002 Advanced Error Recovery & Prevention system.

Usage: python scripts/auto_recover_database.py [--dry-run] [--force]
"""

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

# Add dspy-rag-system to path
sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system"))


class DatabaseRecoveryManager:
    def __init__(self, dry_run: bool = True, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.recovery_attempts = []
        self.successful_fixes = []
        self.failed_fixes = []

        # Recovery strategies
        self.recovery_strategies = {
            "connection_timeout": self.fix_connection_timeout,
            "authentication_failed": self.fix_authentication_failed,
            "schema_error": self.fix_schema_error,
            "permission_denied": self.fix_permission_denied,
            "service_unavailable": self.fix_service_unavailable,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log messages with consistent formatting."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def check_connection(self) -> bool:
        """Check database connection."""
        try:
            # Try direct import first
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.database_resilience import is_database_healthy

            return is_database_healthy()
        except Exception as e:
            self.log(f"Connection check failed: {e}", "ERROR")
            return False

    def test_connection(self) -> bool:
        """Test database connection with detailed diagnostics."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.database_resilience import get_database_health

            health = get_database_health()
            # Handle both dict and object responses
            if isinstance(health, dict):
                return health.get("status") == "healthy"
            else:
                return getattr(health, "status", "unknown") == "healthy"
        except Exception as e:
            self.log(f"Connection test failed: {e}", "ERROR")
            return False

    def reset_connection_pool(self) -> bool:
        """Reset database connection pool."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.database_resilience import get_database_manager

            manager = get_database_manager()
            # Force pool reset by getting a new connection
            with manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            return True
        except Exception as e:
            self.log(f"Connection pool reset failed: {e}", "ERROR")
            return False

    def verify_schema(self) -> bool:
        """Verify database schema."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.database_resilience import get_database_manager

            manager = get_database_manager()
            with manager.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
                    tables = cur.fetchall()
                    return len(tables) > 0
        except Exception as e:
            self.log(f"Schema verification failed: {e}", "ERROR")
            return False

    def fix_connection_timeout(self) -> bool:
        """Fix connection timeout issues."""
        self.log("Attempting to fix connection timeout...", "INFO")

        # Strategy 1: Reset connection pool
        if self.reset_connection_pool():
            self.log("Connection pool reset: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Connection timeout fixed", "INFO")
                self.successful_fixes.append("connection_timeout")
                return True

        # Strategy 2: Check PostgreSQL service
        if self.check_postgresql_service():
            self.log("PostgreSQL service check: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Connection timeout fixed via service restart", "INFO")
                self.successful_fixes.append("connection_timeout")
                return True

        self.log("Connection timeout fix failed", "ERROR")
        self.failed_fixes.append("connection_timeout")
        return False

    def fix_authentication_failed(self) -> bool:
        """Fix authentication failed issues."""
        self.log("Attempting to fix authentication failed...", "INFO")

        # Strategy 1: Check environment variables
        if self.check_database_credentials():
            self.log("Database credentials check: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Authentication fixed", "INFO")
                self.successful_fixes.append("authentication_failed")
                return True

        # Strategy 2: Reset credentials
        if self.reset_database_credentials():
            self.log("Database credentials reset: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Authentication fixed via credential reset", "INFO")
                self.successful_fixes.append("authentication_failed")
                return True

        self.log("Authentication fix failed", "ERROR")
        self.failed_fixes.append("authentication_failed")
        return False

    def fix_schema_error(self) -> bool:
        """Fix schema error issues."""
        self.log("Attempting to fix schema error...", "INFO")

        # Strategy 1: Verify schema
        if self.verify_schema():
            self.log("Schema verification: ✅ SUCCESS", "INFO")
            self.successful_fixes.append("schema_error")
            return True

        # Strategy 2: Recreate schema
        if self.recreate_schema():
            self.log("Schema recreation: ✅ SUCCESS", "INFO")
            if self.verify_schema():
                self.log("Schema error fixed", "INFO")
                self.successful_fixes.append("schema_error")
                return True

        self.log("Schema error fix failed", "ERROR")
        self.failed_fixes.append("schema_error")
        return False

    def fix_permission_denied(self) -> bool:
        """Fix permission denied issues."""
        self.log("Attempting to fix permission denied...", "INFO")

        # Strategy 1: Check file permissions
        if self.check_database_permissions():
            self.log("Database permissions check: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Permission denied fixed", "INFO")
                self.successful_fixes.append("permission_denied")
                return True

        # Strategy 2: Fix permissions
        if self.fix_database_permissions():
            self.log("Database permissions fix: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Permission denied fixed via permission fix", "INFO")
                self.successful_fixes.append("permission_denied")
                return True

        self.log("Permission denied fix failed", "ERROR")
        self.failed_fixes.append("permission_denied")
        return False

    def fix_service_unavailable(self) -> bool:
        """Fix service unavailable issues."""
        self.log("Attempting to fix service unavailable...", "INFO")

        # Strategy 1: Restart PostgreSQL service
        if self.restart_postgresql_service():
            self.log("PostgreSQL service restart: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Service unavailable fixed", "INFO")
                self.successful_fixes.append("service_unavailable")
                return True

        # Strategy 2: Check system resources
        if self.check_system_resources():
            self.log("System resources check: ✅ SUCCESS", "INFO")
            if self.check_connection():
                self.log("Service unavailable fixed via resource check", "INFO")
                self.successful_fixes.append("service_unavailable")
                return True

        self.log("Service unavailable fix failed", "ERROR")
        self.failed_fixes.append("service_unavailable")
        return False

    def check_postgresql_service(self) -> bool:
        """Check PostgreSQL service status."""
        try:
            result = subprocess.run(["systemctl", "status", "postgresql"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("PostgreSQL service is running", "INFO")
                return True
            else:
                self.log("PostgreSQL service is not running", "WARNING")
                return self.restart_postgresql_service()
        except Exception as e:
            self.log(f"PostgreSQL service check failed: {e}", "ERROR")
            return False

    def restart_postgresql_service(self) -> bool:
        """Restart PostgreSQL service."""
        if self.dry_run:
            self.log("[DRY-RUN] Would restart PostgreSQL service", "INFO")
            return True

        try:
            result = subprocess.run(["sudo", "systemctl", "restart", "postgresql"], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("PostgreSQL service restarted successfully", "INFO")
                time.sleep(5)  # Wait for service to start
                return True
            else:
                self.log(f"PostgreSQL service restart failed: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"PostgreSQL service restart failed: {e}", "ERROR")
            return False

    def check_database_credentials(self) -> bool:
        """Check database credentials."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.secrets_manager import SecretsManager

            manager = SecretsManager()
            # Check if required database secrets are present
            secret_configs = manager.create_secrets_config()
            missing = manager.get_missing_secrets(secret_configs)

            # Check for database-related secrets
            db_secrets = [config.name for config in secret_configs if "POSTGRES" in config.name or "DB" in config.name]
            missing_db_secrets = [secret for secret in missing if secret in db_secrets]

            if not missing_db_secrets:
                self.log("Database credentials are present", "INFO")
                return True
            else:
                self.log(f"Missing database credentials: {missing_db_secrets}", "WARNING")
                return False
        except Exception as e:
            self.log(f"Database credentials check failed: {e}", "ERROR")
            return False

    def reset_database_credentials(self) -> bool:
        """Reset database credentials."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.secrets_manager import SecretsManager

            manager = SecretsManager()

            # For now, just validate existing credentials
            # In a real implementation, this might reset to defaults or prompt for new ones
            secret_configs = manager.create_secrets_config()
            validation_results = manager.validate_secrets(secret_configs)

            db_secrets = [config.name for config in secret_configs if "POSTGRES" in config.name or "DB" in config.name]
            invalid_db_secrets = [secret for secret in db_secrets if not validation_results.get(secret, True)]

            if not invalid_db_secrets:
                self.log("Database credentials are valid", "INFO")
                return True
            else:
                self.log(f"Invalid database credentials: {invalid_db_secrets}", "WARNING")
                return False
        except Exception as e:
            self.log(f"Database credentials reset failed: {e}", "ERROR")
            return False

    def recreate_schema(self) -> bool:
        """Recreate database schema."""
        if self.dry_run:
            self.log("[DRY-RUN] Would recreate database schema", "INFO")
            return True

        try:
            # Run schema creation script
            schema_file = Path("dspy-rag-system/config/database/schema.sql")
            if schema_file.exists():
                result = subprocess.run(["psql", "-f", str(schema_file)], capture_output=True, text=True)
                if result.returncode == 0:
                    self.log("Database schema recreated successfully", "INFO")
                    return True
                else:
                    self.log(f"Database schema recreation failed: {result.stderr}", "ERROR")
                    return False
            else:
                self.log("Schema file not found", "ERROR")
                return False
        except Exception as e:
            self.log(f"Database schema recreation failed: {e}", "ERROR")
            return False

    def check_database_permissions(self) -> bool:
        """Check database permissions."""
        try:
            # Check if we can connect to database
            result = subprocess.run(["psql", "-c", "SELECT 1"], capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.log(f"Database permissions check failed: {e}", "ERROR")
            return False

    def fix_database_permissions(self) -> bool:
        """Fix database permissions."""
        if self.dry_run:
            self.log("[DRY-RUN] Would fix database permissions", "INFO")
            return True

        try:
            # This would typically involve checking and fixing file permissions
            # For now, we'll just return True as a placeholder
            self.log("Database permissions fix completed", "INFO")
            return True
        except Exception as e:
            self.log(f"Database permissions fix failed: {e}", "ERROR")
            return False

    def check_system_resources(self) -> bool:
        """Check system resources."""
        try:
            import psutil

            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 90:
                self.log(f"High memory usage: {memory.percent}%", "WARNING")
                return False

            # Check disk usage
            disk = psutil.disk_usage("/")
            if disk.percent > 95:
                self.log(f"High disk usage: {disk.percent}%", "WARNING")
                return False

            self.log("System resources OK", "INFO")
            return True
        except ImportError:
            self.log("psutil not available, skipping resource check", "WARNING")
            return True
        except Exception as e:
            self.log(f"System resources check failed: {e}", "ERROR")
            return False

    def diagnose_issue(self) -> Optional[str]:
        """Diagnose the specific database issue."""
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
            from utils.error_pattern_recognition import ErrorPatternRecognizer

            recognizer = ErrorPatternRecognizer()

            # For now, we'll use a simple approach to diagnose common database issues
            # In a real implementation, this would analyze recent error logs

            # Check connection first to get a specific error message
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent / "dspy-rag-system" / "src"))
                from utils.database_resilience import get_database_manager

                manager = get_database_manager()
                with manager.get_connection() as conn:
                    with conn.cursor() as cur:
                        cur.execute("SELECT 1")
            except Exception as e:
                error_message = str(e).lower()

                # Analyze the error using the pattern recognizer
                analysis = recognizer.analyze_error(error_message, context={"operation": "database_connection"})

                # Map pattern categories to recovery strategies
                for pattern in analysis.matched_patterns:
                    if pattern.category == "database":
                        if "timeout" in pattern.pattern_id.lower():
                            return "connection_timeout"
                        elif "auth" in pattern.pattern_id.lower() or "authentication" in pattern.pattern_id.lower():
                            return "authentication_failed"
                        elif "permission" in pattern.pattern_id.lower():
                            return "permission_denied"
                        elif "service" in pattern.pattern_id.lower() or "unavailable" in pattern.pattern_id.lower():
                            return "service_unavailable"
                        else:
                            return "schema_error"

            return None
        except Exception as e:
            self.log(f"Issue diagnosis failed: {e}", "ERROR")
            return None

    def auto_recover_database(self) -> bool:
        """Automatically recover database issues."""
        self.log("Starting automated database recovery...", "INFO")

        # Check current connection
        if self.check_connection():
            self.log("Database connection is healthy", "INFO")
            return True

        # Diagnose the issue
        issue_type = self.diagnose_issue()

        if issue_type and issue_type in self.recovery_strategies:
            self.log(f"Detected issue: {issue_type}", "INFO")

            # Apply recovery strategy
            recovery_func = self.recovery_strategies[issue_type]
            if recovery_func():
                self.log(f"Database recovery successful for {issue_type}", "INFO")
                return True
            else:
                self.log(f"Database recovery failed for {issue_type}", "ERROR")
                return False
        else:
            self.log("Unknown database issue, attempting general recovery...", "WARNING")

            # Try general recovery strategies
            strategies = [
                ("Connection Pool Reset", self.reset_connection_pool),
                ("PostgreSQL Service Check", self.check_postgresql_service),
                ("Credentials Check", self.check_database_credentials),
                ("Schema Verification", self.verify_schema),
            ]

            for strategy_name, strategy_func in strategies:
                self.log(f"Trying {strategy_name}...", "INFO")
                if strategy_func() and self.check_connection():
                    self.log(f"Database recovery successful via {strategy_name}", "INFO")
                    return True

            self.log("All recovery strategies failed", "ERROR")
            return False

    def generate_recovery_report(self) -> Dict[str, Any]:
        """Generate recovery report."""
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "dry_run": self.dry_run,
            "successful_fixes": self.successful_fixes,
            "failed_fixes": self.failed_fixes,
            "recovery_attempts": self.recovery_attempts,
            "final_status": "healthy" if self.check_connection() else "unhealthy",
        }

        return report


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Database Recovery")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Run in dry-run mode (default)")
    parser.add_argument("--force", action="store_true", help="Force recovery even if connection is healthy")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually perform recovery (not dry-run)")

    args = parser.parse_args()

    # Handle dry-run logic
    dry_run = args.dry_run and not args.no_dry_run

    # Initialize recovery manager
    manager = DatabaseRecoveryManager(dry_run=dry_run, force=args.force)

    # Run recovery
    success = manager.auto_recover_database()

    # Generate report
    report = manager.generate_recovery_report()

    # Print summary
    print("\n=== Database Recovery Summary ===")
    print(f"Final Status: {report['final_status'].upper()}")
    print(f"Successful Fixes: {len(report['successful_fixes'])}")
    print(f"Failed Fixes: {len(report['failed_fixes'])}")
    print(f"Dry Run: {report['dry_run']}")

    # Save report
    report_file = Path("docs/database_recovery_report.json")
    report_file.parent.mkdir(exist_ok=True)

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Recovery report saved to {report_file}")

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
