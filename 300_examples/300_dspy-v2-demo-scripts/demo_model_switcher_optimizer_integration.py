#!/usr/bin/env python3
"""
Demonstration of ModelSwitcher Optimizer Integration

This script demonstrates how the LabeledFewShot optimizer integrates with
the ModelSwitcher for dynamic optimization across different models.
"""

import os
import sys
import time

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from dspy import Example

from dspy_modules.model_switcher import LocalModel, ModelSwitcher


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


def demonstrate_model_switcher_optimizer_integration():
    """Demonstrate ModelSwitcher optimizer integration"""

    print("🚀 DSPy v2 Optimization: ModelSwitcher Optimizer Integration Demo")
    print("=" * 70)
    print()

    # Create ModelSwitcher
    switcher = ModelSwitcher()
    print("🔧 Created ModelSwitcher")
    print(f"  Optimizer enabled: {switcher.optimizer_enabled}")
    print(f"  Active optimizer: {switcher.active_optimizer}")
    print()

    # Create training examples
    train_examples = [
        Example(inputs={"question": "What is 2+2?"}, outputs={"answer": "4"}),
        Example(inputs={"question": "What is the capital of France?"}, outputs={"answer": "Paris"}),
        Example(inputs={"question": "What color is the sky?"}, outputs={"answer": "Blue"}),
        Example(inputs={"question": "Calculate 3+3"}, outputs={"answer": "6"}),
        Example(inputs={"question": "What is the largest planet?"}, outputs={"answer": "Jupiter"}),
    ]

    print("📊 Training Examples:")
    for i, example in enumerate(train_examples, 1):
        inputs = example.get("inputs")
        outputs = example.get("outputs")
        print(f"  {i}. Q: {inputs['question']} | A: {outputs['answer']}")

    print("\n" + "=" * 70)

    # Test optimizer functionality
    if switcher.optimizer_enabled:
        print("🔧 Testing Optimizer Integration...")

        # Enable optimizer
        success = switcher.enable_optimizer("labeled_few_shot")
        print(f"  Enable optimizer: {'✅ Success' if success else '❌ Failed'}")

        # Create program
        program = MockProgram("DemoProgram")
        print(f"  Created program: {program.name}")

        # Test optimization
        print("\n🔄 Running optimization through ModelSwitcher...")
        start_time = time.time()

        result = switcher.optimize_program(program, train_examples, simple_quality_metric)

        optimization_time = time.time() - start_time

        if result:
            print(f"  ✅ Optimization completed: {result.success}")
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
        else:
            print("  ❌ Optimization failed")

        print("\n" + "=" * 70)

        # Test with different models
        print("🔄 Testing Optimizer with Different Models...")
        models_to_test = [LocalModel.LLAMA_3_1_8B, LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B]

        for model in models_to_test:
            print(f"\n  Testing with {model.value}:")

            # Switch model
            success = switcher.switch_model(model)
            print(f"    Model switch: {'✅ Success' if success else '❌ Failed'}")

            # Verify optimizer is still enabled
            optimizer_stats = switcher.get_optimizer_stats()
            print(f"    Optimizer enabled: {optimizer_stats['enabled']}")
            print(f"    Active optimizer: {optimizer_stats['active_optimizer']}")

        print("\n" + "=" * 70)

        # Test optimizer statistics
        print("📊 Optimizer Statistics:")
        optimizer_stats = switcher.get_optimizer_stats()

        if optimizer_stats["enabled"]:
            stats = optimizer_stats["stats"]
            print(f"  Total optimizations: {stats['total_optimizations']}")
            print(f"  Successful optimizations: {stats['successful_optimizations']}")
            print(f"  Success rate: {stats['success_rate']:.2%}")
            print(f"  Average improvement: {stats['average_improvement']:.4f}")
            print(f"  Total optimization time: {stats['total_optimization_time']:.2f}s")
            print(f"  Average optimization time: {stats['average_optimization_time']:.2f}s")
        else:
            print("  Optimizer not enabled")

        print("\n" + "=" * 70)

        # Test ModelSwitcher stats with optimizer info
        print("📊 ModelSwitcher Statistics with Optimizer Info:")
        stats = switcher.get_stats()

        print(f"  Current model: {stats['current_model']}")
        print(f"  Switch count: {stats['switch_count']}")
        print(f"  Available models: {len(stats['available_models'])}")

        optimizer_info = stats["optimizer"]
        print(f"  Optimizer enabled: {optimizer_info['enabled']}")
        print(f"  Active optimizer: {optimizer_info['active_optimizer']}")

        if optimizer_info["optimization_stats"]:
            opt_stats = optimizer_info["optimization_stats"]
            print(f"  Total optimizations: {opt_stats['total_optimizations']}")
            print(f"  Success rate: {opt_stats['success_rate']:.2%}")

        print("\n" + "=" * 70)

        # Test performance overhead
        print("⚡ Performance Overhead Test:")

        # Test without optimizer
        switcher.disable_optimizer()
        start_time = time.time()

        for _ in range(3):
            switcher.switch_model(LocalModel.LLAMA_3_1_8B)

        time_without_optimizer = time.time() - start_time

        # Test with optimizer
        switcher.enable_optimizer("labeled_few_shot")
        start_time = time.time()

        for _ in range(3):
            switcher.switch_model(LocalModel.LLAMA_3_1_8B)

        time_with_optimizer = time.time() - start_time

        overhead_ratio = time_with_optimizer / time_without_optimizer
        print(f"  Time without optimizer: {time_without_optimizer:.4f}s")
        print(f"  Time with optimizer: {time_with_optimizer:.4f}s")
        print(f"  Overhead ratio: {overhead_ratio:.2f}x")
        print(f"  Performance impact: {'✅ Minimal' if overhead_ratio < 1.5 else '⚠️  High'}")

    else:
        print("❌ Optimizer system not available")
        print("   This demo requires the DSPy optimizer system to be installed.")

    print("\n" + "=" * 70)
    print("🎉 ModelSwitcher Optimizer Integration Demo Complete!")
    print()
    print("Key Features Demonstrated:")
    print("  ✅ Optimizer initialization and configuration")
    print("  ✅ Program optimization through ModelSwitcher")
    print("  ✅ Optimizer persistence across model switches")
    print("  ✅ Statistics collection and reporting")
    print("  ✅ Performance overhead measurement")
    print("  ✅ Error handling and validation")
    print()
    print("Next Steps:")
    print("  🔄 Integrate with real DSPy modules")
    print("  📊 Add more sophisticated optimization techniques")
    print("  🎯 Implement BootstrapFewShot and MIPRO optimizers")
    print("  🔧 Add teleprompter integration for real-time optimization")


if __name__ == "__main__":
    demonstrate_model_switcher_optimizer_integration()
