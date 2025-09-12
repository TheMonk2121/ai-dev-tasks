from __future__ import annotations
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
import os
#!/usr/bin/env python3
"""
Documentation Cleanup Script
Identify redundant files, improve organization, and clean up temporary files.
"""

def analyze_guide_files():
    """Analyze 400_guides files for redundancy and organization."""
    print("📚 Documentation Analysis")
    print("=" * 50)

    guides_dir = Path("400_guides")
    guide_files = list(guides_dir.glob("400_*.md"))

    print(f"📊 Found {len(guide_files)} guide files")

    # Categorize files by type
    categories = {"core": [], "specialized": [], "temporary": [], "legacy": []}

    for file_path in guide_files:
        filename = file_path.name

        # Core guides (essential for AI rehydration)
        if any(
            keyword in filename
            for keyword in [
                "ai-constitution",
                "code-criticality",
                "comprehensive-coding",
                "context-priority",
                "file-analysis",
                "project-overview",
                "system-overview",
                "testing-strategy",
            ]
        ):
            categories["core"].append(filename)

        # Specialized guides (domain-specific)
        elif any(
            keyword in filename
            for keyword in [
                "deployment",
                "integration",
                "migration",
                "performance",
                "security",
                "few-shot",
                "documentation",
                "hydration",
            ]
        ):
            categories["specialized"].append(filename)

        # Temporary/Progress files
        elif any(
            keyword in filename
            for keyword in [
                "broken-links",
                "cleanup-progress",
                "fix-plan",
                "optimization-completion",
                "script-optimization-results",
                "cross-reference-strengthening",
            ]
        ):
            categories["temporary"].append(filename)

        # Legacy files
        else:
            categories["legacy"].append(filename)

    print("\n📂 File Categories:")
    for category, files in categories.items():
        print(f"  {category.title()}: {len(files)} files")
        for filename in sorted(files):
            print(f"    - {filename}")

    return categories, guide_files

def check_cross_references():
    """Check cross-reference patterns between guides."""
    print("\n🔗 Cross-Reference Analysis")
    print("=" * 40)

    guides_dir = Path("400_guides")
    reference_pattern = re.compile(r"400_[^/]+\.md")

    reference_counts = defaultdict(int)
    referenced_by = defaultdict(list)

    for file_path in guides_dir.glob("400_*.md"):
        filename = file_path.name
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Find all references to other guides
            references = reference_pattern.findall(content)
            reference_counts[filename] = len(references)

            # Track who references this file
            for ref in references:
                if ref != filename:
                    referenced_by[ref].append(filename)

        except Exception as e:
            print(f"❌ Error reading {filename}: {e}")

    print("📊 Cross-Reference Statistics:")
    print("  Most Referenced Files:")
    most_referenced = sorted(referenced_by.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for filename, referrers in most_referenced:
        print(f"    {filename}: referenced by {len(referrers)} files")

    print("\n  Files with Most References:")
    most_referencing = sorted(reference_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    for filename, count in most_referencing:
        print(f"    {filename}: {count} references")

    return reference_counts, referenced_by

def identify_redundant_content():
    """Identify potentially redundant content between guides."""
    print("\n🔄 Redundancy Analysis")
    print("=" * 30)

    guides_dir = Path("400_guides")
    content_snippets = defaultdict(list)

    # Look for common patterns that might indicate redundancy
    common_patterns = [
        r"## [A-Z][^#\n]+",  # Section headers
        r"### [A-Z][^#\n]+",  # Subsection headers
        r"```[^`]+```",  # Code blocks
    ]

    for file_path in guides_dir.glob("400_*.md"):
        filename = file_path.name
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Extract common patterns
            for pattern in common_patterns:
                matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
                for match in matches:
                    # Create a hash of the content for comparison
                    content_hash = hash(match.strip())
                    content_snippets[content_hash].append((filename, match.strip()[:100]))

        except Exception as e:
            print(f"❌ Error analyzing {filename}: {e}")

    # Find duplicate content
    duplicates = {k: v for k, v in content_snippets.items() if len(v) > 1}

    if duplicates:
        print(f"⚠️  Found {len(duplicates)} potential content duplications:")
        for content_hash, occurrences in list(duplicates.items())[:5]:  # Show first 5
            print(f"  Content appears in {len(occurrences)} files:")
            for filename, snippet in occurrences:
                print(f"    - {filename}: {snippet}...")
    else:
        print("✅ No obvious content duplications found")

    return duplicates

def suggest_cleanup_actions(categories, reference_counts, referenced_by):
    """Suggest cleanup actions based on analysis."""
    print("\n🧹 Cleanup Recommendations")
    print("=" * 40)

    recommendations = []

    # Check for unused files
    unused_files = []
    for filename in categories["specialized"] + categories["legacy"]:
        if filename not in referenced_by or len(referenced_by[filename]) == 0:
            unused_files.append(filename)

    if unused_files:
        recommendations.append(
            {
                "action": "review_unused",
                "files": unused_files,
                "description": f"Review {len(unused_files)} potentially unused files",
            }
        )
        print(f"📋 Review {len(unused_files)} potentially unused files:")
        for filename in unused_files:
            print(f"    - {filename}")

    # Check for temporary files that can be cleaned up
    temp_files = categories["temporary"]
    if temp_files:
        recommendations.append(
            {
                "action": "cleanup_temporary",
                "files": temp_files,
                "description": f"Clean up {len(temp_files)} temporary files",
            }
        )
        print(f"🗑️  Clean up {len(temp_files)} temporary files:")
        for filename in temp_files:
            print(f"    - {filename}")

    # Check for files with low cross-reference coverage
    low_coverage = []
    for filename, count in reference_counts.items():
        if count < 3 and filename in categories["specialized"]:
            low_coverage.append(filename)

    if low_coverage:
        recommendations.append(
            {
                "action": "improve_coverage",
                "files": low_coverage,
                "description": f"Improve cross-references for {len(low_coverage)} files",
            }
        )
        print(f"🔗 Improve cross-references for {len(low_coverage)} files:")
        for filename in low_coverage:
            print(f"    - {filename} ({reference_counts[filename]} references)")

    return recommendations

def create_cleanup_report(categories, reference_counts, referenced_by, recommendations, duplicates):
    """Create a comprehensive cleanup report."""
    print("\n📋 Cleanup Report Generation")
    print("=" * 40)

    report = {
        "summary": {
            "total_guides": sum(len(files) for files in categories.values()),
            "core_files": len(categories["core"]),
            "specialized_files": len(categories["specialized"]),
            "temporary_files": len(categories["temporary"]),
            "legacy_files": len(categories["legacy"]),
        },
        "cross_references": {
            "most_referenced": dict(sorted(referenced_by.items(), key=lambda x: len(x[1]), reverse=True)[:10]),
            "most_referencing": dict(sorted(reference_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
        },
        "duplicates": {
            "count": len(duplicates),
            "details": {str(k): v for k, v in list(duplicates.items())[:10]},  # Include first 10 duplicates
        },
        "recommendations": recommendations,
        "categories": categories,
    }

    # Save report
    report_path = "documentation_cleanup_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"✅ Cleanup report saved to {report_path}")
    return report

def main():
    """Main documentation cleanup function."""
    print("🧹 Documentation Cleanup Analysis")
    print("=" * 50)

    # Analyze guide files
    categories, guide_files = analyze_guide_files()

    # Check cross-references
    reference_counts, referenced_by = check_cross_references()

    # Identify redundant content
    duplicates = identify_redundant_content()

    # Suggest cleanup actions
    recommendations = suggest_cleanup_actions(categories, reference_counts, referenced_by)

    # Create cleanup report
    report = create_cleanup_report(categories, reference_counts, referenced_by, recommendations, duplicates)

    print("\n✅ Documentation cleanup analysis complete!")
    print("📊 Summary:")
    print(f"  - Total Guides: {report['summary']['total_guides']}")
    print(f"  - Core Files: {report['summary']['core_files']}")
    print(f"  - Specialized Files: {report['summary']['specialized_files']}")
    print(f"  - Temporary Files: {report['summary']['temporary_files']}")
    print(f"  - Legacy Files: {report['summary']['legacy_files']}")
    print(f"  - Recommendations: {len(recommendations)}")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
