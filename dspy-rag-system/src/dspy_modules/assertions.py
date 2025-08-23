#!/usr/bin/env python3
"""
Assertion-Based Validation Framework for DSPy

Implements assertion-based validation targeting 37% → 98% reliability improvement
as mentioned in the Adam LK transcript. Provides comprehensive code validation
and reliability checks with minimal performance overhead.
"""

import ast
import inspect
import logging
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from dspy import Module

_LOG = logging.getLogger("dspy_assertions")


class AssertionType(Enum):
    """Types of assertions supported by the framework"""

    # Code Quality Assertions
    TYPE_HINTS = "type_hints"
    DOCSTRINGS = "docstrings"
    NAMING_CONVENTIONS = "naming_conventions"
    CODE_COMPLEXITY = "code_complexity"

    # Logic Assertions
    INPUT_VALIDATION = "input_validation"
    OUTPUT_VALIDATION = "output_validation"
    ERROR_HANDLING = "error_handling"
    BOUNDARY_CHECKS = "boundary_checks"

    # Performance Assertions
    MEMORY_USAGE = "memory_usage"
    EXECUTION_TIME = "execution_time"
    RESOURCE_LEAKS = "resource_leaks"

    # Security Assertions
    INPUT_SANITIZATION = "input_sanitization"
    ACCESS_CONTROL = "access_control"
    DATA_VALIDATION = "data_validation"


class AssertionSeverity(Enum):
    """Severity levels for assertions"""

    CRITICAL = "critical"  # Must pass for deployment
    HIGH = "high"  # Should pass for production
    MEDIUM = "medium"  # Recommended for quality
    LOW = "low"  # Optional improvements


@dataclass
class AssertionResult:
    """Result of an assertion validation"""

    assertion_type: AssertionType
    severity: AssertionSeverity
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class ValidationReport:
    """Comprehensive validation report"""

    module_name: str
    total_assertions: int
    passed_assertions: int
    failed_assertions: int
    critical_failures: int
    reliability_score: float
    execution_time: float
    results: List[AssertionResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage"""
        if self.total_assertions == 0:
            return 0.0
        return (self.passed_assertions / self.total_assertions) * 100

    @property
    def is_critical_safe(self) -> bool:
        """Check if all critical assertions passed"""
        return self.critical_failures == 0


class CodeQualityValidator:
    """Validates code quality aspects"""

    def __init__(self):
        self.naming_patterns = {
            "function": re.compile(r"^[a-z_][a-z0-9_]*$"),
            "class": re.compile(r"^[A-Z][a-zA-Z0-9]*$"),
            "constant": re.compile(r"^[A-Z][A-Z0-9_]*$"),
            "variable": re.compile(r"^[a-z_][a-z0-9_]*$"),
        }

    def validate_type_hints(self, source_code: str) -> AssertionResult:
        """Validate presence and quality of type hints"""
        start_time = time.time()

        try:
            tree = ast.parse(source_code)
            issues = []
            functions_without_hints = 0
            total_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    if not node.returns and not any(
                        isinstance(arg, ast.arg) and arg.annotation for arg in node.args.args
                    ):
                        functions_without_hints += 1
                        issues.append(f"Function '{node.name}' missing type hints")

            passed = functions_without_hints == 0
            message = f"Type hints validation: {total_functions - functions_without_hints}/{total_functions} functions have type hints"

            return AssertionResult(
                assertion_type=AssertionType.TYPE_HINTS,
                severity=AssertionSeverity.HIGH,
                passed=passed,
                message=message,
                details={
                    "total_functions": total_functions,
                    "functions_with_hints": total_functions - functions_without_hints,
                    "functions_without_hints": functions_without_hints,
                    "issues": issues,
                },
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.TYPE_HINTS,
                severity=AssertionSeverity.HIGH,
                passed=False,
                message=f"Type hints validation failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )

    def validate_docstrings(self, source_code: str) -> AssertionResult:
        """Validate presence and quality of docstrings"""
        start_time = time.time()

        try:
            tree = ast.parse(source_code)
            issues = []
            functions_without_docs = 0
            total_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    if not ast.get_docstring(node):
                        functions_without_docs += 1
                        issues.append(f"Function '{node.name}' missing docstring")

            passed = functions_without_docs == 0
            message = f"Docstring validation: {total_functions - functions_without_docs}/{total_functions} functions have docstrings"

            return AssertionResult(
                assertion_type=AssertionType.DOCSTRINGS,
                severity=AssertionSeverity.MEDIUM,
                passed=passed,
                message=message,
                details={
                    "total_functions": total_functions,
                    "functions_with_docs": total_functions - functions_without_docs,
                    "functions_without_docs": functions_without_docs,
                    "issues": issues,
                },
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.DOCSTRINGS,
                severity=AssertionSeverity.MEDIUM,
                passed=False,
                message=f"Docstring validation failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )

    def validate_naming_conventions(self, source_code: str) -> AssertionResult:
        """Validate naming conventions"""
        start_time = time.time()

        try:
            tree = ast.parse(source_code)
            issues = []
            violations = 0
            total_identifiers = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_identifiers += 1
                    if not self.naming_patterns["function"].match(node.name):
                        violations += 1
                        issues.append(f"Function '{node.name}' violates naming convention")

                elif isinstance(node, ast.ClassDef):
                    total_identifiers += 1
                    if not self.naming_patterns["class"].match(node.name):
                        violations += 1
                        issues.append(f"Class '{node.name}' violates naming convention")

                elif isinstance(node, ast.Name):
                    if isinstance(node.ctx, ast.Store):
                        total_identifiers += 1
                        if not self.naming_patterns["variable"].match(node.id):
                            violations += 1
                            issues.append(f"Variable '{node.id}' violates naming convention")

            passed = violations == 0
            message = f"Naming convention validation: {total_identifiers - violations}/{total_identifiers} identifiers follow conventions"

            return AssertionResult(
                assertion_type=AssertionType.NAMING_CONVENTIONS,
                severity=AssertionSeverity.MEDIUM,
                passed=passed,
                message=message,
                details={
                    "total_identifiers": total_identifiers,
                    "compliant_identifiers": total_identifiers - violations,
                    "violations": violations,
                    "issues": issues,
                },
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.NAMING_CONVENTIONS,
                severity=AssertionSeverity.MEDIUM,
                passed=False,
                message=f"Naming convention validation failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )


class LogicValidator:
    """Validates logic and behavior aspects"""

    def validate_input_validation(self, module: Module) -> AssertionResult:
        """Validate presence of input validation"""
        start_time = time.time()

        try:
            source_code = inspect.getsource(module.__class__)
            tree = ast.parse(source_code)

            # Look for common validation patterns
            validation_patterns = ["isinstance", "type", "assert", "if", "raise", "try"]

            validation_count = 0
            total_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    function_source = ast.unparse(node)

                    # Check for validation patterns
                    for pattern in validation_patterns:
                        if pattern in function_source:
                            validation_count += 1
                            break

            passed = validation_count > 0
            message = f"Input validation: {validation_count}/{total_functions} functions have validation logic"

            return AssertionResult(
                assertion_type=AssertionType.INPUT_VALIDATION,
                severity=AssertionSeverity.CRITICAL,
                passed=passed,
                message=message,
                details={
                    "total_functions": total_functions,
                    "functions_with_validation": validation_count,
                    "validation_patterns_found": validation_patterns,
                },
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.INPUT_VALIDATION,
                severity=AssertionSeverity.CRITICAL,
                passed=False,
                message=f"Input validation check failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )

    def validate_error_handling(self, module: Module) -> AssertionResult:
        """Validate presence of error handling"""
        start_time = time.time()

        try:
            source_code = inspect.getsource(module.__class__)
            tree = ast.parse(source_code)

            try_blocks = 0
            total_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    total_functions += 1
                    for child in ast.walk(node):
                        if isinstance(child, ast.Try):
                            try_blocks += 1
                            break

            passed = try_blocks > 0
            message = f"Error handling: {try_blocks}/{total_functions} functions have error handling"

            return AssertionResult(
                assertion_type=AssertionType.ERROR_HANDLING,
                severity=AssertionSeverity.HIGH,
                passed=passed,
                message=message,
                details={"total_functions": total_functions, "functions_with_error_handling": try_blocks},
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.ERROR_HANDLING,
                severity=AssertionSeverity.HIGH,
                passed=False,
                message=f"Error handling check failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )


class PerformanceValidator:
    """Validates performance aspects"""

    def validate_execution_time(self, module: Module, test_inputs: List[Dict[str, Any]]) -> AssertionResult:
        """Validate execution time performance"""
        start_time = time.time()

        try:
            execution_times = []
            max_time_threshold = 1.0  # 1 second threshold

            for test_input in test_inputs:
                test_start = time.time()
                try:
                    # Test the module's forward method
                    if hasattr(module, "forward"):
                        module.forward(**test_input)  # type: ignore[attr-defined]
                    execution_times.append(time.time() - test_start)
                except Exception:
                    # Skip failed executions for timing
                    continue

            if not execution_times:
                return AssertionResult(
                    assertion_type=AssertionType.EXECUTION_TIME,
                    severity=AssertionSeverity.MEDIUM,
                    passed=False,
                    message="No successful executions to measure",
                    details={"error": "All test executions failed"},
                    execution_time=time.time() - start_time,
                )

            avg_time = sum(execution_times) / len(execution_times)
            max_time = max(execution_times)

            passed = max_time < max_time_threshold
            message = f"Execution time: avg={avg_time:.3f}s, max={max_time:.3f}s (threshold: {max_time_threshold}s)"

            return AssertionResult(
                assertion_type=AssertionType.EXECUTION_TIME,
                severity=AssertionSeverity.MEDIUM,
                passed=passed,
                message=message,
                details={
                    "average_time": avg_time,
                    "max_time": max_time,
                    "threshold": max_time_threshold,
                    "test_count": len(execution_times),
                },
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.EXECUTION_TIME,
                severity=AssertionSeverity.MEDIUM,
                passed=False,
                message=f"Execution time validation failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )


class SecurityValidator:
    """Validates security aspects"""

    def validate_input_sanitization(self, module: Module) -> AssertionResult:
        """Validate input sanitization"""
        start_time = time.time()

        try:
            source_code = inspect.getsource(module.__class__)

            # Look for sanitization patterns
            sanitization_patterns = [
                "strip",
                "replace",
                "encode",
                "decode",
                "escape",
                "quote",
                "html.escape",
                "urllib.parse.quote",
                "re.escape",
            ]

            pattern_count = 0
            for pattern in sanitization_patterns:
                if pattern in source_code:
                    pattern_count += 1

            passed = pattern_count > 0
            message = f"Input sanitization: {pattern_count} sanitization patterns found"

            return AssertionResult(
                assertion_type=AssertionType.INPUT_SANITIZATION,
                severity=AssertionSeverity.CRITICAL,
                passed=passed,
                message=message,
                details={"sanitization_patterns_found": pattern_count, "patterns_checked": sanitization_patterns},
                execution_time=time.time() - start_time,
            )

        except Exception as e:
            return AssertionResult(
                assertion_type=AssertionType.INPUT_SANITIZATION,
                severity=AssertionSeverity.CRITICAL,
                passed=False,
                message=f"Input sanitization validation failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time,
            )


class DSPyAssertionFramework:
    """Main assertion framework for DSPy modules"""

    def __init__(self, enable_all_assertions: bool = True):
        """
        Initialize the assertion framework

        Args:
            enable_all_assertions: Whether to enable all assertion types
        """
        self.enable_all_assertions = enable_all_assertions

        # Initialize validators
        self.code_validator = CodeQualityValidator()
        self.logic_validator = LogicValidator()
        self.performance_validator = PerformanceValidator()
        self.security_validator = SecurityValidator()

        # Statistics
        self.validation_count = 0
        self.total_execution_time = 0.0
        self.reliability_history = []

        _LOG.info("DSPy Assertion Framework initialized")

    def validate_module(self, module: Any, test_inputs: Optional[List[Dict[str, Any]]] = None) -> ValidationReport:
        """
        Validate a DSPy module comprehensively

        Args:
            module: DSPy module to validate (can be any type for testing invalid modules)
            test_inputs: Optional test inputs for performance validation

        Returns:
            ValidationReport with comprehensive results
        """
        start_time = time.time()
        module_name = module.__class__.__name__

        _LOG.info(f"Starting validation for module: {module_name}")

        results = []
        test_inputs = test_inputs or []

        try:
            # Get module source code
            source_code = inspect.getsource(module.__class__)

            # Code Quality Assertions
            results.append(self.code_validator.validate_type_hints(source_code))
            results.append(self.code_validator.validate_docstrings(source_code))
            results.append(self.code_validator.validate_naming_conventions(source_code))

            # Logic Assertions
            results.append(self.logic_validator.validate_input_validation(module))
            results.append(self.logic_validator.validate_error_handling(module))

            # Performance Assertions
            results.append(self.performance_validator.validate_execution_time(module, test_inputs))

            # Security Assertions
            results.append(self.security_validator.validate_input_sanitization(module))

        except Exception as e:
            _LOG.error(f"Validation failed for module {module_name}: {e}")
            results.append(
                AssertionResult(
                    assertion_type=AssertionType.TYPE_HINTS,  # Placeholder
                    severity=AssertionSeverity.CRITICAL,
                    passed=False,
                    message=f"Validation framework error: {str(e)}",
                    details={"error": str(e)},
                    execution_time=time.time() - start_time,
                )
            )

        # Calculate statistics
        total_assertions = len(results)
        passed_assertions = sum(1 for r in results if r.passed)
        failed_assertions = total_assertions - passed_assertions
        critical_failures = sum(1 for r in results if r.severity == AssertionSeverity.CRITICAL and not r.passed)

        # Calculate reliability score (0-100)
        reliability_score = (passed_assertions / total_assertions * 100) if total_assertions > 0 else 0.0

        # Generate recommendations
        recommendations = self._generate_recommendations(results)

        # Create report
        report = ValidationReport(
            module_name=module_name,
            total_assertions=total_assertions,
            passed_assertions=passed_assertions,
            failed_assertions=failed_assertions,
            critical_failures=critical_failures,
            reliability_score=reliability_score,
            execution_time=time.time() - start_time,
            results=results,
            recommendations=recommendations,
        )

        # Update statistics
        self.validation_count += 1
        self.total_execution_time += report.execution_time
        self.reliability_history.append(reliability_score)

        _LOG.info(f"Validation completed for {module_name}: {reliability_score:.1f}% reliability")

        return report

    def _generate_recommendations(self, results: List[AssertionResult]) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        for result in results:
            if not result.passed:
                if result.assertion_type == AssertionType.TYPE_HINTS:
                    recommendations.append("Add type hints to all functions and methods")
                elif result.assertion_type == AssertionType.DOCSTRINGS:
                    recommendations.append("Add docstrings to all functions and methods")
                elif result.assertion_type == AssertionType.NAMING_CONVENTIONS:
                    recommendations.append(
                        "Follow Python naming conventions (snake_case for functions, PascalCase for classes)"
                    )
                elif result.assertion_type == AssertionType.INPUT_VALIDATION:
                    recommendations.append("Add input validation to prevent invalid data processing")
                elif result.assertion_type == AssertionType.ERROR_HANDLING:
                    recommendations.append("Add try-catch blocks for robust error handling")
                elif result.assertion_type == AssertionType.EXECUTION_TIME:
                    recommendations.append("Optimize performance-critical code paths")
                elif result.assertion_type == AssertionType.INPUT_SANITIZATION:
                    recommendations.append("Add input sanitization to prevent security vulnerabilities")

        return recommendations

    def get_statistics(self) -> Dict[str, Any]:
        """Get framework statistics"""
        if not self.reliability_history:
            return {
                "total_validations": 0,
                "average_reliability": 0.0,
                "reliability_trend": "no_data",
                "total_execution_time": 0.0,
            }

        avg_reliability = sum(self.reliability_history) / len(self.reliability_history)

        # Calculate trend
        if len(self.reliability_history) >= 2:
            recent_avg = sum(self.reliability_history[-3:]) / min(3, len(self.reliability_history))
            if recent_avg > avg_reliability + 5:
                trend = "improving"
            elif recent_avg < avg_reliability - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "total_validations": self.validation_count,
            "average_reliability": avg_reliability,
            "reliability_trend": trend,
            "total_execution_time": self.total_execution_time,
            "recent_reliability_scores": self.reliability_history[-5:] if self.reliability_history else [],
        }

    def validate_reliability_improvement(self, before_score: float, after_score: float) -> bool:
        """
        Validate if reliability improvement meets the 37% → 98% target

        Args:
            before_score: Reliability score before optimization
            after_score: Reliability score after optimization

        Returns:
            True if improvement meets target
        """
        improvement = after_score - before_score
        target_improvement = 98 - 37  # 61% improvement target

        return improvement >= target_improvement


# Global framework instance
_assertion_framework = None


def get_assertion_framework() -> DSPyAssertionFramework:
    """Get the global assertion framework instance"""
    global _assertion_framework
    if _assertion_framework is None:
        _assertion_framework = DSPyAssertionFramework()
    return _assertion_framework


def validate_dspy_module(module: Any, test_inputs: Optional[List[Dict[str, Any]]] = None) -> ValidationReport:
    """
    Convenience function to validate a DSPy module

    Args:
        module: DSPy module to validate (can be any type for testing invalid modules)
        test_inputs: Optional test inputs for performance validation

    Returns:
        ValidationReport with comprehensive results
    """
    framework = get_assertion_framework()
    return framework.validate_module(module, test_inputs)


def assert_reliability_target(module: Module, target_score: float = 98.0) -> bool:
    """
    Assert that a module meets the reliability target

    Args:
        module: DSPy module to validate
        target_score: Target reliability score (default: 98%)

    Returns:
        True if module meets target
    """
    report = validate_dspy_module(module)
    return report.reliability_score >= target_score
