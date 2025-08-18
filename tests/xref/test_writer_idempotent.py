#!/usr/bin/env python3
"""
Tests for XRef writer idempotent behavior (PR B)
"""

import tempfile
from pathlib import Path

import pytest

from scripts.xref_apply import XRefScanner, XRefWriter


@pytest.mark.tier1
@pytest.mark.kind_unit
class TestXRefWriterIdempotent:
    """Test XRef writer idempotent behavior."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create 000_core directory
            core_dir = repo_path / "000_core"
            core_dir.mkdir()

            # Create test files
            (core_dir / "target_file.md").write_text("# Target File\n\nThis is a target.")

            yield repo_path

    @pytest.fixture
    def scanner(self, temp_repo):
        """Create XRef scanner instance."""
        return XRefScanner(temp_repo, "000_core")

    @pytest.fixture
    def writer(self, scanner):
        """Create XRef writer instance."""
        return XRefWriter(scanner)

    def test_single_xref_block(self, writer, temp_repo):
        """Test that only one xref-autofix block is created."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nThis references `target_file.md`.")

        suggestions = [
            {
                "source_file": "000_core/test_file.md",
                "reference": "target-file",
                "target_path": "000_core/target_file.md",
                "target_title": "Target File",
                "confidence": 0.9,
                "type": "backtick",
            }
        ]

        # Write first time
        result1 = writer.write_suggestions(test_file, suggestions, "stubs")
        assert result1 is True

        # Check content has exactly one block
        content = test_file.read_text()
        assert content.count("<!-- xref-autofix:begin -->") == 1
        assert content.count("<!-- xref-autofix:end -->") == 1

        # Try to write again
        result2 = writer.write_suggestions(test_file, suggestions, "stubs")
        assert result2 is False  # Should not write again

        # Check content is unchanged
        content2 = test_file.read_text()
        assert content == content2

    def test_idempotent_writes(self, writer, temp_repo):
        """Test that multiple writes produce identical results."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nThis references `target_file.md`.")

        suggestions = [
            {
                "source_file": "000_core/test_file.md",
                "reference": "target-file",
                "target_path": "000_core/target_file.md",
                "target_title": "Target File",
                "confidence": 0.9,
                "type": "backtick",
            }
        ]

        # Write first time
        writer.write_suggestions(test_file, suggestions, "stubs")
        content1 = test_file.read_text()

        # Delete the file and recreate
        test_file.unlink()
        test_file.write_text("# Test File\n\nThis references `target_file.md`.")

        # Write second time
        writer.write_suggestions(test_file, suggestions, "stubs")
        content2 = test_file.read_text()

        # Content should be identical
        assert content1 == content2

    def test_no_suggestions(self, writer, temp_repo):
        """Test behavior with no suggestions."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nNo references here.")

        result = writer.write_suggestions(test_file, [], "stubs")
        assert result is False

        # File should be unchanged
        content = test_file.read_text()
        assert "<!-- xref-autofix:begin -->" not in content

    def test_high_confidence_links(self, writer, temp_repo):
        """Test high confidence links are applied inline."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nThis references `target_file.md`.")

        suggestions = [
            {
                "source_file": "000_core/test_file.md",
                "reference": "target-file",
                "target_path": "000_core/target_file.md",
                "target_title": "Target File",
                "confidence": 0.9,
                "type": "backtick",
            }
        ]

        # Write in links mode
        result = writer.write_suggestions(test_file, suggestions, "links")
        assert result is True

        # Check content has inline link
        content = test_file.read_text()
        assert "[Target File](000_core/target_file.md)" in content

    def test_low_confidence_stubs(self, writer, temp_repo):
        """Test low confidence suggestions become stubs."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nThis references something.")

        suggestions = [
            {
                "source_file": "000_core/test_file.md",
                "reference": "something",
                "target_path": "000_core/target_file.md",
                "target_title": "Target File",
                "confidence": 0.5,  # Low confidence
                "type": "mention",
            }
        ]

        # Write in stubs mode
        result = writer.write_suggestions(test_file, suggestions, "stubs")
        assert result is True

        # Check content has stub (not inline link)
        content = test_file.read_text()
        assert "[ ] Add link to Target File" in content
        assert "[Target File](000_core/target_file.md)" not in content

    def test_mixed_confidence(self, writer, temp_repo):
        """Test mixed confidence suggestions."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text("# Test File\n\nThis references `target_file.md` and something else.")

        suggestions = [
            {
                "source_file": "000_core/test_file.md",
                "reference": "target-file",
                "target_path": "000_core/target_file.md",
                "target_title": "Target File",
                "confidence": 0.9,  # High confidence
                "type": "backtick",
            },
            {
                "source_file": "000_core/test_file.md",
                "reference": "something-else",
                "target_path": "000_core/other_file.md",
                "target_title": "Other File",
                "confidence": 0.5,  # Low confidence
                "type": "mention",
            },
        ]

        # Write in stubs mode to include both high and low confidence
        result = writer.write_suggestions(test_file, suggestions, "stubs")
        assert result is True

        # Check content has both inline link and stub
        content = test_file.read_text()
        assert "[Target File](000_core/target_file.md)" in content
        assert "[ ] Add link to Other File" in content

    def test_file_not_found(self, writer, temp_repo):
        """Test behavior when file doesn't exist."""
        nonexistent_file = temp_repo / "000_core" / "nonexistent.md"

        result = writer.write_suggestions(nonexistent_file, [], "stubs")
        assert result is False
