#!/usr/bin/env python3
"""
Integration test for Enhanced Debugging Capabilities
Demonstrates the complete enhanced debugging workflow for B-1007
"""

import time
import traceback
from datetime import datetime

from src.dspy_modules.context_models import PlannerContext
from src.dspy_modules.dynamic_prompts import PromptContext
from src.dspy_modules.enhanced_debugging import (
    EnhancedDebuggingManager,
    analyze_error_patterns,
    correlate_errors,
    enhanced_debugging,
)
from src.dspy_modules.user_preferences import UserPreferenceManager


def test_enhanced_debugging_integration():
    """Test complete enhanced debugging integration"""
    print("🔍 Testing Enhanced Debugging Integration")
    print("=" * 50)

    # Initialize components
    debugging_manager = EnhancedDebuggingManager(enable_privacy=True, max_context_history=50)
    preference_manager = UserPreferenceManager()

    print("✅ Components initialized")

    # Test 1: Context Capture and Privacy
    print("\n📸 Test 1: Context Capture and Privacy")
    print("-" * 30)

    # Create user and role contexts
    user_context = PromptContext(
        user_id="test_user_123",
        session_id="session_456",
        user_preferences={"detail_level": "high", "style": "detailed"},
        dynamic_variables={"current_task": "debugging_test"},
    )

    role_context = PlannerContext(
        session_id="session_456", project_scope="Enhanced Debugging System", backlog_priority="P1"
    )

    # Capture debugging context with sensitive data
    variables = {
        "normal_var": "normal_value",
        "sensitive_password": "secret123",
        "api_key": "sk-1234567890abcdef",
        "user_data": {"name": "John Doe", "email": "john@example.com"},
    }

    debugging_context = debugging_manager.capture_debugging_context(
        user_context=user_context,
        role_context=role_context,
        variable_snapshot=variables,
        correlation_id="corr_test_001",
    )

    print(f"✅ Context captured: {debugging_context.context_id}")
    print(f"   - User ID: {debugging_context.user_context.user_id}")
    print(f"   - Role: {debugging_context.role_context.role.value}")
    print(f"   - Variables: {len(debugging_context.variable_snapshot)} items")

    # Verify privacy protection
    assert debugging_context.variable_snapshot["normal_var"] == "normal_value"
    assert debugging_context.variable_snapshot["sensitive_password"] == "[REDACTED]"
    assert debugging_context.variable_snapshot["api_key"] == "[REDACTED]"
    print("✅ Privacy protection verified")

    # Test 2: Rich Error Message Creation
    print("\n🚨 Test 2: Rich Error Message Creation")
    print("-" * 30)

    # Create different types of errors
    errors = [
        ValueError("Data validation failed: invalid format"),
        ConnectionError("Database connection timeout after 30 seconds"),
        Exception("Security violation: unauthorized access attempt"),
        TimeoutError("Operation timed out: processing took too long"),
    ]

    rich_errors = []
    for error in errors:
        rich_error = debugging_manager.create_rich_error_message(error=error, debugging_context=debugging_context)
        rich_errors.append(rich_error)

        print(f"✅ Error captured: {rich_error.error_id}")
        print(f"   - Type: {rich_error.error_type}")
        print(f"   - Severity: {rich_error.severity.value}")
        print(f"   - User-friendly: {rich_error.user_friendly_message[:60]}...")
        print(f"   - Actions: {len(rich_error.suggested_actions)} suggested")

    # Test 3: Context Correlation
    print("\n🔗 Test 3: Context Correlation")
    print("-" * 30)

    # Create multiple contexts for correlation
    contexts = []
    for i in range(5):
        context = debugging_manager.capture_debugging_context(
            user_context=user_context, correlation_id=f"corr_test_{i:03d}"
        )
        contexts.append(context)
        time.sleep(0.1)  # Small delay for temporal correlation

    # Correlate contexts
    correlation = debugging_manager.correlate_contexts(contexts[0])

    print(f"✅ Correlation created: {correlation.correlation_id}")
    print(f"   - Primary context: {correlation.primary_context.context_id}")
    print(f"   - Related contexts: {len(correlation.related_contexts)}")
    print(f"   - Patterns: {correlation.correlation_patterns}")
    print(f"   - Confidence: {correlation.confidence_score:.2f}")

    # Test 4: Structured Logging
    print("\n📝 Test 4: Structured Logging")
    print("-" * 30)

    # Create structured log entries
    log_entries = []
    for i in range(3):
        log_entry = debugging_manager.log_structured_entry(
            level=["INFO", "WARNING", "ERROR"][i],
            message=f"Test log message {i+1}",
            context_data={
                "operation": f"test_op_{i+1}",
                "status": ["success", "warning", "failed"][i],
                "timestamp": datetime.now().isoformat(),
            },
            source="integration_test",
            correlation_id=f"corr_test_{i:03d}",
        )
        log_entries.append(log_entry)

        print(f"✅ Log entry created: {log_entry.log_id}")
        print(f"   - Level: {log_entry.level}")
        print(f"   - Message: {log_entry.message}")
        print(f"   - Context data: {len(log_entry.context_data)} items")

    # Test 5: Enhanced Debugging Decorator
    print("\n🎯 Test 5: Enhanced Debugging Decorator")
    print("-" * 30)

    @enhanced_debugging(enable_privacy=True, capture_variables=True)
    def test_function_with_error(x, y, password="secret"):
        """Test function that raises an error"""
        if x < 0:
            raise ValueError(f"Invalid value: {x} is negative")
        return x + y

    @enhanced_debugging(enable_privacy=True, capture_variables=True)
    def test_function_success(a, b, api_key="sk-test"):
        """Test function that succeeds"""
        return a * b

    # Test successful execution
    try:
        result = test_function_success(5, 3)
        print(f"✅ Successful execution: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    # Test error execution
    try:
        result = test_function_with_error(-1, 5)
        print(f"✅ Unexpected success: {result}")
    except ValueError as e:
        print(f"✅ Expected error caught: {str(e)[:60]}...")

    # Test 6: Error Pattern Analysis
    print("\n📊 Test 6: Error Pattern Analysis")
    print("-" * 30)

    # Analyze error patterns
    analysis = analyze_error_patterns(rich_errors)

    print("✅ Analysis completed:")
    print(f"   - Total errors: {analysis['total_errors']}")
    print(f"   - Error types: {list(analysis['error_types'].keys())}")
    print(f"   - Severity distribution: {analysis['severity_distribution']}")

    if "temporal_patterns" in analysis:
        patterns = analysis["temporal_patterns"]
        print(f"   - Temporal patterns: {patterns}")

    # Test 7: Error Correlation
    print("\n🔍 Test 7: Error Correlation")
    print("-" * 30)

    # Correlate errors
    error_correlations = correlate_errors(rich_errors)

    print(f"✅ Error correlations: {len(error_correlations)}")
    for i, correlation in enumerate(error_correlations):
        print(f"   - Correlation {i+1}: {correlation.correlation_id}")
        print(f"     Confidence: {correlation.confidence_score:.2f}")
        print(f"     Patterns: {correlation.correlation_patterns}")

    # Test 8: Debugging Summary
    print("\n📋 Test 8: Debugging Summary")
    print("-" * 30)

    summary = debugging_manager.get_debugging_summary()

    print("✅ Summary generated:")
    print(f"   - Total contexts: {summary['total_contexts']}")
    print(f"   - Total errors: {summary['total_errors']}")
    print(f"   - Total correlations: {summary['total_correlations']}")
    print(f"   - Average execution time: {summary.get('avg_execution_time', 'N/A')}")

    if "error_distribution" in summary:
        print(f"   - Error distribution: {summary['error_distribution']}")

    if "correlation_insights" in summary:
        insights = summary["correlation_insights"]
        print(f"   - Correlation insights: {insights}")

    # Test 9: Performance and Privacy
    print("\n⚡ Test 9: Performance and Privacy")
    print("-" * 30)

    # Test privacy with different settings
    privacy_manager = EnhancedDebuggingManager(enable_privacy=False)

    sensitive_data = {"password": "secret123", "credit_card": "1234-5678-9012-3456", "ssn": "123-45-6789"}

    context_no_privacy = privacy_manager.capture_debugging_context(variable_snapshot=sensitive_data)

    # Verify no privacy protection
    assert context_no_privacy.variable_snapshot["password"] == "secret123"
    assert context_no_privacy.variable_snapshot["credit_card"] == "1234-5678-9012-3456"
    print("✅ Privacy disabled correctly")

    # Test performance
    start_time = time.time()
    for i in range(10):
        debugging_manager.capture_debugging_context()
    end_time = time.time()

    avg_time = (end_time - start_time) / 10
    print(f"✅ Performance test: {avg_time:.4f}s average per context capture")

    # Test 10: Integration with User Preferences
    print("\n👤 Test 10: Integration with User Preferences")
    print("-" * 30)

    # Set user preferences
    preference_manager.set_user_preference(
        user_id="test_user_123", preference_key="debug_detail_level", preference_value="high"
    )

    preference_manager.set_user_preference(
        user_id="test_user_123", preference_key="error_notification", preference_value="immediate"
    )

    # Create error with user preferences
    user_pref_context = PromptContext(
        user_id="test_user_123",
        session_id="session_789",
        user_preferences=preference_manager.get_user_preferences("test_user_123"),
        dynamic_variables={},
    )

    error_with_prefs = debugging_manager.create_rich_error_message(
        error=ValueError("User preference test error"), user_context=user_pref_context
    )

    print(f"✅ Error with preferences: {error_with_prefs.error_id}")
    print(f"   - User preferences applied: {len(user_pref_context.user_preferences)}")
    print(f"   - Debug detail level: {user_pref_context.user_preferences.get('debug_detail_level')}")

    print("\n🎉 Enhanced Debugging Integration Test Completed Successfully!")
    print("=" * 60)

    return {
        "status": "success",
        "contexts_captured": len(debugging_manager.context_history),
        "errors_created": len(debugging_manager.error_history),
        "correlations_generated": len(debugging_manager.correlation_cache),
        "privacy_protection": "verified",
        "performance": f"{avg_time:.4f}s average",
        "integration": "complete",
    }


if __name__ == "__main__":
    try:
        result = test_enhanced_debugging_integration()
        print(f"\n📊 Final Results: {result}")
    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        traceback.print_exc()
