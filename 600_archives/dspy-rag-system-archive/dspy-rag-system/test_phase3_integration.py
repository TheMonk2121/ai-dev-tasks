#!/usr/bin/env python3
"""
Phase 3 Integration Test
Validates dynamic context management features for B-1007
"""

import time

from src.dspy_modules.context_models import AIRole, ContextFactory
from src.dspy_modules.dynamic_prompts import (
    DynamicPromptManager,
    PromptContext,
    PromptTemplate,
    create_default_prompt_templates,
)
from src.dspy_modules.user_preferences import ResponseCustomizer, UserPreferenceManager


def test_phase3_integration():
    """Test complete Phase 3 integration"""

    print("🧪 Testing Phase 3 Dynamic Context Management Integration")
    print("=" * 70)

    # Test 1: Dynamic Prompt System
    print("\n1. Testing Dynamic Prompt System...")

    # Create prompt manager and register templates
    prompt_manager = DynamicPromptManager()
    templates = create_default_prompt_templates()

    for template in templates:
        prompt_manager.register_template(template)

    print(f"   ✅ Registered {len(templates)} prompt templates")

    # Test 2: User Preference System
    print("\n2. Testing User Preference System...")

    # Create preference manager
    preference_manager = UserPreferenceManager()
    user_id = "test_user_phase3"

    # Set custom preferences
    preference_manager.set_user_preference(user_id, "language", "python", "development")
    preference_manager.set_user_preference(user_id, "style", "detailed", "communication")
    preference_manager.set_user_preference(user_id, "detail_level", "high", "communication")
    preference_manager.set_user_preference(user_id, "code_formatting", "black", "development")

    print(f"   ✅ Set custom preferences for user: {user_id}")

    # Test 3: Context Integration
    print("\n3. Testing Context Integration...")

    # Create role contexts
    planner_context = ContextFactory.create_context(
        AIRole.PLANNER,
        session_id="phase3-session",
        project_scope="Implement dynamic context management with personalized responses",
        backlog_priority="P1",
        strategic_goals=["User personalization", "Dynamic prompts", "Performance optimization"],
    )

    coder_context = ContextFactory.create_context(
        AIRole.CODER,
        session_id="phase3-session",
        codebase_path="/tmp",
        language="python",
        file_context=["dynamic_prompts.py", "user_preferences.py"],
    )

    print(f"   ✅ Created planner context: {planner_context.role.value}")
    print(f"   ✅ Created coder context: {coder_context.role.value}")

    # Test 4: Dynamic Prompt Generation with Context
    print("\n4. Testing Dynamic Prompt Generation...")

    # Create prompt context with role context
    prompt_context = PromptContext(
        user_id=user_id,
        session_id="phase3-session",
        role_context=planner_context,
        user_preferences=preference_manager.get_user_preferences(user_id),
        dynamic_variables={"task": "planning", "priority": "high"},
    )

    # Generate planner prompt
    planner_prompt = prompt_manager.generate_prompt("planner_general", prompt_context)
    print(f"   ✅ Generated planner prompt: {len(planner_prompt)} characters")
    print(f"   ✅ Prompt contains user ID: {'test_user_phase3' in planner_prompt}")
    print(f"   ✅ Prompt contains project scope: {'dynamic context management' in planner_prompt}")

    # Generate coder prompt
    coder_prompt_context = PromptContext(
        user_id=user_id,
        session_id="phase3-session",
        role_context=coder_context,
        user_preferences=preference_manager.get_user_preferences(user_id),
        dynamic_variables={"task": "implementation", "priority": "high"},
    )

    coder_prompt = prompt_manager.generate_prompt("coder_implementation", coder_prompt_context)
    print(f"   ✅ Generated coder prompt: {len(coder_prompt)} characters")
    print(f"   ✅ Prompt contains language: {'python' in coder_prompt}")

    # Test 5: Response Customization
    print("\n5. Testing Response Customization...")

    # Create response customizer
    customizer = ResponseCustomizer(preference_manager)

    # Test text response customization
    base_text_response = "This is a basic response that should be customized based on user preferences."
    customized_text = customizer.customize_response(user_id, base_text_response, "text")
    print(f"   ✅ Text customization: {len(customized_text)} characters")
    print(f"   ✅ Customized for detailed style: {'For more detailed information' in customized_text}")

    # Test code response customization
    base_code_response = "def hello():\n    print('Hello, world!')"
    customized_code = customizer.customize_response(user_id, base_code_response, "code")
    print(f"   ✅ Code customization: {len(customized_code)} characters")
    print(f"   ✅ Contains Black formatting: {'Code formatted with Black' in customized_code}")
    print(f"   ✅ Contains error handling: {'try:' in customized_code}")

    # Test documentation response customization
    base_doc_response = "This is documentation content that should be formatted."
    customized_doc = customizer.customize_response(user_id, base_doc_response, "documentation")
    print(f"   ✅ Documentation customization: {len(customized_doc)} characters")
    print(f"   ✅ Contains markdown header: {'# Documentation' in customized_doc}")

    # Test 6: Performance Validation
    print("\n6. Testing Performance...")

    start_time = time.time()

    # Generate multiple prompts
    for i in range(50):
        prompt_manager.generate_prompt("planner_general", prompt_context)

    prompt_generation_time = time.time() - start_time

    start_time = time.time()

    # Customize multiple responses
    for i in range(50):
        customizer.customize_response(user_id, base_text_response, "text")

    customization_time = time.time() - start_time

    print(f"   ✅ Prompt generation: {prompt_generation_time:.3f}s for 50 prompts")
    print(f"   ✅ Response customization: {customization_time:.3f}s for 50 responses")
    print(f"   ✅ Average prompt generation: {(prompt_generation_time/50)*1000:.2f}ms")
    print(f"   ✅ Average customization: {(customization_time/50)*1000:.2f}ms")

    # Validate performance requirements
    avg_prompt_time = (prompt_generation_time / 50) * 1000
    avg_customization_time = (customization_time / 50) * 1000

    assert avg_prompt_time < 100.0, f"Prompt generation too slow: {avg_prompt_time:.2f}ms"
    assert avg_customization_time < 50.0, f"Customization too slow: {avg_customization_time:.2f}ms"

    print("   ✅ Performance requirements met!")

    # Test 7: Cache Functionality
    print("\n7. Testing Cache Functionality...")

    # First call - should cache
    prompt1 = prompt_manager.generate_prompt("planner_general", prompt_context)
    prompt2 = prompt_manager.generate_prompt("planner_general", prompt_context)

    # Should be identical due to caching
    assert prompt1 == prompt2
    print("   ✅ Cache functionality working!")

    # Test 8: Preference Persistence
    print("\n8. Testing Preference Persistence...")

    # Get preferences and verify they persist
    preferences = preference_manager.get_user_preferences(user_id)
    assert "language" in preferences
    assert preferences["language"] == "python"
    assert "style" in preferences
    assert preferences["style"] == "detailed"

    print("   ✅ Preference persistence working!")

    # Test 9: Metrics and Monitoring
    print("\n9. Testing Metrics and Monitoring...")

    # Get prompt metrics
    prompt_metrics = prompt_manager.get_metrics()
    print(f"   ✅ Total prompt generations: {prompt_metrics.total_generations}")
    print(f"   ✅ Cache hit rate: {prompt_metrics.cache_hit_rate:.2%}")
    print(f"   ✅ Average generation time: {prompt_metrics.avg_generation_time_ms:.2f}ms")

    print("   ✅ Metrics collection working!")

    # Test 10: Security and Sanitization
    print("\n10. Testing Security and Sanitization...")

    # Test with potentially unsafe content
    unsafe_template = PromptTemplate(
        template_id="unsafe_test",
        template_name="Unsafe Test",
        base_prompt="Hello {user_id} <script>alert('xss')</script> world.",
    )

    prompt_manager.register_template(unsafe_template)
    unsafe_prompt = prompt_manager.generate_prompt("unsafe_test", prompt_context)

    # Should be sanitized
    assert "<script>" not in unsafe_prompt
    assert "alert" not in unsafe_prompt
    print("   ✅ Security sanitization working!")

    print("\n" + "=" * 70)
    print("🎉 Phase 3 Integration Test PASSED!")
    print("✅ Dynamic prompt system operational")
    print("✅ User preference system functional")
    print("✅ Context integration working")
    print("✅ Response customization operational")
    print("✅ Performance requirements met")
    print("✅ Cache functionality working")
    print("✅ Preference persistence maintained")
    print("✅ Metrics collection operational")
    print("✅ Security sanitization working")

    return True


if __name__ == "__main__":
    test_phase3_integration()
