#!/usr/bin/env python3
"""
Quality Comparison Test: Local DSPy Models vs Cursor AI

Deep analysis of output quality, code sophistication, and reasoning depth.
"""

import os
import re
import sys
import time
from typing import Any, Dict, List

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from cursor_integration import quick_task, smart_orchestration


class QualityAnalyzer:
    """Analyze code quality and sophistication"""

    def __init__(self):
        self.quality_metrics = {}

    def analyze_code_quality(self, code: str) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        metrics = {
            "lines_of_code": 0,
            "functions": 0,
            "classes": 0,
            "comments": 0,
            "docstrings": 0,
            "error_handling": 0,
            "type_hints": 0,
            "complexity": 0,
            "best_practices": 0,
            "sophistication_score": 0,
        }

        if not code:
            return metrics

        lines = code.split("\n")
        metrics["lines_of_code"] = len([line for line in lines if line.strip() and not line.strip().startswith("#")])

        # Count functions
        metrics["functions"] = len(re.findall(r"def\s+\w+", code))

        # Count classes
        metrics["classes"] = len(re.findall(r"class\s+\w+", code))

        # Count comments
        metrics["comments"] = len(re.findall(r"#.*", code))

        # Count docstrings
        metrics["docstrings"] = len(re.findall(r'""".*?"""', code, re.DOTALL))

        # Count error handling
        metrics["error_handling"] = len(re.findall(r"try:|except|finally", code))

        # Count type hints
        metrics["type_hints"] = len(re.findall(r":\s*\w+(\[\w+\])?", code))

        # Assess complexity (basic heuristic)
        complexity_factors = [
            len(re.findall(r"if\s+", code)),
            len(re.findall(r"for\s+", code)),
            len(re.findall(r"while\s+", code)),
            len(re.findall(r"def\s+", code)),
            len(re.findall(r"class\s+", code)),
        ]
        metrics["complexity"] = sum(complexity_factors)

        # Assess best practices
        best_practices = 0
        if '"""' in code:  # Docstrings
            best_practices += 1
        if "try:" in code:  # Error handling
            best_practices += 1
        if ": " in code and "def " in code:  # Type hints
            best_practices += 1
        if "logging" in code:  # Logging
            best_practices += 1
        if "assert" in code:  # Assertions
            best_practices += 1
        if "from typing import" in code:  # Type imports
            best_practices += 1
        metrics["best_practices"] = best_practices

        # Calculate sophistication score
        sophistication = (
            metrics["functions"] * 2
            + metrics["classes"] * 3
            + metrics["docstrings"] * 2
            + metrics["error_handling"] * 2
            + metrics["type_hints"] * 1
            + metrics["best_practices"] * 2
            + min(metrics["complexity"], 10)  # Cap complexity
        )
        metrics["sophistication_score"] = sophistication

        return metrics

    def analyze_explanation_quality(self, text: str) -> Dict[str, Any]:
        """Analyze explanation and documentation quality"""
        metrics = {
            "word_count": 0,
            "sections": 0,
            "code_blocks": 0,
            "examples": 0,
            "explanations": 0,
            "comprehensiveness": 0,
        }

        if not text:
            return metrics

        # Word count
        metrics["word_count"] = len(text.split())

        # Count sections (headers)
        metrics["sections"] = len(re.findall(r"^#+\s+", text, re.MULTILINE))

        # Count code blocks
        metrics["code_blocks"] = len(re.findall(r"```\w*", text))

        # Count examples
        metrics["examples"] = len(re.findall(r"Example|example|Usage|usage", text))

        # Count explanations
        metrics["explanations"] = len(re.findall(r"This|because|since|therefore|however", text, re.IGNORECASE))

        # Assess comprehensiveness
        comprehensiveness = 0
        if metrics["word_count"] > 100:
            comprehensiveness += 1
        if metrics["sections"] > 0:
            comprehensiveness += 1
        if metrics["code_blocks"] > 0:
            comprehensiveness += 1
        if metrics["examples"] > 0:
            comprehensiveness += 1
        if metrics["explanations"] > 2:
            comprehensiveness += 1
        metrics["comprehensiveness"] = comprehensiveness

        return metrics


def test_local_model_quality(task: str) -> Dict[str, Any]:
    """Test local DSPy model quality"""
    print("\n🧠 Testing Local DSPy Model Quality...")
    start_time = time.time()

    try:
        result = quick_task(task)
        execution_time = time.time() - start_time

        # Analyze quality
        analyzer = QualityAnalyzer()
        code_quality = analyzer.analyze_code_quality(result)
        explanation_quality = analyzer.analyze_explanation_quality(result)

        print(f"   ✅ Generated in {execution_time:.2f}s")
        print(f"   📊 Code Quality Score: {code_quality['sophistication_score']}")
        print(f"   📝 Explanation Quality: {explanation_quality['comprehensiveness']}/5")

        return {
            "model": "Local DSPy Model",
            "success": True,
            "execution_time": execution_time,
            "result": result,
            "code_quality": code_quality,
            "explanation_quality": explanation_quality,
        }
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"   ❌ Failed: {str(e)}")
        return {"model": "Local DSPy Model", "success": False, "execution_time": execution_time, "error": str(e)}


def test_cursor_ai_quality(task: str) -> Dict[str, Any]:
    """Test Cursor AI quality (simulated)"""
    print("\n🤖 Testing Cursor AI Quality...")
    start_time = time.time()

    # Simulate Cursor AI response
    if "advanced algorithm" in task.lower():
        result = """Here's a Python implementation of a binary search tree:

```python
class Node:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, key):
        self.root = self._insert_recursive(self.root, key)

    def _insert_recursive(self, root, key):
        if root is None:
            return Node(key)

        if key < root.key:
            root.left = self._insert_recursive(root.left, key)
        else:
            root.right = self._insert_recursive(root.right, key)

        return root

    def search(self, key):
        return self._search_recursive(self.root, key)

    def _search_recursive(self, root, key):
        if root is None or root.key == key:
            return root

        if key < root.key:
            return self._search_recursive(root.left, key)
        return self._search_recursive(root.right, key)
```

This implements a basic binary search tree with insert and search operations."""

    elif "production ready" in task.lower():
        result = """Here's a production-ready Python class:

```python
import logging
from typing import Optional, List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class User:
    id: int
    name: str
    email: str
    created_at: datetime

class UserManager:
    def __init__(self):
        self.users: Dict[int, User] = {}
        self.logger = logging.getLogger(__name__)

    def add_user(self, name: str, email: str) -> Optional[User]:
        try:
            user_id = len(self.users) + 1
            user = User(
                id=user_id,
                name=name,
                email=email,
                created_at=datetime.now()
            )
            self.users[user_id] = user
            self.logger.info(f"Added user: {user.name}")
            return user
        except Exception as e:
            self.logger.error(f"Failed to add user: {e}")
            return None

    def get_user(self, user_id: int) -> Optional[User]:
        return self.users.get(user_id)

    def list_users(self) -> List[User]:
        return list(self.users.values())
```

This includes logging, type hints, error handling, and proper structure."""

    else:
        result = """Here's a simple Python function:

```python
def calculate_sum(numbers):
    return sum(numbers)

# Example usage
result = calculate_sum([1, 2, 3, 4, 5])
print(result)  # 15
```

This function calculates the sum of a list of numbers."""

    execution_time = time.time() - start_time

    # Analyze quality
    analyzer = QualityAnalyzer()
    code_quality = analyzer.analyze_code_quality(result)
    explanation_quality = analyzer.analyze_explanation_quality(result)

    print(f"   ✅ Generated in {execution_time:.2f}s")
    print(f"   📊 Code Quality Score: {code_quality['sophistication_score']}")
    print(f"   📝 Explanation Quality: {explanation_quality['comprehensiveness']}/5")

    return {
        "model": "Cursor AI",
        "success": True,
        "execution_time": execution_time,
        "result": result,
        "code_quality": code_quality,
        "explanation_quality": explanation_quality,
    }


def test_orchestration_quality(task: str) -> Dict[str, Any]:
    """Test multi-model orchestration quality"""
    print("\n🎭 Testing Multi-Model Orchestration Quality...")
    start_time = time.time()

    try:
        result = smart_orchestration(task, "moderate_coding")
        execution_time = time.time() - start_time

        # Analyze the combined result
        full_result = ""
        if isinstance(result, dict):
            if "plan" in result:
                full_result += f"PLAN:\n{result['plan']}\n\n"
            if "execution" in result:
                full_result += f"EXECUTION:\n{result['execution']}\n\n"
            if "review" in result:
                full_result += f"REVIEW:\n{result['review']}\n\n"
        else:
            full_result = str(result)

        # Analyze quality
        analyzer = QualityAnalyzer()
        code_quality = analyzer.analyze_code_quality(full_result)
        explanation_quality = analyzer.analyze_explanation_quality(full_result)

        print(f"   ✅ Orchestration completed in {execution_time:.2f}s")
        print(f"   📊 Code Quality Score: {code_quality['sophistication_score']}")
        print(f"   📝 Explanation Quality: {explanation_quality['comprehensiveness']}/5")

        return {
            "model": "Multi-Model Orchestration",
            "success": True,
            "execution_time": execution_time,
            "result": full_result,
            "code_quality": code_quality,
            "explanation_quality": explanation_quality,
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


def print_quality_comparison(results: List[Dict[str, Any]]) -> None:
    """Print detailed quality comparison"""
    print("\n" + "=" * 80)
    print("📊 QUALITY COMPARISON ANALYSIS")
    print("=" * 80)

    successful_results = [r for r in results if r["success"]]

    if not successful_results:
        print("❌ No successful results to compare")
        return

    # Compare code quality
    print("\n🏗️ CODE QUALITY COMPARISON:")
    print("-" * 50)

    for result in successful_results:
        model = result["model"]
        code_quality = result.get("code_quality", {})
        sophistication = code_quality.get("sophistication_score", 0)

        print(f"\n{model}:")
        print(f"  🎯 Sophistication Score: {sophistication}")
        print(f"  📝 Functions: {code_quality.get('functions', 0)}")
        print(f"  🏗️ Classes: {code_quality.get('classes', 0)}")
        print(f"  📚 Docstrings: {code_quality.get('docstrings', 0)}")
        print(f"  🛡️ Error Handling: {code_quality.get('error_handling', 0)}")
        print(f"  🏷️ Type Hints: {code_quality.get('type_hints', 0)}")
        print(f"  ✅ Best Practices: {code_quality.get('best_practices', 0)}")

    # Compare explanation quality
    print("\n📖 EXPLANATION QUALITY COMPARISON:")
    print("-" * 50)

    for result in successful_results:
        model = result["model"]
        explanation_quality = result.get("explanation_quality", {})
        comprehensiveness = explanation_quality.get("comprehensiveness", 0)

        print(f"\n{model}:")
        print(f"  📊 Comprehensiveness: {comprehensiveness}/5")
        print(f"  📝 Word Count: {explanation_quality.get('word_count', 0)}")
        print(f"  📋 Sections: {explanation_quality.get('sections', 0)}")
        print(f"  💻 Code Blocks: {explanation_quality.get('code_blocks', 0)}")
        print(f"  📚 Examples: {explanation_quality.get('examples', 0)}")
        print(f"  💡 Explanations: {explanation_quality.get('explanations', 0)}")

    # Overall quality ranking
    print("\n🏆 OVERALL QUALITY RANKING:")
    print("-" * 50)

    quality_scores = []
    for result in successful_results:
        model = result["model"]
        code_quality = result.get("code_quality", {})
        explanation_quality = result.get("explanation_quality", {})

        # Combined quality score
        code_score = code_quality.get("sophistication_score", 0)
        explanation_score = explanation_quality.get("comprehensiveness", 0) * 5
        combined_score = code_score + explanation_score

        quality_scores.append((model, combined_score, code_score, explanation_score))

    # Sort by combined score
    quality_scores.sort(key=lambda x: x[1], reverse=True)

    for i, (model, combined, code, explanation) in enumerate(quality_scores, 1):
        print(f"  {i}. {model}: {combined} points")
        print(f"     🏗️ Code Quality: {code} | 📖 Explanation: {explanation}")


def main():
    """Run quality comparison test"""
    print("🔍 Quality Comparison: Local DSPy Models vs Cursor AI")
    print("=" * 80)

    # Test tasks focused on quality
    quality_tasks = [
        "Create a production-ready Python class for user management with proper error handling, logging, and type hints",
        "Implement an advanced algorithm with detailed explanations of time complexity and space complexity",
        "Write a comprehensive web API with authentication, rate limiting, and proper documentation",
    ]

    results = []

    for i, task in enumerate(quality_tasks, 1):
        print(f"\n🧪 QUALITY TEST {i}: {task[:60]}...")
        print("=" * 80)

        # Test local model
        local_result = test_local_model_quality(task)
        results.append(local_result)

        # Test Cursor AI
        cursor_result = test_cursor_ai_quality(task)
        results.append(cursor_result)

        # Test orchestration
        orchestration_result = test_orchestration_quality(task)
        results.append(orchestration_result)

        print(f"\n📊 Task {i} Results:")
        successful = [r for r in [local_result, cursor_result, orchestration_result] if r["success"]]
        for result in successful:
            model = result["model"]
            code_score = result.get("code_quality", {}).get("sophistication_score", 0)
            explanation_score = result.get("explanation_quality", {}).get("comprehensiveness", 0)
            print(f"  {model}: Code={code_score}, Explanation={explanation_score}/5")

        if i < len(quality_tasks):
            print("\n" + "⏳" * 40)
            time.sleep(2)

    # Print comprehensive quality comparison
    print_quality_comparison(results)

    print("\n✅ Quality comparison completed!")
    print("\n🎯 Key Quality Insights:")
    print("   - Code sophistication and best practices")
    print("   - Explanation depth and comprehensiveness")
    print("   - Production-readiness and error handling")
    print("   - Multi-model orchestration benefits")


if __name__ == "__main__":
    main()
