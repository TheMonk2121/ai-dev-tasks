#!/usr/bin/env python3.12.123.11
"""
Tests for internal link validation (PR B)
"""

import tempfile
from pathlib import Path

import pytest

from scripts.link_check import LinkChecker


@pytest.mark.tier1
@pytest.mark.kind_unit
class TestInternalLinkValidation:
    """Test internal link validation."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)

            # Create 000_core directory
            core_dir = repo_path / "000_core"
            core_dir.mkdir()

            # Create test files with anchors
            (core_dir / "target_file.md").write_text(
                "# Target File\n\n## Section 1\n\nContent here.\n\n## Section 2\n\nMore content."
            )
            (core_dir / "another_file.md").write_text(
                "# Another File\n\n## Subsection\n\nContent."
            )

            yield repo_path

    @pytest.fixture
    def checker(self, temp_repo):
        """Create link checker instance."""
        return LinkChecker(temp_repo, "000_core")

    def test_valid_file_link(self, checker, temp_repo):
        """Test valid file link."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\nSee [Target File](target_file.md) for details."
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 0

    def test_valid_anchor_link(self, checker, temp_repo):
        """Test valid anchor link."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\nSee [Section 1](target_file.md#section-1) for details."
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 0

    def test_emoji_anchor_same_scope(self, checker, temp_repo):
        """Validate link to an emoji-headed section using the expected slug within the 000_core scope."""
        target = temp_repo / "000_core" / "emoji_target.md"
        target.write_text("# Emoji Target\n\n## ⚡ Quick reference\n\nContent\n")

        source = temp_repo / "000_core" / "emoji_source.md"
        source.write_text(
            "# Emoji Source\n\nSee [Quick ref](emoji_target.md#quick-reference).\n"
        )

        checker.build_file_index()
        broken_links = checker.check_file(source)

        assert len(broken_links) == 0

    def test_cross_folder_parent_directory_link(self, checker, temp_repo):
        """Test that ../ links from a subfolder resolve correctly using pathlib normalization."""
        # Create a subfolder with a file linking up to 000_core/target_file.md
        subdir = temp_repo / "400_guides"
        subdir.mkdir()
        linking_file = subdir / "linking.md"
        linking_file.write_text(
            "# Linking File\n\nSee [Section 1](../000_core/target_file.md#section-1) for details."
        )

        checker.build_file_index()
        broken_links = checker.check_file(linking_file)

        assert len(broken_links) == 0

    def test_repo_wide_scope_cross_folder_emoji_anchor(self, temp_repo):
        """With scope '.', validate 000_core file linking to 400_guides emoji-anchored section."""
        # Create target in 400_guides with emoji heading
        guides_dir = temp_repo / "400_guides"
        guides_dir.mkdir(exist_ok=True)
        target = guides_dir / "metadata_guide.md"
        target.write_text("# Metadata Guide\n\n## ⚡ Quick reference\n\nContent\n")

        # Create source in 000_core linking to the emoji anchor in 400_guides
        source = temp_repo / "000_core" / "readme.md"
        source.write_text(
            "# Core Readme\n\nSee [Quick ref](../400_guides/metadata_guide.md#quick-reference).\n"
        )

        checker = LinkChecker(temp_repo, ".")
        checker.build_file_index()
        broken_links = checker.check_file(source)

        assert len(broken_links) == 0

    def test_missing_file(self, checker, temp_repo):
        """Test missing file link."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\nSee [Missing File](missing_file.md) for details."
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 1
        assert broken_links[0]["error"] == "file_not_found"
        assert broken_links[0]["target_file"] == "000_core/missing_file.md"

    def test_missing_anchor(self, checker, temp_repo):
        """Test missing anchor link."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\nSee [Missing Section](target_file.md#missing-section) for details."
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 1
        assert broken_links[0]["error"] == "anchor_not_found"
        assert broken_links[0]["target_anchor"] == "missing-section"

    def test_external_links_ignored(self, checker, temp_repo):
        """Test that external links are ignored."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            """# Test File

See [GitHub](https://github.com) for details.
Email us at [support@example.com](mailto:support@example.com).
"""
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 0

    def test_anchor_only_links_ignored(self, checker, temp_repo):
        """Test that anchor-only links are ignored."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\n## Section 1\n\nContent.\n\n[Back to top](#test-file)"
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 0

    def test_multiple_broken_links(self, checker, temp_repo):
        """Test multiple broken links in one file."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            """# Test File

See [Missing File](missing_file.md) for details.
Check [Missing Section](target_file.md#missing-section) for more info.
"""
        )

        checker.build_file_index()
        broken_links = checker.check_file(test_file)

        assert len(broken_links) == 2
        errors = [link["error"] for link in broken_links]
        assert "file_not_found" in errors
        assert "anchor_not_found" in errors

    def test_changed_files_check(self, checker, temp_repo):
        """Test checking only changed files."""
        test_file = temp_repo / "000_core" / "test_file.md"
        test_file.write_text(
            "# Test File\n\nSee [Missing File](missing_file.md) for details."
        )

        checker.build_file_index()
        changed_files = [str(test_file)]
        broken_links = checker.check_changed_files(changed_files)

        assert len(broken_links) == 1
        assert broken_links[0]["source_file"] == "000_core/test_file.md"

    def test_scope_check(self, checker, temp_repo):
        """Test checking all files in scope."""
        # Create files with broken links
        test_file1 = temp_repo / "000_core" / "test_file1.md"
        test_file1.write_text(
            "# Test File 1\n\nSee [Missing File](missing_file.md) for details."
        )

        test_file2 = temp_repo / "000_core" / "test_file2.md"
        test_file2.write_text(
            "# Test File 2\n\nCheck [Missing Section](target_file.md#missing-section) for more info."
        )

        checker.build_file_index()
        broken_links = checker.check_scope()

        assert len(broken_links) == 2
        source_files = [link["source_file"] for link in broken_links]
        assert "000_core/test_file1.md" in source_files
        assert "000_core/test_file2.md" in source_files

    def test_empty_scope(self, temp_repo):
        """Test behavior with empty scope."""
        checker = LinkChecker(temp_repo, "nonexistent_scope")
        checker.build_file_index()

        broken_links = checker.check_scope()
        assert len(broken_links) == 0

    def test_file_not_found(self, checker, temp_repo):
        """Test behavior when file doesn't exist."""
        nonexistent_file = temp_repo / "000_core" / "nonexistent.md"
        broken_links = checker.check_file(nonexistent_file)

        assert len(broken_links) == 0
