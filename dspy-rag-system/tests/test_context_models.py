#!/usr/bin/env python3
"""
Tests for Role-Based Context Models
Validates Pydantic context models for B-1007
"""

import os
import tempfile
from datetime import datetime

import pytest

from src.dspy_modules.context_models import (
    AIRole,
    BaseContext,
    CoderContext,
    ContextFactory,
    ContextValidationBenchmark,
    ImplementerContext,
    LegacyContextAdapter,
    PlannerContext,
    ResearcherContext,
)


class TestBaseContext:
    """Test base context model functionality"""

    def test_base_context_creation(self):
        """Test basic context creation"""
        context = BaseContext(role=AIRole.PLANNER, session_id="test-session-123")

        assert context.role == AIRole.PLANNER
        assert context.session_id == "test-session-123"
        assert isinstance(context.timestamp, datetime)

    def test_session_id_validation(self):
        """Test session ID validation"""
        # Valid session ID
        context = BaseContext(role=AIRole.PLANNER, session_id="valid-session-id")
        assert context.session_id == "valid-session-id"

        # Invalid session ID (too short)
        with pytest.raises(ValueError, match="Session ID must be at least 3 characters"):
            BaseContext(role=AIRole.PLANNER, session_id="ab")

    def test_timestamp_validation(self):
        """Test timestamp validation"""
        # Valid timestamp
        context = BaseContext(role=AIRole.PLANNER, session_id="test-session", timestamp=datetime.now())
        assert isinstance(context.timestamp, datetime)

        # Future timestamp should be rejected
        future_time = datetime.now().replace(year=datetime.now().year + 1)
        with pytest.raises(ValueError, match="Timestamp cannot be in the future"):
            BaseContext(role=AIRole.PLANNER, session_id="test-session", timestamp=future_time)


class TestPlannerContext:
    """Test planner context model"""

    def test_planner_context_creation(self):
        """Test planner context creation"""
        context = PlannerContext(
            session_id="planner-session",
            project_scope="Implement Pydantic AI style enhancements for DSPy system",
            backlog_priority="P1",
        )

        assert context.role == AIRole.PLANNER
        assert context.project_scope == "Implement Pydantic AI style enhancements for DSPy system"
        assert context.backlog_priority == "P1"

    def test_project_scope_validation(self):
        """Test project scope validation"""
        # Valid scope
        context = PlannerContext(
            session_id="test-session",
            project_scope="This is a valid project scope with sufficient detail",
            backlog_priority="P1",
        )
        assert len(context.project_scope) >= 10

        # Invalid scope (too short)
        with pytest.raises(ValueError, match="Project scope must be at least 10 characters"):
            PlannerContext(session_id="test-session", project_scope="Short", backlog_priority="P1")

    def test_backlog_priority_validation(self):
        """Test backlog priority validation"""
        valid_priorities = ["P0", "P1", "P2", "P3"]

        for priority in valid_priorities:
            context = PlannerContext(
                session_id="test-session", project_scope="Valid project scope for testing", backlog_priority=priority
            )
            assert context.backlog_priority == priority

        # Invalid priority
        with pytest.raises(ValueError, match="Backlog priority must be one of"):
            PlannerContext(
                session_id="test-session", project_scope="Valid project scope for testing", backlog_priority="P4"
            )

    def test_strategic_goals_validation(self):
        """Test strategic goals validation"""
        context = PlannerContext(
            session_id="test-session",
            project_scope="Valid project scope for testing",
            backlog_priority="P1",
            strategic_goals=["Goal 1", "Goal 2", "Goal 3"],
        )

        assert len(context.strategic_goals) == 3

        # Too many goals
        with pytest.raises(ValueError, match="Cannot have more than 10 strategic goals"):
            PlannerContext(
                session_id="test-session",
                project_scope="Valid project scope for testing",
                backlog_priority="P1",
                strategic_goals=[f"Goal {i}" for i in range(11)],
            )


class TestCoderContext:
    """Test coder context model"""

    def test_coder_context_creation(self):
        """Test coder context creation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = CoderContext(session_id="coder-session", codebase_path=temp_dir, language="python")

            assert context.role == AIRole.CODER
            assert context.codebase_path == temp_dir
            assert context.language == "python"

    def test_codebase_path_validation(self):
        """Test codebase path validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Valid path
            context = CoderContext(session_id="test-session", codebase_path=temp_dir, language="python")
            assert context.codebase_path == temp_dir

        # Invalid path
        with pytest.raises(ValueError, match="Codebase path does not exist"):
            CoderContext(session_id="test-session", codebase_path="/nonexistent/path", language="python")

    def test_language_validation(self):
        """Test programming language validation"""
        supported_languages = ["python", "javascript", "typescript", "go", "rust", "java", "csharp"]

        with tempfile.TemporaryDirectory() as temp_dir:
            for language in supported_languages:
                context = CoderContext(session_id="test-session", codebase_path=temp_dir, language=language)
                assert context.language == language

            # Invalid language
            with pytest.raises(ValueError, match="Language must be one of"):
                CoderContext(session_id="test-session", codebase_path=temp_dir, language="invalid_language")

    def test_file_context_validation(self):
        """Test file context validation"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a test file
            test_file = os.path.join(temp_dir, "test.py")
            with open(test_file, "w") as f:
                f.write("# Test file")

            context = CoderContext(
                session_id="test-session",
                codebase_path=temp_dir,
                language="python",
                file_context=[test_file, "/nonexistent/file.py"],
            )

            # Should only include existing files
            assert len(context.file_context) == 1
            assert context.file_context[0] == test_file


class TestResearcherContext:
    """Test researcher context model"""

    def test_researcher_context_creation(self):
        """Test researcher context creation"""
        context = ResearcherContext(
            session_id="researcher-session",
            research_topic="DSPy 3.0 migration strategies",
            methodology="literature_review",
        )

        assert context.role == AIRole.RESEARCHER
        assert context.research_topic == "DSPy 3.0 migration strategies"
        assert context.methodology == "literature_review"

    def test_research_topic_validation(self):
        """Test research topic validation"""
        # Valid topic
        context = ResearcherContext(
            session_id="test-session",
            research_topic="Valid research topic with sufficient detail",
            methodology="literature_review",
        )
        assert len(context.research_topic) >= 5

        # Invalid topic (too short)
        with pytest.raises(ValueError, match="Research topic must be at least 5 characters"):
            ResearcherContext(session_id="test-session", research_topic="Hi", methodology="literature_review")

    def test_methodology_validation(self):
        """Test methodology validation"""
        valid_methodologies = ["literature_review", "experimental", "case_study", "survey", "analysis"]

        for methodology in valid_methodologies:
            context = ResearcherContext(
                session_id="test-session", research_topic="Valid research topic", methodology=methodology
            )
            assert context.methodology == methodology

        # Invalid methodology
        with pytest.raises(ValueError, match="Methodology must be one of"):
            ResearcherContext(
                session_id="test-session", research_topic="Valid research topic", methodology="invalid_methodology"
            )


class TestImplementerContext:
    """Test implementer context model"""

    def test_implementer_context_creation(self):
        """Test implementer context creation"""
        context = ImplementerContext(
            session_id="implementer-session",
            implementation_plan="This is a detailed implementation plan with sufficient detail for deployment",
            target_environment="development",
        )

        assert context.role == AIRole.IMPLEMENTER
        assert "detailed implementation plan" in context.implementation_plan
        assert context.target_environment == "development"

    def test_implementation_plan_validation(self):
        """Test implementation plan validation"""
        # Valid plan
        context = ImplementerContext(
            session_id="test-session",
            implementation_plan="This is a detailed implementation plan with sufficient detail for deployment",
            target_environment="development",
        )
        assert len(context.implementation_plan) >= 20

        # Invalid plan (too short)
        with pytest.raises(ValueError, match="Implementation plan must be at least 20 characters"):
            ImplementerContext(
                session_id="test-session", implementation_plan="Short plan", target_environment="development"
            )

    def test_target_environment_validation(self):
        """Test target environment validation"""
        valid_environments = ["development", "staging", "production", "testing"]

        for environment in valid_environments:
            context = ImplementerContext(
                session_id="test-session",
                implementation_plan="This is a detailed implementation plan with sufficient detail",
                target_environment=environment,
            )
            assert context.target_environment == environment

        # Invalid environment
        with pytest.raises(ValueError, match="Target environment must be one of"):
            ImplementerContext(
                session_id="test-session",
                implementation_plan="This is a detailed implementation plan with sufficient detail",
                target_environment="invalid_environment",
            )


class TestContextFactory:
    """Test context factory functionality"""

    def test_create_planner_context(self):
        """Test creating planner context via factory"""
        context = ContextFactory.create_context(
            AIRole.PLANNER, session_id="factory-test", project_scope="Test project scope", backlog_priority="P1"
        )

        assert isinstance(context, PlannerContext)
        assert context.role == AIRole.PLANNER

    def test_create_coder_context(self):
        """Test creating coder context via factory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            context = ContextFactory.create_context(
                AIRole.CODER, session_id="factory-test", codebase_path=temp_dir, language="python"
            )

            assert isinstance(context, CoderContext)
            assert context.role == AIRole.CODER

    def test_create_researcher_context(self):
        """Test creating researcher context via factory"""
        context = ContextFactory.create_context(
            AIRole.RESEARCHER,
            session_id="factory-test",
            research_topic="Test research topic",
            methodology="literature_review",
        )

        assert isinstance(context, ResearcherContext)
        assert context.role == AIRole.RESEARCHER

    def test_create_implementer_context(self):
        """Test creating implementer context via factory"""
        context = ContextFactory.create_context(
            AIRole.IMPLEMENTER,
            session_id="factory-test",
            implementation_plan="This is a detailed implementation plan with sufficient detail",
            target_environment="development",
        )

        assert isinstance(context, ImplementerContext)
        assert context.role == AIRole.IMPLEMENTER

    def test_invalid_role(self):
        """Test factory with invalid role"""
        with pytest.raises(ValueError, match="Unsupported role"):
            ContextFactory.create_context("invalid_role", session_id="test")

    def test_context_validation(self):
        """Test context validation"""
        context = ContextFactory.create_context(
            AIRole.PLANNER, session_id="validation-test", project_scope="Test project scope", backlog_priority="P1"
        )

        assert ContextFactory.validate_context(context) is True


class TestLegacyContextAdapter:
    """Test backward compatibility adapter"""

    def test_from_dict_planner(self):
        """Test creating planner context from dict"""
        data = {
            "role": "planner",
            "session_id": "adapter-test",
            "project_scope": "Test project scope",
            "backlog_priority": "P1",
        }

        context = LegacyContextAdapter.from_dict(data)
        assert isinstance(context, PlannerContext)
        assert context.role == AIRole.PLANNER

    def test_from_dict_coder(self):
        """Test creating coder context from dict"""
        with tempfile.TemporaryDirectory() as temp_dir:
            data = {"role": "coder", "session_id": "adapter-test", "codebase_path": temp_dir, "language": "python"}

            context = LegacyContextAdapter.from_dict(data)
            assert isinstance(context, CoderContext)
            assert context.role == AIRole.CODER

    def test_from_dict_unknown_role(self):
        """Test handling unknown role"""
        data = {
            "role": "unknown_role",
            "session_id": "adapter-test",
            "project_scope": "Test project scope",
            "backlog_priority": "P1",
        }

        context = LegacyContextAdapter.from_dict(data)
        assert isinstance(context, PlannerContext)  # Should default to planner
        assert context.role == AIRole.PLANNER

    def test_to_dict(self):
        """Test converting context to dict"""
        context = PlannerContext(session_id="dict-test", project_scope="Test project scope", backlog_priority="P1")

        data = LegacyContextAdapter.to_dict(context)
        assert isinstance(data, dict)
        assert data["role"] == "planner"
        assert data["session_id"] == "dict-test"


class TestContextValidationBenchmark:
    """Test performance benchmarking"""

    def test_benchmark_validation_overhead(self):
        """Test validation overhead benchmarking"""
        context = PlannerContext(
            session_id="benchmark-test", project_scope="Test project scope for benchmarking", backlog_priority="P1"
        )

        results = ContextValidationBenchmark.benchmark_validation_overhead(context, iterations=100)

        assert "total_time_ms" in results
        assert "avg_time_ms" in results
        assert "iterations" in results
        assert "overhead_percent" in results
        assert results["iterations"] == 100
        assert results["total_time_ms"] > 0
        assert results["avg_time_ms"] > 0


if __name__ == "__main__":
    pytest.main([__file__])
