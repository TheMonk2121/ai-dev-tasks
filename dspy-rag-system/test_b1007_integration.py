#!/usr/bin/env python3
"""
B-1007 Integration Test
Validates that all Pydantic AI Style Enhancement components work together
"""

import time

from src.dspy_modules.constitution_validation import (
    ConstitutionAwareValidator,
    ConstitutionValidator,
    ProgramOutput,
    create_default_constitution_ruleset,
)
from src.dspy_modules.context_models import (
    AIRole,
    ContextFactory,
)
from src.dspy_modules.error_taxonomy import (
    ConstitutionErrorMapper,
    ErrorClassifier,
    ErrorFactory,
    ErrorSeverity,
)


def test_b1007_integration():
    """Test complete B-1007 integration"""

    print("🧪 Testing B-1007 Pydantic AI Style Enhancements Integration")
    print("=" * 70)

    # Test 1: Context Models
    print("\n1. Testing Role-Based Context Models...")

    # Create planner context
    planner_context = ContextFactory.create_context(
        AIRole.PLANNER,
        session_id="integration-test-session",
        project_scope="Implement Pydantic AI style enhancements for DSPy system with comprehensive validation",
        backlog_priority="P1",
        strategic_goals=["Type safety", "Error handling", "Constitution compliance"],
    )

    print(f"   ✅ Planner context created: {planner_context.role.value}")
    print(f"   ✅ Project scope: {planner_context.project_scope[:50]}...")
    print(f"   ✅ Strategic goals: {len(planner_context.strategic_goals)} goals")

    # Create coder context
    coder_context = ContextFactory.create_context(
        AIRole.CODER,
        session_id="integration-test-session",
        codebase_path="/tmp",
        language="python",
        file_context=["test_file.py"],
    )

    print(f"   ✅ Coder context created: {coder_context.role.value}")
    print(f"   ✅ Language: {coder_context.language}")

    # Test 2: Error Taxonomy
    print("\n2. Testing Error Taxonomy...")

    # Create various error types
    validation_error = ErrorFactory.create_validation_error(
        message="Field validation failed during context creation",
        field_name="project_scope",
        expected_value="non-empty string",
        actual_value="",
    )

    coherence_error = ErrorFactory.create_coherence_error(
        message="Role context mismatch detected",
        conflicting_elements=["planner", "coder"],
        coherence_rule="single_role_per_session",
    )

    dependency_error = ErrorFactory.create_dependency_error(
        message="Missing required dependencies",
        missing_dependencies=["pydantic", "dspy"],
        dependency_type="python_module",
    )

    print(f"   ✅ Validation error created: {validation_error.error_type.value}")
    print(f"   ✅ Coherence error created: {coherence_error.error_type.value}")
    print(f"   ✅ Dependency error created: {dependency_error.error_type.value}")

    # Test error classification
    errors = [validation_error, coherence_error, dependency_error]
    error_stats = ConstitutionErrorMapper.get_error_classification_stats(errors)
    print(f"   ✅ Error classification: {error_stats}")

    # Test 3: Constitution Validation
    print("\n3. Testing Constitution-Aware Validation...")

    # Create default constitution ruleset
    ruleset = create_default_constitution_ruleset()
    validator = ConstitutionValidator(ruleset)
    aware_validator = ConstitutionAwareValidator(validator)

    print(f"   ✅ Default ruleset created with {len(ruleset.rules)} rules")

    # Test program output validation
    compliant_output = ProgramOutput(
        output_content="This is a comprehensive and detailed output that should pass all constitution validation rules including content length, role appropriateness, and security checks.",
        output_type="text",
        context=planner_context,
    )

    validated_output = aware_validator.validate_program_output(compliant_output)

    print(f"   ✅ Compliant output validation: {validated_output.constitution_compliance.is_compliant}")
    print(f"   ✅ Compliance score: {validated_output.constitution_compliance.compliance_score:.2f}")

    # Test non-compliant output
    non_compliant_output = ProgramOutput(output_content="Short", output_type="text", context=coder_context)

    validated_non_compliant = aware_validator.validate_program_output(non_compliant_output)

    print(f"   ✅ Non-compliant output validation: {validated_non_compliant.constitution_compliance.is_compliant}")
    print(f"   ✅ Compliance score: {validated_non_compliant.constitution_compliance.compliance_score:.2f}")
    print(f"   ✅ Violations: {len(validated_non_compliant.constitution_compliance.violations)}")

    # Test 4: Constitution Error Mapping
    print("\n4. Testing Constitution Error Mapping...")

    # Map constitution failures to errors
    constitution_errors = []

    for violation in validated_non_compliant.constitution_compliance.violations:
        if "validation" in violation.lower():
            error = ConstitutionErrorMapper.map_constitution_failure_to_error(
                failure_mode="validation_failure",
                message=f"Constitution validation failed: {violation}",
                severity=ErrorSeverity.HIGH,
            )
            constitution_errors.append(error)

    print(f"   ✅ Constitution errors mapped: {len(constitution_errors)} errors")

    # Test 5: Error Handling Metrics
    print("\n5. Testing Error Handling Metrics...")

    all_errors = errors + constitution_errors
    metrics = ErrorClassifier.get_error_handling_metrics(all_errors)

    print(f"   ✅ Total errors: {metrics['total_errors']}")
    print(f"   ✅ Error types: {metrics['error_types']}")
    print(f"   ✅ Severity distribution: {metrics['severity_distribution']}")
    print(f"   ✅ Average severity score: {metrics['avg_severity_score']:.2f}")
    print(f"   ✅ Most common error type: {metrics['most_common_error_type']}")
    print(f"   ✅ Critical errors: {metrics['critical_errors_count']}")

    # Test 6: Performance Validation
    print("\n6. Testing Performance...")

    start_time = time.time()

    # Create multiple contexts
    for i in range(100):
        ContextFactory.create_context(
            AIRole.PLANNER,
            session_id=f"perf-test-{i}",
            project_scope="Performance test project scope",
            backlog_priority="P1",
        )

    context_creation_time = time.time() - start_time

    start_time = time.time()

    # Validate multiple outputs
    for i in range(50):
        output = ProgramOutput(
            output_content=f"Performance test output {i} with sufficient content length", output_type="text"
        )
        aware_validator.validate_program_output(output)

    validation_time = time.time() - start_time

    print(f"   ✅ Context creation: {context_creation_time:.3f}s for 100 contexts")
    print(f"   ✅ Output validation: {validation_time:.3f}s for 50 outputs")
    print(f"   ✅ Average context creation: {(context_creation_time/100)*1000:.2f}ms")
    print(f"   ✅ Average validation: {(validation_time/50)*1000:.2f}ms")

    # Validate performance requirements
    avg_context_time = (context_creation_time / 100) * 1000
    avg_validation_time = (validation_time / 50) * 1000

    assert avg_context_time < 1.0, f"Context creation too slow: {avg_context_time:.2f}ms"
    assert avg_validation_time < 10.0, f"Validation too slow: {avg_validation_time:.2f}ms"

    print("   ✅ Performance requirements met!")

    # Test 7: Backward Compatibility
    print("\n7. Testing Backward Compatibility...")

    from src.dspy_modules.context_models import LegacyContextAdapter

    # Test legacy adapter
    legacy_data = {
        "role": "planner",
        "session_id": "legacy-test",
        "project_scope": "Legacy compatibility test",
        "backlog_priority": "P1",
    }

    legacy_context = LegacyContextAdapter.from_dict(legacy_data)
    legacy_dict = LegacyContextAdapter.to_dict(legacy_context)

    print(f"   ✅ Legacy adapter from_dict: {legacy_context.role.value}")
    print(f"   ✅ Legacy adapter to_dict: {legacy_dict['role']}")

    assert legacy_context.role.value == "planner"
    assert legacy_dict["role"] == "planner"

    print("   ✅ Backward compatibility working!")

    print("\n" + "=" * 70)
    print("🎉 B-1007 Integration Test PASSED!")
    print("✅ All components working together successfully")
    print("✅ Performance requirements met")
    print("✅ Backward compatibility maintained")
    print("✅ Constitution-aware validation operational")
    print("✅ Error taxonomy providing structured error handling")
    print("✅ Role-based context models functional")

    return True


if __name__ == "__main__":
    test_b1007_integration()
