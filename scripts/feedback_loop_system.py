#!/usr/bin/env python3
"""
Advanced Feedback Loops & Lessons Integration System (B-103)

Captures systematic feedback from linter/test errors and git commits,
aggregates lessons learned, and influences backlog prioritization.

Usage:
    python3 scripts/feedback_loop_system.py --collect-errors
    python3 scripts/feedback_loop_system.py --analyze-commits
    python3 scripts/feedback_loop_system.py --update-lessons
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import yaml


@dataclass
class FeedbackItem:
    """Represents a single feedback item from the development process."""

    source: str  # "linter", "test", "git", "manual"
    timestamp: datetime
    severity: str  # "error", "warning", "info"
    category: str  # "code_quality", "test_failure", "performance", etc.
    message: str
    file_path: str | None = None
    line_number: int | None = None
    context: dict = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class LessonLearned:
    """Represents a lesson learned from feedback analysis."""

    title: str
    description: str
    category: str
    severity: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    patterns: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    backlog_impact: dict = field(default_factory=dict)


@dataclass
class FeedbackAnalysis:
    """Results of feedback analysis."""

    total_items: int
    error_count: int
    warning_count: int
    info_count: int
    categories: dict[str, int]
    lessons_learned: list[LessonLearned]
    backlog_recommendations: list[str]


class FeedbackLoopSystem:
    """Advanced feedback loop system for consensus framework."""

    def __init__(self, config_path: str | None = None):
        self.config = self._load_config(config_path)
        self.feedback_db_path = Path("data/feedback_loop.jsonl")
        self.lessons_db_path = Path("data/lessons_learned.jsonl")
        self._ensure_data_dirs()

    def _load_config(self, config_path: str | None) -> dict:
        """Load configuration for the feedback loop system."""
        default_config = {
            "sources": {
                "linter": {
                    "enabled": True,
                    "patterns": ["ruff", "pylint", "flake8"],
                    "severity_mapping": {"E": "error", "W": "warning", "I": "info"},
                },
                "tests": {
                    "enabled": True,
                    "patterns": ["pytest", "test"],
                    "failure_patterns": ["FAILED", "ERROR", "AssertionError"],
                },
                "git": {
                    "enabled": True,
                    "commit_patterns": ["fix", "bug", "error", "test", "refactor"],
                    "time_window_days": 30,
                },
            },
            "analysis": {"min_frequency": 2, "pattern_threshold": 0.7, "backlog_influence_threshold": 3},
            "output": {
                "feedback_file": "data/feedback_loop.jsonl",
                "lessons_file": "data/lessons_learned.jsonl",
                "backlog_updates": True,
            },
        }

        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                user_config = yaml.safe_load(f)
                # Merge user config with defaults
                default_config.update(user_config)

        return default_config

    def _ensure_data_dirs(self):
        """Ensure data directories exist."""
        self.feedback_db_path.parent.mkdir(parents=True, exist_ok=True)
        self.lessons_db_path.parent.mkdir(parents=True, exist_ok=True)

    def collect_linter_feedback(self) -> list[FeedbackItem]:
        """Collect feedback from linter runs."""
        feedback_items = []

        try:
            # Run ruff to collect linting issues
            result = subprocess.run(
                ["ruff", "check", "--output-format=json"], capture_output=True, text=True, cwd=Path.cwd()
            )

            if result.returncode != 0:
                # Parse ruff output
                try:
                    ruff_data = json.loads(result.stdout)
                    for issue in ruff_data:
                        feedback_items.append(
                            FeedbackItem(
                                source="linter",
                                timestamp=datetime.now(),
                                severity=self.config["sources"]["linter"]["severity_mapping"].get(
                                    issue.get("code", "E")[0], "warning"
                                ),
                                category="code_quality",
                                message=issue.get("message", "Unknown linting issue"),
                                file_path=issue.get("filename"),
                                line_number=issue.get("location", {}).get("row"),
                                context={"code": issue.get("code"), "rule": issue.get("rule")},
                                tags=["ruff", "linting"],
                            )
                        )
                except json.JSONDecodeError:
                    # Fallback to parsing text output
                    for line in result.stdout.split("\n"):
                        if line.strip():
                            feedback_items.append(
                                FeedbackItem(
                                    source="linter",
                                    timestamp=datetime.now(),
                                    severity="warning",
                                    category="code_quality",
                                    message=line.strip(),
                                    tags=["ruff", "linting"],
                                )
                            )
        except FileNotFoundError:
            print("Warning: ruff not found, skipping linter feedback collection")

        return feedback_items

    def collect_test_feedback(self) -> list[FeedbackItem]:
        """Collect feedback from test runs."""
        feedback_items = []

        try:
            # Run pytest to collect test failures
            result = subprocess.run(
                ["python", "-m", "pytest", "--tb=short", "-q"], capture_output=True, text=True, cwd=Path.cwd()
            )

            if result.returncode != 0:
                # Parse test output for failures
                output_lines = result.stdout.split("\n") + result.stderr.split("\n")

                for line in output_lines:
                    if any(pattern in line for pattern in self.config["sources"]["tests"]["failure_patterns"]):
                        feedback_items.append(
                            FeedbackItem(
                                source="test",
                                timestamp=datetime.now(),
                                severity="error",
                                category="test_failure",
                                message=line.strip(),
                                tags=["pytest", "testing"],
                            )
                        )
        except Exception as e:
            print(f"Warning: Error collecting test feedback: {e}")

        return feedback_items

    def collect_git_feedback(self, days: int = 30) -> list[FeedbackItem]:
        """Collect feedback from git commit history."""
        feedback_items = []

        try:
            # Get recent commits
            since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            result = subprocess.run(
                ["git", "log", f"--since={since_date}", "--pretty=format:%H|%an|%ad|%s|%b", "--date=short"],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )

            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    if line.strip():
                        parts = line.split("|", 4)
                        if len(parts) >= 4:
                            commit_hash, author, date, subject, body = (
                                parts[0],
                                parts[1],
                                parts[2],
                                parts[3],
                                parts[4] if len(parts) > 4 else "",
                            )

                            # Check for patterns in commit message
                            commit_text = f"{subject} {body}".lower()
                            patterns = self.config["sources"]["git"]["commit_patterns"]

                            for pattern in patterns:
                                if pattern in commit_text:
                                    severity = "error" if pattern in ["fix", "bug", "error"] else "info"
                                    category = "bug_fix" if pattern in ["fix", "bug"] else "development"

                                    feedback_items.append(
                                        FeedbackItem(
                                            source="git",
                                            timestamp=datetime.strptime(date, "%Y-%m-%d"),
                                            severity=severity,
                                            category=category,
                                            message=f"Commit: {subject}",
                                            context={"hash": commit_hash, "author": author, "pattern": pattern},
                                            tags=["git", "commit", pattern],
                                        )
                                    )
                                    break
        except Exception as e:
            print(f"Warning: Error collecting git feedback: {e}")

        return feedback_items

    def save_feedback(self, feedback_items: list[FeedbackItem]):
        """Save feedback items to the database."""
        with open(self.feedback_db_path, "a") as f:
            for item in feedback_items:
                json.dump(
                    {
                        "source": item.source,
                        "timestamp": item.timestamp.isoformat(),
                        "severity": item.severity,
                        "category": item.category,
                        "message": item.message,
                        "file_path": item.file_path,
                        "line_number": item.line_number,
                        "context": item.context,
                        "tags": item.tags,
                    },
                    f,
                )
                f.write("\n")

    def load_feedback(self, days: int = 30) -> list[FeedbackItem]:
        """Load feedback items from the database."""
        feedback_items = []
        cutoff_date = datetime.now() - timedelta(days=days)

        if self.feedback_db_path.exists():
            with open(self.feedback_db_path) as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            timestamp = datetime.fromisoformat(data["timestamp"])
                            if timestamp >= cutoff_date:
                                feedback_items.append(
                                    FeedbackItem(
                                        source=data["source"],
                                        timestamp=timestamp,
                                        severity=data["severity"],
                                        category=data["category"],
                                        message=data["message"],
                                        file_path=data.get("file_path"),
                                        line_number=data.get("line_number"),
                                        context=data.get("context", {}),
                                        tags=data.get("tags", []),
                                    )
                                )
                        except (json.JSONDecodeError, KeyError):
                            continue

        return feedback_items

    def analyze_feedback(self, feedback_items: list[FeedbackItem]) -> FeedbackAnalysis:
        """Analyze feedback items to extract lessons learned."""
        if not feedback_items:
            return FeedbackAnalysis(0, 0, 0, 0, {}, [], [])

        # Count statistics
        total_items = len(feedback_items)
        error_count = sum(1 for item in feedback_items if item.severity == "error")
        warning_count = sum(1 for item in feedback_items if item.severity == "warning")
        info_count = sum(1 for item in feedback_items if item.severity == "info")

        # Count by category
        categories = {}
        for item in feedback_items:
            categories[item.category] = categories.get(item.category, 0) + 1

        # Extract lessons learned
        lessons_learned = self._extract_lessons(feedback_items)

        # Generate backlog recommendations
        backlog_recommendations = self._generate_backlog_recommendations(lessons_learned)

        return FeedbackAnalysis(
            total_items=total_items,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            categories=categories,
            lessons_learned=lessons_learned,
            backlog_recommendations=backlog_recommendations,
        )

    def _extract_lessons(self, feedback_items: list[FeedbackItem]) -> list[LessonLearned]:
        """Extract lessons learned from feedback items."""
        lessons = []

        # Group by category and message patterns
        category_groups = {}
        for item in feedback_items:
            if item.category not in category_groups:
                category_groups[item.category] = []
            category_groups[item.category].append(item)

        for category, items in category_groups.items():
            # Find common patterns
            message_patterns = {}
            for item in items:
                # Extract key words from message
                words = re.findall(r"\b\w+\b", item.message.lower())
                key_words = [
                    w for w in words if len(w) > 3 and w not in ["this", "that", "with", "from", "have", "been", "will"]
                ]

                for word in key_words:
                    if word not in message_patterns:
                        message_patterns[word] = []
                    message_patterns[word].append(item)

            # Create lessons for frequent patterns
            min_frequency = self.config["analysis"]["min_frequency"]
            for word, word_items in message_patterns.items():
                if len(word_items) >= min_frequency:
                    # Calculate severity based on items
                    severities = [item.severity for item in word_items]
                    severity = "error" if "error" in severities else "warning" if "warning" in severities else "info"

                    # Generate recommendations
                    recommendations = self._generate_recommendations(category, word, word_items)

                    lesson = LessonLearned(
                        title=f"Frequent {category} issue: {word}",
                        description=f"Pattern '{word}' appears {len(word_items)} times in {category} feedback",
                        category=category,
                        severity=severity,
                        frequency=len(word_items),
                        first_seen=min(item.timestamp for item in word_items),
                        last_seen=max(item.timestamp for item in word_items),
                        patterns=[word],
                        recommendations=recommendations,
                        backlog_impact=self._calculate_backlog_impact(word_items),
                    )
                    lessons.append(lesson)

        return lessons

    def _generate_recommendations(self, category: str, pattern: str, items: list[FeedbackItem]) -> list[str]:
        """Generate recommendations based on feedback patterns."""
        recommendations = []

        if category == "code_quality":
            recommendations.extend(
                [
                    f"Add linting rules to prevent '{pattern}' issues",
                    "Consider automated code formatting",
                    "Review code style guidelines",
                ]
            )
        elif category == "test_failure":
            recommendations.extend(
                [
                    f"Improve test coverage for '{pattern}' related code",
                    "Add integration tests",
                    "Review test data and fixtures",
                ]
            )
        elif category == "bug_fix":
            recommendations.extend(
                [
                    f"Add validation for '{pattern}' scenarios",
                    "Implement better error handling",
                    "Consider adding monitoring for this pattern",
                ]
            )

        return recommendations

    def _calculate_backlog_impact(self, items: list[FeedbackItem]) -> dict:
        """Calculate potential impact on backlog prioritization."""
        impact = {"priority_boost": 0, "effort_adjustment": 0, "dependencies": []}

        # Calculate impact based on frequency and severity
        error_count = sum(1 for item in items if item.severity == "error")
        warning_count = sum(1 for item in items if item.severity == "warning")

        if error_count > 0:
            impact["priority_boost"] = min(error_count * 0.5, 2.0)  # Max 2.0 boost
            impact["effort_adjustment"] = min(error_count * 0.2, 1.0)  # Max 1.0 hour adjustment

        if warning_count > 0:
            impact["priority_boost"] += min(warning_count * 0.2, 1.0)

        return impact

    def _generate_backlog_recommendations(self, lessons: list[LessonLearned]) -> list[str]:
        """Generate recommendations for backlog updates."""
        recommendations = []

        # Find high-impact lessons
        high_impact_lessons = [
            lesson for lesson in lessons if lesson.frequency >= self.config["analysis"]["backlog_influence_threshold"]
        ]

        for lesson in high_impact_lessons:
            if lesson.backlog_impact["priority_boost"] > 0:
                recommendations.append(
                    f"Consider boosting priority of {lesson.category} related backlog items "
                    f"by {lesson.backlog_impact['priority_boost']:.1f} points"
                )

            if lesson.backlog_impact["effort_adjustment"] > 0:
                recommendations.append(
                    f"Add {lesson.backlog_impact['effort_adjustment']:.1f} hours to effort estimates "
                    f"for {lesson.category} related tasks"
                )

        return recommendations

    def save_lessons(self, lessons: list[LessonLearned]):
        """Save lessons learned to the database."""
        with open(self.lessons_db_path, "a") as f:
            for lesson in lessons:
                json.dump(
                    {
                        "title": lesson.title,
                        "description": lesson.description,
                        "category": lesson.category,
                        "severity": lesson.severity,
                        "frequency": lesson.frequency,
                        "first_seen": lesson.first_seen.isoformat(),
                        "last_seen": lesson.last_seen.isoformat(),
                        "patterns": lesson.patterns,
                        "recommendations": lesson.recommendations,
                        "backlog_impact": lesson.backlog_impact,
                    },
                    f,
                )
                f.write("\n")

    def update_lessons_context(self):
        """Update the lessons learned context file with new insights."""
        if not self.lessons_db_path.exists():
            return

        # Load recent lessons
        recent_lessons = []
        cutoff_date = datetime.now() - timedelta(days=7)  # Last week

        with open(self.lessons_db_path) as f:
            for line in f:
                if line.strip():
                    try:
                        data = json.loads(line)
                        last_seen = datetime.fromisoformat(data["last_seen"])
                        if last_seen >= cutoff_date:
                            recent_lessons.append(data)
                    except (json.JSONDecodeError, KeyError):
                        continue

        # Update lessons context file
        lessons_file = Path("100_memory/105_lessons-learned-context.md")
        if lessons_file.exists():
            # Read existing content
            with open(lessons_file) as f:
                content = f.read()

            # Add new lessons section if not present
            if "## Recent Feedback Lessons" not in content:
                content += "\n\n## Recent Feedback Lessons\n\n"

            # Add recent lessons
            for lesson in recent_lessons[-5:]:  # Last 5 lessons
                lesson_section = f"""
### {lesson['title']} {{#{lesson['category']}-{lesson['frequency']}}}

**Lesson**: {lesson['description']}

**Context**: Based on {lesson['frequency']} occurrences in feedback data.

**Implementation**:
{chr(10).join(f"- {rec}" for rec in lesson['recommendations'])}

**Benefits**:
- Reduces {lesson['category']} issues
- Improves development efficiency
- Better backlog prioritization
"""
                content += lesson_section

            # Write updated content
            with open(lessons_file, "w") as f:
                f.write(content)


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(description="Advanced Feedback Loop System")
    parser.add_argument("--collect-errors", action="store_true", help="Collect linter and test feedback")
    parser.add_argument("--analyze-commits", action="store_true", help="Analyze git commit history")
    parser.add_argument("--update-lessons", action="store_true", help="Update lessons learned context")
    parser.add_argument("--days", type=int, default=30, help="Number of days to analyze")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    args = parser.parse_args()

    system = FeedbackLoopSystem(args.config)

    if args.collect_errors:
        print("Collecting feedback from linter and tests...")
        feedback_items = []
        feedback_items.extend(system.collect_linter_feedback())
        feedback_items.extend(system.collect_test_feedback())
        system.save_feedback(feedback_items)
        print(f"Collected {len(feedback_items)} feedback items")

    if args.analyze_commits:
        print("Analyzing git commit history...")
        feedback_items = system.collect_git_feedback(args.days)
        system.save_feedback(feedback_items)
        print(f"Collected {len(feedback_items)} git feedback items")

    if args.update_lessons:
        print("Updating lessons learned...")
        feedback_items = system.load_feedback(args.days)
        analysis = system.analyze_feedback(feedback_items)
        system.save_lessons(analysis.lessons_learned)
        system.update_lessons_context()
        print(f"Updated {len(analysis.lessons_learned)} lessons learned")

        if args.output == "json":
            print(
                json.dumps(
                    {
                        "analysis": {
                            "total_items": analysis.total_items,
                            "error_count": analysis.error_count,
                            "warning_count": analysis.warning_count,
                            "info_count": analysis.info_count,
                            "categories": analysis.categories,
                        },
                        "lessons_count": len(analysis.lessons_learned),
                        "recommendations": analysis.backlog_recommendations,
                    },
                    indent=2,
                )
            )
        else:
            print("\nFeedback Analysis Summary:")
            print(f"  Total items: {analysis.total_items}")
            print(f"  Errors: {analysis.error_count}")
            print(f"  Warnings: {analysis.warning_count}")
            print(f"  Info: {analysis.info_count}")
            print(f"  Lessons learned: {len(analysis.lessons_learned)}")
            print(f"  Backlog recommendations: {len(analysis.backlog_recommendations)}")

            if analysis.backlog_recommendations:
                print("\nBacklog Recommendations:")
                for rec in analysis.backlog_recommendations:
                    print(f"  - {rec}")


if __name__ == "__main__":
    main()
