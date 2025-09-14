#!/usr/bin/env python3
"""
Audit and enforce chunking and embedding standards across the repository.
"""

import os


def audit_chunking_standards() -> dict[str, list[str]]:
    """Audit the codebase for chunking and embedding standard violations."""

    violations = {
        "embedding_dimensions": [],
        "chunking_implementation": [],
        "database_usage": [],
        "model_consistency": [],
    }

    # Check embedding dimensions
    print("🔍 Auditing embedding dimensions...")

    # Check for 1024 dimension usage (should be 384)
    embedding_files = [
        "scripts/utilities/cursor_query_storage.py",
        "scripts/utilities/atlas_graph_storage.py",
        "scripts/utilities/atlas_enhanced_chunking.py",
        "scripts/utilities/atlas_unified_graph_system.py",
    ]

    for file_path in embedding_files:
        if os.path.exists(file_path):
            with open(file_path) as f:
                content = f.read()
                if "embedding_dim = 1024" in content:
                    violations["embedding_dimensions"].append(f"{file_path}: Uses 1024 dimensions (should be 384)")
                if "BAAI/bge-large-en-v1.5" in content:
                    violations["model_consistency"].append(
                        f"{file_path}: Uses BAAI/bge-large-en-v1.5 (should be all-MiniLM-L6-v2)"
                    )

    # Check chunking implementation
    print("🔍 Auditing chunking implementation...")

    # Check if chunking is actually being used
    if os.path.exists("scripts/utilities/cursor_atlas_integration.py"):
        with open("scripts/utilities/cursor_atlas_integration.py") as f:
            content = f.read()
            if "chunk" not in content.lower():
                violations["chunking_implementation"].append("cursor_atlas_integration.py: No chunking implementation")

    # Check database usage
    print("🔍 Auditing database usage...")

    # Check if conv_chunks table is being used
    if os.path.exists("scripts/utilities/cursor_atlas_integration.py"):
        with open("scripts/utilities/cursor_atlas_integration.py") as f:
            content = f.read()
            if "conv_chunks" not in content:
                violations["database_usage"].append("cursor_atlas_integration.py: Not using conv_chunks table")
            if "atlas_node" in content and "conversation" in content:
                violations["database_usage"].append(
                    "cursor_atlas_integration.py: Using atlas_node instead of conv_chunks for conversations"
                )

    return violations


def print_violations(violations: dict[str, list[str]]) -> None:
    """Print all violations found."""

    print("\n🚨 CHUNKING & EMBEDDING STANDARDS VIOLATIONS")
    print("=" * 60)

    total_violations = sum(len(v) for v in violations.values())

    if total_violations == 0:
        print("✅ No violations found!")
        return

    for category, issues in violations.items():
        if issues:
            print(f"\n📋 {category.upper().replace('_', ' ')}:")
            for issue in issues:
                print(f"   ❌ {issue}")

    print(f"\n📊 Total Violations: {total_violations}")


def generate_fix_recommendations() -> None:
    """Generate recommendations for fixing violations."""

    print("\n🔧 FIX RECOMMENDATIONS")
    print("=" * 40)

    print("1. EMBEDDING DIMENSIONS:")
    print("   - Change all embedding_dim = 1024 to embedding_dim = 384")
    print("   - Update vector(1024) to vector(384) in database schemas")
    print("   - Use all-MiniLM-L6-v2 model instead of BAAI/bge-large-en-v1.5")

    print("\n2. CHUNKING IMPLEMENTATION:")
    print("   - Integrate AtlasEnhancedChunking into conversation capture")
    print("   - Implement 350-600 token chunks with 20-25% overlap")
    print("   - Use conv_chunks table instead of atlas_node for conversations")

    print("\n3. DATABASE ARCHITECTURE:")
    print("   - Use conv_chunks table for conversational data")
    print("   - Use atlas_node only for graph relationships and metadata")
    print("   - Implement proper HNSW indexes on conv_chunks.embedding")

    print("\n4. STORAGE FLOW:")
    print("   - Raw conversation → Chunking → conv_chunks → Graph relationships")
    print("   - Memory consolidation processes chunks, not full conversations")
    print("   - Maintain 48-hour retention policy on conv_chunks")


def main():
    """Main audit function."""

    print("🧠 Chunking & Embedding Standards Audit")
    print("=" * 50)

    # Run audit
    violations = audit_chunking_standards()

    # Print results
    print_violations(violations)

    # Generate recommendations
    generate_fix_recommendations()

    # Summary
    total_violations = sum(len(v) for v in violations.values())
    if total_violations > 0:
        print(f"\n⚠️  {total_violations} violations found that need to be fixed!")
        print("   Follow the recommendations above to enforce project standards.")
    else:
        print("\n✅ All chunking and embedding standards are properly enforced!")


if __name__ == "__main__":
    main()
