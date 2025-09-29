from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from regen_guide import AnchorHeaderScanner, AnchorMetadata, GuideGenerator

#!/usr/bin/env python3
"""
Simple validation script for regen_guide.py

Validates that the B-062 implementation works correctly.
"""

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def test_metadata_extraction():
    """Test metadata extraction functionality."""
    print("🧪 Testing metadata extraction...")

    # Create test content
    test_content = """<!-- ANCHOR_KEY: test-anchor -->
<!-- ANCHOR_PRIORITY: 15 -->
<!-- ROLE_PINS: ["planner", "implementer"] -->

# Test File
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    try:
        # Test extraction
        # Create a scanner with the temp directory as project root
        temp_scanner = AnchorHeaderScanner(str(temp_path.parent))
        metadata = temp_scanner.extract_anchor_metadata(temp_path)

        # Validate results
        assert metadata is not None, "Metadata should not be None"
        assert metadata.anchor_key == "test-anchor", f"Expected 'test-anchor', got '{metadata.anchor_key}'"
        assert metadata.anchor_priority == 15, f"Expected 15, got {metadata.anchor_priority}"
        assert metadata.role_pins == [
            "planner",
            "implementer",
        ], f"Expected ['planner', 'implementer'], got {metadata.role_pins}"
        assert (
            metadata.context_reference == "400_guides/400_test.md"
        ), f"Expected '400_guides/400_test.md', got '{metadata.context_reference}'"

        print("✅ Metadata extraction test passed")
        return True

    except Exception as e:
        print(f"❌ Metadata extraction test failed: {e}")
        return False
    finally:
        temp_path.unlink()


def test_priority_grouping():
    """Test priority-based grouping functionality."""
    print("🧪 Testing priority grouping...")

    # Create test metadata
    test_metadata = [
        AnchorMetadata(file_path="test1.md", anchor_key="test1", anchor_priority=0, role_pins=["planner"]),
        AnchorMetadata(file_path="test2.md", anchor_key="test2", anchor_priority=15, role_pins=["implementer"]),
        AnchorMetadata(file_path="test3.md", anchor_key="test3", anchor_priority=25, role_pins=["coder"]),
    ]

    try:
        # Test grouping
        generator = GuideGenerator(test_metadata)
        grouped = generator.group_by_priority()

        # Validate results
        assert "P0 (Critical)" in grouped, "P0 tier should exist"
        assert "P2 (Medium)" in grouped, "P2 tier should exist"

        p0_files = grouped["P0 (Critical)"]
        assert len(p0_files) == 1, f"Expected 1 P0 file, got {len(p0_files)}"
        assert p0_files[0]["priority"] == "P0"

        p2_files = grouped["P2 (Medium)"]
        assert len(p2_files) == 2, f"Expected 2 P2 files, got {len(p2_files)}"

        print("✅ Priority grouping test passed")
        return True

    except Exception as e:
        print(f"❌ Priority grouping test failed: {e}")
        return False


def test_role_grouping():
    """Test role-based grouping functionality."""
    print("🧪 Testing role grouping...")

    # Create test metadata
    test_metadata = [
        AnchorMetadata(
            file_path="test1.md", anchor_key="test1", anchor_priority=0, role_pins=["planner", "implementer"]
        ),
        AnchorMetadata(file_path="test2.md", anchor_key="test2", anchor_priority=15, role_pins=["implementer"]),
        AnchorMetadata(file_path="test3.md", anchor_key="test3", anchor_priority=25, role_pins=["coder"]),
    ]

    try:
        # Test grouping
        generator = GuideGenerator(test_metadata)
        grouped = generator.group_by_role()

        # Validate results
        assert "planner" in grouped, "planner role should exist"
        assert "implementer" in grouped, "implementer role should exist"
        assert "coder" in grouped, "coder role should exist"

        planner_files = grouped["planner"]
        assert len(planner_files) == 1, f"Expected 1 planner file, got {len(planner_files)}"

        implementer_files = grouped["implementer"]
        assert len(implementer_files) == 2, f"Expected 2 implementer files, got {len(implementer_files)}"

        print("✅ Role grouping test passed")
        return True

    except Exception as e:
        print(f"❌ Role grouping test failed: {e}")
        return False


def test_guide_generation():
    """Test guide content generation."""
    print("🧪 Testing guide generation...")

    # Create test metadata
    test_metadata = [
        AnchorMetadata(
            file_path="100_memory/100_cursor-memory-context.md",
            anchor_key="memory-context",
            anchor_priority=0,
            role_pins=["planner", "implementer"],
        ),
        AnchorMetadata(
            file_path="000_core/000_backlog.md", anchor_key="backlog", anchor_priority=10, role_pins=["planner"]
        ),
    ]

    try:
        # Test generation
        generator = GuideGenerator(test_metadata)
        content = generator.generate_guide_content()

        # Validate content
        assert "# 🧠 Context Priority Guide" in content, "Guide title should be present"
        assert "## 📋 Priority-Based Organization" in content, "Priority organization section should be present"
        assert "## 🎭 Role-Based Organization" in content, "Role organization section should be present"
        assert "100_memory/100_cursor-memory-context.md" in content, "Memory context file should be present"
        assert "000_core/000_backlog.md" in content, "Backlog file should be present"

        print("✅ Guide generation test passed")
        return True

    except Exception as e:
        print(f"❌ Guide generation test failed: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🚀 Starting B-062 Context Priority Guide Auto-Generation validation...")
    print()

    tests = [test_metadata_extraction, test_priority_grouping, test_role_grouping, test_guide_generation]

    passed = 0
    total = len(tests)

    for test in tests:
        if test():
            passed += 1
        print()

    print(f"📊 Validation Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! B-062 implementation is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit(main())
