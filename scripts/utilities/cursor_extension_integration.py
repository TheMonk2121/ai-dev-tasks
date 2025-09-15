#!/usr/bin/env python3
"""
Cursor Extension Integration
This script provides a simple API for Cursor to call for conversation capture.
"""

import json
import os
import sys
from datetime import datetime
from typing import Any

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
# Import our working integration
from src.common.db_dsn import resolve_dsn

from .cursor_working_integration import CursorWorkingIntegration


class CursorExtensionAPI:
    """Simple API for Cursor extension integration."""

    dsn: str

    def __init__(self, dsn: str | None = None) -> None:
        resolved_dsn = resolve_dsn()
        if dsn is not None:
            self.dsn = dsn
        else:
            self.dsn = resolved_dsn
        self.session_file: str = os.path.expanduser("~/.cursor_active_session.json")
        self.current_integration: CursorWorkingIntegration | None = None
        self._load_active_session()

    def _load_active_session(self) -> None:
        """Load active session from file."""
        try:
            if os.path.exists(self.session_file):
                with open(self.session_file) as f:
                    session_data = json.load(f)

                if session_data.get("active", False):
                    # Recreate integration with existing session
                    self.current_integration = CursorWorkingIntegration(self.dsn)
                    self.current_integration.session_id = session_data["session_id"]
                    self.current_integration.thread_id = session_data["thread_id"]
        except Exception as e:
            print(f"⚠️  Error loading active session: {e}")

    def _save_active_session(self) -> None:
        """Save active session to file."""
        try:
            if self.current_integration:
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
            print(f"⚠️  Error saving active session: {e}")

    def start_session(self) -> dict[str, Any]:
        """Start a new conversation session."""
        try:
            # Initialize new integration
            self.current_integration = CursorWorkingIntegration(self.dsn)

            # Save session
            self._save_active_session()

            return {
                "success": True,
                "session_id": self.current_integration.session_id,
                "thread_id": self.current_integration.thread_id,
                "message": "Session started successfully",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_query(self, query: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        """Capture a user query."""
        try:
            if not self.current_integration:
                # Auto-start session if none exists
                result = self.start_session()
                if not result["success"]:
                    return result

            turn_id = self.current_integration.capture_user_query(query, metadata)

            if turn_id:
                return {"success": True, "turn_id": turn_id, "message": "Query captured successfully"}
            else:
                return {"success": False, "error": "Failed to capture query"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_response(
        self, response: str, query_turn_id: str | None = None, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Capture an AI response."""
        try:
            if not self.current_integration:
                return {"success": False, "error": "No active session"}

            turn_id = self.current_integration.capture_ai_response(response, query_turn_id, metadata)

            if turn_id:
                return {"success": True, "turn_id": turn_id, "message": "Response captured successfully"}
            else:
                return {"success": False, "error": "Failed to capture response"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_session_stats(self) -> dict[str, Any]:
        """Get current session statistics."""
        try:
            if not self.current_integration:
                return {"success": False, "error": "No active session"}

            stats = self.current_integration.get_session_stats()
            return {"success": True, "stats": stats}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def end_session(self) -> dict[str, Any]:
        """End the current session."""
        try:
            if not self.current_integration:
                return {"success": False, "error": "No active session"}

            # Get final stats
            stats = self.current_integration.get_session_stats()

            # Close session
            self.current_integration.close_session()

            # Clear current integration
            self.current_integration = None
            self._save_active_session()

            return {"success": True, "final_stats": stats, "message": "Session ended successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main() -> None:
    """Main function for testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor Extension Integration API")
    _ = parser.add_argument("--start", action="store_true", help="Start new session")
    _ = parser.add_argument("--query", type=str, help="Capture a query")
    _ = parser.add_argument("--response", type=str, help="Capture a response")
    _ = parser.add_argument("--stats", action="store_true", help="Get session stats")
    _ = parser.add_argument("--end", action="store_true", help="End current session")

    args = parser.parse_args()

    # Initialize API
    api = CursorExtensionAPI()

    if args.start:
        result = api.start_session()
        print(json.dumps(result, indent=2))
    elif args.query:
        result = api.capture_query(args.query)
        print(json.dumps(result, indent=2))
    elif args.response:
        result = api.capture_response(args.response)
        print(json.dumps(result, indent=2))
    elif args.stats:
        result = api.get_session_stats()
        print(json.dumps(result, indent=2))
    elif args.end:
        result = api.end_session()
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python cursor_extension_integration.py --start|--query 'text'|--response 'text'|--stats|--end")


if __name__ == "__main__":
    main()
