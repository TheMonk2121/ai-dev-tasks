from __future__ import annotations
import json
import pathlib
from typing import Any
        import yaml
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
"""
Test Set Hardening & Robustness Validation

Implements comprehensive test cases and edge case handling
for the retrieval pipeline to ensure production reliability.
"""




# Test case validation
def validate_test_cases(test_cases: list[dict[str, Any]]) -> tuple[bool, list[str]]:
    """Validate test case format and completeness."""
    errors = []

    for i, case in enumerate(test_cases):
        case_id = case.get("query_id", f"case_{i}")

        # Required fields
        required_fields = ["query_id", "query", "gt_answer", "retrieved_context"]
        for field in required_fields:
            if field not in case:
                errors.append(f"{case_id}: Missing required field '{field}'")
            elif not case[field]:
                errors.append(f"{case_id}: Empty value for field '{field}'")

        # Query validation
        query = case.get("query", "")
        if query:
            if len(query.strip()) < 5:
                errors.append(f"{case_id}: Query too short (< 5 chars)")
            if len(query) > 1000:
                errors.append(f"{case_id}: Query too long (> 1000 chars)")

        # Ground truth validation
        gt_answer = case.get("gt_answer", "")
        if gt_answer and len(gt_answer.strip()) < 10:
            errors.append(f"{case_id}: Ground truth answer too short (< 10 chars)")

        # Context validation
        context = case.get("retrieved_context", [])
        if isinstance(context, list):
            if len(context) == 0:
                errors.append(f"{case_id}: No retrieved context provided")
            elif len(context) > 50:
                errors.append(f"{case_id}: Too many context items (> 50)")

            for j, ctx in enumerate(context):
                if not isinstance(ctx, str):
                    errors.append(f"{case_id}: Context item {j} is not a string")
                elif len(ctx.strip()) < 20:
                    errors.append(f"{case_id}: Context item {j} too short (< 20 chars)")
        else:
            errors.append(f"{case_id}: retrieved_context must be a list")

    return len(errors) == 0, errors


def generate_edge_cases() -> list[dict[str, Any]]:
    """Generate edge case test scenarios."""
    edge_cases = [
        {
            "query_id": "edge_empty_query",
            "query": "",
            "gt_answer": "Should handle empty queries gracefully",
            "retrieved_context": ["Empty query handling context"],
            "expected_behavior": "graceful_failure",
        },
        {
            "query_id": "edge_very_long_query",
            "query": "What is " + "very " * 200 + "long query about DSPy?",
            "gt_answer": "Should handle very long queries",
            "retrieved_context": ["Long query handling context"],
            "expected_behavior": "truncate_or_handle",
        },
        {
            "query_id": "edge_special_chars",
            "query": "What about files with special chars: @#$%^&*()[]{}|\\;':\",./<>?",
            "gt_answer": "Should handle special characters in queries",
            "retrieved_context": ["Special character handling context"],
            "expected_behavior": "normal_processing",
        },
        {
            "query_id": "edge_unicode",
            "query": "What about unicode: 你好世界 🌍 café naïve résumé",
            "gt_answer": "Should handle unicode characters",
            "retrieved_context": ["Unicode handling context"],
            "expected_behavior": "normal_processing",
        },
        {
            "query_id": "edge_no_context",
            "query": "Query with no relevant context available",
            "gt_answer": "Not in context.",
            "retrieved_context": [],
            "expected_behavior": "no_context_response",
        },
        {
            "query_id": "edge_duplicate_context",
            "query": "Query with duplicate context items",
            "gt_answer": "Should deduplicate context",
            "retrieved_context": [
                "This is duplicate content",
                "This is duplicate content",
                "This is duplicate content",
            ],
            "expected_behavior": "deduplication",
        },
        {
            "query_id": "edge_malformed_context",
            "query": "Query with malformed context",
            "gt_answer": "Should handle malformed context gracefully",
            "retrieved_context": ["", "   ", "\n\n\n", "Valid context item"],
            "expected_behavior": "filter_invalid",
        },
    ]

    return edge_cases


def test_retrieval_robustness(retrieval_fn, test_cases: list[dict[str, Any]]) -> dict[str, Any]:
    """Test retrieval pipeline robustness with edge cases."""
    results = {"total_cases": len(test_cases), "passed": 0, "failed": 0, "errors": 0, "case_results": []}

    for case in test_cases:
        case_id = case["query_id"]
        query = case["query"]
        expected_behavior = case.get("expected_behavior", "normal_processing")

        try:
            # Run retrieval
            result = retrieval_fn(query)

            case_result = {
                "case_id": case_id,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "expected_behavior": expected_behavior,
                "actual_result": result,
                "status": "unknown",
            }

            # Validate behavior based on expectations
            if expected_behavior == "graceful_failure":
                if "error" in result or result.get("answer") == "Not in context.":
                    case_result["status"] = "passed"
                    results["passed"] += 1
                else:
                    case_result["status"] = "failed"
                    case_result["reason"] = "Should have failed gracefully"
                    results["failed"] += 1

            elif expected_behavior == "no_context_response":
                if result.get("answer") == "Not in context.":
                    case_result["status"] = "passed"
                    results["passed"] += 1
                else:
                    case_result["status"] = "failed"
                    case_result["reason"] = "Should return 'Not in context.'"
                    results["failed"] += 1

            elif expected_behavior == "normal_processing":
                if "answer" in result and result.get("context_used", False):
                    case_result["status"] = "passed"
                    results["passed"] += 1
                else:
                    case_result["status"] = "failed"
                    case_result["reason"] = "Should process normally"
                    results["failed"] += 1

            else:
                # Default: just check that we got some result
                if "answer" in result:
                    case_result["status"] = "passed"
                    results["passed"] += 1
                else:
                    case_result["status"] = "failed"
                    case_result["reason"] = "No answer returned"
                    results["failed"] += 1

            results["case_results"].append(case_result)

        except Exception as e:
            case_result = {
                "case_id": case_id,
                "query": query[:100] + "..." if len(query) > 100 else query,
                "expected_behavior": expected_behavior,
                "status": "error",
                "error": str(e),
            }
            results["case_results"].append(case_result)
            results["errors"] += 1

    return results


def validate_pipeline_components(config_path: str = "config/retrieval.yaml") -> dict[str, Any]:
    """Validate that all pipeline components are properly configured."""
    try:

        config = yaml.safe_load(pathlib.Path(config_path).read_text())
    except Exception as e:
        return {"valid": False, "error": f"Config loading failed: {e}"}

    validation_results = {"valid": True, "warnings": [], "errors": [], "component_status": {}}

    # Validate fusion config
    fusion = config.get("fusion", {})
    if not fusion:
        validation_results["errors"].append("Missing fusion configuration")
        validation_results["valid"] = False
    else:
        lambda_lex = fusion.get("lambda_lex", 0)
        lambda_sem = fusion.get("lambda_sem", 0)
        if abs((lambda_lex + lambda_sem) - 1.0) > 0.01:
            validation_results["warnings"].append(f"Fusion weights don't sum to 1.0: {lambda_lex + lambda_sem}")

        k = fusion.get("k", 0)
        if k <= 0:
            validation_results["errors"].append("Invalid fusion k parameter")
            validation_results["valid"] = False

    validation_results["component_status"]["fusion"] = (
        "valid" if not any("fusion" in error for error in validation_results["errors"]) else "invalid"
    )

    # Validate prefilter config
    prefilter = config.get("prefilter", {})
    if prefilter:
        min_bm25 = prefilter.get("min_bm25_score", 0)
        min_vector = prefilter.get("min_vector_score", 0)

        if min_bm25 < 0 or min_bm25 > 1:
            validation_results["warnings"].append(f"BM25 threshold may be out of range: {min_bm25}")

        if min_vector < 0 or min_vector > 1:
            validation_results["warnings"].append(f"Vector threshold may be out of range: {min_vector}")

    validation_results["component_status"]["prefilter"] = "valid"

    # Validate rerank config
    rerank = config.get("rerank", {})
    if rerank:
        alpha = rerank.get("alpha", 0.7)
        if alpha < 0 or alpha > 1:
            validation_results["warnings"].append(f"Rerank alpha out of range [0,1]: {alpha}")

    validation_results["component_status"]["rerank"] = "valid"

    # Validate quality gates
    tuning = config.get("tuning", {})
    quality_gates = tuning.get("quality_gates", {})
    if not quality_gates:
        validation_results["warnings"].append("No quality gates configured")
    else:
        soft_gates = quality_gates.get("soft", {})
        hard_gates = quality_gates.get("hard", {})

        # Check that hard gates are stricter than soft gates
        for metric in ["recall_at_20", "f1_score", "faithfulness"]:
            soft_val = soft_gates.get(metric, 0)
            hard_val = hard_gates.get(metric, 0)
            if hard_val > soft_val:
                validation_results["warnings"].append(
                    f"Hard gate for {metric} ({hard_val}) higher than soft gate ({soft_val})"
                )

    validation_results["component_status"]["quality_gates"] = "valid"

    return validation_results


def run_comprehensive_tests(retrieval_fn, output_path: str = "test_hardening_results.json") -> None:
    """Run comprehensive robustness testing."""
    print("🧪 Starting comprehensive retrieval robustness testing...")

    # Generate edge cases
    edge_cases = generate_edge_cases()
    print(f"📊 Generated {len(edge_cases)} edge case scenarios")

    # Validate test cases
    valid, errors = validate_test_cases(edge_cases)
    if not valid:
        print("⚠️ Test case validation warnings:")
        for error in errors[:5]:  # Show first 5 errors
            print(f"  - {error}")
        if len(errors) > 5:
            print(f"  ... and {len(errors) - 5} more")

    # Run robustness tests
    print("⚡ Running robustness tests...")
    robustness_results = test_retrieval_robustness(retrieval_fn, edge_cases)

    # Validate pipeline configuration
    print("🔧 Validating pipeline configuration...")
    config_validation = validate_pipeline_components()

    # Compile results
    results = {
        "test_summary": {
            "total_edge_cases": len(edge_cases),
            "robustness_passed": robustness_results["passed"],
            "robustness_failed": robustness_results["failed"],
            "robustness_errors": robustness_results["errors"],
            "config_valid": config_validation["valid"],
            "config_warnings": len(config_validation["warnings"]),
            "config_errors": len(config_validation["errors"]),
        },
        "robustness_results": robustness_results,
        "config_validation": config_validation,
        "edge_cases": edge_cases,
    }

    # Save results
    pathlib.Path(output_path).write_text(json.dumps(results, indent=2))
    print(f"💾 Test results saved to {output_path}")

    # Print summary
    print("\n🏆 Test Hardening Results:")
    print(f"   Edge Cases: {len(edge_cases)}")
    print(f"   Passed: {robustness_results['passed']}")
    print(f"   Failed: {robustness_results['failed']}")
    print(f"   Errors: {robustness_results['errors']}")
    print(f"   Config Valid: {config_validation['valid']}")
    print(f"   Config Warnings: {len(config_validation['warnings'])}")

    if config_validation["warnings"]:
        print("\n⚠️ Configuration Warnings:")
        for warning in config_validation["warnings"][:3]:
            print(f"   - {warning}")

    if config_validation["errors"]:
        print("\n❌ Configuration Errors:")
        for error in config_validation["errors"]:
            print(f"   - {error}")
