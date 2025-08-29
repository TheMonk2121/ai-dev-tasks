#!/usr/bin/env python3
"""
Test Coder role specifically with gate simplification prompt
"""

import sys

sys.path.append("src")

from src.dspy_modules.model_switcher import cursor_orchestrate_task


def test_coder_gate_simplification():
    """Test Coder role with gate simplification prompt"""

    print("🧪 Testing CODER Role with Gate Simplification")
    print("=" * 60)

    discussion_prompt = """Analyze the current gate system and provide recommendations for simplification.

Current Gates:
1. Input Validation Gate - validates roles and tasks
2. Rate Limiting Gate - 100 requests/hour limit
3. Security Monitoring Gate - logs and blocks suspicious activity
4. Failure Threshold Gate - 3 failures = fallback only
5. Memory Rehydrator Availability Gate - checks if memory rehydrator is available
6. Subprocess Timeout Gate - progressive timeouts (5s, 10s, 15s)
7. Cache TTL Gate - 5-minute cache expiration
8. Scribe Context Gate - real-time context availability
9. Performance Optimization Gate - optimized vs standard retrieval
10. Context Monitoring Gate - performance alerts and blocking

The problem: These gates are creating friction and preventing smooth interaction with DSPy agents.

Please provide:
1. Essential gates for core functionality and security
2. Over-engineered gates that can be simplified or removed
3. Simple, elegant gate system design
4. Recommendations for maintaining security while reducing complexity
5. Minimum viable gate system for a solo developer

Focus on practical implementation and coding standards."""

    print("🎭 Testing CODER role with gate simplification prompt...")
    try:
        result = cursor_orchestrate_task(discussion_prompt, "analysis", "coder")

        print(f"Result keys: {list(result.keys()) if result else 'No result'}")

        if result and "implementation" in result:
            print(f"✅ Coder Implementation ({len(result['implementation'])} chars):")
            print(result["implementation"])
        elif result and "error" in result:
            print(f"❌ Coder Error: {result['error']}")
        else:
            print("❌ No response from Coder")
            print(f"Result: {result}")

    except Exception as e:
        print(f"❌ Error with Coder: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    test_coder_gate_simplification()
