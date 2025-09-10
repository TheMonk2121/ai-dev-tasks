#!/usr/bin/env python3
"""
Test script for Model Switcher

Tests the model switching functionality and integration with DSPy.
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import LocalModel, ModelSwitcher


def test_model_switcher():
    """Test the model switcher functionality."""
    print("🧪 Testing Model Switcher...")

    # Create model switcher
    switcher = ModelSwitcher()

    # Test 1: Basic model switching
    print("\n1. Testing basic model switching...")
    success = switcher.switch_model(LocalModel.LLAMA_3_1_8B)
    print(f"   Switch to Llama 3.1 8B: {'✅' if success else '❌'}")

    success = switcher.switch_model(LocalModel.MISTRAL_7B)
    print(f"   Switch to Mistral 7B: {'✅' if success else '❌'}")

    # Test 2: Task-based model selection
    print("\n2. Testing task-based model selection...")
    planning_model = switcher.get_model_for_task("planning")
    print(f"   Planning task → {planning_model.value}")

    fast_model = switcher.get_model_for_task("fast_completion")
    print(f"   Fast completion task → {fast_model.value}")

    large_context_model = switcher.get_model_for_task("large_context")
    print(f"   Large context task → {large_context_model.value}")

    # Test 3: Role-based model selection
    print("\n3. Testing role-based model selection...")
    planner_model = switcher.get_model_for_role("planner")
    print(f"   Planner role → {planner_model.value}")

    implementer_model = switcher.get_model_for_role("implementer")
    print(f"   Implementer role → {implementer_model.value}")

    coder_model = switcher.get_model_for_role("coder")
    print(f"   Coder role → {coder_model.value}")

    # Test 4: Task orchestration
    print("\n4. Testing task orchestration...")
    task = "Create a Python function to calculate fibonacci numbers"
    results = switcher.orchestrate_task(task, "moderate_coding", "coder")

    print("   Task orchestration results:")
    for step, result in results.items():
        print(f"     {step}: {result[:100]}...")

    # Test 5: Statistics
    print("\n5. Testing statistics...")
    stats = switcher.get_stats()
    print(f"   Current model: {stats['current_model']}")
    print(f"   Switch count: {stats['switch_count']}")
    print(f"   Available models: {stats['available_models']}")

    print("\n✅ Model Switcher tests completed!")


def test_dspy_integration():
    """Test DSPy integration with model switcher."""
    print("\n🧪 Testing DSPy Integration...")

    try:
        from dspy_modules.model_switcher import ModelSwitchingModule

        # Create model switcher and module
        switcher = ModelSwitcher()
        module = ModelSwitchingModule(switcher)

        # Test DSPy module
        task = "Write a simple Python function"
        result = module.forward(task, "light_coding", "coder")

        print(f"   DSPy module result: {result[:100]}...")
        print("   ✅ DSPy integration successful!")

    except Exception as e:
        print(f"   ❌ DSPy integration failed: {e}")


if __name__ == "__main__":
    test_model_switcher()
    test_dspy_integration()
