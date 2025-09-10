#!/usr/bin/env python3
"""
Test script to fix Ollama connection issues in DSPy system
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

import dspy

from src.dspy_modules.model_switcher import LocalModel, ModelSwitcher


def test_models():
    """Test different models to find one that works"""
    models_to_test = [LocalModel.MISTRAL_7B, LocalModel.PHI_3_5_3_8B, LocalModel.LLAMA_3_1_8B]

    switcher = ModelSwitcher()

    for model in models_to_test:
        print(f"\nTesting {model.value}...")
        try:
            success = switcher.switch_model(model)
            if success:
                print(f"✅ {model.value} works!")
                return model
            else:
                print(f"❌ {model.value} failed")
        except Exception as e:
            print(f"❌ {model.value} error: {e}")

    return None


def test_dspy_with_model(model):
    """Test DSPy system with a working model"""
    print(f"\nTesting DSPy system with {model.value}...")

    try:
        # Configure DSPy with the working model
        lm = dspy.LM(
            model=f"ollama/{model.value}",
            temperature=0.0,
            max_tokens=4096,
        )
        dspy.configure(lm=lm)

        # Test with a simple query
        response = lm("Say 'Hello DSPy!'")
        print(f"✅ DSPy response: {response}")
        return True

    except Exception as e:
        print(f"❌ DSPy test failed: {e}")
        return False


if __name__ == "__main__":
    print("🔧 Testing Ollama models for DSPy integration...")

    # Test models
    working_model = test_models()

    if working_model:
        print(f"\n🎉 Found working model: {working_model.value}")

        # Test DSPy integration
        if test_dspy_with_model(working_model):
            print(f"\n✅ DSPy integration successful with {working_model.value}")
            print(f"💡 To use this model, configure DSPy to use: ollama/{working_model.value}")
        else:
            print("\n❌ DSPy integration failed")
    else:
        print("\n❌ No working models found")
        print("💡 Try restarting Ollama: brew services restart ollama")
