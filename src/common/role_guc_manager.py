#!/usr/bin/env python3
"""Role-based GUC manager for workload isolation in B-1070."""

import logging
import os
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# Role-specific GUC configurations
ROLE_GUCS = {
    "ltst_memory": {
        "work_mem": "64MB",  # Higher for bulk vector operations
        "maintenance_work_mem": "256MB",  # Higher for index maintenance
        "effective_cache_size": "8GB",  # Optimized for vector similarity
        "shared_preload_libraries": "vector,pg_stat_statements",
        "vector.ef_search": "100",  # pgvector: higher for accuracy
        "vector.hnsw_ef_search": "100",  # pgvector: HNSW search depth
    },
    "ragchecker_eval": {
        "work_mem": "32MB",  # Lower for evaluation workloads
        "maintenance_work_mem": "64MB",  # Lower for evaluation
        "effective_cache_size": "4GB",  # Dedicated for evaluations
        "shared_preload_libraries": "vector,pg_stat_statements",
        "vector.ef_search": "50",  # pgvector: faster, less accurate
        "vector.hnsw_ef_search": "50",  # pgvector: faster HNSW search
    },
    "default": {
        "work_mem": "16MB",  # Conservative default
        "maintenance_work_mem": "64MB",
        "effective_cache_size": "4GB",
        "shared_preload_libraries": "vector,pg_stat_statements",
        "vector.ef_search": "75",  # Balanced pgvector settings
        "vector.hnsw_ef_search": "75",
    },
}


class RoleGUCManager:
    """Manages PostgreSQL GUC settings based on workload roles."""

    def __init__(self, dsn: str | None = None):
        """Initialize the GUC manager."""
        if dsn is None:
            # Try to resolve DSN
            try:
                sys.path.insert(0, str(Path(__file__).parent.parent))
                from common.db_dsn import resolve_dsn

                dsn = resolve_dsn(strict=False, emit_warning=False)
            except ImportError:
                dsn = os.getenv("DATABASE_URL", "postgresql://danieljacobs@localhost:5432/ai_agency")

        self.dsn = dsn
        self.current_role = "default"
        self.applied_settings: dict[str, str] = {}

    def set_role(self, role: str) -> bool:
        """Set the current workload role and apply corresponding GUCs."""
        if role not in ROLE_GUCS:
            logger.warning(f"Unknown role '{role}', using 'default'")
            role = "default"

        self.current_role = role
        logger.info(f"Setting role to: {role}")

        # Apply role-specific GUCs
        return self.apply_role_gucs()

    def apply_role_gucs(self) -> bool:
        """Apply the current role's GUC settings to PostgreSQL."""
        if not self.dsn:
            logger.error("No DSN available for GUC application")
            return False

        role_config = ROLE_GUCS[self.current_role]
        logger.info(f"Applying {self.current_role} GUCs: {list(role_config.keys())}")

        success_count = 0
        total_count = len(role_config)

        for guc_name, guc_value in role_config.items():
            if self._apply_guc(guc_name, guc_value):
                success_count += 1
                self.applied_settings[guc_name] = guc_value
            else:
                logger.warning(f"Failed to apply {guc_name} = {guc_value}")

        success_rate = success_count / total_count
        logger.info(f"GUC application: {success_count}/{total_count} successful ({success_rate:.1%})")

        return success_rate >= 0.8  # 80% success threshold

    def _apply_guc(self, guc_name: str, guc_value: str) -> bool:
        """Apply a single GUC setting."""
        try:
            # Handle special pgvector settings
            if guc_name.startswith("vector."):
                # These are runtime settings, not system settings
                return self._apply_runtime_guc(guc_name, guc_value)
            else:
                # Standard PostgreSQL GUCs
                return self._apply_system_guc(guc_name, guc_value)

        except Exception as e:
            logger.error(f"Error applying GUC {guc_name}: {e}")
            return False

    def _apply_system_guc(self, guc_name: str, guc_value: str) -> bool:
        """Apply a system-level GUC setting."""
        try:
            cmd = ["psql", self.dsn, "-Atqc", f"ALTER SYSTEM SET {guc_name} = '{guc_value}';"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.debug(f"Applied system GUC: {guc_name} = {guc_value}")
                return True
            else:
                logger.warning(f"Failed to apply {guc_name}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout applying GUC {guc_name}")
            return False
        except Exception as e:
            logger.error(f"Exception applying GUC {guc_name}: {e}")
            return False

    def _apply_runtime_guc(self, guc_name: str, guc_value: str) -> bool:
        """Apply a runtime GUC setting (session-level)."""
        try:
            cmd = ["psql", self.dsn, "-Atqc", f"SET {guc_name} = '{guc_value}';"]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                logger.debug(f"Applied runtime GUC: {guc_name} = {guc_value}")
                return True
            else:
                logger.warning(f"Failed to apply runtime GUC {guc_name}: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"Timeout applying runtime GUC {guc_name}")
            return False
        except Exception as e:
            logger.error(f"Exception applying runtime GUC {guc_name}: {e}")
            return False

    def get_current_settings(self) -> dict[str, str]:
        """Get the currently applied GUC settings."""
        return self.applied_settings.copy()

    def get_role_config(self, role: str | None = None) -> dict[str, str]:
        """Get the GUC configuration for a specific role."""
        if role is None:
            role = self.current_role
        return ROLE_GUCS.get(role, ROLE_GUCS["default"]).copy()

    def reset_to_default(self) -> bool:
        """Reset all GUCs to default values."""
        logger.info("Resetting GUCs to default values")
        self.current_role = "default"
        return self.apply_role_gucs()

    def create_session_config(self, role: str) -> str:
        """Create a session configuration script for the specified role."""
        role_config = ROLE_GUCS.get(role, ROLE_GUCS["default"])

        config_lines = [
            f"-- Role: {role} GUC Configuration",
            "-- Generated by RoleGUCManager",
            "",
        ]

        for guc_name, guc_value in role_config.items():
            if guc_name.startswith("vector."):
                config_lines.append(f"SET {guc_name} = '{guc_value}';")
            else:
                config_lines.append(f"ALTER SYSTEM SET {guc_name} = '{guc_value}';")

        return "\n".join(config_lines)

    def save_config(self, filepath: str | None = None) -> str:
        """Save the current role configuration to a file."""
        if filepath is None:
            timestamp = int(time.time())
            filepath = f"metrics/system_diagnostics/role_guc_{self.current_role}_{timestamp}.sql"

        config_content = self.create_session_config(self.current_role)

        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, "w") as f:
            f.write(config_content)

        logger.info(f"Saved role configuration to: {filepath}")
        return filepath


def main():
    """Test the RoleGUCManager."""
    import time
    logging.basicConfig(level=logging.INFO)

    print("🧪 Testing RoleGUCManager")
    print("=" * 50)

    manager = RoleGUCManager()

    # Test different roles
    for role in ["default", "ltst_memory", "ragchecker_eval"]:
        print(f"\n🔧 Testing role: {role}")
        success = manager.set_role(role)
        print(f"   Success: {success}")

        if success:
            settings = manager.get_current_settings()
            print(f"   Applied: {len(settings)} settings")

            # Save configuration
            config_file = manager.save_config()
            print(f"   Config saved: {config_file}")

        time.sleep(1)  # Brief pause between roles

    print("\n✅ RoleGUCManager test completed")


if __name__ == "__main__":
    main()
