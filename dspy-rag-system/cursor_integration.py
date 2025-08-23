#!/usr/bin/env python3
"""
Cursor AI Integration for Local DSPy System

Simple interface for Cursor AI to call local models via DSPy.
Provides clean function calls that Cursor can easily invoke.
"""

import os
import sys
from typing import Any, Dict

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import LocalModel, ModelSwitcher, cursor_execute_task, cursor_orchestrate_task


def quick_task(task: str, task_type: str = "moderate_coding") -> str:
    """
    Quick single-model task execution for Cursor AI

    Args:
        task: Task to perform
        task_type: Type of task (planning, coding, analysis, etc.)

    Returns:
        Task result as string
    """
    try:
        result = cursor_execute_task(task, task_type, "coder")
        if result["success"]:
            return result["result"]
        else:
            return f"Error: {result['error']}"
    except Exception as e:
        return f"Error: {str(e)}"


def smart_orchestration(task: str, task_type: str = "moderate_coding") -> Dict[str, Any]:
    """
    Smart multi-model orchestration for Cursor AI

    Args:
        task: Task to orchestrate
        task_type: Type of task

    Returns:
        Dictionary with orchestration results
    """
    try:
        result = cursor_orchestrate_task(task, task_type, "coder")
        return result
    except Exception as e:
        return {"success": False, "error": str(e), "fallback": "Using Cursor AI fallback"}


def code_generation(prompt: str, language: str = "python") -> str:
    """
    Specialized code generation using local models

    Args:
        prompt: Code generation prompt
        language: Programming language

    Returns:
        Generated code
    """
    task = f"Generate {language} code: {prompt}"
    return quick_task(task, "moderate_coding")


def code_review(code: str, language: str = "python") -> str:
    """
    Code review using local models

    Args:
        code: Code to review
        language: Programming language

    Returns:
        Code review feedback
    """
    task = f"Review this {language} code and provide feedback:\n\n{code}"
    return quick_task(task, "code_review")


def document_analysis(document: str) -> str:
    """
    Document analysis using large context models

    Args:
        document: Document content to analyze

    Returns:
        Analysis result
    """
    task = f"Analyze this document:\n\n{document}"
    return quick_task(task, "documentation_analysis")


def planning_task(description: str) -> str:
    """
    Planning and reasoning tasks

    Args:
        description: Task description to plan

    Returns:
        Planning result
    """
    task = f"Create a detailed plan for: {description}"
    return quick_task(task, "planning")


def get_system_status() -> Dict[str, Any]:
    """
    Get current system status and available models

    Returns:
        System status information
    """
    try:
        switcher = ModelSwitcher()
        stats = switcher.get_stats()
        return {
            "success": True,
            "current_model": stats["current_model"],
            "available_models": stats["available_models"],
            "switch_count": stats["switch_count"],
            "load_times": stats["model_load_times"],
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def switch_to_model(model_name: str) -> Dict[str, Any]:
    """
    Manually switch to a specific model

    Args:
        model_name: Model to switch to (llama3.1:8b, mistral:7b, phi3.5:3.8b)

    Returns:
        Switch result
    """
    try:
        switcher = ModelSwitcher()

        # Map model names to enum
        model_mapping = {
            "llama3.1:8b": LocalModel.LLAMA_3_1_8B,
            "mistral:7b": LocalModel.MISTRAL_7B,
            "phi3.5:3.8b": LocalModel.PHI_3_5_3_8B,
        }

        if model_name not in model_mapping:
            return {"success": False, "error": f"Unknown model: {model_name}. Available: {list(model_mapping.keys())}"}

        success = switcher.switch_model(model_mapping[model_name])
        return {
            "success": success,
            "current_model": switcher.current_model.value if switcher.current_model else None,
            "message": f"Switched to {model_name}" if success else f"Failed to switch to {model_name}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# Example usage for testing
if __name__ == "__main__":
    print("🧪 Testing Cursor Integration...")

    # Test quick task
    print("\n1. Quick task:")
    result = quick_task("Write a Python function to calculate fibonacci numbers")
    print(f"Result: {result[:200]}...")

    # Test code generation
    print("\n2. Code generation:")
    code = code_generation("function to sort a list", "python")
    print(f"Code: {code[:200]}...")

    # Test system status
    print("\n3. System status:")
    status = get_system_status()
    print(f"Status: {status}")

    print("\n✅ Cursor integration test completed!")
