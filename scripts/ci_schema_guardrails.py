#!/usr/bin/env python3
"""
CI Schema Guardrails

Prevents schema sprawl by blocking re-introduction of extra schemas
and ensuring schema validation passes.
"""

import subprocess
import sys
from pathlib import Path


def check_schema_creep():
    """Check for re-introduction of extra schemas"""
    print("🔍 Checking for schema creep...")

    # Check for legacy schema class definitions
    patterns = [
        r"class\s+Case\(",
        r"class\s+RAGCheckerResult\(",
        r"class\s+QuerySample\(",
        r"class\s+EvalItem\(",
    ]

    violations = []
    for pattern in patterns:
        try:
            result = subprocess.run(
                ["grep", "-r", "-n", pattern, "evals", "dspy-rag-system", "300_experiments"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                violations.extend(result.stdout.strip().split("\n"))
        except subprocess.CalledProcessError:
            pass

    if violations:
        print("❌ Schema creep detected:")
        for violation in violations:
            print(f"  {violation}")
        return False

    print("✅ No schema creep detected")
    return True


def validate_gold_schema():
    """Run gold schema validation"""
    print("🔍 Validating gold schema...")

    try:
        result = subprocess.run(["python3", "scripts/validate_gold_schema.py"], capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ Gold schema validation failed:")
            print(result.stderr)
            return False

        print("✅ Gold schema validation passed")
        print(result.stdout)
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Schema validation error: {e}")
        return False


def run_schema_tests():
    """Run schema round-trip tests"""
    print("🔍 Running schema tests...")

    try:
        result = subprocess.run(
            ["python3", "-m", "pytest", "tests/test_schema_roundtrip.py", "tests/test_enhanced_schemas.py", "-q"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            print("❌ Schema tests failed:")
            print(result.stdout)
            print(result.stderr)
            return False

        print("✅ Schema tests passed")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Test execution error: {e}")
        return False


def main():
    """Main CI guardrail function"""
    print("🛡️  Running CI Schema Guardrails")
    print("=" * 50)

    checks = [
        check_schema_creep,
        validate_gold_schema,
        run_schema_tests,
    ]

    all_passed = True
    for check in checks:
        if not check():
            all_passed = False
        print()

    if all_passed:
        print("🎉 All schema guardrails passed!")
        return 0
    else:
        print("💥 Schema guardrails failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
