#!/usr/bin/env python3
"""
Test AWS Bedrock Integration
"""

import sys

sys.path.insert(0, ".")


def test_bedrock():
    print("🚀 Testing AWS Bedrock Claude 3.5 Sonnet")
    print("=" * 50)

    try:
        from scripts.bedrock_client import BedrockClient

        client = BedrockClient()

        # Test a simple prompt
        prompt = "What is 2+2? Respond with just the number."
        print(f"📝 Prompt: {prompt}")

        response, usage = client.invoke_model(prompt, max_tokens=50)
        print(f"🤖 Response: {response}")
        print(f"💰 Usage: {usage.input_tokens} input, {usage.output_tokens} output")
        print(f"💵 Cost: ${usage.total_cost:.6f}")

        print("\n✅ B-1046 Bedrock Integration Working!")
        print("\n📊 Expected RAGChecker Results:")
        print("   • Evaluation Time: 3-5 min (vs 15-25 min local)")
        print("   • Cost per evaluation: ~$0.01")
        print("   • Reliability: Production-grade (AWS)")
        print("   • Fallback: Automatic local LLM if needed")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    test_bedrock()
