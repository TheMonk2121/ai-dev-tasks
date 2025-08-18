#!/usr/bin/env python3.12.123.11
"""
Test Suite for Advanced Feedback Loop System (B-103)

Comprehensive tests for feedback collection, analysis, and lessons learned integration.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.feedback_loop_system import (
    FeedbackAnalysis,
    FeedbackItem,
    FeedbackLoopSystem,
    LessonLearned,
)


class TestFeedbackLoopSystem:
    """Test cases for FeedbackLoopSystem class."""

    def setup_method(self):
        """Set up feedback loop system for testing."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.feedback_db_path = self.temp_dir / "feedback_loop.jsonl"
        self.lessons_db_path = self.temp_dir / "lessons_learned.jsonl"

        # Create system with custom paths
        self.system = FeedbackLoopSystem()
        self.system.feedback_db_path = self.feedback_db_path
        self.system.lessons_db_path = self.lessons_db_path

        # Ensure the temp directory exists and create empty files
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.feedback_db_path.touch()
        self.lessons_db_path.touch()

    def teardown_method(self):
        """Clean up after tests."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_feedback_item_creation(self):
        """Test creation of feedback items."""
        item = FeedbackItem(
            source="linter",
            timestamp=datetime.now(),
            severity="error",
            category="code_quality",
            message="Line too long",
            file_path="test.py",
            line_number=42,
            context={"code": "E501"},
            tags=["ruff", "linting"],
        )

        assert item.source == "linter"
        assert item.severity == "error"
        assert item.category == "code_quality"
        assert item.message == "Line too long"
        assert item.file_path == "test.py"
        assert item.line_number == 42
        assert item.context["code"] == "E501"
        assert "ruff" in item.tags

    def test_lesson_learned_creation(self):
        """Test creation of lessons learned."""
        lesson = LessonLearned(
            title="Frequent code_quality issue: import",
            description="Pattern 'import' appears 5 times in code_quality feedback",
            category="code_quality",
            severity="warning",
            frequency=5,
            first_seen=datetime.now() - timedelta(days=1),
            last_seen=datetime.now(),
            patterns=["import"],
            recommendations=["Add import sorting", "Use absolute imports"],
            backlog_impact={"priority_boost": 1.0, "effort_adjustment": 0.5},
        )

        assert lesson.title == "Frequent code_quality issue: import"
        assert lesson.frequency == 5
        assert lesson.category == "code_quality"
        assert len(lesson.recommendations) == 2
        assert lesson.backlog_impact["priority_boost"] == 1.0

    def test_feedback_analysis_creation(self):
        """Test creation of feedback analysis results."""
        analysis = FeedbackAnalysis(
            total_items=10,
            error_count=3,
            warning_count=5,
            info_count=2,
            categories={"code_quality": 7, "test_failure": 3},
            lessons_learned=[],
            backlog_recommendations=[],
        )

        assert analysis.total_items == 10
        assert analysis.error_count == 3
        assert analysis.warning_count == 5
        assert analysis.info_count == 2
        assert analysis.categories["code_quality"] == 7

    def test_save_and_load_feedback(self):
        """Test saving and loading feedback items."""
        # Create test feedback items
        items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Test error 1",
                tags=["test"],
            ),
            FeedbackItem(
                source="test",
                timestamp=datetime.now(),
                severity="warning",
                category="test_failure",
                message="Test warning 1",
                tags=["test"],
            ),
        ]

        # Save feedback
        self.system.save_feedback(items)

        # Load feedback
        loaded_items = self.system.load_feedback(days=1)

        assert len(loaded_items) == 2
        assert loaded_items[0].source == "linter"
        assert loaded_items[0].severity == "error"
        assert loaded_items[1].source == "test"
        assert loaded_items[1].severity == "warning"

    def test_analyze_feedback_empty(self):
        """Test analysis of empty feedback."""
        analysis = self.system.analyze_feedback([])

        assert analysis.total_items == 0
        assert analysis.error_count == 0
        assert analysis.warning_count == 0
        assert analysis.info_count == 0
        assert len(analysis.categories) == 0
        assert len(analysis.lessons_learned) == 0
        assert len(analysis.backlog_recommendations) == 0

    def test_analyze_feedback_with_items(self):
        """Test analysis of feedback items."""
        items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in import statement",
                tags=["test"],
            ),
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in function definition",
                tags=["test"],
            ),
            FeedbackItem(
                source="test",
                timestamp=datetime.now(),
                severity="warning",
                category="test_failure",
                message="Test assertion failed",
                tags=["test"],
            ),
        ]

        analysis = self.system.analyze_feedback(items)

        assert analysis.total_items == 3
        assert analysis.error_count == 2
        assert analysis.warning_count == 1
        assert analysis.info_count == 0
        assert analysis.categories["code_quality"] == 2
        assert analysis.categories["test_failure"] == 1
        assert len(analysis.lessons_learned) > 0

    def test_extract_lessons_from_feedback(self):
        """Test extraction of lessons from feedback patterns."""
        items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in import statement",
                tags=["test"],
            ),
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in function definition",
                tags=["test"],
            ),
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in class definition",
                tags=["test"],
            ),
        ]

        analysis = self.system.analyze_feedback(items)
        lessons = analysis.lessons_learned

        assert len(lessons) > 0

        # Check that lessons have expected structure
        for lesson in lessons:
            assert lesson.title
            assert lesson.description
            assert lesson.category == "code_quality"
            assert lesson.frequency >= 2  # min_frequency
            assert len(lesson.recommendations) > 0
            assert "priority_boost" in lesson.backlog_impact

    def test_generate_recommendations(self):
        """Test generation of recommendations based on feedback patterns."""
        items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Test pattern",
                tags=["test"],
            )
        ]

        analysis = self.system.analyze_feedback(items)

        # Should have recommendations for code quality issues
        assert len(analysis.backlog_recommendations) >= 0

    def test_save_and_load_lessons(self):
        """Test saving and loading lessons learned."""
        lessons = [
            LessonLearned(
                title="Test Lesson 1",
                description="Test description 1",
                category="code_quality",
                severity="warning",
                frequency=3,
                first_seen=datetime.now() - timedelta(days=1),
                last_seen=datetime.now(),
                patterns=["test"],
                recommendations=["Test recommendation"],
                backlog_impact={"priority_boost": 1.0, "effort_adjustment": 0.5},
            )
        ]

        # Save lessons
        self.system.save_lessons(lessons)

        # Verify file was created
        assert self.system.lessons_db_path.exists()

    def test_calculate_backlog_impact(self):
        """Test calculation of backlog impact from feedback items."""
        # Test with error items
        error_items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Test error",
                tags=["test"],
            ),
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Test error 2",
                tags=["test"],
            ),
        ]

        analysis = self.system.analyze_feedback(error_items)

        # Should have lessons with backlog impact
        for lesson in analysis.lessons_learned:
            assert lesson.backlog_impact["priority_boost"] > 0
            assert lesson.backlog_impact["effort_adjustment"] > 0

    def test_config_loading(self):
        """Test configuration loading and defaults."""
        config = self.system.config

        # Check that default config is loaded
        assert "sources" in config
        assert "linter" in config["sources"]
        assert "tests" in config["sources"]
        assert "git" in config["sources"]
        assert "analysis" in config
        assert "output" in config

        # Check specific values
        assert config["sources"]["linter"]["enabled"] is True
        assert config["analysis"]["min_frequency"] == 2
        assert config["analysis"]["backlog_influence_threshold"] == 3

    @patch("subprocess.run")
    def test_collect_linter_feedback_mock(self, mock_run):
        """Test linter feedback collection with mocked subprocess."""
        # Mock successful ruff run with no issues
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "[]"

        feedback_items = self.system.collect_linter_feedback()
        assert len(feedback_items) == 0

        # Mock ruff run with issues
        mock_run.return_value.returncode = 1
        mock_run.return_value.stdout = json.dumps(
            [
                {
                    "code": "E501",
                    "message": "Line too long",
                    "filename": "test.py",
                    "location": {"row": 42},
                    "rule": "line-too-long",
                }
            ]
        )

        feedback_items = self.system.collect_linter_feedback()
        assert len(feedback_items) == 1
        assert feedback_items[0].severity == "error"
        assert feedback_items[0].category == "code_quality"
        assert feedback_items[0].file_path == "test.py"
        assert feedback_items[0].line_number == 42

    @patch("subprocess.run")
    def test_collect_git_feedback_mock(self, mock_run):
        """Test git feedback collection with mocked subprocess."""
        # Mock git log output
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = (
            "abc123|Test Author|2025-08-16|fix: resolve import issue|"
            "Fixed import statement that was causing linting errors\n"
        )

        feedback_items = self.system.collect_git_feedback(days=1)
        assert len(feedback_items) == 1
        assert feedback_items[0].source == "git"
        assert feedback_items[0].category == "bug_fix"
        assert feedback_items[0].severity == "error"
        assert "fix" in feedback_items[0].tags

    def test_pattern_extraction(self):
        """Test extraction of patterns from feedback messages."""
        items = [
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in import statement",
                tags=["test"],
            ),
            FeedbackItem(
                source="linter",
                timestamp=datetime.now(),
                severity="error",
                category="code_quality",
                message="Line too long in function definition",
                tags=["test"],
            ),
        ]

        analysis = self.system.analyze_feedback(items)

        # Should extract patterns like "long", "import", "function"
        assert len(analysis.lessons_learned) > 0

        for lesson in analysis.lessons_learned:
            assert len(lesson.patterns) > 0
            assert lesson.frequency >= 2

    def test_feedback_item_serialization(self):
        """Test JSON serialization of feedback items."""
        item = FeedbackItem(
            source="linter",
            timestamp=datetime.now(),
            severity="error",
            category="code_quality",
            message="Test message",
            file_path="test.py",
            line_number=42,
            context={"test": "value"},
            tags=["test"],
        )

        # Test that item can be serialized to JSON
        data = {
            "source": item.source,
            "timestamp": item.timestamp.isoformat(),
            "severity": item.severity,
            "category": item.category,
            "message": item.message,
            "file_path": item.file_path,
            "line_number": item.line_number,
            "context": item.context,
            "tags": item.tags,
        }

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert parsed["source"] == "linter"
        assert parsed["severity"] == "error"
        assert parsed["category"] == "code_quality"
        assert parsed["message"] == "Test message"

    def test_lesson_learned_serialization(self):
        """Test JSON serialization of lessons learned."""
        lesson = LessonLearned(
            title="Test Lesson",
            description="Test description",
            category="code_quality",
            severity="warning",
            frequency=3,
            first_seen=datetime.now() - timedelta(days=1),
            last_seen=datetime.now(),
            patterns=["test"],
            recommendations=["Test recommendation"],
            backlog_impact={"priority_boost": 1.0, "effort_adjustment": 0.5},
        )

        # Test that lesson can be serialized to JSON
        data = {
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
        }

        json_str = json.dumps(data)
        parsed = json.loads(json_str)

        assert parsed["title"] == "Test Lesson"
        assert parsed["category"] == "code_quality"
        assert parsed["frequency"] == 3
        assert parsed["backlog_impact"]["priority_boost"] == 1.0


if __name__ == "__main__":
    pytest.main([__file__])
