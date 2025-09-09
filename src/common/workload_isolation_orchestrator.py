#!/usr/bin/env python3
"""Workload isolation orchestrator for B-1070 database optimization."""

import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from common.cache_separation_manager import CacheSeparationManager
from common.role_guc_manager import RoleGUCManager

logger = logging.getLogger(__name__)


class WorkloadIsolationOrchestrator:
    """Orchestrates workload isolation through GUCs and cache separation."""

    def __init__(self, dsn: str | None = None):
        """Initialize the workload isolation orchestrator."""
        self.guc_manager = RoleGUCManager(dsn)
        self.cache_manager = CacheSeparationManager()
        self.current_role = "default"
        self.isolation_status: dict[str, dict[str, Any]] = {}

        logger.info("WorkloadIsolationOrchestrator initialized")

    def isolate_workload(self, role: str) -> bool:
        """Apply complete workload isolation for a specific role."""
        logger.info(f"Applying workload isolation for role: {role}")

        # Track isolation steps
        isolation_results = {"guc_application": False, "cache_separation": False, "overall_success": False}

        try:
            # Step 1: Apply role-specific GUCs
            logger.info("Step 1: Applying role-specific GUCs")
            isolation_results["guc_application"] = self.guc_manager.set_role(role)

            if not isolation_results["guc_application"]:
                logger.error("GUC application failed")
                return False

            # Step 2: Set cache separation
            logger.info("Step 2: Setting cache separation")
            isolation_results["cache_separation"] = self.cache_manager.set_role(role)

            if not isolation_results["cache_separation"]:
                logger.error("Cache separation failed")
                return False

            # Step 3: Verify isolation
            logger.info("Step 3: Verifying isolation")
            verification_passed = self._verify_isolation(role)

            isolation_results["overall_success"] = verification_passed
            self.isolation_status[role] = isolation_results

            if verification_passed:
                self.current_role = role
                logger.info(f"Workload isolation for {role} completed successfully")
            else:
                logger.error(f"Workload isolation verification failed for {role}")

            return verification_passed

        except Exception as e:
            logger.error(f"Error during workload isolation: {e}")
            isolation_results["overall_success"] = False
            self.isolation_status[role] = isolation_results
            return False

    def _verify_isolation(self, role: str) -> bool:
        """Verify that workload isolation is properly applied."""
        try:
            # Verify GUC settings
            guc_settings = self.guc_manager.get_current_settings()
            expected_gucs = self.guc_manager.get_role_config(role)

            guc_verification = True
            for guc_name, expected_value in expected_gucs.items():
                if guc_name.startswith("vector."):
                    # Runtime GUCs are applied per-session, not globally
                    continue
                if guc_name not in guc_settings:
                    logger.warning(f"Expected GUC {guc_name} not found in applied settings")
                    guc_verification = False

            # Verify cache separation
            cache_info = self.cache_manager.get_cache_info(role)
            cache_verification = cache_info["base_dir"] is not None

            # Verify database connectivity
            db_verification = self._verify_database_connectivity()

            overall_verification = guc_verification and cache_verification and db_verification

            logger.info(
                f"Isolation verification: GUCs={guc_verification}, Cache={cache_verification}, DB={db_verification}"
            )

            return overall_verification

        except Exception as e:
            logger.error(f"Error during isolation verification: {e}")
            return False

    def _verify_database_connectivity(self) -> bool:
        """Verify database connectivity after GUC changes."""
        try:
            # Simple connectivity test
            import psycopg2

            conn = psycopg2.connect(self.guc_manager.dsn)
            cur = conn.cursor()

            # Test basic query
            cur.execute("SELECT 1")
            result = cur.fetchone()

            cur.close()
            conn.close()

            # Ensure result exists and has expected value
            if result is None:
                logger.error("Query returned no result")
                return False

            return result[0] == 1

        except Exception as e:
            logger.error(f"Database connectivity verification failed: {e}")
            return False

    def get_isolation_status(self, role: str | None = None) -> dict[str, Any]:
        """Get the isolation status for a specific role or current role."""
        if role is None:
            role = self.current_role

        if role not in self.isolation_status:
            return {"status": "not_applied", "role": role}

        status = self.isolation_status[role].copy()
        status["role"] = role
        status["timestamp"] = time.time()

        # Add current GUC and cache info
        status["guc_settings"] = self.guc_manager.get_current_settings()
        status["cache_info"] = self.cache_manager.get_cache_info(role)

        return status

    def get_all_isolation_statuses(self) -> dict:
        """Get isolation status for all roles."""
        all_statuses = {}

        for role in ["default", "ltst_memory", "ragchecker_eval"]:
            all_statuses[role] = self.get_isolation_status(role)

        return all_statuses

    def reset_to_default(self) -> bool:
        """Reset all isolation to default settings."""
        logger.info("Resetting workload isolation to default")

        try:
            # Reset GUCs
            guc_success = self.guc_manager.reset_to_default()

            # Reset cache role
            cache_success = self.cache_manager.set_role("default")

            # Reset current role
            self.current_role = "default"

            success = guc_success and cache_success

            if success:
                logger.info("Successfully reset to default isolation")
            else:
                logger.warning("Partial reset - some components failed")

            return success

        except Exception as e:
            logger.error(f"Error resetting isolation: {e}")
            return False

    def create_isolation_report(self, filepath: str | None = None) -> str:
        """Create a comprehensive isolation report."""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"metrics/system_diagnostics/workload_isolation_{timestamp}.json"

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        report = {
            "timestamp": time.time(),
            "current_role": self.current_role,
            "isolation_statuses": self.get_all_isolation_statuses(),
            "guc_configurations": {},
            "cache_configurations": {},
            "system_info": {"dsn": self.guc_manager.dsn, "project_root": str(self.cache_manager.project_root)},
        }

        # Add GUC configurations
        for role in ["default", "ltst_memory", "ragchecker_eval"]:
            report["guc_configurations"][role] = self.guc_manager.get_role_config(role)

        # Add cache configurations
        for role in ["default", "ltst_memory", "ragchecker_eval"]:
            report["cache_configurations"][role] = self.cache_manager.get_cache_info(role)

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Isolation report saved to: {filepath}")
        return filepath

    def run_isolation_test(self) -> bool:
        """Run a comprehensive isolation test for all roles."""
        logger.info("Running comprehensive workload isolation test")

        test_results = {}
        overall_success = True

        for role in ["default", "ltst_memory", "ragchecker_eval"]:
            logger.info(f"Testing isolation for role: {role}")

            # Apply isolation
            success = self.isolate_workload(role)
            test_results[role] = success

            if not success:
                overall_success = False
                logger.error(f"Isolation test failed for role: {role}")

            # Brief pause between roles
            time.sleep(2)

        # Reset to default
        self.reset_to_default()

        # Log results
        logger.info("Isolation test results:")
        for role, success in test_results.items():
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"  {role}: {status}")

        logger.info(f"Overall isolation test: {'✅ PASS' if overall_success else '❌ FAIL'}")

        return overall_success


def main():
    """Test the WorkloadIsolationOrchestrator."""
    import time

    logging.basicConfig(level=logging.INFO)

    print("🧪 Testing WorkloadIsolationOrchestrator")
    print("=" * 50)

    orchestrator = WorkloadIsolationOrchestrator()

    # Test isolation for each role
    for role in ["default", "ltst_memory", "ragchecker_eval"]:
        print(f"\n🔧 Testing workload isolation for: {role}")

        success = orchestrator.isolate_workload(role)
        print(f"   Isolation success: {success}")

        if success:
            status = orchestrator.get_isolation_status(role)
            print(f"   GUCs applied: {len(status.get('guc_settings', {}))}")
            print(f"   Cache base dir: {status.get('cache_info', {}).get('base_dir', 'N/A')}")

        time.sleep(1)

    # Get overall status
    print("\n📊 Overall Isolation Status:")
    all_statuses = orchestrator.get_all_isolation_statuses()
    for role, status in all_statuses.items():
        overall_status = "✅ Active" if status.get("overall_success", False) else "❌ Inactive"
        print(f"   {role}: {overall_status}")

    # Create report
    report_file = orchestrator.create_isolation_report()
    print(f"   Report saved: {report_file}")

    # Reset to default
    print("\n🔄 Resetting to default...")
    reset_success = orchestrator.reset_to_default()
    print(f"   Reset success: {reset_success}")

    print("\n✅ WorkloadIsolationOrchestrator test completed")


if __name__ == "__main__":
    main()
