#!/usr/bin/env python3
"""
Signature Validation Demo
-------------------------
Demonstrates runtime validation for DSPy signatures.
"""

import sys

sys.path.append("src")

from dspy_modules.documentation_retrieval import DocumentationQuerySignature
from dspy_modules.model_switcher import LocalTaskSignature, ModelSelectionSignature
from dspy_modules.signature_validator import get_signature_performance, get_validation_summary, validate_signature_io


def demo_model_selection_validation():
    """Demonstrate validation with ModelSelectionSignature"""
    print("🔍 **Model Selection Signature Validation**")
    print("=" * 50)

    # Create signature with default values
    signature = ModelSelectionSignature(
        task="default",
        task_type="default",
        complexity="default",
        context_size="0",
        selected_model="default",
        reasoning="default",
        confidence="0.0",
        expected_performance="default",
    )

    # Test valid inputs and outputs
    valid_inputs = {
        "task": "Implement a new feature",
        "task_type": "coding",
        "complexity": "moderate",
        "context_size": 8192,
    }

    valid_outputs = {
        "selected_model": "cursor-native",
        "reasoning": "Best for coding tasks",
        "confidence": 0.85,
        "expected_performance": "High accuracy for code generation",
    }

    print("✅ Testing valid I/O...")
    result = validate_signature_io(signature, valid_inputs, valid_outputs)
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")
    print(f"   Execution time: {result.execution_time:.6f}s")
    print(f"   Input tokens: {result.input_tokens}")
    print(f"   Output tokens: {result.output_tokens}")

    # Test invalid inputs (missing field)
    invalid_inputs = {
        "task": "Implement a new feature",
        "task_type": "coding",
        # Missing complexity and context_size
    }

    print("\n❌ Testing invalid inputs (missing fields)...")
    result = validate_signature_io(signature, invalid_inputs, valid_outputs)
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {result.errors}")
    print(f"   Warnings: {result.warnings}")

    # Test invalid outputs (missing field)
    invalid_outputs = {
        "selected_model": "cursor-native",
        "reasoning": "Best for coding tasks",
        # Missing confidence and expected_performance
    }

    print("\n❌ Testing invalid outputs (missing fields)...")
    result = validate_signature_io(signature, valid_inputs, invalid_outputs)
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {result.errors}")
    print(f"   Warnings: {result.warnings}")


def demo_local_task_validation():
    """Demonstrate validation with LocalTaskSignature"""
    print("\n🔍 **Local Task Signature Validation**")
    print("=" * 50)

    # Create signature with default values
    signature = LocalTaskSignature(
        task="default",
        task_type="default",
        role="default",
        complexity="default",
        result="default",
        confidence="0.0",
        model_used="default",
        reasoning="default",
    )

    # Test valid inputs and outputs
    valid_inputs = {"task": "Write a Python function", "task_type": "coding", "role": "coder", "complexity": "moderate"}

    valid_outputs = {
        "result": "def example_function(): return 'Hello World'",
        "confidence": 0.9,
        "model_used": "cursor-native",
        "reasoning": "Generated a simple Python function",
    }

    print("✅ Testing valid I/O...")
    result = validate_signature_io(signature, valid_inputs, valid_outputs)
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")


def demo_documentation_query_validation():
    """Demonstrate validation with DocumentationQuerySignature"""
    print("\n🔍 **Documentation Query Signature Validation**")
    print("=" * 50)

    # Create signature with default values
    signature = DocumentationQuerySignature(
        user_query="default",
        context_type="default",
        query_type="default",
        processed_query="default",
        search_categories="default",
        expected_context="default",
    )

    # Test valid inputs and outputs
    valid_inputs = {
        "user_query": "How do I use DSPy signatures?",
        "context_type": "implementation",
        "query_type": "reference",
    }

    valid_outputs = {
        "processed_query": "DSPy signature usage implementation reference",
        "search_categories": ["dspy", "signatures", "implementation"],
        "expected_context": "Code examples and usage patterns",
    }

    print("✅ Testing valid I/O...")
    result = validate_signature_io(signature, valid_inputs, valid_outputs)
    print(f"   Valid: {result.is_valid}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Warnings: {len(result.warnings)}")


def demo_performance_metrics():
    """Demonstrate performance metrics collection"""
    print("\n📊 **Performance Metrics Collection**")
    print("=" * 50)

    # Get performance summary
    summary = get_validation_summary()
    print(f"Total validations: {summary['total_validations']}")
    print(f"Success rate: {summary['success_rate']:.2%}")
    print(f"Total errors: {summary['total_errors']}")
    print(f"Total warnings: {summary['total_warnings']}")
    print(f"Signatures tracked: {summary['signatures_tracked']}")
    print(f"Average execution time: {summary['avg_execution_time']:.6f}s")

    # Get specific signature performance
    if "ModelSelectionSignature" in summary["signatures_tracked"]:
        print("\n📈 ModelSelectionSignature Performance:")
        performance = get_signature_performance("ModelSelectionSignature")
        print(f"   Total executions: {performance['total_executions']}")
        print(f"   Success rate: {performance['success_rate']:.2%}")
        print(f"   Average execution time: {performance['avg_execution_time']:.6f}s")
        print(f"   Average input tokens: {performance['avg_input_tokens']:.1f}")
        print(f"   Average output tokens: {performance['avg_output_tokens']:.1f}")


def main():
    """Run all validation demos"""
    print("🚀 **DSPy Signature Validation Demo**")
    print("=" * 60)
    print("This demo shows runtime validation for DSPy signatures.")
    print("It validates input/output field completeness and collects performance metrics.")
    print()

    try:
        demo_model_selection_validation()
        demo_local_task_validation()
        demo_documentation_query_validation()
        demo_performance_metrics()

        print("\n✅ **Demo completed successfully!**")
        print("\nKey benefits of signature validation:")
        print("• Prevents runtime errors from missing fields")
        print("• Ensures data integrity across signatures")
        print("• Collects performance metrics for optimization")
        print("• Provides detailed error reporting")

    except Exception as e:
        print(f"\n❌ **Demo failed: {e}**")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
