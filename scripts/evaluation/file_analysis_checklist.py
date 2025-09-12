from __future__ import annotations
import os
import sys
from typing import Any
from typing import Any, Dict, List, Optional, Union
#!/usr/bin/env python3
"""
File Analysis Checklist Enforcer
Ensures proper analysis before suggesting file deletion or deprecation
"""

def check_context_loading():
    """Step 1: Verify context loading files exist and are readable"""
    required_files = [
        "100_cursor-memory-context.md",
        "000_backlog.md",
        "400_system-overview.md",
        "400_project-overview.md",
    ]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ MISSING CONTEXT FILES:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    print("✅ Step 1: Context loading files available")
    return True

def check_file_organization():
    """Step 2: Verify file organization understanding"""
    required_files = ["200_naming-conventions.md", "400_context-priority-guide.md"]

    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)

    if missing_files:
        print("❌ MISSING ORGANIZATION FILES:")
        for file in missing_files:
            print(f"   - {file}")
        return False

    print("✅ Step 2: File organization files available")
    return True

def analyze_file_references(target_file: str) -> dict[str, Any]:
    """Step 3: Cross-reference analysis"""
    if not os.path.exists(target_file):
        return {"error": f"Target file {target_file} does not exist"}

    # Find all files that reference the target file
    references = []
    core_files = ["100_cursor-memory-context.md", "000_backlog.md", "400_system-overview.md"]
    core_references = []

    # Search for references in markdown files
    for root, dirs, files in os.walk("."):
        if "venv" in root or "600_archives" in root:
            continue

        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                        if target_file in content:
                            references.append(file_path)
                            if file in core_files:
                                core_references.append(file_path)
                except Exception as e:
                    print(f"Warning: Could not read {file_path}: {e}")

    return {
        "target_file": target_file,
        "total_references": len(references),
        "core_references": len(core_references),
        "references": references,
        "core_references_list": core_references,
    }

def check_content_freshness(target_file: str) -> dict[str, Any]:
    """Step 4: Content analysis"""
    if not os.path.exists(target_file):
        return {"error": f"Target file {target_file} does not exist"}

    try:
        with open(target_file, encoding="utf-8") as f:
            content = f.read()

        # Check for legacy model references
        legacy_models = ["Mistral", "Yi-Coder", "Mixtral"]
        legacy_references = []
        for model in legacy_models:
            if model in content:
                legacy_references.append(model)

        # Check for memory context importance
        memory_context = "LOW"
        if "" in content:
            memory_context = "HIGH"
        elif "" in content:
            memory_context = "MEDIUM"

        # Check for recent timestamps
        recent_indicators = ["2024-08", "2024-09", "2024-10", "2024-11", "2024-12"]
        is_recent = any(indicator in content for indicator in recent_indicators)

        return {
            "legacy_model_references": legacy_references,
            "memory_context_importance": memory_context,
            "is_recent": is_recent,
            "content_length": len(content),
        }
    except Exception as e:
        return {"error": f"Could not analyze content: {e}"}

def determine_file_tier(target_file: str, reference_analysis: dict, content_analysis: dict) -> str:
    """Step 6: Tier-based decision"""

    # Check if it's a core file
    core_files = ["000_backlog.md", "100_cursor-memory-context.md", "400_system-overview.md"]
    if target_file in core_files:
        return "TIER_1_CRITICAL"

    # Check if referenced by core files
    if reference_analysis.get("core_references", 0) > 0:
        return "TIER_2_HIGH"

    # Check memory context importance
    if content_analysis.get("memory_context_importance") == "HIGH":
        return "TIER_2_HIGH"

    # Check if in archives
    if "600_archives" in target_file or "legacy" in target_file.lower():
        return "TIER_3_MEDIUM"

    # Check if orphaned
    if reference_analysis.get("total_references", 0) == 0:
        return "TIER_4_LOW"

    return "TIER_2_HIGH"  # Default to high tier for safety

def run_analysis_checklist(target_file: str):
    """Run the complete mandatory analysis checklist"""
    print("🚨 MANDATORY FILE ANALYSIS CHECKLIST")
    print("=" * 50)

    # Step 1: Context Loading
    print("\n📋 Step 1: Context Loading")
    if not check_context_loading():
        print("❌ FAILED: Cannot proceed without context files")
        return False

    # Step 2: File Organization
    print("\n📋 Step 2: File Organization Understanding")
    if not check_file_organization():
        print("❌ FAILED: Cannot proceed without organization files")
        return False

    # Step 3: Cross-Reference Analysis
    print(f"\n📋 Step 3: Cross-Reference Analysis for {target_file}")
    reference_analysis = analyze_file_references(target_file)
    if "error" in reference_analysis:
        print(f"❌ ERROR: {reference_analysis['error']}")
        return False

    print(f"   - Total references: {reference_analysis['total_references']}")
    print(f"   - Core file references: {reference_analysis['core_references']}")
    if reference_analysis["core_references_list"]:
        print(f"   - Referenced by: {', '.join(reference_analysis['core_references_list'])}")

    # Step 4: Content Analysis
    print(f"\n📋 Step 4: Content Analysis for {target_file}")
    content_analysis = check_content_freshness(target_file)
    if "error" in content_analysis:
        print(f"❌ ERROR: {content_analysis['error']}")
        return False

    print(f"   - Memory context: {content_analysis['memory_context_importance']}")
    print(f"   - Legacy model references: {content_analysis['legacy_model_references']}")
    print(f"   - Recent content: {content_analysis['is_recent']}")

    # Step 5: Safety Validation
    print("\n📋 Step 5: Safety Validation")
    print("   - Cross-references shown above")
    print(
        "   - Legacy evidence: Legacy model references found"
        if content_analysis["legacy_model_references"]
        else "   - Legacy evidence: No legacy models found"
    )
    print("   - Alternative: Suggest archiving rather than deletion")

    # Step 6: Tier-Based Decision
    print("\n📋 Step 6: Tier-Based Decision")
    tier = determine_file_tier(target_file, reference_analysis, content_analysis)
    print(f"   - Determined tier: {tier}")

    # Final Recommendation
    print("\n🎯 FINAL RECOMMENDATION")
    if tier == "TIER_1_CRITICAL":
        print("❌ DO NOT DELETE: Critical file - never suggest removal")
    elif tier == "TIER_2_HIGH":
        print("⚠️  ARCHIVE ONLY: High-value file - extensive analysis required")
    elif tier == "TIER_3_MEDIUM":
        print("📦 ARCHIVE: Medium-value file - preserve for historical context")
    elif tier == "TIER_4_LOW":
        print("✅ SAFE TO REMOVE: Low-value file - safe with validation")

    print("\n📊 Analysis Summary:")
    print(f"   - File: {target_file}")
    print(f"   - Tier: {tier}")
    print(f"   - References: {reference_analysis['total_references']}")
    print(f"   - Core references: {reference_analysis['core_references']}")
    print(f"   - Memory context: {content_analysis['memory_context_importance']}")
    print(f"   - Legacy models: {content_analysis['legacy_model_references']}")

    return True

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_analysis_checklist.py <target_file>")
        print("Example: python file_analysis_checklist.py CURSOR_NATIVE_AI_STRATEGY.md")
        sys.exit(1)

    target_file = sys.argv[1]
    success = run_analysis_checklist(target_file)

    if not success:
        sys.exit(1)
