#!/usr/bin/env python3
"""
Test Local DSPy Models vs Cursor AI

Comprehensive comparison of local model performance against Cursor AI
on various coding tasks to validate the multi-agent system.
"""

import os
import sys
import time
from datetime import datetime
from typing import Any

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import smart_orchestration
from dspy_modules.model_switcher import LocalModel, ModelSwitcher


class CursorAITester:
    """Simulates Cursor AI responses for comparison"""

    def __init__(self):
        self.name = "Cursor AI"

    def generate_response(self, task: str, task_type: str = "coding") -> str:
        """Simulate Cursor AI response"""
        # This would normally call Cursor AI, but for testing we'll simulate
        # realistic responses based on the task type

        if "fibonacci" in task.lower():
            return """Here's a Python function to calculate Fibonacci numbers:

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
            return """Here's a Python function to sort a list:

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

        elif "palindrome" in task.lower():
            return """Here's a Python function to check if a string is a palindrome:

```python
def is_palindrome(text):
    \"\"\"Check if a string is a palindrome (reads the same forwards and backwards).\"\"\"
    # Remove spaces and convert to lowercase
    cleaned = ''.join(char.lower() for char in text if char.isalnum())
    return cleaned == cleaned[::-1]

# Example usage
print(is_palindrome("racecar"))  # True
print(is_palindrome("hello"))    # False
print(is_palindrome("A man a plan a canal Panama"))  # True
```

This function ignores spaces, punctuation, and case."""

        else:
            return f"Cursor AI response to: {task}\n\nThis is a simulated response for testing purposes."


class ModelComparisonTester:
    """Test local models vs Cursor AI"""

    def __init__(self):
        self.model_switcher = ModelSwitcher()
        self.cursor_ai = CursorAITester()
        self.results = []

    def test_single_model(self, task: str, model: LocalModel, role: str = "coder") -> dict[str, Any]:
        """Test a single model on a task"""
        start_time = time.time()

        try:
            # Switch to the model
            if self.model_switcher.switch_model(model):
                # Execute the task
                result = self.model_switcher.orchestrate_task(task, "moderate_coding", role)
                execution_time = time.time() - start_time

                return {
                    "model": model.value,
                    "role": role,
                    "task": task,
                    "result": result.get("execution", "No result"),
                    "execution_time": execution_time,
                    "success": True,
                    "model_used": model.value,
                    "confidence": 0.8,
                }
            else:
                return {
                    "model": model.value,
                    "role": role,
                    "task": task,
                    "result": "Model switch failed",
                    "execution_time": time.time() - start_time,
                    "success": False,
                    "error": "Failed to switch model",
                }
        except Exception as e:
            return {
                "model": model.value,
                "role": role,
                "task": task,
                "result": f"Error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e),
            }

    def test_cursor_ai(self, task: str) -> dict[str, Any]:
        """Test Cursor AI on a task"""
        start_time = time.time()

        try:
            result = self.cursor_ai.generate_response(task)
            execution_time = time.time() - start_time

            return {
                "model": "Cursor AI",
                "role": "general",
                "task": task,
                "result": result,
                "execution_time": execution_time,
                "success": True,
                "model_used": "Cursor AI",
                "confidence": 0.9,  # Simulated confidence
            }
        except Exception as e:
            return {
                "model": "Cursor AI",
                "role": "general",
                "task": task,
                "result": f"Error: {str(e)}",
                "execution_time": time.time() - start_time,
                "success": False,
                "error": str(e),
            }

    def run_comparison_test(self, task: str, task_name: str) -> None:
        """Run comparison test between all models and Cursor AI"""
        print(f"\n🧪 Testing: {task_name}")
        print(f"Task: {task}")
        print("=" * 80)

        # Test all local models
        local_models = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B]

        for model in local_models:
            print(f"\n📊 Testing {model.value}...")
            result = self.test_single_model(task, model, "coder")
            self.results.append(result)

            if result["success"]:
                print(f"   ✅ Success in {result['execution_time']:.2f}s")
                print(f"   🎯 Confidence: {result['confidence']:.2f}")
                print(f"   📝 Result preview: {result['result'][:100]}...")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")

        # Test Cursor AI
        print("\n📊 Testing Cursor AI...")
        cursor_result = self.test_cursor_ai(task)
        self.results.append(cursor_result)

        if cursor_result["success"]:
            print(f"   ✅ Success in {cursor_result['execution_time']:.2f}s")
            print(f"   🎯 Confidence: {cursor_result['confidence']:.2f}")
            print(f"   📝 Result preview: {cursor_result['result'][:100]}...")
        else:
            print(f"   ❌ Failed: {cursor_result.get('error', 'Unknown error')}")

    def run_orchestration_test(self, task: str, task_name: str) -> None:
        """Test the multi-model orchestration"""
        print(f"\n🎭 Testing Multi-Model Orchestration: {task_name}")
        print(f"Task: {task}")
        print("=" * 80)

        start_time = time.time()

        try:
            result = smart_orchestration(task, "moderate_coding")
            execution_time = time.time() - start_time

            print(f"   ✅ Orchestration completed in {execution_time:.2f}s")

            if "plan" in result:
                print(f"   📋 Plan: {result['plan'][:100]}...")
            if "execution" in result:
                print(f"   ⚡ Execution: {result['execution'][:100]}...")
            if "review" in result:
                print(f"   🔍 Review: {result['review'][:100]}...")

        except Exception as e:
            print(f"   ❌ Orchestration failed: {str(e)}")

    def print_summary(self) -> None:
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)

        successful_results = [r for r in self.results if r["success"]]
        failed_results = [r for r in self.results if not r["success"]]

        print(f"✅ Successful tests: {len(successful_results)}")
        print(f"❌ Failed tests: {len(failed_results)}")

        if successful_results:
            print("\n🏆 Performance Rankings (by speed):")
            sorted_results = sorted(successful_results, key=lambda x: x["execution_time"])

            for i, result in enumerate(sorted_results, 1):
                model = result["model"]
                time_taken = result["execution_time"]
                confidence = result.get("confidence", 0.0)
                print(f"   {i}. {model}: {time_taken:.2f}s (confidence: {confidence:.2f})")

        if failed_results:
            print("\n❌ Failed Tests:")
            for result in failed_results:
                print(f"   - {result['model']}: {result.get('error', 'Unknown error')}")


def main():
    """Run comprehensive model comparison tests"""
    print("🚀 DSPy Models vs Cursor AI - Comprehensive Test Suite")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    tester = ModelComparisonTester()

    # Test tasks
    test_tasks = [
        ("Write a Python function to calculate the nth Fibonacci number", "Fibonacci Function"),
        ("Create a function to sort a list of numbers", "List Sorting"),
        ("Write a function to check if a string is a palindrome", "Palindrome Check"),
        ("Create a function to find the maximum value in a list", "Max Value Finder"),
        ("Write a function to reverse a string", "String Reversal"),
    ]

    # Run individual model tests
    print("\n🔬 PHASE 1: Individual Model Testing")
    print("=" * 80)

    for task, task_name in test_tasks:
        tester.run_comparison_test(task, task_name)
        time.sleep(2)  # Brief pause between tests

    # Run orchestration tests
    print("\n🎭 PHASE 2: Multi-Model Orchestration Testing")
    print("=" * 80)

    orchestration_tasks = [
        ("Design and implement a simple calculator class", "Calculator Class"),
        ("Create a data structure for managing a todo list", "Todo List Manager"),
        ("Build a simple text processing utility", "Text Processor"),
    ]

    for task, task_name in orchestration_tasks:
        tester.run_orchestration_test(task, task_name)
        time.sleep(3)  # Longer pause for orchestration

    # Print summary
    tester.print_summary()

    print(f"\n✅ Test suite completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Key Insights:")
    print("   - Compare execution times between models")
    print("   - Check quality of generated code")
    print("   - Evaluate confidence scores")
    print("   - Assess orchestration effectiveness")


if __name__ == "__main__":
    main()
