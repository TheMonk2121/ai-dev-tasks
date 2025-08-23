#!/usr/bin/env python3
"""
Demonstration of LabeledFewShot Optimizer

This script demonstrates the core functionality of the LabeledFewShot optimizer
based on Adam LK's DSPy transcript implementation.
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dspy import Example
from dspy_modules.optimizers import LabeledFewShotOptimizer, get_optimizer_manager, optimize_program


def simple_quality_metric(example: Example, prediction) -> float:
    """Simple metric function for demonstration"""
    expected = example.get("outputs", {}).get("answer", "")
    actual = prediction.answer if hasattr(prediction, "answer") else str(prediction)

    # Simple similarity metric
    if expected.lower() == actual.lower():
        return 1.0
    elif expected.lower() in actual.lower() or actual.lower() in expected.lower():
        return 0.5
    else:
        return 0.0


class MockProgram:
    """Mock program for demonstration"""

    def __init__(self, name="MockProgram"):
        self.name = name
        self.examples = []

    def forward(self, question: str):
        """Mock forward pass"""

        class MockResult:
            def __init__(self, answer):
                self.answer = answer

        # Simple mock responses based on question content
        if "math" in question.lower() or "calculate" in question.lower():
            return MockResult("The answer is 42")
        elif "capital" in question.lower():
            return MockResult("The capital is Paris")
        elif "color" in question.lower():
            return MockResult("The color is blue")
        else:
            return MockResult("I don't know the answer")

    def demo(self, example):
        """Add example to program (mock implementation)"""
        self.examples.append(example)
        return self


def demonstrate_labeled_few_shot_optimizer():
    """Demonstrate the LabeledFewShot optimizer"""

    print("🚀 DSPy v2 Optimization: LabeledFewShot Optimizer Demo")
    print("=" * 60)
    print()

    # Create training examples
    train_examples = [
        Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
        Example(inputs={"question": "What is the capital of France?"}, outputs={"answer": "Paris"}),
        Example(inputs={"question": "What color is the sky?"}, outputs={"answer": "Blue"}),
        Example(inputs={"question": "Calculate 3+3"}, outputs={"answer": "6"}),
        Example(inputs={"question": "What is the largest planet?"}, outputs={"answer": "Jupiter"}),
    ]

    validation_examples = [
        Example(inputs={"question": "What is 4+4?"}, outputs={"answer": "8"}),
        Example(inputs={"question": "What is the capital of Japan?"}, outputs={"answer": "Tokyo"}),
    ]

    print("📊 Training Examples:")
    for i, example in enumerate(train_examples, 1):
        inputs = example.get("inputs")
        outputs = example.get("outputs")
        print(f"  {i}. Q: {inputs['question']} | A: {outputs['answer']}")

    print("\n📊 Validation Examples:")
    for i, example in enumerate(validation_examples, 1):
        inputs = example.get("inputs")
        outputs = example.get("outputs")
        print(f"  {i}. Q: {inputs['question']} | A: {outputs['answer']}")

    print("\n" + "=" * 60)

    # Create optimizer
    optimizer = LabeledFewShotOptimizer(k=3, metric_threshold=0.1)
    print(f"🔧 Created LabeledFewShot optimizer with k={optimizer.k}")

    # Create program
    program = MockProgram("DemoProgram")
    print(f"🤖 Created mock program: {program.name}")

    # Run optimization
    print("\n🔄 Running LabeledFewShot optimization...")
    start_time = time.time()

    result = optimizer.optimize_program(program, train_examples, simple_quality_metric, validation_examples)

    optimization_time = time.time() - start_time

    print("\n📈 Optimization Results:")
    print(f"  ✅ Success: {result.success}")
    print(f"  📊 Performance Improvement: {result.performance_improvement:.4f}")
    print(f"  📝 Examples Used: {result.examples_used}")
    print(f"  ⏱️  Optimization Time: {result.optimization_time:.2f}s")
    print(f"  🎯 Total Time: {optimization_time:.2f}s")

    if result.metrics:
        print(f"  📊 Baseline Score: {result.metrics['baseline_score']:.4f}")
        print(f"  📊 Optimized Score: {result.metrics['optimized_score']:.4f}")
        print(f"  📊 Improvement %: {result.metrics['improvement_percentage']:.2f}%")

    if result.error_message:
        print(f"  ❌ Error: {result.error_message}")

    print("\n" + "=" * 60)

    # Test optimizer manager
    print("🔧 Testing Optimizer Manager...")
    manager = get_optimizer_manager()

    print(f"  📋 Available optimizers: {list(manager.optimizers.keys())}")
    print(f"  🎯 Active optimizer: {manager.active_optimizer}")

    # Test convenience function
    print("\n🔄 Testing convenience function...")
    result2 = optimize_program(program, train_examples, simple_quality_metric, "labeled_few_shot")

    print(f"  ✅ Success: {result2.success}")
    print(f"  📊 Examples Used: {result2.examples_used}")

    # Show statistics
    print("\n📊 Optimization Statistics:")
    stats = optimizer.get_optimization_stats()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.4f}")
        else:
            print(f"  {key}: {value}")

    print("\n" + "=" * 60)
    print("🎉 LabeledFewShot Optimizer Demo Complete!")
    print()
    print("Key Features Demonstrated:")
    print("  ✅ Example selection (k=3)")
    print("  ✅ Performance measurement")
    print("  ✅ Optimization result tracking")
    print("  ✅ Statistics collection")
    print("  ✅ Manager integration")
    print("  ✅ Convenience functions")
    print()
    print("Next Steps:")
    print("  🔄 Integrate with real DSPy modules")
    print("  📊 Add more sophisticated metrics")
    print("  🎯 Implement BootstrapFewShot optimizer")
    print("  🔧 Add teleprompter integration")


if __name__ == "__main__":
    demonstrate_labeled_few_shot_optimizer()
