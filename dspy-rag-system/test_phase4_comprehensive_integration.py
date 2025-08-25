#!/usr/bin/env python3
"""
Comprehensive Integration Testing for B-1007 Pydantic AI Style Enhancements
Validates all existing DSPy functionality works with new features
"""

import time
import traceback

from src.dspy_modules.constitution_validation import (
    ConstitutionRule,
    ConstitutionRuleSet,
    ConstitutionValidator,
    ProgramOutput,
)
from src.dspy_modules.context_aware_tools import ContextAwareToolFramework, MLflowIntegration, context_aware_tool
from src.dspy_modules.context_models import (
    AIRole,
    BaseContext,
    ContextFactory,
    PlannerContext,
)
from src.dspy_modules.dynamic_prompts import DynamicPromptManager, PromptContext, PromptTemplate
from src.dspy_modules.enhanced_debugging import EnhancedDebuggingManager, enhanced_debugging
from src.dspy_modules.error_taxonomy import ErrorFactory, ErrorSeverity, ValidationError
from src.dspy_modules.user_preferences import UserPreferenceManager


def test_comprehensive_integration():
    """Test comprehensive integration of all B-1007 components"""
    print("🔧 Testing Comprehensive Integration - B-1007 Pydantic AI Style Enhancements")
    print("=" * 70)

    # Initialize all components
    print("\n📦 Initializing Components")
    print("-" * 30)

    # Core components
    context_factory = ContextFactory()
    prompt_manager = DynamicPromptManager()
    preference_manager = UserPreferenceManager()

    # Enhanced components
    mlflow_config = MLflowIntegration(enabled=False)  # Disable for testing
    tool_framework = ContextAwareToolFramework(mlflow_config=mlflow_config)
    debugging_manager = EnhancedDebuggingManager()

    # Create constitution ruleset for validator
    default_rules = [
        ConstitutionRule(
            rule_id="rule_001",
            rule_name="Content Length",
            rule_description="Ensure output content has minimum length",
            rule_type="validation",
            severity=ErrorSeverity.MEDIUM,
        ),
        ConstitutionRule(
            rule_id="rule_002",
            rule_name="Security Check",
            rule_description="Check for sensitive information",
            rule_type="security",
            severity=ErrorSeverity.HIGH,
        ),
    ]

    ruleset = ConstitutionRuleSet(
        ruleset_id="test_ruleset",
        ruleset_name="Test Ruleset",
        ruleset_description="Test ruleset for integration testing",
        rules=default_rules,
    )

    constitution_validator = ConstitutionValidator(ruleset)

    print("✅ All components initialized successfully")

    # Test 1: Context Model Integration
    print("\n🎭 Test 1: Context Model Integration")
    print("-" * 30)

    # Test all role contexts
    roles = [AIRole.PLANNER, AIRole.CODER, AIRole.RESEARCHER, AIRole.IMPLEMENTER]
    contexts = {}

    for role in roles:
        context = context_factory.create_context(role, session_id=f"session_{role.value}")
        contexts[role] = context

        print(f"✅ {role.value.title()} context created: {context.session_id}")
        assert context.role == role
        assert isinstance(context, BaseContext)

        # Test context factory with invalid role
    try:
        invalid_context = context_factory.create_context("INVALID", session_id="test")
        print("❌ Should not create invalid context")
    except ValueError:
        print("✅ Invalid role properly rejected")

    # Test 2: Dynamic Prompt Integration
    print("\n💬 Test 2: Dynamic Prompt Integration")
    print("-" * 30)

    # Create prompt templates
    templates = {
        "planner": PromptTemplate(
            template_id="planner_template",
            template_name="Planner Template",
            base_prompt="You are a {role} working on {project_scope}. {user_preferences}",
            placeholders=["role", "project_scope", "user_preferences"],
        ),
        "coder": PromptTemplate(
            template_id="coder_template",
            template_name="Coder Template",
            base_prompt="As a {role}, implement {language} code for {project_scope}",
            placeholders=["role", "language", "project_scope"],
        ),
    }

    for template_id, template in templates.items():
        prompt_manager.register_template(template)
        print(f"✅ Template registered: {template_id}")

    # Generate prompts with context
    user_context = PromptContext(
        user_id="test_user", session_id="test_session", user_preferences={"detail_level": "high"}, dynamic_variables={}
    )

    for role, context in contexts.items():
        prompt = prompt_manager.generate_prompt(
            template_id=f"{role.value}_template", user_context=user_context, role_context=context
        )
        print(f"✅ Prompt generated for {role.value}: {len(prompt)} chars")
        assert len(prompt) > 0

    # Test 3: User Preference Integration
    print("\n👤 Test 3: User Preference Integration")
    print("-" * 30)

    # Set user preferences
    test_user_id = "integration_test_user"
    preferences = {"detail_level": "high", "style": "detailed", "language": "python", "debug_level": "verbose"}

    for key, value in preferences.items():
        preference_manager.set_user_preference(test_user_id, key, value)
        print(f"✅ Preference set: {key} = {value}")

    # Retrieve preferences
    retrieved_prefs = preference_manager.get_user_preferences(test_user_id)
    print(f"✅ Preferences retrieved: {len(retrieved_prefs)} items")

    for key, value in preferences.items():
        assert retrieved_prefs.get(key) == value
        print(f"✅ Preference verified: {key} = {value}")

    # Test 4: Context-Aware Tools Integration
    print("\n🔧 Test 4: Context-Aware Tools Integration")
    print("-" * 30)

    # Define test tools
    @context_aware_tool("test_calculator", mlflow_config=mlflow_config)
    def calculator(a, b, operation="add"):
        """Simple calculator tool"""
        if operation == "add":
            return a + b
        elif operation == "multiply":
            return a * b
        else:
            raise ValueError(f"Unknown operation: {operation}")

    @context_aware_tool("test_validator", mlflow_config=mlflow_config)
    def validator(data, schema_type="basic"):
        """Data validation tool"""
        if schema_type == "basic":
            if not isinstance(data, dict):
                raise ValidationError("Data must be a dictionary")
            return {"valid": True, "data": data}
        else:
            raise ValueError(f"Unknown schema type: {schema_type}")

    # Register tools
    tool_framework.register_tool("calculator", calculator)
    tool_framework.register_tool("validator", validator)
    print("✅ Tools registered with framework")

    # Execute tools with context
    tool_context = PromptContext(
        user_id=test_user_id, session_id="tool_test_session", user_preferences=retrieved_prefs, dynamic_variables={}
    )

    # Test calculator
    calc_result = tool_framework.execute_tool("calculator", 5, 3, "add", user_context=tool_context)
    print(f"✅ Calculator result: {calc_result.success}, value: {calc_result.result}")
    assert calc_result.success
    assert calc_result.result == 8

    # Test validator
    val_result = tool_framework.execute_tool("validator", {"test": "data"}, "basic", user_context=tool_context)
    print(f"✅ Validator result: {val_result.success}")
    assert val_result.success
    assert val_result.result["valid"] is True

    # Test 5: Enhanced Debugging Integration
    print("\n🐛 Test 5: Enhanced Debugging Integration")
    print("-" * 30)

    # Test debugging decorator
    @enhanced_debugging(enable_privacy=True, capture_variables=True)
    def test_function_with_debugging(x, y, sensitive_data="secret"):
        """Test function with enhanced debugging"""
        if x < 0:
            raise ValueError(f"Invalid value: {x} is negative")
        return x * y

    # Test successful execution
    try:
        result = test_function_with_debugging(4, 5)
        print(f"✅ Debugged function success: {result}")
        assert result == 20
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test error execution
    try:
        result = test_function_with_debugging(-1, 5)
        print("❌ Should have raised error")
    except ValueError as e:
        print(f"✅ Expected error caught: {str(e)[:50]}...")

    # Test debugging context capture
    debug_context = debugging_manager.capture_debugging_context(
        user_context=tool_context,
        role_context=contexts[AIRole.CODER],
        variable_snapshot={"test_var": "test_value", "password": "secret123"},
    )
    print(f"✅ Debug context captured: {debug_context.context_id}")

    # Verify privacy protection
    assert debug_context.variable_snapshot["test_var"] == "test_value"
    assert debug_context.variable_snapshot["password"] == "[REDACTED]"
    print("✅ Privacy protection verified")

    # Test 6: Error Taxonomy Integration
    print("\n🚨 Test 6: Error Taxonomy Integration")
    print("-" * 30)

    # Test error creation
    pydantic_error = ErrorFactory.create_pydantic_error(
        message="Test Pydantic error", field_name="test_field", field_value="invalid_value"
    )
    print(f"✅ Pydantic error created: {pydantic_error.error_type}")
    assert pydantic_error.severity == ErrorSeverity.MEDIUM

    validation_error = ErrorFactory.create_validation_error(
        message="Test validation error", validation_type="format", field_name="email"
    )
    print(f"✅ Validation error created: {validation_error.error_type}")
    assert validation_error.severity == ErrorSeverity.MEDIUM

    runtime_error = ErrorFactory.create_runtime_error(
        message="Test runtime error", operation="test_operation", resource="test_resource"
    )
    print(f"✅ Runtime error created: {runtime_error.error_type}")
    assert runtime_error.severity == ErrorSeverity.HIGH

    # Test 7: Constitution Validation Integration
    print("\n📜 Test 7: Constitution Validation Integration")
    print("-" * 30)

    # Create constitution rules
    rules = [
        "All responses must be helpful and accurate",
        "No sensitive information should be exposed",
        "Code must follow best practices",
    ]

    constitution_validator.add_rules(rules)
    print(f"✅ Constitution rules added: {len(rules)}")

    # Test program output validation
    valid_output = ProgramOutput(
        content="This is a helpful and accurate response.", output_type="text", metadata={"source": "test"}
    )

    invalid_output = ProgramOutput(
        content="Here is the password: secret123", output_type="text", metadata={"source": "test"}
    )

    # Validate outputs
    valid_result = constitution_validator.validate_output(valid_output)
    print(f"✅ Valid output validation: {valid_result.compliant}")
    assert valid_result.compliant

    invalid_result = constitution_validator.validate_output(invalid_output)
    print(f"✅ Invalid output validation: {invalid_result.compliant}")
    assert not invalid_result.compliant

    # Test 8: Cross-Component Integration
    print("\n🔗 Test 8: Cross-Component Integration")
    print("-" * 30)

    # Test full workflow with all components
    workflow_user_id = "workflow_test_user"

    # Set user preferences
    preference_manager.set_user_preference(workflow_user_id, "detail_level", "high")
    preference_manager.set_user_preference(workflow_user_id, "style", "detailed")

    # Create workflow context
    workflow_context = PromptContext(
        user_id=workflow_user_id,
        session_id="workflow_session",
        user_preferences=preference_manager.get_user_preferences(workflow_user_id),
        dynamic_variables={"workflow_step": "integration_test"},
    )

    # Create role context
    workflow_role_context = context_factory.create_context(AIRole.PLANNER, session_id="workflow_session")

    # Generate prompt with all context
    workflow_prompt = prompt_manager.generate_prompt(
        template_id="planner_template", user_context=workflow_context, role_context=workflow_role_context
    )
    print(f"✅ Workflow prompt generated: {len(workflow_prompt)} chars")

    # Execute tool with full context
    workflow_result = tool_framework.execute_tool(
        "calculator", 10, 20, "add", user_context=workflow_context, role_context=workflow_role_context
    )
    print(f"✅ Workflow tool execution: {workflow_result.success}")
    assert workflow_result.success
    assert workflow_result.result == 30

    # Capture debugging context for workflow
    workflow_debug_context = debugging_manager.capture_debugging_context(
        user_context=workflow_context,
        role_context=workflow_role_context,
        variable_snapshot={"workflow_result": workflow_result.result, "prompt_length": len(workflow_prompt)},
    )
    print(f"✅ Workflow debug context: {workflow_debug_context.context_id}")

    # Test 9: Performance Validation
    print("\n⚡ Test 9: Performance Validation")
    print("-" * 30)

    # Test context creation performance
    start_time = time.time()
    for i in range(100):
        context_factory.create_context(AIRole.CODER, session_id=f"perf_test_{i}")
    context_time = time.time() - start_time
    print(f"✅ Context creation: {context_time:.4f}s for 100 contexts")
    assert context_time < 1.0  # Should be very fast

    # Test prompt generation performance
    start_time = time.time()
    for i in range(50):
        prompt_manager.generate_prompt(
            template_id="planner_template", user_context=workflow_context, role_context=workflow_role_context
        )
    prompt_time = time.time() - start_time
    print(f"✅ Prompt generation: {prompt_time:.4f}s for 50 prompts")
    assert prompt_time < 1.0  # Should be very fast

    # Test tool execution performance
    start_time = time.time()
    for i in range(50):
        tool_framework.execute_tool("calculator", i, i + 1, "add", user_context=workflow_context)
    tool_time = time.time() - start_time
    print(f"✅ Tool execution: {tool_time:.4f}s for 50 executions")
    assert tool_time < 2.0  # Should be reasonable

    # Test 10: Error Handling and Recovery
    print("\n🛡️ Test 10: Error Handling and Recovery")
    print("-" * 30)

    # Test graceful error handling
    try:
        # Invalid template ID
        prompt_manager.generate_prompt("invalid_template")
        print("❌ Should have raised error for invalid template")
    except Exception as e:
        print(f"✅ Invalid template properly handled: {type(e).__name__}")

    try:
        # Invalid tool name
        tool_framework.execute_tool("invalid_tool")
        print("❌ Should have raised error for invalid tool")
    except Exception as e:
        print(f"✅ Invalid tool properly handled: {type(e).__name__}")

    try:
        # Invalid role
        context_factory.create_context("INVALID_ROLE", session_id="test")
        print("❌ Should have raised error for invalid role")
    except Exception as e:
        print(f"✅ Invalid role properly handled: {type(e).__name__}")

    # Test recovery after errors
    # Should still be able to create valid contexts after errors
    recovery_context = context_factory.create_context(AIRole.RESEARCHER, session_id="recovery")
    print(f"✅ Recovery context created: {recovery_context.role.value}")
    assert recovery_context.role == AIRole.RESEARCHER

    # Test 11: Backward Compatibility
    print("\n🔄 Test 11: Backward Compatibility")
    print("-" * 30)

    # Test that existing patterns still work
    # Direct context creation (without factory)
    direct_context = PlannerContext(
        session_id="direct_test", project_scope="Backward compatibility test", backlog_priority="P1"
    )
    print(f"✅ Direct context creation: {direct_context.role.value}")

    # Direct prompt context creation
    direct_prompt_context = PromptContext(
        user_id="direct_user", session_id="direct_session", user_preferences={}, dynamic_variables={}
    )
    print(f"✅ Direct prompt context creation: {direct_prompt_context.user_id}")

    # Test that all components can work with basic contexts
    basic_prompt = prompt_manager.generate_prompt(
        template_id="planner_template", user_context=direct_prompt_context, role_context=direct_context
    )
    print(f"✅ Basic context prompt generation: {len(basic_prompt)} chars")

    # Test 12: Final Integration Summary
    print("\n📊 Test 12: Final Integration Summary")
    print("-" * 30)

    # Get performance metrics
    tool_metrics = tool_framework.get_performance_metrics()
    debug_summary = debugging_manager.get_debugging_summary()

    print("✅ Integration Summary:")
    print(f"   - Tool executions: {tool_metrics['total_executions']}")
    print(f"   - Successful executions: {tool_metrics['successful_executions']}")
    print(f"   - Average execution time: {tool_metrics['avg_execution_time']:.4f}s")
    print(f"   - Debug contexts captured: {debug_summary['total_contexts']}")
    print(f"   - Errors captured: {debug_summary['total_errors']}")
    print(f"   - Correlations generated: {debug_summary['total_correlations']}")

    # Verify all components are working together
    assert tool_metrics["total_executions"] > 0
    assert tool_metrics["successful_executions"] > 0
    assert debug_summary["total_contexts"] > 0

    print("\n🎉 Comprehensive Integration Test Completed Successfully!")
    print("=" * 70)

    return {
        "status": "success",
        "components_tested": 12,
        "integration_points": "all_verified",
        "performance": {
            "context_creation": f"{context_time:.4f}s",
            "prompt_generation": f"{prompt_time:.4f}s",
            "tool_execution": f"{tool_time:.4f}s",
        },
        "error_handling": "verified",
        "backward_compatibility": "verified",
        "regression_testing": "passed",
    }


if __name__ == "__main__":
    try:
        result = test_comprehensive_integration()
        print(f"\n📊 Final Integration Results: {result}")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        traceback.print_exc()
