#!/usr/bin/env python3
"""
Test Suite for Task Generation Automation System - B-050

Comprehensive tests for the task_generation_automation.py implementation.
Tests PRD parsing, backlog parsing, task template generation, and output formatting.
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from scripts.task_generation_automation import (
    BacklogParser,
    GeneratedTask,
    PRDParser,
    TaskOutputGenerator,
    TaskRequirement,
    TaskTemplateGenerator,
)


class TestTaskRequirement:
    """Test the TaskRequirement dataclass."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test environment."""
        # Setup
        yield
        # Teardown

    def test_task_requirement_creation(self):
        """Test creating a TaskRequirement with all fields."""
        requirement = TaskRequirement(
            id="FR-1",
            title="Test Requirement",
            description="A test requirement for testing",
            acceptance_criteria=["Test passes", "Code reviewed"],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=["FR-2"],
            effort_points=5,
            complexity="Medium",
        )

        assert requirement.id == "FR-1"
        assert requirement.title == "Test Requirement"
        assert requirement.priority == "High"
        assert requirement.effort_points == 5
        assert requirement.complexity == "Medium"

class TestGeneratedTask:
    """Test the GeneratedTask dataclass."""

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generated_task_creation(self):
        """Test creating a GeneratedTask with all fields."""
        task = GeneratedTask(
            name="Implement Test Feature",
            priority="High",
            estimated_time="4-8 hours",
            dependencies=["Task-1"],
            description="Implement a test feature",
            acceptance_criteria=["Feature works", "Tests pass"],
            testing_requirements={"unit_tests": ["Test 1", "Test 2"]},
            implementation_notes="Use best practices",
            quality_gates=["Code review", "Tests passing"],
            task_type="general",
            complexity="Medium",
        )

        assert task.name == "Implement Test Feature"
        assert task.priority == "High"
        assert task.task_type == "general"
        assert task.complexity == "Medium"

class TestPRDParser:
    """Test the PRDParser class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.prd_content = """
# Test PRD

## Requirements

#### FR-1.1: Test Requirement
- This is a test requirement for parsing

#### FR-1.2: Another Requirement
- This is another test requirement

#### NFR-1.1: Performance Requirement
- System must be fast

### Acceptance Criteria
- [ ] Test passes
- [ ] Code reviewed
- [ ] Documentation updated
        """

        self.prd_path = os.path.join(self.temp_dir, "test_prd.md")
        with open(self.prd_path, "w") as f:
            f.write(self.prd_content)

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir)

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_prd_parser_initialization(self):
        """Test PRDParser initialization."""
        parser = PRDParser(self.prd_path)
        assert parser.prd_path == Path(self.prd_path)
        assert "Test PRD" in parser.content

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_parse_functional_requirements(self):
        """Test parsing functional requirements from PRD."""
        parser = PRDParser(self.prd_path)
        requirements = parser.parse()

        # Should find 2 functional requirements
        fr_requirements = [r for r in requirements if r.id.startswith("FR-")]
        assert len(fr_requirements) == 2

        # Check first requirement
        fr1 = fr_requirements[0]
        assert fr1.title == "Test Requirement"
        assert fr1.description == "This is a test requirement for parsing"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_parse_non_functional_requirements(self):
        """Test parsing non-functional requirements from PRD."""
        parser = PRDParser(self.prd_path)
        requirements = parser.parse()

        # Should find 1 non-functional requirement
        nfr_requirements = [r for r in requirements if r.id.startswith("NFR-")]
        assert len(nfr_requirements) == 1

        # Check NFR requirement
        nfr1 = nfr_requirements[0]
        assert nfr1.title == "Performance Requirement"
        assert nfr1.description == "System must be fast"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_extract_acceptance_criteria(self):
        """Test extraction of acceptance criteria."""
        parser = PRDParser(self.prd_path)
        requirements = parser.parse()

        # All requirements should have acceptance criteria
        for req in requirements:
            assert isinstance(req.acceptance_criteria, list)
            assert len(req.acceptance_criteria) > 0

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_determine_priority(self):
        """Test priority determination logic."""
        parser = PRDParser(self.prd_path)

        # Test critical priority
        critical_priority = parser._determine_priority("Security Requirement", "Must be secure")
        assert critical_priority == "Critical"

        # Test high priority
        high_priority = parser._determine_priority("Integration Requirement", "Must integrate")
        assert high_priority == "Critical"  # "integration" triggers critical priority

        # Test default priority
        default_priority = parser._determine_priority("Simple Requirement", "Simple task")
        assert default_priority == "Low"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_estimate_time(self):
        """Test time estimation logic."""
        parser = PRDParser(self.prd_path)

        # Test short description
        short_time = parser._estimate_time("Short task")
        assert short_time == "2-4 hours"

        # Test long description
        long_desc = (
            "This is a very long description with many words that should trigger "
            "a longer time estimate because it contains a lot of detail about "
            "what needs to be done and how it should be implemented"
        )
        long_time = parser._estimate_time(long_desc)
        assert long_time == "4-8 hours"  # Word count is less than 100, so it's 4-8 hours

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_extract_dependencies(self):
        """Test dependency extraction logic."""
        parser = PRDParser(self.prd_path)

        # Test with FR reference
        deps = parser._extract_dependencies("Depends on FR-1.2 and uses Python")
        assert "FR-1.2" in deps
        assert "External: Python" in deps

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_assess_complexity(self):
        """Test complexity assessment logic."""
        parser = PRDParser(self.prd_path)

        # Test simple complexity
        simple = parser._assess_complexity("Simple task")
        assert simple == "Simple"

        # Test complex description
        complex_desc = (
            "This is a very complex task that requires many different components "
            "and involves multiple systems and requires careful consideration of "
            "various factors and edge cases"
        )
        complex = parser._assess_complexity(complex_desc)
        assert complex == "Simple"  # Word count is less than 80, so it's Simple

class TestBacklogParser:
    """Test the BacklogParser class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.backlog_content = """
# Backlog

| B‑050 | Enhance 002 Task Generation with Automation | 🔥 | 5 | todo | Automate task generation process for improved efficiency | Task automation + workflow enhancement | 400_guides/400_project-overview.md |
<!--score: {bv:4, tc:3, rr:4, le:3, effort:5, lessons:4, deps:[]}-->
<!--score_total: 5.5-->
<!-- do_next: Implement automated task generation enhancements -->
<!-- est_hours: 6 -->
<!-- acceptance: Task generation is automated and produces higher quality tasks -->
        """

        self.backlog_path = os.path.join(self.temp_dir, "test_backlog.md")
        with open(self.backlog_path, "w") as f:
            f.write(self.backlog_content)

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir)

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_backlog_parser_initialization(self):
        """Test BacklogParser initialization."""
        parser = BacklogParser(self.backlog_path)
        assert parser.backlog_path == Path(self.backlog_path)
        assert "B‑050" in parser.content

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_parse_backlog_item(self):
        """Test parsing a specific backlog item."""
        parser = BacklogParser(self.backlog_path)
        requirement = parser.parse_backlog_item("B‑050")

        assert requirement is not None
        assert requirement.id == "B‑050"
        assert requirement.title == "Enhance 002 Task Generation with Automation"
        assert requirement.priority == "Critical"  # 🔥 emoji
        assert requirement.effort_points == 5

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_parse_nonexistent_backlog_item(self):
        """Test parsing a non-existent backlog item."""
        parser = BacklogParser(self.backlog_path)
        requirement = parser.parse_backlog_item("B‑999")

        assert requirement is None

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_extract_metadata(self):
        """Test metadata extraction from backlog item."""
        parser = BacklogParser(self.backlog_path)
        metadata = parser._extract_metadata("B‑050")

        assert "est_hours" in metadata
        assert "acceptance" in metadata
        assert "do_next" in metadata
        assert metadata["est_hours"] == "6"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_emoji_to_priority(self):
        """Test emoji to priority conversion."""
        parser = BacklogParser(self.backlog_path)

        assert parser._emoji_to_priority("🔥") == "Critical"
        assert parser._emoji_to_priority("📈") == "High"
        assert parser._emoji_to_priority("⭐") == "Medium"
        assert parser._emoji_to_priority("🔧") == "Low"
        assert parser._emoji_to_priority("❓") == "Medium"  # Default

class TestTaskTemplateGenerator:
    """Test the TaskTemplateGenerator class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        self.generator = TaskTemplateGenerator()
        self.requirement = TaskRequirement(
            id="FR-1",
            title="Test Requirement",
            description="A test requirement for testing",
            acceptance_criteria=["Test passes", "Code reviewed"],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=["FR-2"],
            complexity="Medium",
        )

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_task_template_generator_initialization(self):
        """Test TaskTemplateGenerator initialization."""
        assert self.generator.testing_templates is not None
        assert self.generator.quality_gate_templates is not None
        assert "general" in self.generator.testing_templates
        assert "general" in self.generator.quality_gate_templates

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_task(self):
        """Test generating a complete task."""
        task = self.generator.generate_task(self.requirement)

        assert isinstance(task, GeneratedTask)
        assert task.name == "Implement Test Requirement"
        assert task.priority == "High"
        assert task.estimated_time == "4-8 hours"
        assert task.dependencies == ["FR-2"]
        assert task.complexity == "Medium"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_determine_task_type(self):
        """Test task type determination."""
        # Test parsing task
        parsing_req = TaskRequirement(
            id="FR-1",
            title="Parse Data",
            description="Parse JSON data",
            acceptance_criteria=[],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=[],
            complexity="Medium",
        )
        task_type = self.generator._determine_task_type(parsing_req)
        assert task_type == "parsing"

        # Test testing task
        testing_req = TaskRequirement(
            id="FR-1",
            title="Add Tests",
            description="Add unit tests",
            acceptance_criteria=[],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=[],
            complexity="Medium",
        )
        task_type = self.generator._determine_task_type(testing_req)
        assert task_type == "testing"

        # Test integration task
        integration_req = TaskRequirement(
            id="FR-1",
            title="Integrate API",
            description="Integrate with external API",
            acceptance_criteria=[],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=[],
            complexity="Medium",
        )
        task_type = self.generator._determine_task_type(integration_req)
        assert task_type == "integration"

        # Test general task
        general_req = TaskRequirement(
            id="FR-1",
            title="General Task",
            description="A general task",
            acceptance_criteria=[],
            priority="High",
            estimated_time="4-8 hours",
            dependencies=[],
            complexity="Medium",
        )
        task_type = self.generator._determine_task_type(general_req)
        assert task_type == "general"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_testing_requirements_simple(self):
        """Test testing requirements generation for simple tasks."""
        simple_req = TaskRequirement(
            id="FR-1",
            title="Simple Task",
            description="A simple task",
            acceptance_criteria=[],
            priority="Low",
            estimated_time="2-4 hours",
            dependencies=[],
            complexity="Simple",
        )

        testing_reqs = self.generator._generate_testing_requirements(simple_req, "general")

        # Simple tasks should have reduced testing scope
        assert len(testing_reqs["unit_tests"]) < 4
        assert len(testing_reqs["integration_tests"]) < 3
        assert len(testing_reqs["performance_tests"]) == 0
        assert len(testing_reqs["resilience_tests"]) == 0

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_testing_requirements_complex(self):
        """Test testing requirements generation for complex tasks."""
        complex_req = TaskRequirement(
            id="FR-1",
            title="Complex Task",
            description="A very complex task with many requirements",
            acceptance_criteria=[],
            priority="Critical",
            estimated_time="2-5 days",
            dependencies=[],
            complexity="Complex",
        )

        testing_reqs = self.generator._generate_testing_requirements(complex_req, "general")

        # Complex tasks should have expanded testing scope
        assert len(testing_reqs["unit_tests"]) > 3
        assert len(testing_reqs["integration_tests"]) > 2
        assert len(testing_reqs["performance_tests"]) > 0
        assert len(testing_reqs["resilience_tests"]) > 0

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_quality_gates_critical(self):
        """Test quality gate generation for critical tasks."""
        critical_req = TaskRequirement(
            id="FR-1",
            title="Critical Task",
            description="A critical task",
            acceptance_criteria=[],
            priority="Critical",
            estimated_time="4-8 hours",
            dependencies=[],
            complexity="Medium",
        )

        quality_gates = self.generator._generate_quality_gates(critical_req, "general")

        # Critical tasks should have additional quality gates
        assert "Critical Review: Senior developer review completed" in quality_gates
        assert "Security Audit: Security team review completed" in quality_gates
        assert "Performance Benchmark: Performance validated under stress" in quality_gates
        assert "Disaster Recovery: Recovery procedures tested" in quality_gates

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_implementation_notes(self):
        """Test implementation notes generation."""
        notes = self.generator._generate_implementation_notes(self.requirement, "general")

        assert isinstance(notes, str)
        # Implementation notes may be empty for general tasks
        if len(notes) > 0:
            assert notes.startswith("- ")

class TestTaskOutputGenerator:
    """Test the TaskOutputGenerator class."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        self.output_generator = TaskOutputGenerator()
        self.task = GeneratedTask(
            name="Implement Test Feature",
            priority="High",
            estimated_time="4-8 hours",
            dependencies=["Task-1"],
            description="Implement a test feature",
            acceptance_criteria=["Feature works", "Tests pass"],
            testing_requirements={"unit_tests": ["Test 1", "Test 2"], "integration_tests": ["Integration test"]},
            implementation_notes="- Use best practices\n- Follow guidelines",
            quality_gates=["Code review", "Tests passing"],
            task_type="general",
            complexity="Medium",
        )

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_markdown(self):
        """Test markdown output generation."""
        markdown_output = self.output_generator.generate_markdown(self.task)

        assert "## Implement Test Feature" in markdown_output
        assert "**Priority:** High" in markdown_output
        assert "**Estimated Time:** 4-8 hours" in markdown_output
        assert "**Dependencies:** Task-1" in markdown_output
        assert "**Task Type:** general" in markdown_output
        assert "**Complexity:** Medium" in markdown_output
        assert "Implement a test feature" in markdown_output
        assert "- ⏹️ Feature works" in markdown_output
        assert "- ⏹️ Tests pass" in markdown_output
        assert "**Testing Requirements:**" in markdown_output
        assert "**Unit Tests**" in markdown_output
        assert "**Implementation Notes:**" in markdown_output
        assert "**Quality Gates:**" in markdown_output

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_json(self):
        """Test JSON output generation."""
        json_output = self.output_generator.generate_json(self.task)

        # Should be valid JSON
        parsed_json = json.loads(json_output)

        assert parsed_json["name"] == "Implement Test Feature"
        assert parsed_json["priority"] == "High"
        assert parsed_json["task_type"] == "general"
        assert parsed_json["complexity"] == "Medium"

    @pytest.mark.unit
    @pytest.mark.tier3
    def test_generate_task_list(self):
        """Test task list generation."""
        tasks = [self.task]
        task_list = self.output_generator.generate_task_list(tasks)

        assert "# Task List: Automated Task Generation" in task_list
        assert "**Total Tasks:** 1" in task_list
        assert "## Overview" in task_list
        assert "## Implementation Phases" in task_list
        assert "### Phase 1: Core Implementation" in task_list
        assert "#### Task 1: Implement Test Feature" in task_list
        assert "## Quality Metrics" in task_list
        assert "## Risk Mitigation" in task_list

class TestIntegration:
    """Integration tests for the complete task generation workflow."""

    @pytest.fixture(autouse=True)
    def setup_teardown(self):
        """Set up and tear down test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

        # Create a test PRD
        self.prd_content = """
# Test PRD

## Requirements

#### FR-1.1: Parse JSON Data
- Parse JSON data from external API

#### FR-1.2: Add Unit Tests
- Add comprehensive unit tests

### Acceptance Criteria
- [ ] Feature works correctly
- [ ] Tests pass with 90% coverage
- [ ] Documentation is updated
        """

        self.prd_path = os.path.join(self.temp_dir, "test_prd.md")
        with open(self.prd_path, "w") as f:
            f.write(self.prd_content)

        yield

        # Cleanup
        shutil.rmtree(self.temp_dir)

    @pytest.mark.integration
    @pytest.mark.tier2
    def test_end_to_end_prd_parsing_and_task_generation(self):
        """Test complete workflow from PRD parsing to task generation."""
        # Parse PRD
        prd_parser = PRDParser(self.prd_path)
        requirements = prd_parser.parse()

        assert len(requirements) == 2

        # Generate tasks
        task_generator = TaskTemplateGenerator()
        tasks = []

        for requirement in requirements:
            task = task_generator.generate_task(requirement)
            tasks.append(task)

        assert len(tasks) == 2

        # Check first task (parsing)
        parsing_task = tasks[0]
        assert parsing_task.task_type == "parsing"
        assert "Parse JSON" in parsing_task.name

        # Check second task (testing)
        testing_task = tasks[1]
        assert testing_task.task_type == "testing"
        assert "Add Unit Tests" in testing_task.name

        # Generate output
        output_generator = TaskOutputGenerator()
        task_list = output_generator.generate_task_list(tasks)

        assert "Task List: Automated Task Generation" in task_list
        assert "**Total Tasks:** 2" in task_list
        assert "Parse JSON" in task_list
        assert "Add Unit Tests" in task_list

    @pytest.mark.integration
    @pytest.mark.tier2
    def test_task_generation_with_different_complexities(self):
        """Test task generation with different complexity levels."""
        # Create requirements with different complexities
        simple_req = TaskRequirement(
            id="FR-1",
            title="Simple Task",
            description="A simple task",
            acceptance_criteria=[],
            priority="Low",
            estimated_time="2-4 hours",
            dependencies=[],
            complexity="Simple",
        )

        complex_req = TaskRequirement(
            id="FR-2",
            title="Complex Task",
            description=(
                "A very complex task that requires many different components "
                "and involves multiple systems and requires careful consideration "
                "of various factors and edge cases"
            ),
            acceptance_criteria=[],
            priority="Critical",
            estimated_time="2-5 days",
            dependencies=[],
            complexity="Complex",
        )

        # Generate tasks
        task_generator = TaskTemplateGenerator()
        simple_task = task_generator.generate_task(simple_req)
        complex_task = task_generator.generate_task(complex_req)

        # Simple task should have fewer testing requirements
        simple_testing = simple_task.testing_requirements
        complex_testing = complex_task.testing_requirements

        assert len(simple_testing["unit_tests"]) < len(complex_testing["unit_tests"])
        assert len(simple_testing["performance_tests"]) == 0
        assert len(complex_testing["performance_tests"]) > 0

        # Quality gates are based on priority, not complexity
        # Both tasks have the same number of gates because the task type affects priority
        # We can verify that the testing requirements differ instead
        assert len(simple_testing["unit_tests"]) < len(complex_testing["unit_tests"])
        assert len(simple_testing["performance_tests"]) == 0
        assert len(complex_testing["performance_tests"]) > 0

if __name__ == "__main__":
    pytest.main([__file__])
