#!/usr/bin/env python3
"""
Add deprecation notices to archived 00-12 documents
"""

from pathlib import Path

# Define the mapping of old files to their replacements
DEPRECATION_MAPPING = {
    "400_01_documentation-playbook.md": "400_guides/400_03_system-overview-and-architecture.md",
    "400_02_governance-and-ai-constitution.md": "400_guides/400_02_memory-rehydration-context-management.md",
    "400_05_coding-and-prompting-standards.md": "400_guides/400_04_development-workflow-and-standards.md and 400_guides/400_05_codebase-organization-patterns.md",
    "400_06_memory-and-context-systems.md": "400_guides/400_01_memory-system-architecture.md",
    "400_07_ai-frameworks-dspy.md": "400_guides/400_09_ai-frameworks-dspy.md",
    "400_08_integrations-editor-and-models.md": "400_guides/400_10_integrations-models.md",
    "400_11_deployments-ops-and-observability.md": "400_guides/400_11_performance-optimization.md",
    "400_12_product-management-and-roadmap.md": "400_guides/400_12_advanced-configurations.md",
}

def add_deprecation_notice(file_path: str, replacement: str):
    """Add deprecation notice to a file."""

    # Read the current content
    with open(file_path, encoding="utf-8") as f:
        content = f.read()

    # Create deprecation notice
    deprecation_notice = f"""# 🚨 DEPRECATED DOCUMENT

**This document has been deprecated and archived as part of the documentation restructuring.**

## 📋 **Deprecation Information**
- **Date Deprecated**: 2025-01-31
- **Reason**: Replaced by new structured documentation system
- **Replacement**: `{replacement}`
- **Status**: Archived for reference only

## 🔄 **Migration Path**
- **For new users**: Read the replacement document instead
- **For returning users**: Use the new structured documentation with enhanced navigation
- **For reference**: This document is preserved for historical context

---

"""

    # Add the deprecation notice at the beginning
    new_content = deprecation_notice + content

    # Write back to file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"✅ Added deprecation notice to {file_path}")

def main():
    """Add deprecation notices to all archived files."""

    archive_dir = Path("600_archives/400_guides/deprecated-00-12-docs")

    if not archive_dir.exists():
        print(f"❌ Archive directory not found: {archive_dir}")
        return

    for filename, replacement in DEPRECATION_MAPPING.items():
        file_path = archive_dir / filename

        if file_path.exists():
            add_deprecation_notice(str(file_path), replacement)
        else:
            print(f"⚠️  File not found: {file_path}")

    print("\n🎉 Deprecation notices added to all archived files!")

if __name__ == "__main__":
    main()
