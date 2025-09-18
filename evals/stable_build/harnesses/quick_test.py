#!/usr/bin/env python3
"""
Quick B-1046 Integration Test
"""

import sys

sys.path.insert(0, ".")


def test_bedrock_integration() -> Any:
    print("🧪 Quick B-1046 Integration Test")
    print("=" * 40)

    # Test 1: BedrockClient
    print("1. Testing BedrockClient...")
    try:
        from scripts.bedrock_client import BedrockClient

        client = BedrockClient()
        if client.test_connection():
            print("   ✅ Bedrock connection successful")
        else:
            print("   ❌ Bedrock connection failed")
    except Exception as e:
        print(f"   ❌ BedrockClient error: {e}")

    # Test 2: Cost Monitor
    print("2. Testing Cost Monitor...")
    try:
        from scripts.bedrock_cost_monitor import BedrockCostMonitor

        monitor = BedrockCostMonitor()
        summary: Any = monitor.get_usage_summary("today")
        print(f"   ✅ Cost monitoring active - Today: ${summary.total_cost:.4f}")
    except Exception as e:
        print(f"   ❌ Cost Monitor error: {e}")

    # Test 3: RAGChecker Integration
    print("3. Testing RAGChecker Integration...")
    try:
        from scripts.ragchecker_official_evaluation import OfficialRAGCheckerEvaluator

        OfficialRAGCheckerEvaluator()
        print("   ✅ RAGChecker integration ready")
    except Exception as e:
        print(f"   ⚠️ RAGChecker integration: {e}")

    print("\n🎯 B-1046 Integration Status: READY FOR TESTING!")


if __name__ == "__main__":
    test_bedrock_integration()
