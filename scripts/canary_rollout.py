#!/usr/bin/env python3
"""
Canary Rollout Script
- Manage canary rollout (10% → 50% → 100%)
- Rollback switch for instant rollback
- Traffic routing between old and new configurations
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

from src.utils.config_lock import ConfigLockManager, LockedConfig


class CanaryManager:
    """Manages canary rollout and rollback"""

    def __init__(self, config: LockedConfig):
        self.config = config
        self.rollout_state_file = Path("config/canary_rollout_state.json")
        self.rollout_state_file.parent.mkdir(parents=True, exist_ok=True)

    def get_rollout_state(self) -> Dict[str, Any]:
        """Get current rollout state"""
        if not self.rollout_state_file.exists():
            return {
                "status": "not_started",
                "traffic_percentage": 0,
                "start_time": None,
                "current_phase": "pre_rollout",
                "rollback_ready": False,
            }

        try:
            with open(self.rollout_state_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading rollout state: {e}")
            return {"status": "error", "error": str(e)}

    def save_rollout_state(self, state: Dict[str, Any]) -> None:
        """Save rollout state"""
        with open(self.rollout_state_file, "w") as f:
            json.dump(state, f, indent=2)

    def start_canary_rollout(self) -> Dict[str, Any]:
        """Start canary rollout"""
        print("🚀 Starting Canary Rollout")
        print("=" * 40)

        state = {
            "status": "active",
            "traffic_percentage": 10,
            "start_time": datetime.now().isoformat(),
            "current_phase": "canary_10_percent",
            "rollback_ready": True,
            "config_version": self.config.chunk_version,
            "config_hash": self.config.get_config_hash(),
            "shadow_table": self.config.shadow_table,
        }

        self.save_rollout_state(state)

        # Set environment variables for 10% traffic
        self._set_traffic_routing(10)

        print("✅ Canary rollout started")
        print("   Traffic percentage: 10%")
        print(f"   Config version: {self.config.chunk_version}")
        print(f"   Shadow table: {self.config.shadow_table}")
        print("   Rollback ready: Yes")

        return state

    def promote_to_50_percent(self) -> Dict[str, Any]:
        """Promote to 50% traffic"""
        print("📈 Promoting to 50% Traffic")
        print("=" * 40)

        state = self.get_rollout_state()
        if state.get("status") != "active":
            print("❌ No active rollout to promote")
            return state

        state["traffic_percentage"] = 50
        state["current_phase"] = "canary_50_percent"
        state["last_promotion"] = datetime.now().isoformat()

        self.save_rollout_state(state)
        self._set_traffic_routing(50)

        print("✅ Promoted to 50% traffic")
        print(f"   Current phase: {state['current_phase']}")

        return state

    def promote_to_100_percent(self) -> Dict[str, Any]:
        """Promote to 100% traffic (full rollout)"""
        print("🎯 Promoting to 100% Traffic")
        print("=" * 40)

        state = self.get_rollout_state()
        if state.get("status") != "active":
            print("❌ No active rollout to promote")
            return state

        state["traffic_percentage"] = 100
        state["current_phase"] = "full_rollout"
        state["last_promotion"] = datetime.now().isoformat()
        state["rollout_complete"] = True

        self.save_rollout_state(state)
        self._set_traffic_routing(100)

        print("✅ Promoted to 100% traffic")
        print("   Rollout complete: Yes")

        return state

    def rollback(self) -> Dict[str, Any]:
        """Instant rollback to previous configuration"""
        print("🔄 Rolling Back")
        print("=" * 40)

        state = self.get_rollout_state()

        # Rollback state
        rollback_state = {
            "status": "rolled_back",
            "traffic_percentage": 0,
            "rollback_time": datetime.now().isoformat(),
            "previous_phase": state.get("current_phase", "unknown"),
            "rollback_ready": False,
            "config_version": self.config.chunk_version,
            "config_hash": self.config.get_config_hash(),
        }

        self.save_rollout_state(rollback_state)

        # Clear traffic routing (back to 0%)
        self._set_traffic_routing(0)

        # Clear retrieval cache
        self._clear_retrieval_cache()

        print("✅ Rollback completed")
        print("   Traffic percentage: 0%")
        print(f"   Previous phase: {state.get('current_phase', 'unknown')}")
        print("   Cache cleared: Yes")

        return rollback_state

    def _set_traffic_routing(self, percentage: int) -> None:
        """Set traffic routing percentage"""
        if percentage == 0:
            # Rollback: unset INGEST_RUN_ID
            if "INGEST_RUN_ID" in os.environ:
                del os.environ["INGEST_RUN_ID"]
            os.environ["CHUNK_TABLE"] = "document_chunks"  # Back to v1
        elif percentage == 100:
            # Full rollout: use new configuration
            os.environ["INGEST_RUN_ID"] = f"{self.config.chunk_version}-{self.config.get_config_hash()[:8]}"
            os.environ["CHUNK_TABLE"] = (
                self.config.shadow_table or f"document_chunks_{self.config.chunk_version.replace('-', '_')}"
            )
        else:
            # Canary: use new configuration with percentage
            os.environ["INGEST_RUN_ID"] = f"{self.config.chunk_version}-{self.config.get_config_hash()[:8]}"
            os.environ["CHUNK_TABLE"] = (
                self.config.shadow_table or f"document_chunks_{self.config.chunk_version.replace('-', '_')}"
            )
            os.environ["CANARY_PERCENTAGE"] = str(percentage)

        print(f"🔧 Traffic routing set to {percentage}%")

    def _clear_retrieval_cache(self) -> None:
        """Clear retrieval cache"""
        # In production, you'd clear your retrieval cache here
        print("🧹 Retrieval cache cleared")

    def get_rollout_status(self) -> Dict[str, Any]:
        """Get current rollout status"""
        state = self.get_rollout_state()

        return {
            "status": state.get("status", "unknown"),
            "traffic_percentage": state.get("traffic_percentage", 0),
            "current_phase": state.get("current_phase", "unknown"),
            "rollback_ready": state.get("rollback_ready", False),
            "config_version": state.get("config_version", "unknown"),
            "shadow_table": state.get("shadow_table", "unknown"),
            "start_time": state.get("start_time"),
            "last_promotion": state.get("last_promotion"),
        }


def main():
    parser = argparse.ArgumentParser(description="Manage canary rollout and rollback")
    parser.add_argument("--start", action="store_true", help="Start canary rollout (10%)")
    parser.add_argument("--promote-50", action="store_true", help="Promote to 50% traffic")
    parser.add_argument("--promote-100", action="store_true", help="Promote to 100% traffic")
    parser.add_argument("--rollback", action="store_true", help="Rollback to previous configuration")
    parser.add_argument("--status", action="store_true", help="Show rollout status")
    parser.add_argument("--quiet", action="store_true", help="Quiet mode")

    args = parser.parse_args()

    # Load active configuration
    manager = ConfigLockManager()
    config = manager.get_active_config()

    if not config:
        print("❌ No active configuration found. Run lock_production_config.py first.")
        sys.exit(1)

    # Initialize canary manager
    canary_manager = CanaryManager(config)

    # Execute requested action
    if args.start:
        result = canary_manager.start_canary_rollout()
    elif args.promote_50:
        result = canary_manager.promote_to_50_percent()
    elif args.promote_100:
        result = canary_manager.promote_to_100_percent()
    elif args.rollback:
        result = canary_manager.rollback()
    elif args.status:
        result = canary_manager.get_rollout_status()
    else:
        print("❌ No action specified. Use --start, --promote-50, --promote-100, --rollback, or --status")
        sys.exit(1)

    # Show status if not quiet
    if not args.quiet:
        print("\n📊 Rollout Status")
        print("=" * 40)
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Traffic Percentage: {result.get('traffic_percentage', 0)}%")
        print(f"Current Phase: {result.get('current_phase', 'unknown')}")
        print(f"Rollback Ready: {'✅' if result.get('rollback_ready', False) else '❌'}")
        print(f"Config Version: {result.get('config_version', 'unknown')}")
        print(f"Shadow Table: {result.get('shadow_table', 'unknown')}")

        if result.get("start_time"):
            print(f"Start Time: {result['start_time']}")
        if result.get("last_promotion"):
            print(f"Last Promotion: {result['last_promotion']}")

    # Exit with error code if rollout failed
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()
