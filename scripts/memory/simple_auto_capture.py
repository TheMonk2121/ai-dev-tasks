#!/usr/bin/env python3
"""
Simple automatic conversation capture system.
This version is more reliable and doesn't get stuck.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.common.db_dsn import resolve_dsn

# Import our working integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "utilities"))
from cursor_working_integration import CursorWorkingIntegration


class SimpleAutoCapture:
    """Simple automatic conversation capture system."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or resolve_dsn()
        self.session_file: str = os.path.expanduser("~/.cursor_simple_capture.json")
        self.current_integration: CursorWorkingIntegration | None = None
        self.capture_active: bool = False

        print("🚀 Simple Auto Capture System")
        print("=" * 40)

    def start_capture(self: Any):
        """Start automatic conversation capture."""
        if self.capture_active:
            print("⚠️  Capture already active")
            return False

        try:
            print("🎯 Starting conversation capture...")

            # Initialize new integration
            self.current_integration = CursorWorkingIntegration(self.dsn)
            self.capture_active = True

            # Save session info
            self._save_session()

            print("✅ Auto capture started")
            print(f"   Session ID: {self.current_integration.session_id}")
            print(f"   Thread ID: {self.current_integration.thread_id}")
            print(f"   Session file: {self.session_file}")

            return True

        except Exception as e:
            print(f"❌ Error starting capture: {e}")
            return False

    def stop_capture(self: Any):
        """Stop automatic conversation capture."""
        if not self.capture_active:
            print("⚠️  No active capture to stop")
            return False

        try:
            print("🛑 Stopping conversation capture...")

            if self.current_integration:
                # Get final stats
                stats = self.current_integration.get_session_stats()
                print("📊 Final session stats:")
                for key, value in stats.items():
                    print(f"   {key}: {value}")

                # Close session
                self.current_integration.close_session()

            self.capture_active = False
            self.current_integration = None

            # Clear session file
            self._clear_session()

            print("✅ Auto capture stopped")
            return True

        except Exception as e:
            print(f"❌ Error stopping capture: {e}")
            return False

    def capture_query(self, query: str, metadata: dict[str, object] | None = None) -> str | None:
        """Capture a user query."""
        if not self.capture_active or not self.current_integration:
            print("⚠️  Auto capture not active")
            return None

        try:
            return self.current_integration.capture_user_query(query, metadata)
        except Exception as e:
            print(f"❌ Error capturing query: {e}")
            return None

    def capture_response(
        self, response: str, query_turn_id: str | None = None, metadata: dict[str, object] | None = None
    ) -> str | None:
        """Capture an AI response."""
        if not self.capture_active or not self.current_integration:
            print("⚠️  Auto capture not active")
            return None

        try:
            return self.current_integration.capture_ai_response(response, query_turn_id, metadata)
        except Exception as e:
            print(f"❌ Error capturing response: {e}")
            return None

    def get_status(self) -> dict[str, object]:
        """Get current status."""
        if not self.capture_active or not self.current_integration:
            return {"active": False, "message": "No active capture"}

        try:
            stats = self.current_integration.get_session_stats()
            return {
                "active": True,
                "session_id": self.current_integration.session_id,
                "thread_id": self.current_integration.thread_id,
                "stats": stats,
            }
        except Exception as e:
            return {"active": False, "error": str(e)}

    def _save_session(self) -> None:
        """Save session info to file."""
        try:
            if self.current_integration:
                session_data = {
                    "active": True,
                    "session_id": self.current_integration.session_id,
                    "thread_id": self.current_integration.thread_id,
                    "started_at": datetime.now().isoformat(),
                }

                with open(self.session_file, "w") as f:
                    json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Error saving session: {e}")

    def _clear_session(self) -> None:
        """Clear session file."""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"⚠️  Error clearing session: {e}")


def main() -> None:
    """Main function."""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Simple Auto Capture System")
    _: Any = parser.add_argument("--start", action="store_true", help="Start capture")
    _: Any = parser.add_argument("--stop", action="store_true", help="Stop capture")
    _: Any = parser.add_argument("--status", action="store_true", help="Show status")
    _: Any = parser.add_argument("--test", action="store_true", help="Run test capture")

    args: Any = parser.parse_args()

    # Initialize auto capture
    auto_capture = SimpleAutoCapture()

    start: bool = getattr(args, "start", False)
    stop: bool = getattr(args, "stop", False)
    status: bool = getattr(args, "status", False)
    test: bool = getattr(args, "test", False)

    if start:
        success: Any = auto_capture.start_capture()
        if success:
            print("\n💡 To capture conversations, call:")
            print("   auto_capture.capture_query('your question')")
            print("   auto_capture.capture_response('AI response')")
        sys.exit(0 if success else 1)

    elif stop:
        success: Any = auto_capture.stop_capture()
        sys.exit(0 if success else 1)

    elif status:
        status_data: Any = auto_capture.get_status()
        if status_data.get("active", False):
            print("🟢 Capture is ACTIVE")
            print(f"   Session: {status_data.get('session_id', 'Unknown')}")
            print(f"   Thread: {status_data.get('thread_id', 'Unknown')}")
            stats: Any = status_data.get("stats", {})
            if isinstance(stats, dict):
                for key, value in stats.items():
                    print(f"   {key}: {value}")
        else:
            print("🔴 Capture is INACTIVE")
            error: Any = status_data.get("error")
            if error:
                print(f"   Error: {error}")
        sys.exit(0)

    elif test:
        print("🧪 Running test capture...")

        # Start capture
        if not auto_capture.start_capture():
            print("❌ Failed to start capture")
            sys.exit(1)

        # Test conversation
        query_id = auto_capture.capture_query(
            "Test query: How do I set up automatic conversation capture?", {"test": True}
        )

        if query_id:
            response_id = auto_capture.capture_response(
                "Test response: You can set up automatic conversation capture using the SimpleAutoCapture class.",
                query_id,
                {"test": True},
            )

            if response_id:
                print("✅ Test capture successful!")

                # Show status
                status_data = auto_capture.get_status()
                print(f"📊 Status: {status_data}")
            else:
                print("❌ Failed to capture response")
        else:
            print("❌ Failed to capture query")

        # Stop capture
        _: Any = auto_capture.stop_capture()
        sys.exit(0)

    else:
        print("Usage: python simple_auto_capture.py --start|--stop|--status|--test")
        sys.exit(1)


if __name__ == "__main__":
    main()
