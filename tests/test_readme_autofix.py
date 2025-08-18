"""
Tests for README autofix tool.
"""

import os
import tempfile

import pytest

from scripts.readme_autofix import (
    build_marker_content,
    discover_readme_files,
    find_marker_block,
    get_missing_sections,
    has_section_synonym,
    infer_owner,
    process_readme_file,
)


@pytest.fixture
def temp_repo():
    """Create a temporary repository structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test structure
        test_dirs = [
            "400_guides/",
            "000_core/",
            "600_archives/",  # Should be ignored
            "node_modules/",  # Should be ignored
        ]

        for test_dir in test_dirs:
            os.makedirs(os.path.join(temp_dir, test_dir), exist_ok=True)

        # Create test files
        test_files = {
            "400_guides/test1.md": "# Test 1\n\nContent without required sections",
            "400_guides/test2.md": "# Test 2\n\n## Purpose\n\nHas purpose\n\n## Usage\n\nHas usage\n\n## Owner\n\nCore Team\n\n## Last Reviewed\n\n2025-01-01",
            "000_core/test3.md": "# Test 3\n\n## Overview\n\nHas overview synonym\n\n## How to Use\n\nHas usage synonym",
            "600_archives/test4.md": "# Test 4\n\nShould be ignored",
            "node_modules/test5.md": "# Test 5\n\nShould be ignored",
        }

        for file_path, content in test_files.items():
            full_path = os.path.join(temp_dir, file_path)
            with open(full_path, "w") as f:
                f.write(content)

        yield temp_dir


def test_discover_readme_files(temp_repo):
    """Test README file discovery respects scope and ignores."""
    files = discover_readme_files(temp_repo)

    # Should find files in scope
    assert any("400_guides/test1.md" in f for f in files)
    assert any("400_guides/test2.md" in f for f in files)
    assert any("000_core/test3.md" in f for f in files)

    # Should ignore files in ignored segments
    assert not any("600_archives/test4.md" in f for f in files)
    assert not any("node_modules/test5.md" in f for f in files)


def test_has_section_synonym():
    """Test synonym detection for required sections."""
    content = """
# Test Document

## Purpose
This is the purpose.

## How to Use
This is how to use it.

## Owner
This is the owner.

## Last Updated
This was last updated.
"""

    assert has_section_synonym(content, "purpose")
    assert has_section_synonym(content, "usage")  # "How to Use" synonym
    assert has_section_synonym(content, "owner")
    assert has_section_synonym(content, "last_reviewed")  # "Last Updated" synonym


def test_find_marker_block():
    """Test marker block detection."""
    content = """
# Test Document

Content here.

<!-- README_AUTOFIX_START -->
# Auto-generated sections
## Missing sections to add:
## Purpose
Describe the purpose and scope of this document
<!-- README_AUTOFIX_END -->

More content.
"""

    marker_pos = find_marker_block(content)
    assert marker_pos is not None
    start, end = marker_pos

    # Verify positions
    assert (
        content[start : start + len("<!-- README_AUTOFIX_START -->")]
        == "<!-- README_AUTOFIX_START -->"
    )
    assert (
        content[end - len("<!-- README_AUTOFIX_END -->") : end]
        == "<!-- README_AUTOFIX_END -->"
    )


def test_infer_owner():
    """Test owner inference based on file path."""
    assert infer_owner("400_guides/test.md") == "Documentation Team"
    assert infer_owner("000_core/test.md") == "Core Team"
    assert infer_owner("unknown/path.md") == "TBD"


def test_get_missing_sections():
    """Test missing section detection."""
    # Complete document
    complete_content = """
# Test Document

## Purpose
Purpose here.

## Usage
Usage here.

## Owner
Owner here.

## Last Reviewed
Date here.
"""
    missing = get_missing_sections(complete_content)
    assert len(missing) == 0

    # Incomplete document
    incomplete_content = """
# Test Document

## Purpose
Purpose here.

## Usage
Usage here.
"""
    missing = get_missing_sections(incomplete_content)
    assert "owner" in missing
    assert "last_reviewed" in missing
    assert "purpose" not in missing
    assert "usage" not in missing


def test_build_marker_content():
    """Test marker content generation."""
    missing_sections = {"owner", "last_reviewed"}
    file_path = "400_guides/test.md"

    # Dry run mode
    content = build_marker_content(missing_sections, file_path, write_mode=False)
    assert "<!-- README_AUTOFIX_START -->" in content
    assert "<!-- README_AUTOFIX_END -->" in content
    assert "Documentation Team" in content  # Owner inferred
    # In dry-run we expect the date placeholder token, not a real date
    assert "YYYY-MM-DD" in content

    # Write mode
    content = build_marker_content(missing_sections, file_path, write_mode=True)
    assert "<!-- README_AUTOFIX_START -->" in content
    assert "<!-- README_AUTOFIX_END -->" in content
    assert "Documentation Team" in content
    # Should have actual date in write mode
    assert "2025-" in content or "2024-" in content


def test_process_readme_file_dry_run(temp_repo):
    """Test README processing in dry-run mode."""
    file_path = os.path.join(temp_repo, "400_guides/test1.md")

    result = process_readme_file(file_path, write_mode=False)

    assert result["file"] == file_path
    assert result["status"] == "dry_run"
    assert result["modified"] is False
    assert len(result["missing_sections"]) > 0

    # Verify file wasn't actually modified
    with open(file_path) as f:
        content = f.read()
    assert "<!-- README_AUTOFIX_START -->" not in content


def test_process_readme_file_write_mode(temp_repo):
    """Test README processing in write mode."""
    file_path = os.path.join(temp_repo, "400_guides/test1.md")

    result = process_readme_file(file_path, write_mode=True)

    assert result["file"] == file_path
    assert result["status"] == "updated"
    assert result["modified"] is True

    # Verify file was actually modified
    with open(file_path) as f:
        content = f.read()
    assert "<!-- README_AUTOFIX_START -->" in content
    assert "<!-- README_AUTOFIX_END -->" in content
    # Check that owner inference worked (should be "Documentation Team" for 400_guides)
    assert "Documentation Team" in content


def test_process_readme_file_complete(temp_repo):
    """Test README processing for complete documents."""
    file_path = os.path.join(temp_repo, "400_guides/test2.md")

    result = process_readme_file(file_path, write_mode=False)

    assert result["file"] == file_path
    assert result["status"] == "complete"
    assert result["modified"] is False
    assert len(result["missing_sections"]) == 0


def test_process_readme_file_idempotent(temp_repo):
    """Test that processing is idempotent."""
    file_path = os.path.join(temp_repo, "400_guides/test1.md")

    # First run - should modify
    result1 = process_readme_file(file_path, write_mode=True)
    assert result1["modified"] is True
    assert result1["status"] == "updated"

    # Second run - should not modify (content is stable after timestamp normalization)
    result2 = process_readme_file(file_path, write_mode=True)
    assert result2["modified"] is False
    assert result2["status"] == "no_change"


def test_process_readme_file_synonyms_respected(temp_repo):
    """Test that synonyms are respected and don't create duplicates."""
    file_path = os.path.join(temp_repo, "000_core/test3.md")

    result = process_readme_file(file_path, write_mode=False)

    # Should recognize "Overview" as purpose synonym and "How to Use" as usage synonym
    assert "purpose" not in result["missing_sections"]
    assert "usage" not in result["missing_sections"]
    # Should still need owner and last_reviewed
    assert "owner" in result["missing_sections"]
    assert "last_reviewed" in result["missing_sections"]


def test_process_readme_file_unicode_error(temp_repo):
    """Test handling of Unicode decode errors."""
    # Create a binary file with .md extension
    file_path = os.path.join(temp_repo, "400_guides/binary.md")
    with open(file_path, "wb") as f:
        f.write(b"\xff\xfe\x00\x01\x02\x03")  # Invalid UTF-8 sequence

    result = process_readme_file(file_path, write_mode=False)

    assert "error" in result
    assert "Unicode decode error" in result["error"]
    assert result["modified"] is False


def test_process_readme_file_marker_update(temp_repo):
    """Test that existing marker blocks are updated, not duplicated."""
    file_path = os.path.join(temp_repo, "400_guides/test1.md")

    # Add initial marker block
    with open(file_path) as f:
        content = f.read()

    initial_marker = """<!-- README_AUTOFIX_START -->
# Auto-generated sections
## Missing sections to add:
## Purpose
Describe the purpose and scope of this document
<!-- README_AUTOFIX_END -->"""

    content += "\n\n" + initial_marker
    with open(file_path, "w") as f:
        f.write(content)

    # Process again - should update existing marker, not add new one
    result = process_readme_file(file_path, write_mode=True)
    assert result["modified"] is True

    # Verify only one marker block exists
    with open(file_path) as f:
        final_content = f.read()

    marker_starts = final_content.count("<!-- README_AUTOFIX_START -->")
    marker_ends = final_content.count("<!-- README_AUTOFIX_END -->")

    assert marker_starts == 1
    assert marker_ends == 1
