#!/usr/bin/env python3
"""
Test script to verify if context is being included in model prompts.
"""

import os
import sys

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from dspy_modules.model_switcher import ModelSwitcher, get_context_for_role


def test_context_inclusion():
    """Test if context is being included in model prompts."""

    print("🧠 Testing Context Inclusion...\n")

    # Test 1: Get context directly
    print("📋 Test 1: Getting context directly")
    print("-" * 50)

    try:
        context = get_context_for_role("researcher", "What is DSPy?")
        print(f"Context length: {len(context)} characters")
        print(f"Context preview: {context[:500]}...")

        # Check if DSPy is mentioned in context
        if "DSPy" in context:
            print("✅ DSPy is mentioned in context")
        else:
            print("❌ DSPy is NOT mentioned in context")

    except Exception as e:
        print(f"❌ Error getting context: {e}")

    print("\n" + "=" * 60 + "\n")

    # Test 2: Check if context is used in model response
    print("📋 Test 2: Checking if context is used in model response")
    print("-" * 50)

    try:
        switcher = ModelSwitcher()
        switcher.switch_model(switcher.get_model_for_role("researcher"))

        # Ask a specific question that should use the context
        question = "Based on the project context, what is DSPy and what does it do in this AI development ecosystem?"
        response = switcher.current_lm(question)
        response_text = response[0] if isinstance(response, list) else str(response)

        print(f"Question: {question}")
        print(f"Response: {response_text[:300]}...")

        # Check if response mentions DSPy correctly
        if "DSPy" in response_text and ("framework" in response_text.lower() or "ai" in response_text.lower()):
            print("✅ Response correctly mentions DSPy as an AI framework")
        elif "DSPy" in response_text:
            print("⚠️ Response mentions DSPy but may not be accurate")
        else:
            print("❌ Response does not mention DSPy")

    except Exception as e:
        print(f"❌ Error testing model response: {e}")

    print("\n" + "=" * 60 + "\n")

    # Test 3: Test with explicit context prompt
    print("📋 Test 3: Testing with explicit context prompt")
    print("-" * 50)

    try:
        # Get context first
        context = get_context_for_role("researcher", "What is DSPy?")

        # Create explicit prompt with context
        explicit_prompt = f"""Based on the following project context, answer the question:

CONTEXT:
{context[:1000]}...

QUESTION: What is DSPy in this AI development ecosystem?

Please be specific about what DSPy is and how it's used in this project."""

        response = switcher.current_lm(explicit_prompt)
        response_text = response[0] if isinstance(response, list) else str(response)

        print(f"Response: {response_text[:400]}...")

        # Check if response is more accurate
        if "DSPy" in response_text and (
            "framework" in response_text.lower() or "ai" in response_text.lower() or "agent" in response_text.lower()
        ):
            print("✅ Response correctly identifies DSPy as an AI framework")
        else:
            print("❌ Response still not accurate about DSPy")

    except Exception as e:
        print(f"❌ Error testing explicit context: {e}")


if __name__ == "__main__":
    test_context_inclusion()
