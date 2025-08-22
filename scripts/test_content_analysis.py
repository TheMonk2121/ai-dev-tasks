#!/usr/bin/env python3
"""
Test Content Analysis for Role Assignment
-----------------------------------------
Test the content analysis functionality with real archived files.
"""

from pathlib import Path

from role_assignment_metadata import RoleAssignmentMetadata


def test_content_analysis():
    """Test content analysis with real archived files."""
    metadata_system = RoleAssignmentMetadata()

    # Test files to analyze
    test_files = [
        "600_archives/artifacts/prds/PRD-B-101-cSpell-Automation-Integration.md",
        "600_archives/artifacts/prds/PRD-B-102-Cursor-Native-AI-Role-Coordination-System.md",
        "600_archives/artifacts/000_core_temp_files/PRD-Chunk-Relationship-Visualization.md",
    ]

    print("Testing Content Analysis for Role Assignment")
    print("=" * 50)

    for file_path in test_files:
        path = Path(file_path)
        if not path.exists():
            print(f"⚠️  File not found: {file_path}")
            continue

        print(f"\n📄 Analyzing: {file_path}")

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            # Get assignment
            assignment = metadata_system.assign_roles_to_file(path, content)

            print(f"  📋 Assigned roles: {sorted(assignment.roles)}")
            print(f"  🔍 Source: {assignment.source}")
            print(f"  🎯 Confidence: {assignment.confidence:.2f}")
            print(f"  ✅ Valid: {metadata_system.validate_role_assignment(assignment)}")

            if metadata_system.validation_errors:
                print(f"  ⚠️  Validation errors: {metadata_system.validation_errors}")

            # Test content analysis specifically
            content_roles = metadata_system.analyze_content_for_roles(content, path)
            print(f"  🔬 Content analysis roles: {sorted(content_roles)}")

            # Test default roles
            default_roles = metadata_system.get_default_roles_for_file(path)
            print(f"  📁 Default roles: {sorted(default_roles)}")

        except Exception as e:
            print(f"  ❌ Error analyzing file: {e}")


if __name__ == "__main__":
    test_content_analysis()
