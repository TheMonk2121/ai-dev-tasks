#!/usr/bin/env python3
"""
Test Suite for Broken Link Validation System

Comprehensive tests to ensure all markdown links resolve to existing files.
Addresses the testing gap identified where Cursor Problems pane caught
broken links that our validation missed.
"""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple, Union

import pytest


class TestBrokenLinkValidation:
    """Test cases for broken link validation."""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Set up test environment with test markdown files."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test directory structure
        self.create_test_structure()

        yield

        # Clean up
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_test_structure(self):
        """Create test markdown files and directory structure."""
        # Create directories
        os.makedirs("400_guides", exist_ok=True)
        os.makedirs("100_memory", exist_ok=True)
        os.makedirs("500_research", exist_ok=True)

        # Create valid target files
        Path("400_guides/400_system-overview.md").write_text("# System Overview\nContent here")
        Path("100_memory/100_cursor-memory-context.md").write_text("# Memory Context\nContent here")
        Path("500_research/cursor_native_ai_assessment.md").write_text("# AI Assessment\nContent here")

        # Create test files with various link types
        self.test_files = {
            "valid_links.md": """# Valid Links Test
- [System Overview](400_guides/400_system-overview.md) - Should work
- [Memory Context](100_memory/100_cursor-memory-context.md) - Should work
- [Research Link](500_research/cursor_native_ai_assessment.md) - Should work
""",
            "broken_links.md": """# Broken Links Test
- [Missing File](400_guides/missing-file.md) - Should fail
- [Wrong Path](../../nonexistent/file.md) - Should fail
- [Self Reference](broken_links.md) - Should work (self-reference)
""",
            "mixed_links.md": """# Mixed Links Test
- [Valid](400_guides/400_system-overview.md) - Good
- [Invalid](missing/path.md) - Bad
- [Another Valid](100_memory/100_cursor-memory-context.md) - Good
""",
            "400_guides/subfolder_test.md": """# Subfolder Test
- [Parent Reference](../100_memory/100_cursor-memory-context.md) - Should work
- [Research Link](../500_research/cursor_native_ai_assessment.md) - Should work
- [Broken Parent](../missing-file.md) - Should fail
""",
        }

        # Write test files
        for filename, content in self.test_files.items():
            file_path = Path(filename)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)

    def extract_markdown_links(self, file_path: str) -> List[Tuple[str, str]]:
        """Extract markdown links from a file.

        Returns:
            List of tuples (link_text, link_url)
        """
        try:
            content = Path(file_path).read_text()
        except (FileNotFoundError, PermissionError, UnicodeDecodeError):
            # Return empty list if file can't be read
            return []

        # Regex to match [text](url) pattern - handle escaped brackets and titles
        link_pattern = r"\[([^\]]*)\]\(([^)]+)(?:\s+\"([^\"]*)\")?\)"
        matches = re.findall(link_pattern, content)
        # Return only link_text and link_url (ignore title if present)
        return [(text, url) for text, url, *_ in matches]

    def resolve_relative_path(self, source_file: str, link_url: str) -> str:
        """Resolve relative path from source file to target."""
        # If the link starts with a directory name (like "200_setup/", "400_guides/", etc.),
        # treat it as relative to the project root, not the source file's directory
        if "/" in link_url and not link_url.startswith("../") and not link_url.startswith("./"):
            # This looks like a project-root-relative path
            target_path = Path(link_url)
        else:
            # This is a file-relative path
            source_dir = Path(source_file).parent
            target_path = source_dir / link_url
        return str(target_path.resolve())

    def is_relative_link(self, url: Union[str, None]) -> bool:
        """Check if URL is a relative file link (not external/anchor)."""
        # Handle empty or None URLs
        if not url or not isinstance(url, str):
            return False

        # Skip external links, anchors, and non-file links
        if url.startswith(("http://", "https://", "mailto:", "#", "tel:", "ftp://")) or "://" in url:
            return False

        # Skip generic placeholder links
        if url.lower() in ["url", "link", "path", "file", "placeholder"]:
            return False

        # Skip URLs that are clearly not file paths
        if url.startswith(("javascript:", "data:", "blob:")):
            return False

        # Only consider .md files or files with clear extensions
        return url.endswith(".md")

    def validate_file_links(self, file_path: str) -> List[str]:
        """Validate all links in a markdown file.

        Returns:
            List of broken link error messages
        """
        errors = []
        links = self.extract_markdown_links(file_path)

        for link_text, link_url in links:
            if self.is_relative_link(link_url):
                target_path = self.resolve_relative_path(file_path, link_url)
                if not os.path.exists(target_path):
                    errors.append(f"Broken link in {file_path}: [{link_text}]({link_url}) -> {target_path}")

        return errors

    def test_extract_markdown_links(self):
        """Test markdown link extraction."""
        links = self.extract_markdown_links("valid_links.md")
        assert len(links) == 3
        assert ("System Overview", "400_guides/400_system-overview.md") in links
        assert ("Memory Context", "100_memory/100_cursor-memory-context.md") in links

    def test_relative_link_detection(self):
        """Test relative link detection logic."""
        # Valid relative links
        assert self.is_relative_link("400_guides/file.md")
        assert self.is_relative_link("../other/file.md")
        assert self.is_relative_link("file.md")

        # External links
        assert not self.is_relative_link("https://example.com")
        assert not self.is_relative_link("http://example.com")
        assert not self.is_relative_link("ftp://example.com")

        # Anchors and other protocols
        assert not self.is_relative_link("#anchor")
        assert not self.is_relative_link("mailto:test@example.com")
        assert not self.is_relative_link("tel:+1234567890")
        assert not self.is_relative_link("javascript:alert('test')")
        assert not self.is_relative_link("data:text/plain,test")

        # Placeholder links
        assert not self.is_relative_link("url")
        assert not self.is_relative_link("link")
        assert not self.is_relative_link("path")
        assert not self.is_relative_link("file")
        assert not self.is_relative_link("placeholder")

        # Edge cases
        assert not self.is_relative_link("")
        assert not self.is_relative_link(None)
        assert not self.is_relative_link("   ")

    def test_valid_links_pass(self):
        """Test that valid links pass validation."""
        errors = self.validate_file_links("valid_links.md")
        assert len(errors) == 0, f"Valid links should not produce errors: {errors}"

    def test_broken_links_detected(self):
        """Test that broken links are properly detected."""
        errors = self.validate_file_links("broken_links.md")
        assert len(errors) >= 2, "Should detect at least 2 broken links"

        # Check specific broken links are caught
        error_text = " ".join(errors)
        assert "missing-file.md" in error_text
        assert "nonexistent/file.md" in error_text

    def test_mixed_links_partial_errors(self):
        """Test file with mix of valid and broken links."""
        errors = self.validate_file_links("mixed_links.md")
        assert len(errors) == 1, f"Should detect exactly 1 broken link, got: {errors}"
        assert "missing/path.md" in errors[0]

    def test_subfolder_relative_paths(self):
        """Test relative path resolution from subfolders."""
        errors = self.validate_file_links("400_guides/subfolder_test.md")
        assert len(errors) == 1, f"Should detect 1 broken link in subfolder, got: {errors}"
        assert "missing-file.md" in errors[0]

    def test_self_reference_links(self):
        """Test that self-referencing links work correctly."""
        # Add self-reference to existing file
        Path("self_ref.md").write_text("# Self Reference\n[Self](self_ref.md)")
        errors = self.validate_file_links("self_ref.md")
        assert len(errors) == 0, "Self-references should be valid"

    def test_comprehensive_validation_function(self):
        """Test the main validation function that checks all files."""

        def validate_all_markdown_files(root_dir: str = ".") -> Dict[str, List[str]]:
            """Validate all markdown files in directory."""
            all_errors = {}

            for file_path in Path(root_dir).rglob("*.md"):
                if file_path.is_file():
                    errors = self.validate_file_links(str(file_path))
                    if errors:
                        all_errors[str(file_path)] = errors

            return all_errors

        all_errors = validate_all_markdown_files()

        # Should find errors in broken_links.md, mixed_links.md, and subfolder_test.md
        assert len(all_errors) >= 3, f"Should find broken links in multiple files: {all_errors}"
        assert any("broken_links.md" in path for path in all_errors.keys())
        assert any("mixed_links.md" in path for path in all_errors.keys())
        assert any("subfolder_test.md" in path for path in all_errors.keys())

class TestRealProjectBrokenLinks:
    """Test broken links in the actual project (if run from project root)."""

    @pytest.mark.skipif(not os.path.exists("400_guides"), reason="Not in project root")
    def test_no_broken_links_in_project(self):
        """Test that the real project has no broken links."""

        def validate_project_links() -> Dict[str, List[str]]:
            """Validate links in actual project files."""
            # Create validator instance directly to avoid circular import
            validator = TestBrokenLinkValidation()

            all_errors = {}

            # Focus on key directories that were recently reorganized
            key_dirs = ["400_guides", "100_memory", "000_core", "dspy-rag-system"]

            for dir_name in key_dirs:
                if os.path.exists(dir_name):
                    for file_path in Path(dir_name).rglob("*.md"):
                        if file_path.is_file():
                            errors = validator.validate_file_links(str(file_path))
                            if errors:
                                all_errors[str(file_path)] = errors

            return all_errors

        project_errors = validate_project_links()

        # If this fails, it means we have broken links in the project
        assert len(project_errors) == 0, f"Found broken links in project: {project_errors}"

if __name__ == "__main__":
    # Allow running this test directly
    pytest.main([__file__, "-v"])
