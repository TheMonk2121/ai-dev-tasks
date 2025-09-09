#!/usr/bin/env python3
"""
Debugging Effectiveness Tracker

This script implements the feedback loop system for analyzing and improving
agent troubleshooting patterns and memory system effectiveness.
"""

import json
import re
import sqlite3
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class DebuggingEffectivenessTracker:
    """Tracks and analyzes debugging session effectiveness."""

    def __init__(self, db_path: str = "debugging_sessions.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS debugging_sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT,
                    technology TEXT,
                    issue_type TEXT,
                    problem_identification_time TEXT,
                    root_cause_time TEXT,
                    resolution_time TEXT,
                    total_iterations INTEGER,
                    patterns_used TEXT,
                    context_retrieved TEXT,
                    context_utilized BOOLEAN,
                    resolution_success BOOLEAN,
                    performance_improvement TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS pattern_effectiveness (
                    pattern TEXT,
                    usage_count INTEGER,
                    success_rate REAL,
                    avg_time_to_resolution REAL,
                    context_retrieval_success REAL,
                    learning_transfer_rate REAL,
                    last_updated TEXT
                )
            """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_performance (
                    metric_name TEXT PRIMARY KEY,
                    value REAL,
                    timestamp TEXT
                )
            """
            )

    def start_session(self, technology: str, issue_type: str) -> str:
        """Start tracking a new debugging session."""
        session_id = f"session_{int(time.time())}_{technology}_{issue_type}"

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO debugging_sessions
                (session_id, timestamp, technology, issue_type, problem_identification_time)
                VALUES (?, ?, ?, ?, ?)
            """,
                (session_id, datetime.now().isoformat(), technology, issue_type, None),
            )

        return session_id

    def record_pattern_usage(self, session_id: str, pattern: str):
        """Record a troubleshooting pattern used in a session."""
        with sqlite3.connect(self.db_path) as conn:
            # Get existing patterns
            result = conn.execute(
                "SELECT patterns_used FROM debugging_sessions WHERE session_id = ?", (session_id,)
            ).fetchone()

            if result and result[0]:
                patterns = json.loads(result[0])
            else:
                patterns = []

            patterns.append(pattern)

            conn.execute(
                "UPDATE debugging_sessions SET patterns_used = ? WHERE session_id = ?",
                (json.dumps(patterns), session_id),
            )

    def record_context_retrieval(self, session_id: str, context_items: list[str], utilized: bool):
        """Record context retrieval and utilization."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE debugging_sessions
                SET context_retrieved = ?, context_utilized = ?
                WHERE session_id = ?
            """,
                (json.dumps(context_items), utilized, session_id),
            )

    def complete_session(
        self, session_id: str, success: bool, iterations: int, performance_improvement: str | None = None
    ):
        """Mark a debugging session as complete."""
        resolution_time = datetime.now().isoformat()

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE debugging_sessions
                SET resolution_time = ?, resolution_success = ?, total_iterations = ?,
                    performance_improvement = ?
                WHERE session_id = ?
            """,
                (resolution_time, success, iterations, performance_improvement, session_id),
            )

    def analyze_pattern_effectiveness(self) -> dict[str, Any]:
        """Analyze the effectiveness of different troubleshooting patterns."""
        with sqlite3.connect(self.db_path) as conn:
            # Get all sessions with patterns
            sessions = conn.execute(
                """
                SELECT patterns_used, resolution_success, total_iterations,
                       (julianday(resolution_time) - julianday(timestamp)) * 24 * 60 as duration_minutes
                FROM debugging_sessions
                WHERE patterns_used IS NOT NULL AND resolution_time IS NOT NULL
            """
            ).fetchall()

        pattern_stats = {}

        for session in sessions:
            patterns = json.loads(session[0])
            success = session[1]
            iterations = session[2]
            duration = session[3]

            for pattern in patterns:
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {
                        "usage_count": 0,
                        "success_count": 0,
                        "total_iterations": 0,
                        "total_duration": 0,
                    }

                pattern_stats[pattern]["usage_count"] += 1
                if success:
                    pattern_stats[pattern]["success_count"] += 1
                pattern_stats[pattern]["total_iterations"] += iterations
                pattern_stats[pattern]["total_duration"] += duration

        # Calculate effectiveness metrics
        effectiveness = {}
        for pattern, stats in pattern_stats.items():
            effectiveness[pattern] = {
                "usage_count": stats["usage_count"],
                "success_rate": stats["success_count"] / stats["usage_count"],
                "avg_iterations": stats["total_iterations"] / stats["usage_count"],
                "avg_duration_minutes": stats["total_duration"] / stats["usage_count"],
            }

        return effectiveness

    def generate_effectiveness_report(self) -> str:
        """Generate a comprehensive effectiveness report."""
        pattern_effectiveness = self.analyze_pattern_effectiveness()

        report = "# Debugging Effectiveness Report\n\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Overall statistics
        with sqlite3.connect(self.db_path) as conn:
            total_sessions = conn.execute("SELECT COUNT(*) FROM debugging_sessions").fetchone()[0]
            successful_sessions = conn.execute(
                "SELECT COUNT(*) FROM debugging_sessions WHERE resolution_success = 1"
            ).fetchone()[0]
            avg_iterations = conn.execute(
                "SELECT AVG(total_iterations) FROM debugging_sessions WHERE total_iterations IS NOT NULL"
            ).fetchone()[0]

        report += "## Overall Statistics\n\n"
        report += f"- **Total Sessions**: {total_sessions}\n"
        report += f"- **Success Rate**: {successful_sessions/total_sessions*100:.1f}%\n"
        report += f"- **Average Iterations**: {avg_iterations:.1f}\n\n"

        # Pattern effectiveness
        report += "## Pattern Effectiveness\n\n"
        report += "| Pattern | Usage Count | Success Rate | Avg Iterations | Avg Duration (min) |\n"
        report += "|---------|-------------|--------------|----------------|-------------------|\n"

        for pattern, stats in sorted(pattern_effectiveness.items(), key=lambda x: x[1]["success_rate"], reverse=True):
            report += f"| {pattern[:50]}... | {stats['usage_count']} | {stats['success_rate']:.1%} | {stats['avg_iterations']:.1f} | {stats['avg_duration_minutes']:.1f} |\n"

        # Recommendations
        report += "\n## Recommendations\n\n"

        # Most effective patterns
        effective_patterns = [
            p for p, s in pattern_effectiveness.items() if s["success_rate"] > 0.8 and s["usage_count"] > 2
        ]
        if effective_patterns:
            report += "### Most Effective Patterns\n"
            for pattern in effective_patterns[:3]:
                report += f"- **{pattern}**: High success rate, consider promoting\n"

        # Patterns needing improvement
        ineffective_patterns = [
            p for p, s in pattern_effectiveness.items() if s["success_rate"] < 0.5 and s["usage_count"] > 1
        ]
        if ineffective_patterns:
            report += "\n### Patterns Needing Improvement\n"
            for pattern in ineffective_patterns[:3]:
                report += f"- **{pattern}**: Low success rate, consider refining\n"

        return report

    def detect_debugging_patterns(self, text: str) -> list[str]:
        """Detect troubleshooting patterns in text."""
        patterns = [
            r"I can see the issue",
            r"I see the problem",
            r"The issue is",
            r"The problem is",
            r"The issue is still there",
            r"The problem keeps persisting",
            r"Let me check what's happening",
            r"Let me debug this by",
            r"Let me try a different approach",
            r"Let me fix this by",
            r"Perfect! The script is working correctly",
            r"Excellent! The fix was successful",
        ]

        detected = []
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                detected.append(pattern)

        return detected

    def update_memory_system(self, insights: dict[str, Any]):
        """Update memory system based on effectiveness insights."""
        # This would integrate with the existing memory system
        # For now, we'll just log the insights
        with open("debugging_insights.json", "w") as f:
            json.dump(insights, f, indent=2)

        print("Memory system updated with debugging insights")


def main():
    """Main function to demonstrate the tracking system."""
    tracker = DebuggingEffectivenessTracker()

    # Example usage
    print("Starting debugging effectiveness tracking...")

    # Start a session
    session_id = tracker.start_session("bash_scripts", "shellcheck_warnings")
    print(f"Started session: {session_id}")

    # Record pattern usage
    tracker.record_pattern_usage(session_id, "I can see the issue...")
    tracker.record_pattern_usage(session_id, "Let me try a different approach...")

    # Record context retrieval
    tracker.record_context_retrieval(session_id, ["similar_shellcheck_fix_2024-12-15"], True)

    # Complete session
    tracker.complete_session(session_id, True, 3, "25%_faster_than_baseline")

    # Generate report
    report = tracker.generate_effectiveness_report()
    print("\n" + report)

    # Save report
    with open("debugging_effectiveness_report.md", "w") as f:
        f.write(report)

    print("\nReport saved to debugging_effectiveness_report.md")


if __name__ == "__main__":
    main()
