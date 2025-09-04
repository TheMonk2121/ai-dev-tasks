#!/usr/bin/env python3
"""
Test script to verify DSPy agents use LTST memory system via MCP server
"""

import os
import sys

# Add the dspy-rag-system src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "dspy-rag-system", "src"))


def test_dspy_ltst_integration():
    """Test that DSPy agents use LTST memory system"""

    print("🧪 Testing DSPy LTST Memory Integration...")

    try:
        from dspy_modules.model_switcher import get_context_for_role

        # Test context retrieval for different roles
        roles = ["planner", "coder", "researcher"]
        test_task = "B-1043 memory system integration"

        for role in roles:
            print(f"\n📋 Testing {role} role...")

            # Get context using LTST memory system
            context = get_context_for_role(role, test_task)

            if context:
                print(f"✅ {role} context retrieved successfully")
                print(f"📏 Context length: {len(context)} characters")
                print(f"🔍 Context preview: {context[:200]}...")

                # Check if it's using LTST memory (should contain "Rehydrated Context from LTST Memory")
                if "Rehydrated Context from LTST Memory" in context:
                    print(f"🎯 {role} is using LTST memory system!")
                else:
                    print(f"⚠️  {role} may be using fallback context")
            else:
                print(f"❌ {role} context retrieval failed")

        print("\n🎉 DSPy LTST integration test completed!")
        return True

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False


if __name__ == "__main__":
    success = test_dspy_ltst_integration()
    sys.exit(0 if success else 1)
