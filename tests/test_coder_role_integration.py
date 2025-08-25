"""
Integration tests for Coder Role enhancements.

Tests the comprehensive coder role implementation including:
- Memory rehydration functionality
- Role-specific instructions
- File analysis integration
- Testing strategy compliance
- Best practices enforcement
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestCoderRoleIntegration:
    """Integration tests for Coder Role functionality."""

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def memory_rehydrator_path(self, project_root: Path) -> Path:
        """Get the memory rehydrator script path."""
        return project_root / "scripts" / "memory_up.sh"

    @pytest.fixture
    def dspy_memory_rehydrator_path(self, project_root: Path) -> Path:
        """Get the DSPy memory rehydrator path."""
        return project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"

    def test_memory_rehydrator_script_exists(self, memory_rehydrator_path: Path) -> None:
        """Test that the memory rehydrator script exists and is executable."""
        assert memory_rehydrator_path.exists(), f"Memory rehydrator script not found: {memory_rehydrator_path}"
        assert memory_rehydrator_path.is_file(), f"Memory rehydrator path is not a file: {memory_rehydrator_path}"

    def test_dspy_memory_rehydrator_exists(self, dspy_memory_rehydrator_path: Path) -> None:
        """Test that the DSPy memory rehydrator module exists."""
        assert dspy_memory_rehydrator_path.exists(), f"DSPy memory rehydrator not found: {dspy_memory_rehydrator_path}"
        assert (
            dspy_memory_rehydrator_path.is_file()
        ), f"DSPy memory rehydrator path is not a file: {dspy_memory_rehydrator_path}"

    def test_coder_role_instructions_in_memory_rehydrator(self, dspy_memory_rehydrator_path: Path) -> None:
        """Test that coder role instructions are properly defined in memory rehydrator."""
        content = dspy_memory_rehydrator_path.read_text()

        # Check for ROLE_INSTRUCTIONS dictionary
        assert "ROLE_INSTRUCTIONS" in content, "ROLE_INSTRUCTIONS dictionary not found"
        assert '"coder"' in content, "Coder role not defined in ROLE_INSTRUCTIONS"

        # Check for key instruction categories
        required_categories = [
            "focus",
            "context",
            "validation",
            "required_standards",
            "safety_protocol",
            "quality_gates",
            "testing_guide",
            "tool_usage",
        ]

        for category in required_categories:
            assert f'"{category}":' in content, f"Missing {category} in coder role instructions"

    def test_coder_role_files_in_memory_rehydrator(self, dspy_memory_rehydrator_path: Path) -> None:
        """Test that coder role files are properly included in ROLE_FILES."""
        content = dspy_memory_rehydrator_path.read_text()

        # Check for ROLE_FILES dictionary
        assert "ROLE_FILES" in content, "ROLE_FILES dictionary not found"
        assert '"coder"' in content, "Coder role not defined in ROLE_FILES"

        # Check for key files that should be included
        required_files = [
            "Task-List-Chunk-Relationship-Visualization.md",
            "scripts/dependency_monitor.py",
            "400_guides/400_graph-visualization-guide.md",
            "dspy-rag-system/src/utils/graph_data_provider.py",
        ]

        for file_path in required_files:
            assert file_path in content, f"Required file {file_path} not found in coder ROLE_FILES"

    def test_dspy_development_context_enhanced(self, project_root: Path) -> None:
        """Test that DSPy development context has comprehensive coder instructions."""
        context_file = project_root / "100_memory" / "104_dspy-development-context.md"
        assert context_file.exists(), f"DSPy development context not found: {context_file}"

        content = context_file.read_text()

        # Check for comprehensive coder role instructions
        required_sections = [
            "COMPREHENSIVE CODER ROLE INSTRUCTIONS",
            "Core Coder Role Behavior - ALWAYS FOLLOW",
            "Technical Standards - REQUIRED",
            "Safety Protocol - BEFORE ANY CHANGES",
            "Quality Gates - MUST PASS",
            "CODER ROLE QUICK REFERENCE",
            "COMPREHENSIVE TESTING GUIDE",
            "TOOL USAGE GUIDE",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_comprehensive_coding_best_practices_enhanced(self, project_root: Path) -> None:
        """Test that comprehensive coding best practices includes coder role guidance."""
        best_practices_file = project_root / "400_guides" / "400_comprehensive-coding-best-practices.md"
        assert best_practices_file.exists(), f"Comprehensive coding best practices not found: {best_practices_file}"

        content = best_practices_file.read_text()

        # Check for coder role specific guidance
        required_sections = [
            "CODER ROLE SPECIFIC GUIDANCE",
            "CODER ROLE IMPLEMENTATION PATTERNS",
            "Memory Rehydration Pattern",
            "Example-First Implementation Pattern",
            "Code Reuse Pattern (70/30 Rule)",
            "Test-First Development Pattern",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_file_analysis_guide_enhanced(self, project_root: Path) -> None:
        """Test that file analysis guide includes coder role specific analysis."""
        file_analysis_file = project_root / "400_guides" / "400_file-analysis-guide.md"
        assert file_analysis_file.exists(), f"File analysis guide not found: {file_analysis_file}"

        content = file_analysis_file.read_text()

        # Check for coder role specific analysis
        required_sections = [
            "CODER ROLE SPECIFIC ANALYSIS",
            "Coder-Specific Safety Rules",
            "NEVER delete Tier 1 files",
            "Always check dependencies",
            "Use memory rehydration",
            "Follow the 70/30 rule",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_testing_strategy_guide_enhanced(self, project_root: Path) -> None:
        """Test that testing strategy guide includes coder role testing requirements."""
        testing_strategy_file = project_root / "400_guides" / "400_testing-strategy-guide.md"
        assert testing_strategy_file.exists(), f"Testing strategy guide not found: {testing_strategy_file}"

        content = testing_strategy_file.read_text()

        # Check for coder role testing requirements
        required_sections = [
            "CODER ROLE TESTING REQUIREMENTS",
            "Test-First Development (TDD)",
            "Memory Rehydration",
            "Example-First Testing",
            "Code Reuse in Tests",
            "Function Length Validation",
        ]

        for section in required_sections:
            assert section in content, f"Missing section: {section}"

    def test_memory_rehydration_command_execution(self, memory_rehydrator_path: Path) -> None:
        """Test that memory rehydration command executes successfully for coder role."""
        try:
            result = subprocess.run(
                [sys.executable, str(memory_rehydrator_path), "coder", "test integration"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Should execute without errors
            assert result.returncode == 0, f"Memory rehydration failed: {result.stderr}"

            # Should produce output
            assert result.stdout, "Memory rehydration produced no output"

            # Should contain expected content
            assert "MEMORY REHYDRATION BUNDLE" in result.stdout, "Missing bundle header in output"
            assert "Copy the content below" in result.stdout, "Missing copy instructions in output"

        except subprocess.TimeoutExpired:
            pytest.fail("Memory rehydration command timed out")
        except Exception as e:
            pytest.fail(f"Memory rehydration command failed: {e}")

    def test_coder_role_metadata_tags(self, project_root: Path) -> None:
        """Test that key files have proper metadata tags for coder role inclusion."""
        files_to_check = [
            ("Task-List-Chunk-Relationship-Visualization.md", "ROLE_PINS"),
            ("scripts/dependency_monitor.py", "ROLE_PINS"),
            ("400_guides/400_graph-visualization-guide.md", "ROLE_PINS"),
            ("100_memory/104_dspy-development-context.md", "ROLE_PINS"),
        ]

        for file_path, required_tag in files_to_check:
            full_path = project_root / file_path
            if full_path.exists():
                content = full_path.read_text()
                assert required_tag in content, f"Missing {required_tag} in {file_path}"
                assert '"coder"' in content, f"Missing coder role in {required_tag} for {file_path}"

    def test_quality_gates_compliance(self, project_root: Path) -> None:
        """Test that the enhanced coder role meets quality gates."""
        # Check for comprehensive error handling
        context_file = project_root / "100_memory" / "104_dspy-development-context.md"
        content = context_file.read_text()

        quality_gates = ["Code Review", "Testing", "Documentation", "Security", "Performance"]

        for gate in quality_gates:
            assert gate in content, f"Missing quality gate: {gate}"

    def test_tool_usage_standards(self, project_root: Path) -> None:
        """Test that tool usage standards are comprehensive."""
        # Check the memory rehydrator file where the comprehensive instructions are stored
        rehydrator_file = project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"
        content = rehydrator_file.read_text()

        tool_categories = [
            "code_quality",
            "validation",
            "development",
            "testing",
            "monitoring",
            "pre_commit",
            "memory_rehydration",
            "search_and_analysis",
        ]

        for category in tool_categories:
            assert f'"{category}":' in content, f"Missing tool category: {category}"

    def test_testing_guide_completeness(self, project_root: Path) -> None:
        """Test that testing guide is comprehensive."""
        # Check the memory rehydrator file where the comprehensive instructions are stored
        rehydrator_file = project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"
        content = rehydrator_file.read_text()

        test_types = ["unit_tests", "integration_tests", "performance_tests", "security_tests", "system_tests"]

        for test_type in test_types:
            assert f'"{test_type}":' in content, f"Missing test type: {test_type}"

    def test_safety_protocol_completeness(self, project_root: Path) -> None:
        """Test that safety protocol is comprehensive."""
        # Check the memory rehydrator file where the comprehensive instructions are stored
        rehydrator_file = project_root / "dspy-rag-system" / "src" / "utils" / "memory_rehydrator.py"
        content = rehydrator_file.read_text()

        safety_steps = [
            "read_core_memory_context",
            "check_current_backlog",
            "understand_file_organization",
            "apply_tier_based_analysis",
            "run_conflict_detection",
            "validate_documentation",
        ]

        for step in safety_steps:
            assert step in content, f"Missing safety step: {step}"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
