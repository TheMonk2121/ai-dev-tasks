#!/usr/bin/env python3
"""
Test Suite for Documentation Coherence Validation System - B-060

Comprehensive tests for the doc_coherence_validator.py implementation.
Tests all validation tasks and edge cases.
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from doc_coherence_validator import DocCoherenceValidator


class TestDocCoherenceValidator:
    """Test cases for DocCoherenceValidator class."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.validator = DocCoherenceValidator(dry_run=True)

        # Create test files
        self.create_test_files()

        yield

        # Clean up test environment
        shutil.rmtree(self.test_dir)

    def create_test_files(self):
        """Create test markdown files for validation."""
        test_files = {
            "100_test-memory-context.md": """# Test Memory Context
<!-- CONTEXT_REFERENCE: 400_test-system-overview.md -->
<!-- BACKLOG_REFERENCE: 000_test-backlog.md -->
Current Sprint: B-001
""",
            "400_test-system-overview.md": """# Test System Overview
System architecture includes DSPy and PostgreSQL.
""",
            "000_test-backlog.md": """# Test Backlog
| B-001 | Test Item | 🔥 | 2 | todo | Test description | Tech | None |
""",
            "200_test-naming-conventions.md": """# Test Naming Conventions
Valid three-digit prefix file.
""",
            "invalid_file.md": """# Invalid File
This file has no three-digit prefix.
""",
            "README.md": """# Test README
This is a valid README file.
""",
        }

        for filename, content in test_files.items():
            file_path = Path(self.test_dir) / filename
            with open(file_path, "w") as f:
                f.write(content)

    def test_initialization(self):
        """Test validator initialization."""
        validator = DocCoherenceValidator(dry_run=True)
        assert validator.dry_run
        assert isinstance(validator.validation_results, dict)
        assert isinstance(validator.errors, list)
        assert isinstance(validator.warnings, list)

    def test_should_exclude(self):
        """Test file exclusion logic."""
        # Test excluded patterns
        excluded_files = [
            "venv/test.md",
            "node_modules/test.md",
            "docs/legacy/test.md",
            "__pycache__/test.md",
            ".git/test.md",
        ]

        for file_path in excluded_files:
            path = Path(file_path)
            assert self.validator._should_exclude(path)

        # Test included files
        included_files = ["100_test.md", "400_test.md", "README.md"]

        for file_path in included_files:
            path = Path(file_path)
            assert not self.validator._should_exclude(path)

    def test_read_file(self):
        """Test file reading functionality."""
        # Test successful read
        test_file = Path(self.test_dir) / "100_test-memory-context.md"
        content = self.validator.read_file(test_file)
        assert content is not None
        assert "Test Memory Context" in content

        # Test non-existent file
        non_existent = Path(self.test_dir) / "non_existent.md"
        content = self.validator.read_file(non_existent)
        assert content is None
        assert "non_existent.md" in str(self.validator.errors[-1])

    def test_write_file(self):
        """Test file writing functionality."""
        test_file = Path(self.test_dir) / "test_write.md"
        test_content = "Test content for writing"

        # Test dry-run write
        result = self.validator.write_file(test_file, test_content)
        assert result
        assert not test_file.exists()  # Should not actually write in dry-run

        # Test actual write
        self.validator.dry_run = False
        result = self.validator.write_file(test_file, test_content)
        assert result
        assert test_file.exists()

        with open(test_file) as f:
            content = f.read()
        assert content == test_content

    @patch("doc_coherence_validator.Path")
    def test_validate_cross_references(self, mock_path):
        """Test cross-reference validation."""
        # Mock file structure
        mock_path.return_value.exists.return_value = True
        mock_path.return_value.suffix = ".md"

        # Test with valid references
        with patch.object(
            self.validator, "markdown_files", [Path("100_test-memory-context.md"), Path("400_test-system-overview.md")]
        ):
            with patch.object(self.validator, "read_file") as mock_read:
                mock_read.side_effect = [
                    "<!-- CONTEXT_REFERENCE: 400_test-system-overview.md -->",
                    "System overview content",
                ]

                result = self.validator.task_1_validate_cross_references()
                assert result

        # Test with broken references
        with patch.object(self.validator, "markdown_files", [Path("100_test-memory-context.md")]):
            with patch.object(self.validator, "read_file") as mock_read:
                mock_read.return_value = "<!-- CONTEXT_REFERENCE: non_existent.md -->"

                with patch.object(Path, "exists") as mock_exists:
                    mock_exists.return_value = False

                    result = self.validator.task_1_validate_cross_references()
                    assert not result

    def test_validate_file_naming_conventions(self):
        """Test file naming convention validation."""
        # Test with valid files
        with patch.object(
            self.validator,
            "markdown_files",
            [Path("100_test-memory-context.md"), Path("200_test-naming-conventions.md"), Path("README.md")],
        ):
            result = self.validator.task_2_validate_file_naming_conventions()
            assert result

        # Test with invalid files
        with patch.object(
            self.validator, "markdown_files", [Path("invalid_file.md"), Path("100_test-memory-context.md")]
        ):
            result = self.validator.task_2_validate_file_naming_conventions()
            assert not result

    def test_validate_backlog_references(self):
        """Test backlog reference validation."""
        # Test with valid references
        with patch.object(self.validator, "read_file") as mock_read:
            mock_read.side_effect = [
                "| B-001 | Test Item |",  # Backlog content
                "Reference to B-001 in documentation",  # Doc content
            ]

            result = self.validator.task_3_validate_backlog_references()
            assert result

        # Test with invalid references
        with patch.object(self.validator, "read_file") as mock_read:
            mock_read.side_effect = [
                "| B-001 | Test Item |",  # Backlog content
                "Reference to B-999 in documentation",  # Doc content with invalid ref
            ]

            result = self.validator.task_3_validate_backlog_references()
            assert not result

    def test_validate_memory_context_coherence(self):
        """Test memory context coherence validation."""
        # Test with coherent content
        with patch.object(self.validator, "read_file") as mock_read:
            mock_read.side_effect = [
                "Current Sprint: B-001",  # Memory context
                "| B-001 | Test Item |",  # Backlog
                "System architecture includes DSPy",  # System overview
            ]

            result = self.validator.task_4_validate_memory_context_coherence()
            assert result

        # Test with incoherent content
        with patch.object(self.validator, "read_file") as mock_read:
            mock_read.side_effect = [
                "Current Sprint: B-999",  # Memory context with invalid ref
                "| B-001 | Test Item |",  # Backlog
                "System architecture",  # System overview
            ]

            result = self.validator.task_4_validate_memory_context_coherence()
            assert not result

    @patch("doc_coherence_validator.subprocess.run")
    def test_cursor_ai_semantic_validation(self, mock_run):
        """Test Cursor AI semantic validation."""
        # Mock Cursor AI as available
        self.validator.cursor_ai_enabled = True

        # Mock successful Cursor AI response
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = '{"issues": []}'

        with patch.object(self.validator, "priority_files", {"memory_context": ["100_test-memory-context.md"]}):
            with patch.object(Path, "exists") as mock_exists:
                mock_exists.return_value = True

                with patch.object(self.validator, "read_file") as mock_read:
                    mock_read.return_value = "Test content"

                    result = self.validator.task_5_cursor_ai_semantic_validation()
                    assert result

        # Test with Cursor AI issues
        mock_run.return_value.stdout = '{"issues": [{"type": "warning", "description": "Test issue"}]}'

        with patch.object(self.validator, "priority_files", {"memory_context": ["100_test-memory-context.md"]}):
            with patch.object(Path, "exists") as mock_exists:
                mock_exists.return_value = True

                with patch.object(self.validator, "read_file") as mock_read:
                    mock_read.return_value = "Test content"

                    result = self.validator.task_5_cursor_ai_semantic_validation()
                    assert not result

    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Set up test data
        self.validator.validation_results = {"Cross-reference validation": True, "File naming conventions": False}
        self.validator.errors = ["Test error"]
        self.validator.warnings = ["Test warning"]

        with patch.object(Path, "mkdir"):
            with patch("builtins.open", create=True) as mock_open:
                mock_file = MagicMock()
                mock_open.return_value.__enter__.return_value = mock_file

                result = self.validator.task_6_generate_validation_report()
                assert result

                # Verify report was written
                mock_open.assert_called()
                mock_file.write.assert_called()

    def test_run_all_validations(self):
        """Test running all validation tasks."""
        # Mock all tasks to return True
        with (
            patch.object(self.validator, "task_1_validate_cross_references", return_value=True),
            patch.object(self.validator, "task_2_validate_file_naming_conventions", return_value=True),
            patch.object(self.validator, "task_3_validate_backlog_references", return_value=True),
            patch.object(self.validator, "task_4_validate_memory_context_coherence", return_value=True),
            patch.object(self.validator, "task_5_cursor_ai_semantic_validation", return_value=True),
            patch.object(self.validator, "task_6_generate_validation_report", return_value=True),
        ):

            result = self.validator.run_all_validations()
            assert result
            assert len(self.validator.validation_results) == 6

        # Test with some failures
        with (
            patch.object(self.validator, "task_1_validate_cross_references", return_value=False),
            patch.object(self.validator, "task_2_validate_file_naming_conventions", return_value=True),
            patch.object(self.validator, "task_3_validate_backlog_references", return_value=True),
            patch.object(self.validator, "task_4_validate_memory_context_coherence", return_value=True),
            patch.object(self.validator, "task_5_cursor_ai_semantic_validation", return_value=True),
            patch.object(self.validator, "task_6_generate_validation_report", return_value=True),
        ):

            result = self.validator.run_all_validations()
            assert not result

    def test_cursor_ai_availability_check(self):
        """Test Cursor AI availability checking."""
        # Test when Cursor AI is available
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0

            result = self.validator._check_cursor_ai_availability()
            assert result

        # Test when Cursor AI is not available
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 1

            result = self.validator._check_cursor_ai_availability()
            assert not result

    def test_validate_file_with_cursor_ai(self):
        """Test Cursor AI file validation."""
        test_file = Path("test.md")

        # Test successful validation
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"issues": []}'

            with patch.object(self.validator, "read_file") as mock_read:
                mock_read.return_value = "Test content"

                issues = self.validator._validate_file_with_cursor_ai(test_file, "test_category")
                assert len(issues) == 0

        # Test validation with issues
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = '{"issues": [{"type": "warning", "description": "Test issue"}]}'

            with patch.object(self.validator, "read_file") as mock_read:
                mock_read.return_value = "Test content"

                issues = self.validator._validate_file_with_cursor_ai(test_file, "test_category")
                assert len(issues) == 1
                assert issues[0]["issue"] == "Test issue"


class TestDocCoherenceValidatorIntegration:
    """Integration tests for the validation system."""

    def setUp(self):
        """Set up integration test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create a minimal project structure
        self.create_project_structure()

    def tearDown(self):
        """Clean up integration test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_project_structure(self):
        """Create a minimal project structure for testing."""
        # Create test files
        files = {
            "000_backlog.md": """# Test Backlog
| B-001 | Test Item | 🔥 | 2 | todo | Test description | Tech | None |
""",
            "100_cursor-memory-context.md": """# Test Memory Context
<!-- CONTEXT_REFERENCE: 400_system-overview.md -->
Current Sprint: B-001
""",
            "400_system-overview.md": """# Test System Overview
System architecture includes DSPy and PostgreSQL.
""",
            "400_project-overview.md": """# Test Project Overview
Project overview content.
""",
            "400_context-priority-guide.md": """# Test Context Priority Guide
Context priority guide content.
""",
        }

        for filename, content in files.items():
            with open(filename, "w") as f:
                f.write(content)

    def test_full_validation_workflow(self):
        """Test the complete validation workflow."""
        # Copy validator script to test directory
        validator_script = Path(__file__).parent.parent / "scripts" / "doc_coherence_validator.py"
        if validator_script.exists():
            shutil.copy(validator_script, self.test_dir)

            # Import and run validator
            from doc_coherence_validator import DocCoherenceValidator

            validator = DocCoherenceValidator(dry_run=True)
            result = validator.run_all_validations()

            # Should pass with our test structure
            assert result

    def test_validation_with_issues(self):
        """Test validation with known issues."""
        # Create a file with naming convention issues
        with open("invalid_file.md", "w") as f:
            f.write("# Invalid File\nNo three-digit prefix.")

        # Copy validator script
        validator_script = Path(__file__).parent.parent / "scripts" / "doc_coherence_validator.py"
        if validator_script.exists():
            shutil.copy(validator_script, self.test_dir)

            from doc_coherence_validator import DocCoherenceValidator

            validator = DocCoherenceValidator(dry_run=True)
            result = validator.run_all_validations()

            # Should fail due to naming convention issues
            assert not result


if __name__ == "__main__":
    pytest.main([__file__])


# --- B-100 and B-102 Test Cases ---
import textwrap

from doc_coherence_validator import validate_backlog


def write_backlog(tmp_path: Path, content: str) -> Path:
    """Helper to write test backlog content."""
    p = tmp_path / "000_backlog.md"
    p.write_text(textwrap.dedent(content), encoding="utf-8")
    return p


def test_b100_b102_pass(tmp_path: Path, monkeypatch):
    """Test PASS case: item with multi-rep + cross-refs."""
    # env: strict features on
    monkeypatch.setenv("VALIDATOR_REQUIRE_MULTI_REP", "1")
    monkeypatch.setenv("VALIDATOR_REQUIRE_XREF", "1")
    monkeypatch.setenv("VALIDATOR_STRICT_STALE_XREF", "0")

    # create referenced file to satisfy xref existence
    ref_file = tmp_path / "500_reference-cards.md"
    ref_file.write_text("# rag-lessons-from-jerry\ncontent", encoding="utf-8")

    content = """
    | B-100 | Multi-rep demo | 🔄 | 5 | todo | Example with summary+refs |
    <!--score: {"bv":4,"tc":3,"rr":3,"le":5,"lessons":4,"effort":3,"deps":[]}-->
    <!--score_total: 3.7-->
    <!-- lessons_applied: ["500_reference-cards.md#rag-lessons-from-jerry"] -->
    """

    path = write_backlog(tmp_path, content)
    code, report, summary = validate_backlog(str(path))
    assert code == 0, f"Expected PASS, got report:\n{report}"


def test_b100_fail_insufficient_reps(tmp_path: Path, monkeypatch):
    """Test FAIL case: insufficient representations."""
    monkeypatch.setenv("VALIDATOR_REQUIRE_MULTI_REP", "1")
    monkeypatch.setenv("VALIDATOR_REQUIRE_XREF", "0")

    content = """
    | B-101 | Raw only demo | 🧪 | 3 | todo | No summary, no refs |
    """
    path = write_backlog(tmp_path, content)
    code, report, summary = validate_backlog(str(path))
    assert code == 2
    assert "INSUFFICIENT_REPRESENTATIONS" in report


def test_b102_fail_missing_xref(tmp_path: Path, monkeypatch):
    """Test FAIL case: missing cross-references."""
    monkeypatch.setenv("VALIDATOR_REQUIRE_MULTI_REP", "0")
    monkeypatch.setenv("VALIDATOR_REQUIRE_XREF", "1")

    content = """
    | B-102 | No xrefs demo | 🧪 | 3 | todo | Missing references |
    <!--score: {"bv":3,"tc":2,"rr":2,"le":3,"lessons":3,"effort":2,"deps":[]}-->
    <!--score_total: 3.1-->
    """
    path = write_backlog(tmp_path, content)
    code, report, summary = validate_backlog(str(path))
    assert code == 2
    assert "MISSING_CROSS_REFERENCE" in report


def test_stale_xref_warn(tmp_path: Path, monkeypatch):
    """Test WARN case: stale cross-references (non-strict mode)."""
    monkeypatch.setenv("VALIDATOR_REQUIRE_MULTI_REP", "0")
    monkeypatch.setenv("VALIDATOR_REQUIRE_XREF", "1")
    monkeypatch.setenv("VALIDATOR_STRICT_STALE_XREF", "0")

    content = """
    | B-103 | Stale xref warn | 🧪 | 3 | todo | Has xref but file missing |
    <!--score: {"bv":3,"tc":2,"rr":2,"le":3,"lessons":3,"effort":2,"deps":[]}-->
    <!--score_total: 3.1-->
    <!-- lessons_applied: ["500_reference-cards.md#rag-lessons-from-jerry"] -->
    """
    path = write_backlog(tmp_path, content)
    code, report, summary = validate_backlog(str(path))
    assert code in (0, 2)  # could still fail for other rules
    assert "STALE_CROSS_REFERENCE" in report


def test_stale_xref_fail_strict(tmp_path: Path, monkeypatch):
    """Test FAIL case: stale cross-references (strict mode)."""
    monkeypatch.setenv("VALIDATOR_REQUIRE_MULTI_REP", "0")
    monkeypatch.setenv("VALIDATOR_REQUIRE_XREF", "1")
    monkeypatch.setenv("VALIDATOR_STRICT_STALE_XREF", "1")

    content = """
    | B-104 | Stale xref fail | 🧪 | 3 | todo | Strict mode |
    <!--score: {"bv":3,"tc":2,"rr":2,"le":3,"lessons":3,"effort":2,"deps":[]}-->
    <!--score_total: 3.1-->
    <!-- reference_cards: ["500_reference-cards.md#rag-lessons-from-jerry"] -->
    """
    path = write_backlog(tmp_path, content)
    code, report, summary = validate_backlog(str(path))
    assert code == 2
    assert "STALE_CROSS_REFERENCE" in report


def test_impacted_files_are_posix_relative(tmp_path, monkeypatch):
    """Test that impacted_files paths are repo-relative POSIX format."""
    import json
    import subprocess

    # Arrange: create a tiny repo with a README
    d = tmp_path / "docs"
    d.mkdir()
    f = d / "README.md"
    f.write_text("# Title\n")

    # Force --root
    res = subprocess.run(
        ["python3", "scripts/doc_coherence_validator.py", "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    report = json.loads(res.stdout)

    for files in report.get("impacted_files", {}).values():
        for p in files:
            assert not p.startswith(str(tmp_path)), "must be repo-relative"
            assert "\\" not in p, "must be POSIX"


def test_stdout_pure_json_warnings_to_stderr(capsys, tmp_path):
    """Test that stdout contains pure JSON and warnings go to stderr."""
    import json
    import subprocess

    res = subprocess.run(
        ["python3", "scripts/doc_coherence_validator.py", "--ci", "--json", "--root", str(tmp_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    # stdout parses as JSON; stderr may contain WARNs
    json.loads(res.stdout)
    assert res.stdout.strip().startswith("{")
    assert "WARN" not in (res.stdout or ""), "warnings must not pollute JSON stdout"
