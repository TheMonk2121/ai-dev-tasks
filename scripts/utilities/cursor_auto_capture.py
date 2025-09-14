#!/usr/bin/env python3
"""
Automatic conversation capture system for Cursor AI.
This script automatically captures all conversations without manual intervention.
"""

import json
import os
import signal
import sys
from datetime import datetime
from types import FrameType
from typing import cast

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))
from common.db_dsn import resolve_dsn

# Import our working integration
from .cursor_working_integration import CursorWorkingIntegration


class CursorAutoCapture:
    """Automatic conversation capture system."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = cast(str, dsn or resolve_dsn())
        self.current_integration: CursorWorkingIntegration | None = None
        self.capture_active: bool = False
        self.session_file: str = os.path.expanduser("~/.cursor_auto_capture.json")

        print("🚀 Cursor Auto Capture System")
        print("=" * 50)

        # Load existing session if available
        self._load_session()

        # Set up signal handlers for graceful shutdown
        _ = signal.signal(signal.SIGINT, self._signal_handler)
        _ = signal.signal(signal.SIGTERM, self._signal_handler)

    def _load_session(self) -> None:
        """Load existing session from file."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file) as f:
                    session_data = cast(dict[str, object], json.load(f))

                if session_data.get("active", False):  # type: ignore[arg-type]
                    session_id = str(session_data.get("session_id", ""))
                    thread_id = str(session_data.get("thread_id", ""))
                    print(f"📂 Found active session: {session_id}")
                    # Recreate integration with existing session
                    self.current_integration = CursorWorkingIntegration(self.dsn)
                    self.current_integration.session_id = session_id
                    self.current_integration.thread_id = thread_id
                    self.capture_active = True
                else:
                    print("📂 No active session found")
            else:
                print("📂 No session file found")
        except Exception as e:
            print(f"⚠️  Error loading session: {e}")

    def _save_session(self) -> None:
        """Save current session to file."""
        try:
            if self.current_integration and self.capture_active:
                session_data = {
                    "active": True,
                    "session_id": self.current_integration.session_id,
                    "thread_id": self.current_integration.thread_id,
                    "last_updated": datetime.now().isoformat(),
                }

                with open(self.session_file, "w") as f:
                    json.dump(session_data, f, indent=2)
            else:
                # Clear session file if no active session
                if os.path.exists(self.session_file):
                    os.remove(self.session_file)
        except Exception as e:
            print(f"⚠️  Error saving session: {e}")

    def start_capture(self) -> None:
        """Start automatic conversation capture."""
        if self.capture_active:
            print("⚠️  Capture already active")
            return

        print("🎯 Starting automatic conversation capture...")

        # Initialize new integration
        self.current_integration = CursorWorkingIntegration(self.dsn)
        self.capture_active = True

        # Save session
        self._save_session()

        print("✅ Auto capture started")
        print(f"   Session ID: {self.current_integration.session_id}")
        print(f"   Thread ID: {self.current_integration.thread_id}")
        print(f"   Session file: {self.session_file}")
        print("\n💡 The system is now automatically capturing all conversations!")
        print("   Press Ctrl+C to stop capture")

    def stop_capture(self) -> None:
        """Stop automatic conversation capture."""
        if not self.capture_active:
            print("⚠️  No active capture to stop")
            return

        print("🛑 Stopping automatic conversation capture...")

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
        self._save_session()

        print("✅ Auto capture stopped")

    def capture_user_query(
        self, query: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str | None:
        """Capture a user query (called by external systems)."""
        if not self.capture_active or not self.current_integration:
            print("⚠️  Auto capture not active")
            return None

        return self.current_integration.capture_user_query(query, metadata)

    def capture_ai_response(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> str | None:
        """Capture an AI response (called by external systems)."""
        if not self.capture_active or not self.current_integration:
            print("⚠️  Auto capture not active")
            return None

        return self.current_integration.capture_ai_response(response, query_turn_id, metadata)

    def get_session_stats(self) -> dict[str, str | int | float | bool | None]:
        """Get current session statistics."""
        if not self.capture_active or not self.current_integration:
            return {"error": "No active session"}

        return self.current_integration.get_session_stats()

    def _signal_handler(self, signum: int, _frame: FrameType | None) -> None:
        """Handle shutdown signals."""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.stop_capture()
        sys.exit(0)

    def run_interactive(self) -> None:
        """Run in interactive mode for testing."""
        print("🎮 Interactive Mode - Testing Auto Capture")
        print("=" * 50)

        self.start_capture()

        try:
            while True:
                print("\n📝 Enter a test query (or 'quit' to stop):")
                query = input("> ").strip()

                if query.lower() in ["quit", "exit", "stop"]:
                    break

                if query:
                    # Capture user query
                    query_id = self.capture_user_query(query, {"test": True})

                    if query_id:
                        # Simulate AI response
                        response = f"Test response to: {query}"
                        _ = self.capture_ai_response(response, query_id, {"test": True})

                        print(f"✅ Captured: {query[:50]}...")

                        # Show stats
                        stats = self.get_session_stats()
                        print(f"   Messages: {stats.get('message_count', 0)}")

        except KeyboardInterrupt:
            pass
        finally:
            self.stop_capture()


def main() -> None:
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Auto Capture System")
    _ = parser.add_argument("--start", action="store_true", help="Start auto capture")
    _ = parser.add_argument("--stop", action="store_true", help="Stop auto capture")
    _ = parser.add_argument("--status", action="store_true", help="Show status")
    _ = parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")

    args = parser.parse_args()

    # Initialize auto capture
    auto_capture = CursorAutoCapture()

    start: bool = getattr(args, "start", False)
    stop: bool = getattr(args, "stop", False)
    status: bool = getattr(args, "status", False)
    interactive: bool = getattr(args, "interactive", False)

    if start:
        auto_capture.start_capture()
    elif stop:
        auto_capture.stop_capture()
    elif status:
        if auto_capture.capture_active:
            stats = auto_capture.get_session_stats()
            print("🟢 Auto capture is ACTIVE")
            print(f"   Session: {stats.get('session_id', 'Unknown')}")
            print(f"   Messages: {stats.get('message_count', 0)}")
        else:
            print("🔴 Auto capture is INACTIVE")
    elif interactive:
        auto_capture.run_interactive()
    else:
        print("Usage: python cursor_auto_capture.py --start|--stop|--status|--interactive")
        print("\nCommands:")
        print("  --start      Start automatic conversation capture")
        print("  --stop       Stop automatic conversation capture")
        print("  --status     Show current capture status")
        print("  --interactive Run in interactive test mode")


if __name__ == "__main__":
    main()
