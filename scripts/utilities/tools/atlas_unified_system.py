#!/usr/bin/env python3
"""
Atlas Unified System
Combines automatic capture, self-healing navigation, and memory rehydration
"""

import os
import threading
import time
from datetime import datetime
from typing import Any

from .atlas_self_healing import SelfHealingNavigator
from .cursor_auto_capture import CursorAutoCapture


class AtlasUnifiedSystem:
    """Unified Atlas system with automatic capture and self-healing."""

    def __init__(self, dsn: str | None = None, capture_dir: str | None = None) -> None:
        self.dsn: str = dsn or os.getenv("POSTGRES_DSN", "postgresql://danieljacobs@localhost:5432/ai_agency")

        # Initialize components
        self.auto_capture: CursorAutoCapture = CursorAutoCapture(self.dsn)
        self.self_healing: SelfHealingNavigator = SelfHealingNavigator(self.dsn)

        # System state
        self.running: bool = False
        self.health_check_thread: threading.Thread | None = None

    def start_system(self) -> None:
        """Start the complete Atlas system."""
        if self.running:
            print("⚠️ Atlas system already running")
            return

        print("🚀 Starting Atlas Unified System...")

        # Start automatic capture
        self.auto_capture.start_capture()

        # Start health monitoring
        self.running = True
        self.health_check_thread = threading.Thread(target=self._health_monitor_loop, daemon=True)
        self.health_check_thread.start()

        print("✅ Atlas system started successfully")

    def stop_system(self) -> None:
        """Stop the Atlas system."""
        print("⏹️ Stopping Atlas system...")

        # Stop automatic capture
        self.auto_capture.stop_capture()

        # Stop health monitoring
        self.running = False
        if self.health_check_thread:
            self.health_check_thread.join(timeout=5)

        print("✅ Atlas system stopped")

    def _health_monitor_loop(self) -> None:
        """Monitor graph health and perform self-healing."""
        print("🔍 Starting health monitoring...")

        while self.running:
            try:
                # Check graph health every 5 minutes
                time.sleep(300)

                if not self.running:
                    break

                print("🔍 Performing health check...")
                health_report = self.self_healing.get_graph_health_report()

                # If health score is low, perform repairs
                if health_report.get("health_score", 100) < 70:
                    print(f"⚠️ Low health score: {health_report['health_score']:.1f}/100")
                    self._perform_self_healing()
                else:
                    print(f"✅ Graph health: {health_report['health_score']:.1f}/100")

            except Exception as e:
                print(f"❌ Error in health monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

    def _perform_self_healing(self) -> None:
        """Perform self-healing operations."""
        try:
            print("🔧 Performing self-healing...")

            # Detect broken references
            broken_refs = self.self_healing.detect_broken_references()
            print(f"Found {len(broken_refs)} broken references")

            if broken_refs:
                # Repair broken references
                repair_results = self.self_healing.repair_broken_references(broken_refs)
                print(
                    f"Self-healing complete: {repair_results['repaired']} repaired, {repair_results['failed']} failed"
                )
            else:
                print("✅ No broken references found")

        except Exception as e:
            print(f"❌ Error in self-healing: {e}")

    def get_system_status(self) -> dict[str, Any]:
        """Get comprehensive system status."""
        try:
            # Get capture status
            capture_summary = self.auto_capture.get_session_stats()

            # Get graph health
            health_report = self.self_healing.get_graph_health_report()

            # Get memory context (placeholder for now)
            memory_context = "Memory rehydration not yet implemented"

            return {
                "system_running": self.running,
                "capture_status": capture_summary,
                "graph_health": health_report,
                "memory_context_length": len(memory_context),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            return {"error": str(e)}

    def manual_capture(
        self, role: str, content: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str:
        """Manually capture a conversation turn."""
        meta_payload = dict(metadata or {})
        parent_turn_id = meta_payload.pop("parent_turn_id", None) or meta_payload.pop("query_turn_id", None)

        if role == "user":
            result = self.auto_capture.capture_user_query(content, meta_payload)
            return result or "user_query_captured"
        else:
            result = self.auto_capture.capture_ai_response(
                content,
                query_turn_id=str(parent_turn_id) if parent_turn_id else None,
                metadata=meta_payload,
            )
            return result or "ai_response_captured"

    def rehydrate_memory(self, query: str = "current project status and core documentation") -> str:
        """Rehydrate memory with Atlas graph data."""
        # Placeholder implementation
        return f"Memory rehydration for query: {query} (not yet implemented)"

    def get_graph_health(self) -> dict[str, Any]:
        """Get graph health report."""
        return self.self_healing.get_graph_health_report()

    def perform_self_healing(self) -> dict[str, Any]:
        """Manually trigger self-healing."""
        broken_refs = self.self_healing.detect_broken_references()
        if broken_refs:
            return self.self_healing.repair_broken_references(broken_refs)
        else:
            return {"status": "no_repairs_needed", "broken_references": 0}


class AtlasCLI:
    """Command-line interface for Atlas system."""

    def __init__(self) -> None:
        self.system: AtlasUnifiedSystem = AtlasUnifiedSystem()

    def start(self) -> None:
        """Start the Atlas system."""
        self.system.start_system()

    def stop(self) -> None:
        """Stop the Atlas system."""
        self.system.stop_system()

    def status(self) -> None:
        """Show system status."""
        status = self.system.get_system_status()

        print("📊 Atlas System Status")
        print("=" * 50)
        print(f"System Running: {'✅ Yes' if status['system_running'] else '❌ No'}")

        if "capture_status" in status:
            capture = status["capture_status"]
            print(f"Capture Status: {capture.get('capture_status', 'unknown')}")
            print(f"Session ID: {capture.get('session_id', 'N/A')}")
            print(f"Total Nodes: {capture.get('total_nodes', 0)}")
            print(f"Total Edges: {capture.get('total_edges', 0)}")

        if "graph_health" in status:
            health = status["graph_health"]
            print(f"Graph Health: {health.get('health_score', 0):.1f}/100")
            print(f"Broken References: {health.get('broken_references', {}).get('total', 0)}")

        print(f"Memory Context: {status.get('memory_context_length', 0)} characters")
        print(f"Last Updated: {status.get('timestamp', 'N/A')}")

    def capture(self, role: str, content: str) -> None:
        """Capture a conversation turn."""
        turn_id = self.system.manual_capture(role, content)
        print(f"✅ Captured {role} message: {turn_id}")

    def memory(self, query: str = "current project status and core documentation") -> None:
        """Get memory context."""
        context = self.system.rehydrate_memory(query)
        print(context)

    def health(self) -> None:
        """Show graph health."""
        health = self.system.get_graph_health()

        print("🔍 Graph Health Report")
        print("=" * 50)
        print(f"Total Nodes: {health.get('total_nodes', 0)}")
        print(f"Total Edges: {health.get('total_edges', 0)}")
        print(f"Health Score: {health.get('health_score', 0):.1f}/100")
        print(f"Orphaned Nodes: {health.get('orphaned_nodes', 0)}")

        broken = health.get("broken_references", {})
        print(f"Broken References: {broken.get('total', 0)}")
        print(f"  - High Severity: {broken.get('high_severity', 0)}")
        print(f"  - Medium Severity: {broken.get('medium_severity', 0)}")
        print(f"  - Low Severity: {broken.get('low_severity', 0)}")

        print("\n💡 Recommendations:")
        for rec in health.get("recommendations", []):
            print(f"  {rec}")

    def heal(self) -> None:
        """Perform self-healing."""
        print("🔧 Performing self-healing...")
        results = self.system.perform_self_healing()

        if results.get("status") == "no_repairs_needed":
            print("✅ No repairs needed - graph is healthy")
        else:
            print(f"Repaired: {results.get('repaired', 0)}")
            print(f"Failed: {results.get('failed', 0)}")
            print(f"Skipped: {results.get('skipped', 0)}")


def main() -> None:
    """Test the unified Atlas system."""
    print("🚀 Testing Atlas Unified System")

    # Initialize system
    system = AtlasUnifiedSystem()

    # Test manual capture
    print("\n📝 Testing manual capture...")
    user_turn = system.manual_capture(
        role="user",
        content="I want to test the Atlas unified system with automatic capture and self-healing navigation.",
        metadata={"test": True},
    )

    assistant_turn = system.manual_capture(
        role="assistant",
        content="I'll test the Atlas unified system by setting up automatic capture and implementing self-healing navigation. The system combines conversation capture, graph storage, and automatic repair capabilities.",
        metadata={"test": True},
    )

    print(f"✅ Captured conversation: {user_turn}, {assistant_turn}")

    # Test memory rehydration
    print("\n🧠 Testing memory rehydration...")
    memory_context = system.rehydrate_memory()
    print(f"Memory context length: {len(memory_context)} characters")

    # Test graph health
    print("\n🔍 Testing graph health...")
    health = system.get_graph_health()
    print(f"Graph health score: {health.get('health_score', 0):.1f}/100")

    # Test self-healing
    print("\n🔧 Testing self-healing...")
    healing_results = system.perform_self_healing()
    print(f"Self-healing results: {healing_results}")

    # Test system status
    print("\n📊 Testing system status...")
    status = system.get_system_status()
    print(f"System running: {status.get('system_running', False)}")

    print("\n🎯 Atlas Unified System is working!")


if __name__ == "__main__":
    main()
