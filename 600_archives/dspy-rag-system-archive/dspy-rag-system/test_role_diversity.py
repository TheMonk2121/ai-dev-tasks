#!/usr/bin/env python3
"""
Test script to check role diversity in DSPy responses
"""

import sys

sys.path.append("src")

from src.dspy_modules.model_switcher import cursor_orchestrate_task


def test_role_diversity():
    """Test if different roles give different responses"""

    simple_prompt = "What is your primary responsibility as an AI assistant?"

    print("🧪 Testing Role Diversity in DSPy Responses")
    print("=" * 60)

    roles = ["planner", "implementer", "researcher", "coder"]

    responses = {}

    for role in roles:
        print(f"\n🎭 Testing {role.upper()} role...")
        try:
            result = cursor_orchestrate_task(simple_prompt, "analysis", role)

            # Handle different response formats based on role
            response = None
            if result and "plan" in result:
                response = result["plan"]
            elif result and "execution" in result:
                response = result["execution"]
            elif result and "analysis" in result:
                response = result["analysis"]
            elif result and "implementation" in result:
                response = result["implementation"]
            elif result and "review" in result:
                response = result["review"]
            elif result and "response" in result:
                response = result["response"]
            elif result and "error" in result:
                print(f"❌ {role.capitalize()} error: {result['error']}")
                continue
            else:
                print(f"❌ No response from {role}")
                print(f"Result keys: {list(result.keys()) if result else 'No result'}")
                continue

            if response:
                responses[role] = response
                print(f"✅ {role.capitalize()} response length: {len(response)} characters")
                print(f"📝 First 200 chars: {response[:200]}...")

        except Exception as e:
            print(f"❌ Error with {role}: {e}")

    # Check for diversity
    print("\n🔍 Diversity Analysis:")
    print(f"Total responses: {len(responses)}")

    if len(responses) > 1:
        # Check if responses are identical
        unique_responses = set(responses.values())
        print(f"Unique responses: {len(unique_responses)}")

        if len(unique_responses) == 1:
            print("❌ ALL RESPONSES ARE IDENTICAL - Role diversity is not working!")
        else:
            print("✅ Responses are diverse - Role diversity is working!")

        # Show differences
        for i, role1 in enumerate(roles):
            for role2 in roles[i + 1 :]:
                if role1 in responses and role2 in responses:
                    resp1 = responses[role1]
                    resp2 = responses[role2]
                    if resp1 == resp2:
                        print(f"⚠️  {role1} and {role2} have identical responses")
                    else:
                        print(f"✅ {role1} and {role2} have different responses")
    else:
        print("❌ Not enough responses to analyze diversity")


if __name__ == "__main__":
    test_role_diversity()
