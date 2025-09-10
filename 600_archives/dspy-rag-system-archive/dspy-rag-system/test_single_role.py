#!/usr/bin/env python3
"""
Test single role response for memory implementation
"""

import sys

# Add src to path
sys.path.append("src")

from src.dspy_modules.model_switcher import cursor_orchestrate_task


def test_single_role():
    """Test consulting just the planner role about memory implementation"""

    print("🧠 Consulting PLANNER About 5-Layer Memory System")
    print("=" * 60)

    task = "Review our proposed 5-layer memory system implementation with Turn Buffer, Rolling Summary, Entity Fact Store, Episodic Memory, and Semantic Index. We want to add hybrid rankers combining cosine similarity, BM25, and recency. Also a pruner with audit logs and UPSERT helpers for entity facts. How does this compare to our current LTST memory system? What are the implementation priorities and potential challenges?"

    try:
        result = cursor_orchestrate_task(task, "analysis", "coder")

        if result and "response" in result:
            print("✅ CODER Response:")
            print("=" * 40)
            print(result["response"])
        elif result and "plan" in result:
            print("✅ CODER Plan:")
            print("=" * 40)
            print(result["plan"])
        else:
            print("❌ No response from coder")
            print(f"Result keys: {list(result.keys()) if result else 'No result'}")

    except Exception as e:
        print(f"❌ Error consulting coder: {e}")

    print("\n" + "=" * 60)
    print("🎯 Single Role Test Complete!")


if __name__ == "__main__":
    test_single_role()
