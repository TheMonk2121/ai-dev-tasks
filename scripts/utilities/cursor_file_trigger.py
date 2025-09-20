#!/usr/bin/env python3
"""
Cursor File Trigger System
A simple, reliable automatic conversation capture system using file triggers.
"""

import hashlib
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from src.common.db_dsn import resolve_dsn

# Import our working integration
from .cursor_working_integration import CursorWorkingIntegration


class CursorFileTrigger:
    """File-based trigger system for automatic conversation capture."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn or resolve_dsn()
        self.trigger_dir: Path = Path.home() / ".cursor_triggers"
        self.trigger_dir.mkdir(exist_ok=True)
        self.session_file: Path = self.trigger_dir / "active_session.json"
        self.current_integration: CursorWorkingIntegration | None = None

        print("🚀 Cursor File Trigger System")
        print("=" * 40)

    def start_session(self, session_name: str | None = None) -> bool:
        """Start a new conversation session."""
        try:
            print("🎯 Starting new conversation session...")

            # Initialize integration
            self.current_integration: Any = CursorWorkingIntegration(self.dsn)

            # Save session info
            session_data = {
                "active": True,
                "session_id": self.current_integration.session_id,
                "thread_id": self.current_integration.thread_id,
                "started_at": datetime.now().isoformat(),
                "session_name": session_name or f"Session {datetime.now().strftime('%H:%M')}",
            }

            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=2)

            print(f"✅ Session started: {self.current_integration.session_id}")
            return True

        except Exception as e:
            print(f"❌ Error starting session: {e}")
            return False

    def capture_query(
        self, query: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> str | None:
        """Capture a user query."""
        try:
            # Load session if not active
            if not self.current_integration:
                self._load_session()

            if not self.current_integration:
                print("⚠️  No active session, starting new one...")
                _: Any = self.start_session()

            # Capture query
            turn_id = self.current_integration.capture_user_query(query, metadata)

            if turn_id:
                print(f"✅ Captured query: {query[:50]}...")
                self._save_trigger("query", query, turn_id)

            return turn_id

        except Exception as e:
            print(f"❌ Error capturing query: {e}")
            return None

    def capture_response(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> str | None:
        """Capture an AI response."""
        try:
            # Load session if not active
            if not self.current_integration:
                self._load_session()

            if not self.current_integration:
                print("⚠️  No active session, starting new one...")
                _: Any = self.start_session()

            # Capture response
            turn_id = self.current_integration.capture_ai_response(response, query_turn_id, metadata)

            if turn_id:
                print(f"✅ Captured response: {response[:50]}...")
                self._save_trigger("response", response, turn_id)

            return turn_id

        except Exception as e:
            print(f"❌ Error capturing response: {e}")
            return None

    def end_session(self) -> bool:
        """End the current session."""
        try:
            if not self.current_integration:
                print("⚠️  No active session to end")
                return False

            # Get final stats
            stats = self.current_integration.get_session_stats()
            print("📊 Final session stats:")
            for key, value in stats.items():
                print(f"   {key}: {value}")

            # Close session
            self.current_integration.close_session()
            self.current_integration: Any = None

            # Clear session file
            if self.session_file.exists():
                self.session_file.unlink()

            print("✅ Session ended")
            return True

        except Exception as e:
            print(f"❌ Error ending session: {e}")
            return False

    def _load_session(self) -> None:
        """Load active session from file."""
        try:
            if self.session_file.exists():
                with open(self.session_file) as f:
                    session_data: Any = json.load(f)

                if session_data.get("active", False):  # type: ignore[arg-type]
                    # Recreate integration with existing session
                    self.current_integration: Any = CursorWorkingIntegration(self.dsn)
                    self.current_integration.session_id = str(session_data.get("session_id", ""))
                    self.current_integration.thread_id = str(session_data.get("thread_id", ""))
                    print(f"📂 Loaded session: {session_data['session_id']}")
        except Exception as e:
            print(f"⚠️  Error loading session: {e}")

    def _save_trigger(self, trigger_type: str, content: str, turn_id: str) -> None:
        """Save trigger file for external monitoring."""
        try:
            trigger_data = {
                "type": trigger_type,
                "content": content,
                "turn_id": turn_id,
                "timestamp": datetime.now().isoformat(),
                "session_id": self.current_integration.session_id if self.current_integration else None,
            }

            # Create unique filename
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            trigger_file = self.trigger_dir / f"{trigger_type}_{content_hash}_{int(time.time())}.json"

            with open(trigger_file, "w") as f:
                json.dump(trigger_data, f, indent=2)

        except Exception as e:
            print(f"⚠️  Error saving trigger: {e}")

    def get_status(self) -> dict[str, object]:
        """Get current status."""
        try:
            if not self.current_integration:
                self._load_session()

            if not self.current_integration:
                return {"active": False, "message": "No active session"}

            stats = self.current_integration.get_session_stats()
            return {
                "active": True,
                "session_id": self.current_integration.session_id,
                "thread_id": self.current_integration.thread_id,
                "stats": stats,
            }
        except Exception as e:
            return {"active": False, "error": str(e)}


def main() -> None:
    """Main function."""
    import argparse

    parser: Any = argparse.ArgumentParser(description="Cursor File Trigger System")
    _: Any = parser.add_argument("--start", action="store_true", help="Start new session")
    _: Any = parser.add_argument("--query", type=str, help="Capture a query")
    _: Any = parser.add_argument("--response", type=str, help="Capture a response")
    _: Any = parser.add_argument("--end", action="store_true", help="End current session")
    _: Any = parser.add_argument("--status", action="store_true", help="Show status")
    _: Any = parser.add_argument("--test", action="store_true", help="Run test")

    args: Any = parser.parse_args()

    trigger = CursorFileTrigger()

    start: bool = getattr(args, "start", False)
    query: str | None = getattr(args, "query", None)
    response: str | None = getattr(args, "response", None)
    end: bool = getattr(args, "end", False)
    status: bool = getattr(args, "status", False)
    test: bool = getattr(args, "test", False)

    if start:
        success: Any = trigger.start_session()
        sys.exit(0 if success else 1)
    elif query:
        turn_id: Any = trigger.capture_query(query)
        sys.exit(0 if turn_id else 1)
    elif response:
        turn_id: Any = trigger.capture_response(response)
        sys.exit(0 if turn_id else 1)
    elif end:
        success: Any = trigger.end_session()
        sys.exit(0 if success else 1)
    elif status:
        status_data: Any = trigger.get_status()
        if status_data.get("active", False):
            print("🟢 Session is ACTIVE")
            print(f"   Session: {status_data.get('session_id', 'Unknown')}")
            print(f"   Thread: {status_data.get('thread_id', 'Unknown')}")
        else:
            print("🔴 Session is INACTIVE")
            message: Any = status_data.get("message")
            if message:
                print(f"   {message}")
        sys.exit(0)
    elif test:
        print("🧪 Running test...")

        # Start session
        if not trigger.start_session("Test Session"):
            print("❌ Failed to start session")
            sys.exit(1)

        # Test conversation
        query_id = trigger.capture_query("Test query: How does automatic capture work?")
        if query_id:
            response_id = trigger.capture_response(
                "Test response: It works by capturing queries and responses automatically.", query_id
            )
            if response_id:
                print("✅ Test successful!")
            else:
                print("❌ Failed to capture response")
        else:
            print("❌ Failed to capture query")

        # End session
        _: Any = trigger.end_session()
        sys.exit(0)
    else:
        print("Usage: python cursor_file_trigger.py --start|--query 'text'|--response 'text'|--end|--status|--test")
        sys.exit(1)


if __name__ == "__main__":
    main()
