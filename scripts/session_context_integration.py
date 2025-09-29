#!/usr/bin/env python3
"""
Session Context Integration for Memory Rehydration

Provides integration between session registry and memory rehydration systems.
Enhances memory context with active session information.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from scripts.utilities.session_registry import (
    SessionRegistry,  # type: ignore[import-untyped]
)


class SessionContextIntegrator:
    """Integrates session registry with memory rehydration systems."""

    def __init__(self, registry_path: str = "artifacts/session_registry.json"):
        """Initialize the integrator with a session registry."""
        self.registry: SessionRegistry = SessionRegistry(registry_path=registry_path)

    def get_active_sessions_context(self) -> dict[str, Any]:
        """Get context information for all active sessions."""
        active_sessions = self.registry.get_active_sessions()
        
        return {
            "session_count": len(active_sessions),
            "active_sessions": [
                {
                    "backlog_id": session.backlog_id,
                    "pid": session.pid,
                    "start_time": session.start_time,
                    "worklog_path": session.worklog_path,
                    "context": {
                        "tags": list(session.context.tags),
                        "session_type": session.context.session_type,
                        "priority": session.context.priority,
                        "description": session.context.description,
                    }
                }
                for session in active_sessions
            ]
        }

    def get_sessions_by_context(self, tags: list[str]) -> dict[str, Any]:
        """Get sessions matching specific context tags."""
        matching_sessions = self.registry.get_sessions_by_context(tags)
        
        return {
            "count": len(matching_sessions),
            "matching_sessions": [
                {
                    "backlog_id": session.backlog_id,
                    "pid": session.pid,
                    "start_time": session.start_time,
                    "worklog_path": session.worklog_path,
                    "context": {
                        "tags": list(session.context.tags),
                        "session_type": session.context.session_type,
                        "priority": session.context.priority,
                        "description": session.context.description,
                    }
                }
                for session in matching_sessions
            ]
        }

    def get_session_summary(self) -> str:
        """Generate a human-readable summary of active sessions."""
        active_sessions = self.registry.get_active_sessions()
        
        if not active_sessions:
            return "No active Scribe sessions"
        
        summary_lines = [f"Active Scribe Sessions ({len(active_sessions)})"]
        summary_lines.append("=" * 50)
        
        for session in active_sessions:
            tags_str = ", ".join(sorted(session.context.tags))
            summary_lines.append(
                f"• {session.backlog_id} ({session.context.session_type}, {session.context.priority})"
            )
            summary_lines.append(f"  Tags: {tags_str}")
            summary_lines.append(f"  PID: {session.pid}, Started: {session.start_time}")
            summary_lines.append("")
        
        return "\n".join(summary_lines)

    def enhance_memory_context(self, base_context: dict[str, Any]) -> dict[str, Any]:
        """Enhance memory context with session information."""
        enhanced_context = base_context.copy()
        
        # Add session registry information
        enhanced_context["scribe_sessions"] = self.get_active_sessions_context()
        enhanced_context["session_summary"] = self.get_session_summary()
        enhanced_context["integration_timestamp"] = datetime.now(timezone.utc).isoformat()
        
        return enhanced_context


def integrate_with_memory_rehydrator() -> dict[str, Any]:
    """Integration point for memory rehydration systems."""
    integrator = SessionContextIntegrator()
    
    return {
        "session_registry": integrator.get_active_sessions_context(),
        "session_summary": integrator.get_session_summary(),
        "integration_timestamp": datetime.now(timezone.utc).isoformat(),
    }
