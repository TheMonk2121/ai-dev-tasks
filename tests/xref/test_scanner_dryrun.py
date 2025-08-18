#!/usr/bin/env python3
"""
Tests for XRef scanner dry-run functionality (PR B)
"""

import tempfile
from pathlib import Path

import pytest

from scripts.xref_apply import XRefScanner


@pytest.mark.tier1
@pytest.mark.kind_unit
class TestXRefScannerDryRun:
    """Test XRef scanner dry-run functionality."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create 000_core directory
            core_dir = repo_path / "000_core"
            core_dir.mkdir()

            # Create test files
            (core_dir / "test_file.md").write_text("# Test File\n\nThis is a test.")
            (core_dir / "another_file.md").write_text("# Another File\n\nThis is another test.")
            (core_dir / "guide.md").write_text("# Guide\n\nThis is a guide.")

            yield repo_path

    @pytest.fixture
    def scanner(self, temp_repo):
        """Create XRef scanner instance."""
        return XRefScanner(temp_repo, "000_core")

    def test_build_repo_index(self, scanner):
        """Test repository index building."""
        index = scanner.build_repo_index()

        assert "files" in index
        assert "titles" in index
        assert "anchors" in index

        # Check files are indexed
        assert "000_core/test_file.md" in index["files"]
        assert "000_core/another_file.md" in index["files"]
        assert "000_core/guide.md" in index["files"]

        # Check titles are indexed
        assert "test-file" in index["titles"]
        assert "another-file" in index["titles"]
        assert "guide" in index["titles"]

    def test_detect_backticked_filenames(self, scanner, temp_repo):
        """Test detection of backticked filenames."""
        # Create a file with backticked references
        test_file = temp_repo / "000_core" / "test_file.md"
        content = """# Test File

This references `guide.md` and `another_file.md`.

Also check `test_file.md` itself.
"""
        test_file.write_text(content)

        # Build index
        scanner.repo_index = scanner.build_repo_index()

        # Scan for suggestions
        suggestions = scanner.scan_file(test_file)

        # Should find references to guide.md and another_file.md
        refs = [s["reference"] for s in suggestions]
        assert "guide" in refs
        assert "another-file" in refs
        assert "test-file" not in refs  # Should not suggest linking to self

    def test_detect_title_mentions(self, scanner, temp_repo):
        """Test detection of title mentions."""
        # Create a file with title mentions
        test_file = temp_repo / "000_core" / "test_file.md"
        content = """# Test File

See the Guide for more information.
Check Another File for details.
"""
        test_file.write_text(content)

        # Build index
        scanner.repo_index = scanner.build_repo_index()

        # Scan for suggestions
        suggestions = scanner.scan_file(test_file)

        # Should find title mentions
        refs = [s["reference"] for s in suggestions]
        assert "guide" in refs
        assert "another-file" in refs

    def test_skip_existing_links(self, scanner, temp_repo):
        """Test that existing links are not suggested."""
        # Create a file with existing links
        test_file = temp_repo / "000_core" / "test_file.md"
        content = """# Test File

This has a link to [Guide](guide.md).

But this `another_file.md` is not linked.
"""
        test_file.write_text(content)

        # Build index
        scanner.repo_index = scanner.build_repo_index()

        # Scan for suggestions
        suggestions = scanner.scan_file(test_file)

        # Should not suggest guide.md (already linked)
        refs = [s["reference"] for s in suggestions]
        assert "guide" not in refs
        assert "another-file" in refs

    def test_skip_xref_autofix_blocks(self, scanner, temp_repo):
        """Test that files with xref-autofix blocks are skipped."""
        # Create a file with xref-autofix block
        test_file = temp_repo / "000_core" / "test_file.md"
        content = """# Test File

This references `guide.md`.

<!-- xref-autofix:begin -->
<!-- Cross-references to add: -->
- [Guide](guide.md)
<!-- xref-autofix:end -->
"""
        test_file.write_text(content)

        # Build index
        scanner.repo_index = scanner.build_repo_index()

        # Scan for suggestions
        suggestions = scanner.scan_file(test_file)

        # Should return no suggestions (already has xref block)
        assert len(suggestions) == 0

    def test_confidence_calculation(self, scanner, temp_repo):
        """Test confidence calculation for matches."""
        # Create a file with various references
        test_file = temp_repo / "000_core" / "test_file.md"
        content = """# Test File

This references `guide.md` and `another_file.md`.
Also mentions "Guide" and "Another File".
"""
        test_file.write_text(content)

        # Build index
        scanner.repo_index = scanner.build_repo_index()

        # Scan for suggestions
        suggestions = scanner.scan_file(test_file)

        # Check confidence levels
        for suggestion in suggestions:
            if suggestion["reference"] == "guide":
                assert suggestion["confidence"] >= 0.8  # High confidence for exact match
            elif suggestion["reference"] == "another-file":
                assert suggestion["confidence"] >= 0.8  # High confidence for exact match

    def test_exception_handling(self, scanner, temp_repo):
        """Test exception handling for files."""
        # Create exception file
        exceptions_file = temp_repo / "exceptions.json"
        exceptions_file.write_text(
            """{
            "exceptions": {
                "000_core/test_file.md": [
                    {
                        "key": "xref-missing",
                        "expires": "2025-08-24",
                        "reason": "Test exception"
                    }
                ]
            }
        }"""
        )

        # Load exceptions
        scanner.load_exceptions(exceptions_file)

        # Check exception is recognized
        assert scanner.is_excepted("000_core/test_file.md", "xref-missing")
        assert not scanner.is_excepted("000_core/another_file.md", "xref-missing")

    def test_empty_scope(self, temp_repo):
        """Test behavior with empty scope."""
        scanner = XRefScanner(temp_repo, "nonexistent_scope")
        index = scanner.build_repo_index()

        assert index["files"] == {}
        assert index["titles"] == {}
        assert index["anchors"] == {}

    def test_file_not_found(self, scanner, temp_repo):
        """Test behavior when file doesn't exist."""
        nonexistent_file = temp_repo / "000_core" / "nonexistent.md"
        suggestions = scanner.scan_file(nonexistent_file)

        assert len(suggestions) == 0
