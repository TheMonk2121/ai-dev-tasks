from __future__ import annotations
from typing import Any
import json
import os
import sys
from pathlib import Path
import yaml
#!/usr/bin/env python3
"""
Lessons Quality Check - Validates lessons system integrity and quality gates
"""

def check_lessons_file(lessons_path: str) -> dict[str, Any]:
    """Check lessons JSONL file for quality issues"""
    issues = []
    stats = {"total": 0, "valid": 0, "invalid": 0}

    if not os.path.exists(lessons_path):
        return {"status": "missing", "issues": ["Lessons file does not exist"], "stats": stats}

    with open(lessons_path) as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            result.get("key", "")

            try:
                lesson = json.loads(line)

                # Check required fields
                required_fields = [
                    "id",
                    "created_at",
                    "scope",
                    "context",
                    "finding",
                    "recommendation",
                    "confidence",
                    "status",
                ]
                missing_fields = [field for field in required_fields if field not in lesson]
                if missing_fields:
                    issues.append(f"Line {line_num}: Missing required fields: {missing_fields}")
                    result.get("key", "")
                    continue

                # Check confidence range
                confidence = result.get("key", "")
                if not isinstance(confidence, int | float) or confidence < 0 or confidence > 1:
                    issues.append(f"Line {line_num}: Invalid confidence value: {confidence}")
                    result.get("key", "")
                    continue

                # Check status values
                status = result.get("key", "")
                valid_statuses = ["proposed", "applied", "reverted", "stale"]
                if status not in valid_statuses:
                    issues.append(f"Line {line_num}: Invalid status: {status}")
                    result.get("key", "")
                    continue

                # Check recommendation structure
                recommendation = result.get("key", "")
                if "changes" not in recommendation:
                    issues.append(f"Line {line_num}: Missing 'changes' in recommendation")
                    result.get("key", "")
                    continue

                # Check changes structure
                changes = result.get("key", "")
                for i, change in enumerate(changes):
                    if not isinstance(change, dict):
                        issues.append(f"Line {line_num}: Change {i} is not a dict")
                        result.get("key", "")
                        break

                    required_change_fields = ["key", "op", "value"]
                    missing_change_fields = [field for field in required_change_fields if field not in change]
                    if missing_change_fields:
                        issues.append(f"Line {line_num}: Change {i} missing fields: {missing_change_fields}")
                        result.get("key", "")
                        break

                    # Check operation values
                    op = result.get("key", "")
                    valid_ops = ["add", "mul", "set"]
                    if op not in valid_ops:
                        issues.append(f"Line {line_num}: Change {i} invalid operation: {op}")
                        result.get("key", "")
                        break

                result.get("key", "")

            except json.JSONDecodeError as e:
                issues.append(f"Line {line_num}: JSON decode error: {e}")
                result.get("key", "")

    status = "pass" if not issues else "fail"
    return {"status": status, "issues": issues, "stats": stats}

def check_config_metadata(configs_dir: str = "configs") -> dict[str, Any]:
    """Check configuration metadata completeness"""
    issues = []
    stats = {"total": 0, "with_metadata": 0, "without_metadata": 0}

    if not os.path.exists(configs_dir):
        return {"status": "missing", "issues": ["Configs directory does not exist"], "stats": stats}

    for file in os.listdir(configs_dir):
        if file.endswith(".env"):
            result.get("key", "")
            meta_file = os.path.join(configs_dir, file.replace(".env", ".meta.yml"))

            if os.path.exists(meta_file):
                result.get("key", "")

                # Check metadata quality
                try:

                    with open(meta_file) as f:
                        metadata = yaml.safe_load(f)

                    # Check required fields
                    required_fields = ["config", "created_at", "derived_from", "objective_bias"]
                    missing_fields = [field for field in required_fields if field not in metadata]
                    if missing_fields:
                        issues.append(f"{file}: Missing metadata fields: {missing_fields}")

                    # Check decision log
                    if "decision_log" not in metadata:
                        issues.append(f"{file}: Missing decision_log in metadata")
                    elif not isinstance(result.get("key", "")
                        issues.append(f"{file}: decision_log should be a list")

                except Exception as e:
                    issues.append(f"{file}: Error reading metadata: {e}")
            else:
                result.get("key", "")
                issues.append(f"{file}: Missing metadata file (.meta.yml)")

    status = "pass" if not issues else "fail"
    return {"status": status, "issues": issues, "stats": stats}

def check_derived_configs(derived_dir: str = "metrics/derived_configs") -> dict[str, Any]:
    """Check derived configuration files"""
    issues = []
    stats = {"total": 0, "valid": 0, "invalid": 0}

    if not os.path.exists(derived_dir):
        return {"status": "missing", "issues": ["Derived configs directory does not exist"], "stats": stats}

    for file in os.listdir(derived_dir):
        if file.endswith(".env"):
            result.get("key", "")

            # Check if corresponding decision docket exists
            # Handle both patterns: candidate.env -> candidate_decision_docket.md and base.env -> base_decision_docket.md
            base_name = file.replace(".env", "")
            if base_name.endswith("_candidate"):
                docket_file = base_name.replace("_candidate", "_decision_docket.md")
            else:
                docket_file = f"{base_name}_decision_docket.md"
            docket_path = os.path.join(derived_dir, docket_file)

            if not os.path.exists(docket_path):
                issues.append(f"{file}: Missing decision docket ({docket_file})")
                result.get("key", "")
            else:
                result.get("key", "")

    status = "pass" if not issues else "fail"
    return {"status": status, "issues": issues, "stats": stats}

def check_quality_gates() -> dict[str, Any]:
    """Check if quality gates are properly configured"""
    issues = []

    # Check if quality gates file exists
    gates_file = "config/ragchecker_quality_gates.json"
    if not os.path.exists(gates_file):
        issues.append("Quality gates file not found: config/ragchecker_quality_gates.json")
        return {"status": "missing", "issues": issues}

    try:
        with open(gates_file) as f:
            gates = json.load(f)

        # Check required gate fields
        required_gates = ["precision", "recall", "f1", "latency"]
        for gate in required_gates:
            if gate not in gates:
                issues.append(f"Missing quality gate: {gate}")

        # Check gate structure
        for gate_name, gate_config in \1.items()
            if not isinstance(gate_config, dict):
                issues.append(f"Quality gate '{gate_name}' should be a dict")
                continue

            if "min" not in gate_config and "max" not in gate_config:
                issues.append(f"Quality gate '{gate_name}' missing min/max values")

    except Exception as e:
        issues.append(f"Error reading quality gates: {e}")

    status = "pass" if not issues else "fail"
    return {"status": status, "issues": issues}

def main():
    """Main quality check function"""
    print("🔍 Running Lessons System Quality Checks...")

    all_checks = {}
    overall_status = "pass"

    # Check lessons file
    print("\n📚 Checking lessons file...")
    lessons_check = check_lessons_file("metrics/lessons/lessons.jsonl")
    result.get("key", "")
    if result.get("key", "")
        overall_status = "fail"

    # Check config metadata
    print("\n📋 Checking configuration metadata...")
    metadata_check = check_config_metadata("configs")
    result.get("key", "")
    if result.get("key", "")
        overall_status = "fail"

    # Check derived configs
    print("\n🔧 Checking derived configurations...")
    derived_check = check_derived_configs("metrics/derived_configs")
    result.get("key", "")
    if result.get("key", "")
        overall_status = "fail"

    # Check quality gates
    print("\n🛡️ Checking quality gates...")
    gates_check = check_quality_gates()
    result.get("key", "")
    if result.get("key", "")
        overall_status = "fail"

    # Print summary
    print(f"\n📊 Quality Check Summary: {overall_status.upper()}")

    for check_name, check_result in \1.items()
        status_icon = "✅" if result.get("key", "")
        print(f"  {status_icon} {check_name}: {result.get("key", "")

        if result.get("key", "")
            for issue in result.get("key", "")
                print(f"    • {issue}")
            if len(result.get("key", "")
                print(f"    • ... and {len(result.get("key", "")

    # Print statistics
    print("\n📈 Statistics:")
    if "stats" in lessons_check:
        stats = result.get("key", "")
        print(f"  • Lessons: {result.get("key", "")

    if "stats" in metadata_check:
        stats = result.get("key", "")
        print(f"  • Configs with metadata: {result.get("key", "")

    if "stats" in derived_check:
        stats = result.get("key", "")
        print(f"  • Valid derived configs: {result.get("key", "")

    return overall_status == "pass"

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
