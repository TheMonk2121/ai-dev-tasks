#!/usr/bin/env python3
"""
Simple Test: Local DSPy Models vs Cursor AI

Quick comparison test to see how local models perform against Cursor AI.
"""

import os
import sys
import time
from typing import Any, Dict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import quick_task, smart_orchestration


def test_local_model(task: str, model_name: str) -> Dict[str, Any]:
    """Test a single local model"""
    print(f"\n📊 Testing {model_name}...")
    start_time = time.time()

    try:
        # Use the quick_task function which uses local models
        result = quick_task(task)
        execution_time = time.time() - start_time

        print(f"   ✅ Success in {execution_time:.2f}s")
        print(f"   📝 Result preview: {result[:150]}...")

        return {"model": model_name, "success": True, "execution_time": execution_time, "result": result}
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Failed: {str(e)}")
        return {"model": model_name, "success": False, "execution_time": execution_time, "error": str(e)}


def test_cursor_ai(task: str) -> Dict[str, Any]:
    """Simulate Cursor AI response"""
    print("\n📊 Testing Cursor AI...")
    start_time = time.time()

    # Simulate Cursor AI response
    if "fibonacci" in task.lower():
        result = """Here's a Python function to calculate Fibonacci numbers:

```python
def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b

# Example usage
print(fibonacci(10))  # 55
```

This uses an iterative approach which is more efficient than recursion for large numbers."""
    elif "sort" in task.lower():
        result = """Here's a Python function to sort a list:

```python
def sort_list(lst):
    \"\"\"Sort a list in ascending order.\"\"\"
    return sorted(lst)

# Example usage
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
sorted_numbers = sort_list(numbers)
print(sorted_numbers)  # [1, 1, 2, 3, 4, 5, 6, 9]
```

The `sorted()` function returns a new sorted list without modifying the original."""
    else:
        result = f"Cursor AI response to: {task}\n\nThis is a simulated response for testing purposes."

    execution_time = time.time() - start_time
    print(f"   ✅ Success in {execution_time:.2f}s")
    print(f"   📝 Result preview: {result[:150]}...")

    return {"model": "Cursor AI", "success": True, "execution_time": execution_time, "result": result}


def test_orchestration(task: str) -> Dict[str, Any]:
    """Test multi-model orchestration"""
    print("\n🎭 Testing Multi-Model Orchestration...")
    start_time = time.time()

    try:
        result = smart_orchestration(task, "moderate_coding")
        execution_time = time.time() - start_time

        print(f"   ✅ Orchestration completed in {execution_time:.2f}s")

        if isinstance(result, dict):
            if "plan" in result:
                print(f"   📋 Plan: {result['plan'][:100]}...")
            if "execution" in result:
                print(f"   ⚡ Execution: {result['execution'][:100]}...")
            if "review" in result:
                print(f"   🔍 Review: {result['review'][:100]}...")

        return {
            "model": "Multi-Model Orchestration",
            "success": True,
            "execution_time": execution_time,
            "result": str(result),
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Orchestration failed: {str(e)}")
        return {
            "model": "Multi-Model Orchestration",
            "success": False,
            "execution_time": execution_time,
            "error": str(e),
        }


def main():
    """Run simple comparison test"""
    print("🚀 Simple Test: Local DSPy Models vs Cursor AI")
    print("=" * 60)

    # Test task
    task = "Write a Python function to calculate the nth Fibonacci number"
    print(f"\n🧪 Testing Task: {task}")
    print("=" * 60)

    results = []

    # Test local models (using quick_task which uses the model switcher)
    results.append(test_local_model(task, "Local DSPy Model"))

    # Test Cursor AI
    results.append(test_cursor_ai(task))

    # Test orchestration
    results.append(test_orchestration(task))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)

    successful_results = [r for r in results if r["success"]]
    failed_results = [r for r in results if not r["success"]]

    print(f"✅ Successful tests: {len(successful_results)}")
    print(f"❌ Failed tests: {len(failed_results)}")

    if successful_results:
        print("\n🏆 Performance Rankings (by speed):")
        sorted_results = sorted(successful_results, key=lambda x: x["execution_time"])

        for i, result in enumerate(sorted_results, 1):
            model = result["model"]
            time_taken = result["execution_time"]
            print(f"   {i}. {model}: {time_taken:.2f}s")

    if failed_results:
        print("\n❌ Failed Tests:")
        for result in failed_results:
            print(f"   - {result['model']}: {result.get('error', 'Unknown error')}")

    print("\n✅ Test completed!")
    print("\n🎯 Key Insights:")
    print("   - Local models provide true inference vs simulated responses")
    print("   - Multi-model orchestration enables complex workflows")
    print("   - Hardware constraints affect performance but enable privacy")


if __name__ == "__main__":
    main()
