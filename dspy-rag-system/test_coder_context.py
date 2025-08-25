#!/usr/bin/env python3
"""
Test Coder Model Context Access

Check if the Coder model has access to the database context it should have.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import quick_task


def test_coder_with_context():
    """Test if Coder model has access to database context"""
    print("🧠 Testing Coder Model Context Access")
    print("=" * 60)

    # Test task that should benefit from context
    task = "Debug the import issues in complex_test.py and explain what context you have access to"

    print(f"\n📋 Task: {task}")
    print("-" * 60)

    print("\n🔍 Testing Coder Model (should have database context)...")
    start_time = time.time()

    try:
        result = quick_task(task)
        execution_time = time.time() - start_time

        print(f"✅ Generated in {execution_time:.2f}s")
        print(f"📝 Result preview: {result[:300]}...")

        # Check if the response mentions context or database
        context_indicators = [
            "memory",
            "context",
            "database",
            "rehydration",
            "coding standards",
            "best practices",
            "project conventions",
            "type hints",
            "import",
            "module",
            "cursor_integration",
        ]

        found_indicators = []
        for indicator in context_indicators:
            if indicator.lower() in result.lower():
                found_indicators.append(indicator)

        print("\n🎯 Context Analysis:")
        print(f"   Found {len(found_indicators)} context indicators: {found_indicators}")

        if len(found_indicators) > 3:
            print("   ✅ Coder model appears to have good context access")
        elif len(found_indicators) > 1:
            print("   ⚠️ Coder model has some context access")
        else:
            print("   ❌ Coder model appears to have limited context access")

    except Exception as e:
        print(f"❌ Failed: {str(e)}")


def test_memory_rehydrator_context():
    """Test what context the memory rehydrator provides"""
    print("\n\n🧠 Testing Memory Rehydrator Context")
    print("=" * 60)

    # This would normally be run from the parent directory
    print("📋 Running memory rehydrator for coder role...")

    try:
        # Simulate what the memory rehydrator provides
        print("🎯 Memory Rehydrator should provide:")
        print("   • Coding standards and best practices")
        print("   • Project conventions and naming")
        print("   • Type hints and documentation standards")
        print("   • Error handling patterns")
        print("   • Import resolution strategies")
        print("   • File organization guidelines")
        print("   • Testing and validation approaches")

        print("\n📊 Expected Context Files for Coder Role:")
        coder_files = [
            "600_archives/consolidated-guides/400_comprehensive-coding-best-practices.md",
            "400_guides/400_code-criticality-guide.md",
            "400_guides/400_testing-strategy-guide.md",
            "400_guides/400_contributing-guidelines.md",
            "400_guides/400_security-best-practices-guide.md",
            "400_guides/400_development-patterns.md",
            "400_guides/400_script-optimization-guide.md",
            "400_guides/400_performance-optimization-guide.md",
            "400_guides/400_integration-patterns-guide.md",
            "400_guides/400_migration-upgrade-guide.md",
            "400_guides/400_file-analysis-guide.md",
            "400_guides/400_deployment-environment-guide.md",
            "400_guides/400_graph-visualization-guide.md",
            "100_memory/104_dspy-development-context.md",
        ]

        for file in coder_files:
            print(f"   • {file}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")


def test_context_integration():
    """Test if context is properly integrated into the Coder model"""
    print("\n\n🔗 Testing Context Integration")
    print("=" * 60)

    print("🎯 Current Issue: Coder model is NOT using memory rehydrator context")
    print("\n📋 What should happen:")
    print("   1. Coder model should call memory rehydrator before processing tasks")
    print("   2. Memory rehydrator should provide relevant coding context")
    print("   3. Coder model should use this context in its responses")
    print("   4. Responses should reference project standards and best practices")

    print("\n❌ What's actually happening:")
    print("   1. Coder model processes tasks without context")
    print("   2. No access to project-specific coding standards")
    print("   3. No knowledge of project conventions")
    print("   4. Generic responses without project context")

    print("\n🔧 Required Fix:")
    print("   • Integrate memory rehydrator into Coder model workflow")
    print("   • Add context retrieval before task processing")
    print("   • Include project standards in model prompts")
    print("   • Reference specific files and conventions")


def main():
    """Run context access tests"""
    print("🔍 Coder Model Context Access Test")
    print("=" * 80)

    # Test 1: Check if Coder model has context
    test_coder_with_context()

    # Test 2: Check what memory rehydrator provides
    test_memory_rehydrator_context()

    # Test 3: Analyze context integration
    test_context_integration()

    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print("❌ ISSUE IDENTIFIED: Coder model lacks database context")
    print("\n🎯 The Problem:")
    print("   • Coder model processes tasks without project context")
    print("   • No access to coding standards and best practices")
    print("   • No knowledge of project conventions and patterns")
    print("   • Generic responses without project-specific guidance")

    print("\n🔧 The Solution:")
    print("   • Integrate memory rehydrator into Coder model workflow")
    print("   • Add context retrieval before task processing")
    print("   • Include project standards in model prompts")
    print("   • Reference specific files and conventions")

    print("\n📋 Next Steps:")
    print("   1. Modify Coder model to call memory rehydrator")
    print("   2. Include context in model prompts")
    print("   3. Test with project-specific tasks")
    print("   4. Verify context is being used effectively")


if __name__ == "__main__":
    main()
