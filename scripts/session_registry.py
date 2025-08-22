#!/usr/bin/env python3
"""
Session Registry for Scribe System

Manages active Scribe sessions with context tagging and discovery capabilities.
Provides centralized session tracking and context-aware session management.
"""

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set

import psutil


@dataclass
class SessionContext:
    """Represents context tags and metadata for a session."""

    tags: Set[str]
    session_type: str  # brainstorming, implementation, debug, planning
    priority: str  # high, medium, low
    description: Optional[str] = None
    related_sessions: Optional[List[str]] = None


@dataclass
class SessionInfo:
    """Represents a Scribe session with full metadata."""

    backlog_id: str
    pid: int
    start_time: str
    worklog_path: str
    status: str  # active, completed, paused
    context: SessionContext
    last_activity: Optional[str] = None
    idle_timeout: int = 1800  # 30 minutes default


class SessionRegistry:
    """Manages Scribe session registry with context tagging."""

    def __init__(self, registry_path: str = "artifacts/session_registry.json"):
        self.registry_path = Path(registry_path)
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, SessionInfo] = {}
        self.load_registry()

    def load_registry(self) -> None:
        """Load session registry from file."""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r") as f:
                    data = json.load(f)
                    for backlog_id, session_data in data.get("sessions", {}).items():
                        # Convert context data back to SessionContext
                        context_data = session_data.get("context", {})
                        context = SessionContext(
                            tags=set(context_data.get("tags", [])),
                            session_type=context_data.get("session_type", "brainstorming"),
                            priority=context_data.get("priority", "medium"),
                            description=context_data.get("description"),
                            related_sessions=context_data.get("related_sessions"),
                        )

                        session_info = SessionInfo(
                            backlog_id=session_data["backlog_id"],
                            pid=session_data["pid"],
                            start_time=session_data["start_time"],
                            worklog_path=session_data["worklog_path"],
                            status=session_data["status"],
                            context=context,
                            last_activity=session_data.get("last_activity"),
                            idle_timeout=session_data.get("idle_timeout", 1800),
                        )
                        self.sessions[backlog_id] = session_info
            except Exception as e:
                print(f"Warning: Could not load session registry: {e}")

    def save_registry(self) -> None:
        """Save session registry to file."""
        # Convert sessions to serializable format
        data = {
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "total_sessions": len(self.sessions),
            "active_sessions": len([s for s in self.sessions.values() if s.status == "active"]),
            "sessions": {},
        }

        for backlog_id, session in self.sessions.items():
            session_data = asdict(session)
            # Convert set to list for JSON serialization
            session_data["context"]["tags"] = list(session.context.tags)
            data["sessions"][backlog_id] = session_data

        with open(self.registry_path, "w") as f:
            json.dump(data, f, indent=2)

    def register_session(
        self,
        backlog_id: str,
        pid: int,
        worklog_path: str,
        session_type: str = "brainstorming",
        priority: str = "medium",
        tags: Optional[List[str]] = None,
    ) -> None:
        """Register a new Scribe session."""
        context = SessionContext(tags=set(tags or []), session_type=session_type, priority=priority)

        session_info = SessionInfo(
            backlog_id=backlog_id,
            pid=pid,
            start_time=datetime.now(timezone.utc).isoformat(),
            worklog_path=worklog_path,
            status="active",
            context=context,
        )

        self.sessions[backlog_id] = session_info
        self.save_registry()
        print(f"✅ Registered session {backlog_id} (PID: {pid})")

    def update_session_status(self, backlog_id: str, status: str) -> None:
        """Update session status."""
        if backlog_id in self.sessions:
            self.sessions[backlog_id].status = status
            if status == "completed":
                self.sessions[backlog_id].last_activity = datetime.now(timezone.utc).isoformat()
            self.save_registry()
            print(f"✅ Updated session {backlog_id} status to {status}")
        else:
            print(f"⚠️ Session {backlog_id} not found in registry")

    def add_context_tags(self, backlog_id: str, tags: List[str]) -> None:
        """Add context tags to a session."""
        if backlog_id in self.sessions:
            self.sessions[backlog_id].context.tags.update(tags)
            self.save_registry()
            print(f"✅ Added tags {tags} to session {backlog_id}")
        else:
            print(f"⚠️ Session {backlog_id} not found in registry")

    def remove_context_tags(self, backlog_id: str, tags: List[str]) -> None:
        """Remove context tags from a session."""
        if backlog_id in self.sessions:
            self.sessions[backlog_id].context.tags.difference_update(tags)
            self.save_registry()
            print(f"✅ Removed tags {tags} from session {backlog_id}")
        else:
            print(f"⚠️ Session {backlog_id} not found in registry")

    def get_active_sessions(self) -> List[SessionInfo]:
        """Get all active sessions."""
        return [s for s in self.sessions.values() if s.status == "active"]

    def get_sessions_by_context(self, tags: List[str]) -> List[SessionInfo]:
        """Get sessions that match any of the given context tags."""
        matching_sessions = []
        for session in self.sessions.values():
            if session.context.tags.intersection(set(tags)):
                matching_sessions.append(session)
        return matching_sessions

    def get_session_info(self, backlog_id: str) -> Optional[SessionInfo]:
        """Get detailed information about a specific session."""
        return self.sessions.get(backlog_id)

    def cleanup_completed_sessions(self) -> None:
        """Remove completed sessions older than 7 days."""
        cutoff_time = datetime.now(timezone.utc).timestamp() - (7 * 24 * 3600)
        to_remove = []

        for backlog_id, session in self.sessions.items():
            if session.status == "completed":
                try:
                    session_time = datetime.fromisoformat(session.start_time.replace("Z", "+00:00")).timestamp()
                    if session_time < cutoff_time:
                        to_remove.append(backlog_id)
                except Exception:
                    pass

        for backlog_id in to_remove:
            del self.sessions[backlog_id]

        if to_remove:
            self.save_registry()
            print(f"🧹 Cleaned up {len(to_remove)} old completed sessions")

    def validate_processes(self) -> None:
        """Validate that registered PIDs are still running."""
        for backlog_id, session in list(self.sessions.items()):
            if session.status == "active":
                try:
                    process = psutil.Process(session.pid)
                    if not process.is_running():
                        print(f"⚠️ Session {backlog_id} PID {session.pid} is not running")
                        session.status = "orphaned"
                except psutil.NoSuchProcess:
                    print(f"⚠️ Session {backlog_id} PID {session.pid} not found")
                    session.status = "orphaned"

        self.save_registry()

    def list_sessions(self, show_context: bool = True, status_filter: Optional[str] = None) -> None:
        """List all sessions with optional filtering."""
        sessions = self.sessions.values()
        if status_filter:
            sessions = [s for s in sessions if s.status == status_filter]

        if not sessions:
            print("No sessions found.")
            return

        print(f"\n📊 Session Registry ({len(sessions)} sessions)")
        print("=" * 80)

        for session in sorted(sessions, key=lambda s: s.start_time, reverse=True):
            print(f"\n🔹 {session.backlog_id}")
            print(f"   Status: {session.status}")
            print(f"   PID: {session.pid}")
            print(f"   Started: {session.start_time}")
            print(f"   Type: {session.context.session_type}")
            print(f"   Priority: {session.context.priority}")

            if show_context and session.context.tags:
                print(f"   Context Tags: {', '.join(sorted(session.context.tags))}")

            if session.context.description:
                print(f"   Description: {session.context.description}")

            if session.last_activity:
                print(f"   Last Activity: {session.last_activity}")


def main():
    """CLI interface for session registry management."""
    parser = argparse.ArgumentParser(description="Scribe Session Registry Manager")
    parser.add_argument(
        "command", choices=["list", "register", "update", "tag", "untag", "cleanup", "validate", "info"]
    )
    parser.add_argument("--backlog-id", help="Backlog ID for session operations")
    parser.add_argument("--pid", type=int, help="Process ID for session registration")
    parser.add_argument("--worklog-path", help="Path to worklog file")
    parser.add_argument("--status", choices=["active", "completed", "paused"], help="Session status")
    parser.add_argument("--tags", nargs="+", help="Context tags")
    parser.add_argument(
        "--session-type",
        default="brainstorming",
        choices=["brainstorming", "implementation", "debug", "planning"],
        help="Type of session",
    )
    parser.add_argument("--priority", default="medium", choices=["high", "medium", "low"], help="Session priority")
    parser.add_argument("--no-context", action="store_true", help="Hide context tags in listing")
    parser.add_argument(
        "--status-filter", choices=["active", "completed", "paused", "orphaned"], help="Filter sessions by status"
    )

    args = parser.parse_args()

    registry = SessionRegistry()

    if args.command == "list":
        registry.list_sessions(show_context=not args.no_context, status_filter=args.status_filter)

    elif args.command == "register":
        if not all([args.backlog_id, args.pid, args.worklog_path]):
            print("❌ --backlog-id, --pid, and --worklog-path are required for registration")
            return
        registry.register_session(
            args.backlog_id,
            args.pid,
            args.worklog_path,
            session_type=args.session_type,
            priority=args.priority,
            tags=args.tags,
        )

    elif args.command == "update":
        if not all([args.backlog_id, args.status]):
            print("❌ --backlog-id and --status are required for update")
            return
        registry.update_session_status(args.backlog_id, args.status)

    elif args.command == "tag":
        if not all([args.backlog_id, args.tags]):
            print("❌ --backlog-id and --tags are required for tagging")
            return
        registry.add_context_tags(args.backlog_id, args.tags)

    elif args.command == "untag":
        if not all([args.backlog_id, args.tags]):
            print("❌ --backlog-id and --tags are required for untagging")
            return
        registry.remove_context_tags(args.backlog_id, args.tags)

    elif args.command == "cleanup":
        registry.cleanup_completed_sessions()

    elif args.command == "validate":
        registry.validate_processes()

    elif args.command == "info":
        if not args.backlog_id:
            print("❌ --backlog-id is required for info")
            return
        session = registry.get_session_info(args.backlog_id)
        if session:
            print(f"\n📋 Session Info: {args.backlog_id}")
            print("=" * 50)
            print(f"Status: {session.status}")
            print(f"PID: {session.pid}")
            print(f"Started: {session.start_time}")
            print(f"Type: {session.context.session_type}")
            print(f"Priority: {session.context.priority}")
            print(f"Tags: {', '.join(sorted(session.context.tags))}")
            print(f"Worklog: {session.worklog_path}")
            if session.last_activity:
                print(f"Last Activity: {session.last_activity}")
        else:
            print(f"❌ Session {args.backlog_id} not found")


if __name__ == "__main__":
    main()
