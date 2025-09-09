#!/usr/bin/env python3
"""
Session Context Integration for Memory Rehydration

Enhances memory rehydration with session registry data to provide
rich context about active Scribe sessions and their context tags.
"""

import json
from datetime import datetime, timezone, UTC
from pathlib import Path


class SessionContextIntegrator:
    """Integrates session registry data into memory rehydration."""

    def __init__(self, registry_path: str = "artifacts/session_registry.json"):
        self.registry_path = Path(registry_path)

    def get_active_sessions_context(self) -> dict:
        """Get context about all active Scribe sessions."""
        if not self.registry_path.exists():
            return {"active_sessions": [], "session_count": 0}

        try:
            with open(self.registry_path) as f:
                data = json.load(f)

            active_sessions = []
            for backlog_id, session_data in data.get("sessions", {}).items():
                if session_data.get("status") == "active":
                    context_data = session_data.get("context", {})
                    active_sessions.append(
                        {
                            "backlog_id": backlog_id,
                            "pid": session_data.get("pid"),
                            "start_time": session_data.get("start_time"),
                            "session_type": context_data.get("session_type", "brainstorming"),
                            "priority": context_data.get("priority", "medium"),
                            "tags": context_data.get("tags", []),
                            "worklog_path": session_data.get("worklog_path"),
                            "description": context_data.get("description"),
                        }
                    )

            return {
                "active_sessions": active_sessions,
                "session_count": len(active_sessions),
                "last_updated": data.get("last_updated"),
            }
        except Exception as e:
            return {"active_sessions": [], "session_count": 0, "error": str(e)}

    def get_sessions_by_context(self, tags: list[str]) -> dict:
        """Get sessions that match specific context tags."""
        if not self.registry_path.exists():
            return {"matching_sessions": [], "count": 0}

        try:
            with open(self.registry_path) as f:
                data = json.load(f)

            matching_sessions = []
            for backlog_id, session_data in data.get("sessions", {}).items():
                context_data = session_data.get("context", {})
                session_tags = set(context_data.get("tags", []))
                if session_tags.intersection(set(tags)):
                    matching_sessions.append(
                        {
                            "backlog_id": backlog_id,
                            "status": session_data.get("status"),
                            "session_type": context_data.get("session_type"),
                            "priority": context_data.get("priority"),
                            "tags": list(session_tags),
                            "start_time": session_data.get("start_time"),
                        }
                    )

            return {"matching_sessions": matching_sessions, "count": len(matching_sessions), "search_tags": tags}
        except Exception as e:
            return {"matching_sessions": [], "count": 0, "error": str(e)}

    def get_session_summary(self) -> str:
        """Generate a human-readable summary of active sessions."""
        context = self.get_active_sessions_context()

        if context.get("error"):
            return f"⚠️ Session registry error: {context['error']}"

        if context["session_count"] == 0:
            return "📝 No active Scribe sessions"

        summary_lines = [f"📊 Active Scribe Sessions ({context['session_count']})"]

        for session in context["active_sessions"]:
            tags_str = ", ".join(session["tags"]) if session["tags"] else "none"
            summary_lines.append(f"  • {session['backlog_id']} ({session['session_type']}, {session['priority']})")
            summary_lines.append(f"    Tags: {tags_str}")

        if context.get("last_updated"):
            summary_lines.append(f"\nLast updated: {context['last_updated']}")

        return "\n".join(summary_lines)

    def enhance_memory_context(self, base_context: dict) -> dict:
        """Enhance existing memory context with session registry data."""
        session_context = self.get_active_sessions_context()

        enhanced_context = base_context.copy()
        enhanced_context["scribe_sessions"] = session_context
        enhanced_context["session_summary"] = self.get_session_summary()

        return enhanced_context


def integrate_with_memory_rehydrator():
    """Integration function for memory rehydrator."""
    integrator = SessionContextIntegrator()

    # Get session context
    session_context = integrator.get_active_sessions_context()
    session_summary = integrator.get_session_summary()

    # Return enhanced context
    return {
        "session_registry": session_context,
        "session_summary": session_summary,
        "integration_timestamp": datetime.now(UTC).isoformat(),
    }


def main():
    """CLI interface for session context integration."""
    import argparse

    parser = argparse.ArgumentParser(description="Session Context Integration")
    parser.add_argument("command", choices=["summary", "active", "context", "integrate"])
    parser.add_argument("--tags", nargs="+", help="Context tags to search for")

    args = parser.parse_args()

    integrator = SessionContextIntegrator()

    if args.command == "summary":
        print(integrator.get_session_summary())

    elif args.command == "active":
        context = integrator.get_active_sessions_context()
        print(json.dumps(context, indent=2))

    elif args.command == "context":
        if not args.tags:
            print("❌ --tags required for context search")
            return
        context = integrator.get_sessions_by_context(args.tags)
        print(json.dumps(context, indent=2))

    elif args.command == "integrate":
        integration_data = integrate_with_memory_rehydrator()
        print(json.dumps(integration_data, indent=2))


if __name__ == "__main__":
    main()
