#!/usr/bin/env python3
"""
Scribe Context Provider for DSPy Roles

This module provides real-time session data integration with DSPy roles,
enabling them to access live project context and progress information.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScribeContextProvider:
    """
    Provides real-time session data and integrates with existing ModelSwitcher.

    This class fetches live project context from Scribe and makes it available
    to DSPy roles for better decision-making and strategic planning.
    """

    def __init__(self, project_root: Path | None = None):
        """
        Initialize the Scribe Context Provider.

        Args:
            project_root: Path to the project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self.session_registry_path = self.project_root / "artifacts" / "session_registry.json"
        self.worklogs_path = self.project_root / "artifacts" / "worklogs"

        # Ensure directories exist
        self.worklogs_path.mkdir(parents=True, exist_ok=True)

    def fetch_scribe_context(self) -> dict[str, Any]:
        """
        Fetches real-time session data from the Scribe system.

        Returns:
            dict: Real-time session data including active sessions, progress, and context
        """
        try:
            context = {
                "active_sessions": self._get_active_sessions(),
                "recent_worklogs": self._get_recent_worklogs(),
                "session_registry": self._get_session_registry(),
                "current_branch": self._get_current_branch(),
                "recent_changes": self._get_recent_changes(),
                "timestamp": datetime.now().isoformat(),
            }
            return context
        except Exception as e:
            logger.error(f"Error fetching Scribe context: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_active_session(self) -> dict[str, Any]:
        """
        Retrieves active session information from the Session Registry.

        Returns:
            dict: Active session data including backlog_id, status, and context
        """
        try:
            sessions = self._get_active_sessions()
            if sessions:
                # Return the most recent active session
                return sessions[0]
            return {}
        except Exception as e:
            logger.error(f"Error retrieving active session: {e}")
            return {}

    def get_role_specific_context(self, role: str) -> dict[str, Any]:
        """
        Get context specific to a particular DSPy role.

        Args:
            role: The DSPy role (planner, implementer, coder, researcher, reviewer)

        Returns:
            dict: Role-specific context information
        """
        base_context = self.fetch_scribe_context()

        role_context = {
            "role": role,
            "base_context": base_context,
            "role_focus": self._get_role_focus(role),
            "relevant_sessions": self._get_relevant_sessions_for_role(role),
            "current_work": self._get_current_work_for_role(role),
        }

        return role_context

    def integrate_with_model_switcher(self, model_switcher: Any) -> None:
        """
        Integrates Scribe context with the existing ModelSwitcher.

        Args:
            model_switcher: Instance of the ModelSwitcher to integrate with
        """
        try:
            scribe_context = self.fetch_scribe_context()
            if hasattr(model_switcher, "add_context"):
                model_switcher.add_context(scribe_context)
            elif hasattr(model_switcher, "context"):
                model_switcher.context.update(scribe_context)
            logger.info("Successfully integrated Scribe context with ModelSwitcher")
        except Exception as e:
            logger.error(f"Error integrating with ModelSwitcher: {e}")

    def _get_active_sessions(self) -> list[dict[str, Any]]:
        """Get list of currently active Scribe sessions."""
        try:
            # Run scribe status command
            result = subprocess.run(
                [sys.executable, "scripts/single_doorway.py", "scribe", "status"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                # Parse the output to extract active sessions
                lines = result.stdout.split("\n")
                active_sessions = []

                for line in lines:
                    if "active" in line.lower() and "B-" in line:
                        # Extract backlog ID and status
                        parts = line.split()
                        if len(parts) >= 2:
                            active_sessions.append(
                                {"backlog_id": parts[0], "status": "active", "last_updated": datetime.now().isoformat()}
                            )

                return active_sessions
            return []
        except Exception as e:
            logger.error(f"Error getting active sessions: {e}")
            return []

    def _get_recent_worklogs(self) -> list[dict[str, Any]]:
        """Get recent worklog entries."""
        try:
            worklogs = []
            if self.worklogs_path.exists():
                for worklog_file in self.worklogs_path.glob("*.md"):
                    if worklog_file.stat().st_mtime > (datetime.now().timestamp() - 86400):  # Last 24 hours
                        worklogs.append(
                            {
                                "file": worklog_file.name,
                                "last_modified": datetime.fromtimestamp(worklog_file.stat().st_mtime).isoformat(),
                                "size": worklog_file.stat().st_size,
                            }
                        )
            return worklogs
        except Exception as e:
            logger.error(f"Error getting recent worklogs: {e}")
            return []

    def _get_session_registry(self) -> dict[str, Any]:
        """Get session registry data."""
        try:
            if self.session_registry_path.exists():
                with open(self.session_registry_path) as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error getting session registry: {e}")
            return {}

    def _get_current_branch(self) -> str:
        """Get current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], capture_output=True, text=True, cwd=self.project_root
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return "unknown"

    def _get_recent_changes(self) -> list[str]:
        """Get recent file changes."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~1"], capture_output=True, text=True, cwd=self.project_root
            )
            if result.returncode == 0:
                return [line.strip() for line in result.stdout.split("\n") if line.strip()]
            return []
        except Exception as e:
            logger.error(f"Error getting recent changes: {e}")
            return []

    def _get_role_focus(self, role: str) -> dict[str, Any]:
        """Get focus areas for a specific role."""
        role_focus = {
            "planner": {
                "focus": "strategic planning and resource allocation",
                "key_metrics": ["timeline", "resource_usage", "progress_tracking"],
                "context_priority": "high",
            },
            "implementer": {
                "focus": "technical implementation and system integration",
                "key_metrics": ["code_changes", "integration_status", "technical_debt"],
                "context_priority": "high",
            },
            "coder": {
                "focus": "code development and debugging",
                "key_metrics": ["file_changes", "debugging_sessions", "code_quality"],
                "context_priority": "medium",
            },
            "researcher": {
                "focus": "research and analysis",
                "key_metrics": ["research_sessions", "analysis_progress", "insights"],
                "context_priority": "medium",
            },
            "reviewer": {
                "focus": "quality assurance and review",
                "key_metrics": ["review_sessions", "quality_metrics", "approval_status"],
                "context_priority": "low",
            },
        }
        return role_focus.get(role, {"focus": "general", "key_metrics": [], "context_priority": "low"})

    def _get_relevant_sessions_for_role(self, role: str) -> list[dict[str, Any]]:
        """Get sessions relevant to a specific role."""
        try:
            sessions = self._get_active_sessions()
            role_keywords = {
                "planner": ["plan", "strategy", "roadmap", "backlog"],
                "implementer": ["implement", "integration", "system", "technical"],
                "coder": ["code", "debug", "development", "refactor"],
                "researcher": ["research", "analysis", "investigate", "explore"],
                "reviewer": ["review", "quality", "test", "validate"],
            }

            relevant_sessions = []
            keywords = role_keywords.get(role, [])

            for session in sessions:
                # Check if session context matches role keywords
                if any(keyword in str(session).lower() for keyword in keywords):
                    relevant_sessions.append(session)

            return relevant_sessions
        except Exception as e:
            logger.error(f"Error getting relevant sessions for role {role}: {e}")
            return []

    def _get_current_work_for_role(self, role: str) -> dict[str, Any]:
        """Get current work context for a specific role."""
        try:
            current_work = {
                "role": role,
                "active_sessions": len(self._get_active_sessions()),
                "recent_changes": len(self._get_recent_changes()),
                "current_branch": self._get_current_branch(),
                "worklog_entries": len(self._get_recent_worklogs()),
            }
            return current_work
        except Exception as e:
            logger.error(f"Error getting current work for role {role}: {e}")
            return {"role": role, "error": str(e)}


# Convenience function for easy integration
def get_scribe_context_for_role(role: str) -> dict[str, Any]:
    """
    Convenience function to get Scribe context for a specific role.

    Args:
        role: The DSPy role (planner, implementer, coder, researcher, reviewer)

    Returns:
        dict: Role-specific Scribe context
    """
    provider = ScribeContextProvider()
    return provider.get_role_specific_context(role)
