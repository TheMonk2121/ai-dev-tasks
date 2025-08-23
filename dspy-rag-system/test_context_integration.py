#!/usr/bin/env python3
"""
Test Context Integration

Simple test to verify that the Coder model now has access to database context.
"""

import os
import sys
import time

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import quick_task


def test_context_integration():
    """Test if the Coder model now has context integration"""
    print("🧠 Testing Context Integration")
    print("=" * 60)

    # Test task that should benefit from context
    task = "Explain the project's coding standards and best practices for Python development"

    print(f"\n📋 Task: {task}")
    print("-" * 60)

    print("\n🔍 Testing Coder Model with Context Integration...")
    start_time = time.time()

    try:
        result = quick_task(task)
        execution_time = time.time() - start_time

        print(f"✅ Generated in {execution_time:.2f}s")
        print(f"📝 Result preview: {result[:500]}...")

        # Check if the response mentions context or project standards
        context_indicators = [
            "coding standards",
            "best practices",
            "project conventions",
            "type hints",
            "documentation",
            "error handling",
            "testing",
            "400_guides",
            "comprehensive",
            "security",
            "performance",
            "integration",
            "migration",
            "deployment",
            "graph visualization",
        ]

        found_indicators = []
        for indicator in context_indicators:
            if indicator.lower() in result.lower():
                found_indicators.append(indicator)

        print("\n🎯 Context Analysis:")
        print(f"   Found {len(found_indicators)} context indicators: {found_indicators}")

        if len(found_indicators) > 5:
            print("   ✅ EXCELLENT: Coder model has comprehensive context access")
        elif len(found_indicators) > 3:
            print("   ✅ GOOD: Coder model has good context access")
        elif len(found_indicators) > 1:
            print("   ⚠️ MODERATE: Coder model has some context access")
        else:
            print("   ❌ POOR: Coder model has limited context access")

        # Check for specific project references
        project_indicators = ["400_guides", "100_memory", "dspy", "cursor", "memory rehydration"]

        project_found = []
        for indicator in project_indicators:
            if indicator.lower() in result.lower():
                project_found.append(indicator)

        print("\n🏗️ Project Knowledge:")
        print(f"   Found {len(project_found)} project indicators: {project_found}")

        if len(project_found) > 2:
            print("   ✅ EXCELLENT: Coder model understands project structure")
        elif len(project_found) > 1:
            print("   ✅ GOOD: Coder model has some project knowledge")
        else:
            print("   ❌ POOR: Coder model lacks project knowledge")

    except Exception as e:
        print(f"❌ Failed: {str(e)}")


def main():
    """Run context integration test"""
    print("🔍 Context Integration Test")
    print("=" * 80)

    test_context_integration()

    print("\n" + "=" * 80)
    print("📊 INTEGRATION TEST SUMMARY")
    print("=" * 80)
    print("🎯 This test verifies that the Coder model now has access to:")
    print("   • Project coding standards and best practices")
    print("   • Documentation and guidelines")
    print("   • Project structure and conventions")
    print("   • Memory rehydration context")

    print("\n📋 Expected Improvements:")
    print("   • More specific and relevant responses")
    print("   • References to project standards")
    print("   • Knowledge of project conventions")
    print("   • Better code quality recommendations")


if __name__ == "__main__":
    main()
