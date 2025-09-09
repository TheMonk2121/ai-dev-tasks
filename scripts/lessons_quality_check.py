#!/usr/bin/env python3
"""
Lessons Quality Check - Validates lessons system integrity and quality gates
"""

import json
import os
import sys
from pathlib import Path
from typing import Any


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

            stats["total"] += 1

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
                    stats["invalid"] += 1
                    continue

                # Check confidence range
                confidence = lesson.get("confidence", 0)
                if not isinstance(confidence, int | float) or confidence < 0 or confidence > 1:
                    issues.append(f"Line {line_num}: Invalid confidence value: {confidence}")
                    stats["invalid"] += 1
                    continue

                # Check status values
                status = lesson.get("status", "")
                valid_statuses = ["proposed", "applied", "reverted", "stale"]
                if status not in valid_statuses:
                    issues.append(f"Line {line_num}: Invalid status: {status}")
                    stats["invalid"] += 1
                    continue

                # Check recommendation structure
                recommendation = lesson.get("recommendation", {})
                if "changes" not in recommendation:
                    issues.append(f"Line {line_num}: Missing 'changes' in recommendation")
                    stats["invalid"] += 1
                    continue

                # Check changes structure
                changes = recommendation.get("changes", [])
                for i, change in enumerate(changes):
                    if not isinstance(change, dict):
                        issues.append(f"Line {line_num}: Change {i} is not a dict")
                        stats["invalid"] += 1
                        break

                    required_change_fields = ["key", "op", "value"]
                    missing_change_fields = [field for field in required_change_fields if field not in change]
                    if missing_change_fields:
                        issues.append(f"Line {line_num}: Change {i} missing fields: {missing_change_fields}")
                        stats["invalid"] += 1
                        break

                    # Check operation values
                    op = change.get("op", "")
                    valid_ops = ["add", "mul", "set"]
                    if op not in valid_ops:
                        issues.append(f"Line {line_num}: Change {i} invalid operation: {op}")
                        stats["invalid"] += 1
                        break

                stats["valid"] += 1

            except json.JSONDecodeError as e:
                issues.append(f"Line {line_num}: JSON decode error: {e}")
                stats["invalid"] += 1

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
            stats["total"] += 1
            meta_file = os.path.join(configs_dir, file.replace(".env", ".meta.yml"))

            if os.path.exists(meta_file):
                stats["with_metadata"] += 1

                # Check metadata quality
                try:
                    import yaml

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
                    elif not isinstance(metadata["decision_log"], list):
                        issues.append(f"{file}: decision_log should be a list")

                except Exception as e:
                    issues.append(f"{file}: Error reading metadata: {e}")
            else:
                stats["without_metadata"] += 1
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
            stats["total"] += 1

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
                stats["invalid"] += 1
            else:
                stats["valid"] += 1

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
        for gate_name, gate_config in gates.items():
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
    all_checks["lessons"] = lessons_check
    if lessons_check["status"] != "pass":
        overall_status = "fail"

    # Check config metadata
    print("\n📋 Checking configuration metadata...")
    metadata_check = check_config_metadata("configs")
    all_checks["metadata"] = metadata_check
    if metadata_check["status"] != "pass":
        overall_status = "fail"

    # Check derived configs
    print("\n🔧 Checking derived configurations...")
    derived_check = check_derived_configs("metrics/derived_configs")
    all_checks["derived"] = derived_check
    if derived_check["status"] != "pass":
        overall_status = "fail"

    # Check quality gates
    print("\n🛡️ Checking quality gates...")
    gates_check = check_quality_gates()
    all_checks["gates"] = gates_check
    if gates_check["status"] != "pass":
        overall_status = "fail"

    # Print summary
    print(f"\n📊 Quality Check Summary: {overall_status.upper()}")

    for check_name, check_result in all_checks.items():
        status_icon = "✅" if check_result["status"] == "pass" else "❌"
        print(f"  {status_icon} {check_name}: {check_result['status']}")

        if check_result["status"] != "pass" and check_result["issues"]:
            for issue in check_result["issues"][:3]:  # Show first 3 issues
                print(f"    • {issue}")
            if len(check_result["issues"]) > 3:
                print(f"    • ... and {len(check_result['issues']) - 3} more issues")

    # Print statistics
    print("\n📈 Statistics:")
    if "stats" in lessons_check:
        stats = lessons_check["stats"]
        print(f"  • Lessons: {stats['valid']}/{stats['total']} valid")

    if "stats" in metadata_check:
        stats = metadata_check["stats"]
        print(f"  • Configs with metadata: {stats['with_metadata']}/{stats['total']}")

    if "stats" in derived_check:
        stats = derived_check["stats"]
        print(f"  • Valid derived configs: {stats['valid']}/{stats['total']}")

    return overall_status == "pass"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
