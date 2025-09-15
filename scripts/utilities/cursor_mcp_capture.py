#!/usr/bin/env python3
"""
Cursor MCP Capture Integration

This script provides a bridge between Cursor and the MCP server for automatic conversation capture.
It can be called from Cursor's command palette or as a background service.
"""

import argparse
import json
import os
import sys
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.common.db_dsn import resolve_dsn

from .cursor_working_integration import CursorWorkingIntegration


class TypedArgs(argparse.Namespace):
    """Typed argument parser namespace for better type safety."""

    def __init__(self) -> None:
        super().__init__()
        self.capture_turn: list[str] | None = None
        self.capture_query: str | None = None
        self.capture_response: str | None = None
        self.query_turn_id: str | None = None
        self.metadata: str | None = None
        self.stats: bool = False
        self.close: bool = False


class CursorMCPCapture:
    """Bridge between Cursor and MCP server for conversation capture."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn: str = dsn if dsn is not None else resolve_dsn()
        self.integration: CursorWorkingIntegration = CursorWorkingIntegration(self.dsn)
        self.session_file: str = os.path.expanduser("~/.cursor_mcp_session.json")
        self.last_capture: str | None = None

    def capture_conversation_turn(
        self, user_query: str, ai_response: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> dict[str, object]:
        """Capture a complete conversation turn (query + response)."""
        try:
            if not user_query.strip() and not ai_response.strip():
                return {"success": False, "error": "No content to capture"}

            results = {}

            # Capture user query if provided
            if user_query.strip():
                query_turn_id = self.integration.capture_user_query(user_query, metadata or {})
                results["query_turn_id"] = query_turn_id
                print(f"✅ Captured user query: {user_query[:50]}...")

            # Capture AI response if provided
            if ai_response.strip():
                response_turn_id = self.integration.capture_ai_response(
                    ai_response, results.get("query_turn_id"), metadata or {}
                )
                results["response_turn_id"] = response_turn_id
                print(f"✅ Captured AI response: {ai_response[:50]}...")

            # Update session info
            self._update_session_info(results)

            return {
                "success": True,
                "session_id": self.integration.session_id,
                "thread_id": self.integration.thread_id,
                "results": results,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_user_query_only(
        self, query: str, metadata: dict[str, str | int | float | bool | None] | None = None
    ) -> dict[str, object]:
        """Capture only a user query."""
        try:
            turn_id = self.integration.capture_user_query(query, metadata or {})
            self._update_session_info({"query_turn_id": turn_id})

            return {
                "success": True,
                "turn_id": turn_id,
                "session_id": self.integration.session_id,
                "thread_id": self.integration.thread_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def capture_ai_response_only(
        self,
        response: str,
        query_turn_id: str | None = None,
        metadata: dict[str, str | int | float | bool | None] | None = None,
    ) -> dict[str, object]:
        """Capture only an AI response."""
        try:
            turn_id = self.integration.capture_ai_response(response, query_turn_id, metadata or {})
            self._update_session_info({"response_turn_id": turn_id})

            return {
                "success": True,
                "turn_id": turn_id,
                "session_id": self.integration.session_id,
                "thread_id": self.integration.thread_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _update_session_info(self, results: dict[str, object]) -> None:
        """Update session information file."""
        session_data = {
            "last_capture": datetime.now().isoformat(),
            "session_id": self.integration.session_id,
            "thread_id": self.integration.thread_id,
            "last_results": results,
        }

        try:
            with open(self.session_file, "w") as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Could not update session file: {e}")

    def get_session_stats(self) -> dict[str, object]:
        """Get current session statistics."""
        try:
            stats = self.integration.get_session_stats()
            return {
                "success": True,
                "stats": stats,
                "session_id": self.integration.session_id,
                "thread_id": self.integration.thread_id,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def close_session(self) -> None:
        """Close the current session."""
        try:
            self.integration.close_session()
            print("✅ Session closed")
        except Exception as e:
            print(f"⚠️  Error closing session: {e}")


def main() -> None:
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="Cursor MCP Capture Integration")
    _ = parser.add_argument(
        "--capture-turn", nargs=2, metavar=("QUERY", "RESPONSE"), help="Capture a complete conversation turn"
    )
    _ = parser.add_argument("--capture-query", metavar="QUERY", help="Capture only a user query")
    _ = parser.add_argument("--capture-response", metavar="RESPONSE", help="Capture only an AI response")
    _ = parser.add_argument("--query-turn-id", metavar="TURN_ID", help="Query turn ID for response capture")
    _ = parser.add_argument("--metadata", metavar="JSON", help="Metadata as JSON string")
    _ = parser.add_argument("--stats", action="store_true", help="Get session statistics")
    _ = parser.add_argument("--close", action="store_true", help="Close current session")

    args = parser.parse_args(namespace=TypedArgs())

    # Initialize capture system
    capture = CursorMCPCapture()

    try:
        if args.capture_turn:
            query: str = args.capture_turn[0]
            response: str = args.capture_turn[1]
            turn_metadata: dict[str, str | int | float | bool | None] = (
                json.loads(args.metadata) if args.metadata else {}
            )
            result = capture.capture_conversation_turn(query, response, turn_metadata)
            print(json.dumps(result, indent=2))

        elif args.capture_query:
            query_metadata: dict[str, str | int | float | bool | None] = (
                json.loads(args.metadata) if args.metadata else {}
            )
            result = capture.capture_user_query_only(args.capture_query, query_metadata)
            print(json.dumps(result, indent=2))

        elif args.capture_response:
            response_metadata: dict[str, str | int | float | bool | None] = (
                json.loads(args.metadata) if args.metadata else {}
            )
            result = capture.capture_ai_response_only(args.capture_response, args.query_turn_id, response_metadata)
            print(json.dumps(result, indent=2))

        elif args.stats:
            result = capture.get_session_stats()
            print(json.dumps(result, indent=2))

        elif args.close:
            capture.close_session()

        else:
            parser.print_help()

    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
