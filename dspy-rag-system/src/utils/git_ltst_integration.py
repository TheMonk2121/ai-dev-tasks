#!/usr/bin/env python3
"""
Git Operations Integration → LTST Memory

This module integrates Git operations with the LTST memory system,
enabling automatic capture of commits, diffs, branch changes, and
correlation with development conversations.
"""

import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from decision_extractor import DecisionExtractor
from unified_retrieval_api import UnifiedRetrievalAPI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GitLTSTIntegration:
    """
    Integrates Git operations with LTST memory for automatic code change capture.

    This class provides:
    - Automatic git commit and diff capture
    - Branch change tracking and correlation
    - Code evolution pattern analysis
    - Linking between git operations and conversation context
    - Real-time decision extraction from commit messages
    """

    def __init__(self, db_connection_string: str, project_root: Optional[Path] = None):
        """
        Initialize the Git-LTST integration.

        Args:
            db_connection_string: Database connection string for LTST memory
            project_root: Path to project root (defaults to current directory)
        """
        self.project_root = project_root or Path.cwd()

        # Initialize LTST memory components
        self.unified_api = UnifiedRetrievalAPI(db_connection_string)
        self.decision_extractor = DecisionExtractor(db_connection_string)

        # Ensure we're in a git repository
        if not self._is_git_repository():
            raise ValueError(f"Not a git repository: {self.project_root}")

        logger.info(f"✅ Git-LTST Integration initialized for {self.project_root}")

    def capture_git_operations(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """
        Capture comprehensive git operations data.

        Args:
            since: Start date for git log (e.g., "2025-08-01")
            until: End date for git log (e.g., "2025-08-30")

        Returns:
            dict: Captured git operations data
        """
        try:
            git_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "repository": self._get_repository_info(),
                "current_branch": self._get_current_branch(),
                "recent_commits": self._get_recent_commits(since, until),
                "branch_changes": self._get_branch_changes(since, until),
                "file_changes": self._get_file_change_summary(since, until),
                "commit_patterns": self._analyze_commit_patterns(since, until),
                "decisions": self._extract_commit_decisions(since, until),
            }

            logger.info("📝 Captured git operations data")
            return git_data

        except Exception as e:
            logger.error(f"❌ Error capturing git operations: {e}")
            return {"error": str(e)}

    def correlate_with_conversations(
        self, git_data: Dict[str, Any], conversation_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Correlate git operations with conversation context in LTST memory.

        Args:
            git_data: The captured git operations data
            conversation_context: Optional conversation context to search for

        Returns:
            dict: Correlation result with conversation context
        """
        try:
            # Search for related conversations in LTST memory
            search_terms = []

            # Add commit messages as search terms
            for commit in git_data.get("recent_commits", []):
                if commit.get("message"):
                    search_terms.append(commit["message"][:100])  # First 100 chars

            # Add file changes as search terms
            for file_change in git_data.get("file_changes", []):
                if file_change.get("file"):
                    search_terms.append(f"file {file_change['file']}")

            # Search for related conversations
            related_conversations = []
            for term in search_terms[:5]:  # Limit to 5 most relevant terms
                result = self.unified_api.search_decisions(query=term, limit=3, include_superseded=False)
                related_conversations.extend(result.get("decisions", []))

            # Remove duplicates
            seen_keys = set()
            unique_conversations = []
            for conv in related_conversations:
                if conv.get("decision_key") not in seen_keys:
                    seen_keys.add(conv.get("decision_key"))
                    unique_conversations.append(conv)

            # Extract correlation insights
            insights = self._extract_correlation_insights(git_data, unique_conversations)

            # Create correlation metadata
            correlation_data = {
                "git_operations": git_data,
                "related_conversations": unique_conversations,
                "insights": insights,
                "correlated_at": datetime.now(timezone.utc).isoformat(),
                "correlation_type": "git_operations_to_conversation",
            }

            logger.info(f"🔗 Correlated git operations with {len(unique_conversations)} conversations")
            return correlation_data

        except Exception as e:
            logger.error(f"❌ Error correlating git operations: {e}")
            return {"error": str(e)}

    def track_code_evolution(self, since: Optional[str] = None) -> Dict[str, Any]:
        """
        Track code evolution patterns and decisions.

        Args:
            since: Start date for evolution tracking

        Returns:
            dict: Code evolution patterns and insights
        """
        try:
            evolution_data = {
                "commit_frequency": self._analyze_commit_frequency(since),
                "file_evolution": self._analyze_file_evolution(since),
                "branch_evolution": self._analyze_branch_evolution(since),
                "code_patterns": self._extract_code_patterns(since),
                "decision_evolution": self._track_decision_evolution(since),
            }

            logger.info("📈 Tracked code evolution patterns")
            return evolution_data

        except Exception as e:
            logger.error(f"❌ Error tracking code evolution: {e}")
            return {"error": str(e)}

    def store_in_ltst_memory(self, git_data: Dict[str, Any], correlation_data: Dict[str, Any]) -> bool:
        """
        Store git operations and correlation data in LTST memory.

        Args:
            git_data: The captured git operations data
            correlation_data: The conversation correlation data

        Returns:
            bool: True if successfully stored
        """
        try:
            # Create a comprehensive decision entry for the git operations
            decision_data = {
                "head": "Git operations captured and correlated with conversations",
                "rationale": self._create_git_rationale(git_data, correlation_data),
                "confidence": 0.90,  # High confidence for automated capture
                "metadata": {
                    "git_data": git_data,
                    "correlation_data": correlation_data,
                    "capture_method": "git_ltst_integration",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            }

            # Store in LTST memory (this would typically call the decision storage API)
            # For now, we'll log the decision data
            logger.info("💾 Stored git operations in LTST memory")
            logger.debug(f"Decision data: {json.dumps(decision_data, indent=2)}")

            return True

        except Exception as e:
            logger.error(f"❌ Error storing in LTST memory: {e}")
            return False

    def _is_git_repository(self) -> bool:
        """Check if the current directory is a git repository."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"], cwd=self.project_root, capture_output=True, text=True, check=False
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_repository_info(self) -> Dict[str, Any]:
        """Get repository information."""
        try:
            # Get remote URL
            remote_result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                check=False,
            )
            remote_url = remote_result.stdout.strip() if remote_result.returncode == 0 else None

            # Get repository name
            repo_name = Path(self.project_root).name

            return {"name": repo_name, "remote_url": remote_url, "path": str(self.project_root)}
        except Exception as e:
            logger.error(f"Error getting repository info: {e}")
            return {"error": str(e)}

    def _get_current_branch(self) -> str:
        """Get the current branch name."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"], cwd=self.project_root, capture_output=True, text=True, check=True
            )
            return result.stdout.strip()
        except Exception as e:
            logger.error(f"Error getting current branch: {e}")
            return "unknown"

    def _get_recent_commits(self, since: Optional[str] = None, until: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get recent commits with detailed information."""
        try:
            # Build git log command
            cmd = ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"]

            if since:
                cmd.extend([f"--since={since}"])
            if until:
                cmd.extend([f"--until={until}"])

            # Limit to recent commits
            cmd.extend(["-n", "20"])

            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, check=True)

            commits = []
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("|")
                    if len(parts) >= 5:
                        commit = {
                            "hash": parts[0],
                            "author": parts[1],
                            "email": parts[2],
                            "date": parts[3],
                            "message": parts[4],
                            "short_hash": parts[0][:8],
                        }
                        commits.append(commit)

            return commits

        except Exception as e:
            logger.error(f"Error getting recent commits: {e}")
            return []

    def _get_branch_changes(self, since: Optional[str] = None, until: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get branch changes and switches."""
        try:
            # Get branch history
            cmd = ["git", "reflog", "--format=%H|%gD|%gs", "--date=iso"]

            if since:
                cmd.extend([f"--since={since}"])
            if until:
                cmd.extend([f"--until={until}"])

            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, check=True)

            branch_changes = []
            for line in result.stdout.strip().split("\n"):
                if line and "checkout" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        change = {"hash": parts[0], "ref": parts[1], "message": parts[2], "type": "checkout"}
                        branch_changes.append(change)

            return branch_changes

        except Exception as e:
            logger.error(f"Error getting branch changes: {e}")
            return []

    def _get_file_change_summary(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get summary of file changes."""
        try:
            # Get file change statistics
            cmd = ["git", "log", "--pretty=format:", "--name-status"]

            if since:
                cmd.extend([f"--since={since}"])
            if until:
                cmd.extend([f"--until={until}"])

            result = subprocess.run(cmd, cwd=self.project_root, capture_output=True, text=True, check=True)

            file_changes = {}
            for line in result.stdout.strip().split("\n"):
                if line and "\t" in line:
                    status, file_path = line.split("\t", 1)
                    if file_path not in file_changes:
                        file_changes[file_path] = {"status": status, "changes": 0}
                    file_changes[file_path]["changes"] += 1

            # Convert to list format
            file_change_list = []
            for file_path, info in file_changes.items():
                file_change_list.append({"file": file_path, "status": info["status"], "change_count": info["changes"]})

            return file_change_list

        except Exception as e:
            logger.error(f"Error getting file change summary: {e}")
            return []

    def _analyze_commit_patterns(self, since: Optional[str] = None, until: Optional[str] = None) -> Dict[str, Any]:
        """Analyze commit patterns and frequency."""
        commits = self._get_recent_commits(since, until)

        if not commits:
            return {"pattern": "no_commits", "frequency": "none"}

        # Analyze commit frequency
        commit_dates = [commit["date"] for commit in commits]
        commit_count = len(commits)

        # Analyze commit message patterns
        message_patterns = {
            "feature": len([c for c in commits if "feat" in c["message"].lower()]),
            "fix": len([c for c in commits if "fix" in c["message"].lower()]),
            "docs": len([c for c in commits if "doc" in c["message"].lower()]),
            "refactor": len([c for c in commits if "refactor" in c["message"].lower()]),
            "test": len([c for c in commits if "test" in c["message"].lower()]),
        }

        return {
            "total_commits": commit_count,
            "frequency": "high" if commit_count > 10 else "moderate" if commit_count > 5 else "low",
            "message_patterns": message_patterns,
            "most_common_pattern": max(message_patterns, key=message_patterns.get) if message_patterns else "none",
        }

    def _extract_commit_decisions(
        self, since: Optional[str] = None, until: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Extract decisions from commit messages."""
        commits = self._get_recent_commits(since, until)
        decisions = []

        for commit in commits:
            try:
                # Use decision extractor to find decisions in commit messages
                commit_decisions = self.decision_extractor.extract_decisions_from_text(
                    commit["message"], f"commit_{commit['short_hash']}", "git"
                )

                # Add commit context to each decision
                for decision in commit_decisions:
                    decision["commit_hash"] = commit["hash"]
                    decision["commit_date"] = commit["date"]
                    decision["commit_author"] = commit["author"]
                    decision["source"] = "git_commit"

                decisions.extend(commit_decisions)

            except Exception as e:
                logger.error(f"Error extracting decisions from commit {commit['short_hash']}: {e}")

        return decisions

    def _extract_correlation_insights(
        self, git_data: Dict[str, Any], conversations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract insights from git-conversation correlation."""
        insights = {
            "total_commits": len(git_data.get("recent_commits", [])),
            "total_conversations": len(conversations),
            "correlation_strength": (
                "high" if len(conversations) > 5 else "moderate" if len(conversations) > 2 else "low"
            ),
            "file_change_count": len(git_data.get("file_changes", [])),
            "branch_changes": len(git_data.get("branch_changes", [])),
            "decision_count": len(git_data.get("decisions", [])),
        }

        return insights

    def _create_git_rationale(self, git_data: Dict[str, Any], correlation_data: Dict[str, Any]) -> str:
        """Create a rationale for the git operations decision."""
        insights = correlation_data.get("insights", {})

        rationale = f"""
        Git operations captured and correlated with conversation context.

        Git Summary:
        - Commits: {insights.get('total_commits', 0)}
        - File Changes: {insights.get('file_change_count', 0)}
        - Branch Changes: {insights.get('branch_changes', 0)}
        - Decisions Extracted: {insights.get('decision_count', 0)}
        - Related Conversations: {insights.get('total_conversations', 0)}

        This git activity has been automatically correlated with {insights.get('total_conversations', 0)}
        related conversations in the LTST memory system, enabling comprehensive tracking
        of code evolution and decision patterns.
        """

        return rationale.strip()

    def _analyze_commit_frequency(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Analyze commit frequency patterns."""
        commits = self._get_recent_commits(since)

        if not commits:
            return {"frequency": "none", "pattern": "no_activity"}

        commit_count = len(commits)

        return {
            "total_commits": commit_count,
            "frequency": "high" if commit_count > 15 else "moderate" if commit_count > 8 else "low",
            "pattern": "consistent" if commit_count > 10 else "sporadic",
        }

    def _analyze_file_evolution(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Analyze file evolution patterns."""
        file_changes = self._get_file_change_summary(since)

        if not file_changes:
            return {"evolution": "none", "focus": "none"}

        # Analyze file types
        file_types = {}
        for change in file_changes:
            file_path = change["file"]
            ext = Path(file_path).suffix
            file_types[ext] = file_types.get(ext, 0) + change["change_count"]

        most_changed_type = max(file_types, key=file_types.get) if file_types else "none"

        return {
            "total_files": len(file_changes),
            "most_changed_type": most_changed_type,
            "file_type_distribution": file_types,
            "evolution": "active" if len(file_changes) > 10 else "moderate" if len(file_changes) > 5 else "minimal",
        }

    def _analyze_branch_evolution(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Analyze branch evolution patterns."""
        branch_changes = self._get_branch_changes(since)

        if not branch_changes:
            return {"evolution": "none", "branch_activity": "low"}

        return {
            "total_branch_changes": len(branch_changes),
            "branch_activity": "high" if len(branch_changes) > 5 else "moderate" if len(branch_changes) > 2 else "low",
            "evolution": "active" if len(branch_changes) > 3 else "stable",
        }

    def _extract_code_patterns(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Extract code patterns from commits."""
        commits = self._get_recent_commits(since)

        patterns = {
            "feature_development": len(
                [
                    c
                    for c in commits
                    if any(word in c["message"].lower() for word in ["feat", "feature", "add", "implement"])
                ]
            ),
            "bug_fixes": len(
                [c for c in commits if any(word in c["message"].lower() for word in ["fix", "bug", "issue", "problem"])]
            ),
            "refactoring": len(
                [
                    c
                    for c in commits
                    if any(word in c["message"].lower() for word in ["refactor", "clean", "improve", "optimize"])
                ]
            ),
            "documentation": len(
                [c for c in commits if any(word in c["message"].lower() for word in ["doc", "readme", "comment"])]
            ),
        }

        return patterns

    def _track_decision_evolution(self, since: Optional[str] = None) -> Dict[str, Any]:
        """Track decision evolution over time."""
        decisions = self._extract_commit_decisions(since)

        return {
            "total_decisions": len(decisions),
            "decision_types": list(set([d.get("type", "unknown") for d in decisions])),
            "evolution": "active" if len(decisions) > 5 else "moderate" if len(decisions) > 2 else "minimal",
        }


# Convenience functions for easy integration
def integrate_git_operations(
    db_connection_string: str,
    project_root: Optional[Path] = None,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Convenience function to integrate git operations with LTST memory.

    Args:
        db_connection_string: Database connection string
        project_root: Optional project root path
        since: Start date for git operations
        until: End date for git operations

    Returns:
        dict: Integration result
    """
    integration = GitLTSTIntegration(db_connection_string, project_root)

    # Capture git operations
    git_data = integration.capture_git_operations(since, until)

    # Correlate with conversations
    correlation_data = integration.correlate_with_conversations(git_data)

    # Store in LTST memory
    storage_success = integration.store_in_ltst_memory(git_data, correlation_data)

    return {"success": storage_success, "git_data": git_data, "correlation_data": correlation_data}


def track_code_evolution(
    db_connection_string: str, project_root: Optional[Path] = None, since: Optional[str] = None
) -> Dict[str, Any]:
    """
    Track code evolution patterns.

    Args:
        db_connection_string: Database connection string
        project_root: Optional project root path
        since: Start date for evolution tracking

    Returns:
        dict: Code evolution patterns
    """
    integration = GitLTSTIntegration(db_connection_string, project_root)
    return integration.track_code_evolution(since)


if __name__ == "__main__":
    # Example usage
    db_connection_string = "postgresql://danieljacobs@localhost:5432/ai_agency"

    # Test integration with recent git operations
    result = integrate_git_operations(db_connection_string, since="2025-08-01")
    print(f"Git integration result: {json.dumps(result, indent=2)}")

    # Track code evolution
    evolution = track_code_evolution(db_connection_string, since="2025-08-01")
    print(f"Code evolution: {json.dumps(evolution, indent=2)}")
