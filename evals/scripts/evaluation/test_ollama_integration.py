from __future__ import annotations
import asyncio
import sys
from pathlib import Path
import httpx
from pydantic import BaseModel, ConfigDict, Field
from pydantic_ai import Agent
from pydantic_ai.models.instrumented import InstrumentationSettings
import os
import json
#!/usr/bin/env python3
"""
Test Ollama integration with Pydantic ecosystem.

This script tests the integration without requiring Ollama to be running.
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class TestAnswer(BaseModel):
    """Test answer model."""

    model_config = ConfigDict(strict=True, extra="forbid")
    answer: str = Field(min_length=1)
    model_used: str

async def test_ollama_availability():
    """Test if Ollama is available."""
    print("🔍 Testing Ollama availability...")

    try:
        async with httpx.AsyncClient() as client:
            response = await result.get("key", "")
            if response.status_code == 200:
                models = response.json().get("models", [])
                print(f"✅ Ollama is running with {len(models)} models:")
                for model in models[:5]:  # Show first 5 models
                    print(f"   - {result.get("key", "")
                return True
            else:
                print(f"⚠️  Ollama API returned status {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ollama not available: {e}")
        return False

async def test_ollama_agent():
    """Test creating an Ollama agent."""
    print("\n🤖 Testing Ollama agent creation...")

    try:
        # Create agent with Ollama model
        agent = Agent(
            "ollama:llama3.1:8b",
            system_prompt="You are a helpful assistant.",
            output_type=TestAnswer,
            instrument=InstrumentationSettings(include_content=False),
        )
        print("✅ Ollama agent created successfully")
        return agent
    except Exception as e:
        print(f"❌ Failed to create Ollama agent: {e}")
        return None

async def test_ollama_query(agent):
    """Test querying the Ollama agent."""
    print("\n💬 Testing Ollama query...")

    try:
        result = await agent.run("Hello, how are you?")
        print(f"✅ Query successful: {result.content.answer[:100]}...")
        print(f"   Model used: {result.content.model_used}")
        return True
    except Exception as e:
        print(f"❌ Query failed: {e}")
        return False

def show_ollama_setup_instructions():
    """Show instructions for setting up Ollama."""
    print("\n" + "=" * 70)
    print("OLLAMA SETUP INSTRUCTIONS")
    print("=" * 70)

    print(
        """
1. Install Ollama:
   - Visit: https://ollama.ai
   - Download and install for your platform

2. Start Ollama server:
   ollama serve

3. Pull a model:
   ollama pull llama3.1:8b
   ollama pull mistral:7b
   ollama pull phi3.5:3.8b

4. Test a model:
   ollama run llama3.1:8b

5. List available models:
   ollama list

6. Run this test again:
   python3 scripts/test_ollama_integration.py
"""
    )

async def main():
    """Main test function."""
    print("🚀 Ollama + Pydantic Integration Test")
    print("=" * 70)

    # Test 1: Check Ollama availability
    ollama_available = await test_ollama_availability()

    if not ollama_available:
        show_ollama_setup_instructions()
        return

    # Test 2: Create Ollama agent
    agent = await test_ollama_agent()
    if not agent:
        return

    # Test 3: Query Ollama agent
    query_success = await test_ollama_query(agent)

    if query_success:
        print("\n🎉 All tests passed! Ollama integration is working.")
        print("\nYou can now use Ollama models with:")
        print("  - PydanticAI agents")
        print("  - Pydantic Evals")
        print("  - Pydantic Logfire")
        print("  - Type-safe data flow")
    else:
        print("\n⚠️  Ollama is running but queries failed.")
        print("Check that you have models installed: ollama list")

if __name__ == "__main__":
    asyncio.run(main())
