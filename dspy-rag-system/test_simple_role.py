#!/usr/bin/env python3
"""
Simple test to check role-specific prompts
"""

import sys

sys.path.append("src")

from src.dspy_modules.model_switcher import ModelSwitcher


def test_simple_role():
    """Test simple role-specific responses"""

    print("🧪 Testing Simple Role-Specific Responses")
    print("=" * 50)

    switcher = ModelSwitcher()

    # Test with a simple prompt
    simple_prompt = "What is your primary responsibility?"

    roles = ["planner", "implementer", "researcher", "coder"]

    for role in roles:
        print(f"\n🎭 Testing {role.upper()} role...")
        try:
            # Use the orchestrate_task method directly
            result = switcher.orchestrate_task(simple_prompt, "analysis", role)

            print(f"Result keys: {list(result.keys()) if result else 'No result'}")

            if result:
                for key, value in result.items():
                    if isinstance(value, str) and len(value) > 0:
                        print(f"✅ {key}: {len(value)} characters")
                        print(f"📝 Preview: {value[:100]}...")
                    else:
                        print(f"⚠️  {key}: {value}")
            else:
                print("❌ No result returned")

        except Exception as e:
            print(f"❌ Error with {role}: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_simple_role()
