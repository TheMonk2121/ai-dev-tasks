#!/usr/bin/env python3
"""
Test script to consult local DSPy models about memory system implementation
"""

import sys

# Add src to path
sys.path.append("src")

from src.dspy_modules.model_switcher import cursor_orchestrate_task


def test_memory_consultation():
    """Test consulting local models about memory system implementation"""

    print("🧠 Consulting Local DSPy Models About 5-Layer Memory System")
    print("=" * 60)

    # Test with each role
    roles = ["planner", "implementer", "researcher", "coder"]

    for role in roles:
        print(f"\n🎭 Testing {role.upper()} role:")
        print("-" * 40)

        task = "Review our proposed 5-layer memory system implementation with Turn Buffer, Rolling Summary, Entity Fact Store, Episodic Memory, and Semantic Index. We want to add hybrid rankers combining cosine similarity, BM25, and recency. Also a pruner with audit logs and UPSERT helpers for entity facts. How does this compare to our current LTST memory system? What are the implementation priorities and potential challenges?"

        try:
            result = cursor_orchestrate_task(task, "analysis", role)

            if result and "response" in result:
                print(f"✅ {role.capitalize()} Response:")
                print(result["response"][:2000] + "..." if len(result["response"]) > 2000 else result["response"])
            elif result and "plan" in result:
                print(f"✅ {role.capitalize()} Plan:")
                print(result["plan"][:2000] + "..." if len(result["plan"]) > 2000 else result["plan"])
            else:
                print(f"❌ No response from {role}")
                print(f"Result keys: {list(result.keys()) if result else 'No result'}")

        except Exception as e:
            print(f"❌ Error consulting {role}: {e}")

    print("\n" + "=" * 60)
    print("🎯 Consultation Complete!")


if __name__ == "__main__":
    test_memory_consultation()
