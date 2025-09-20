#!/usr/bin/env python3
"""
Update Gold Cases Script
Updates outdated script references in gold case answers to current paths.
"""

import json
import os
import re
from pathlib import Path

# Mapping of old paths to new paths
PATH_MAPPING = {
    "dspy_modules/retriever/query_rewrite.py": "src/dspy_modules/retriever/query_rewrite.py",
    "scripts/ci_gate_reader.py": "scripts/monitoring/drift_detector.py",  # Functionality equivalent
    "scripts/ragchecker_official_evaluation.py": "scripts/evaluation/ragchecker_official_evaluation.py",
    "dspy_reader_program.py": "src/dspy_modules/dspy_reader_program.py",
    "scripts/cursor_memory_rehydrate.py": "scripts/utilities/cursor_memory_rehydrate.py",
    "scripts/unified_memory_orchestrator.py": "scripts/core/unified_memory_orchestrator.py",
    "dspy_modules/reader/sentence_select.py": "src/dspy_modules/reader/sentence_select.py",
    "scripts/update_baseline_manifest.py": "scripts/utilities/update_baseline_manifest.py",
    "scripts/abp_validation.py": "scripts/utilities/abp_validation.py",
    "dspy_modules/retriever/rerank.py": "src/dspy_modules/retriever/rerank.py",
    "scripts/venv_manager.py": "scripts/utilities/venv_manager.py",
}


def update_answer(answer: str) -> str:
    """Update script paths in an answer string."""
    updated_answer = answer

    for old_path, new_path in PATH_MAPPING.items():
        # Replace in python3 commands
        updated_answer = re.sub(rf"python3\s+{re.escape(old_path)}", f"python3 {new_path}", updated_answer)
        # Replace standalone script references
        updated_answer = updated_answer.replace(old_path, new_path)

    return updated_answer


def verify_script_exists(script_path: str) -> bool:
    """Verify that a script path exists in the current codebase."""
    return os.path.exists(script_path)


def main():
    """Main function to update gold cases."""
    gold_cases_file = Path("evals/data/gold/v1/gold_cases_121.jsonl")

    # Read all gold cases
    with open(gold_cases_file) as f:
        cases = [json.loads(line) for line in f]

    print(f"Processing {len(cases)} gold cases...")

    updated_count = 0
    cases_to_update = []

    for case in cases:
        original_answer = case.get("gt_answer", "")
        updated_answer = update_answer(original_answer)

        if updated_answer != original_answer:
            cases_to_update.append(
                {"id": case["id"], "query": case["query"], "original": original_answer, "updated": updated_answer}
            )
            case["gt_answer"] = updated_answer
            updated_count += 1

    # Write updated cases back to file
    with open(gold_cases_file, "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    print(f"Updated {updated_count} cases:")
    print("=" * 60)

    for update in cases_to_update:
        print(f"{update['id']}: {update['query']}")
        print(f"  OLD: {update['original'][:100]}...")
        print(f"  NEW: {update['updated'][:100]}...")
        print()

    # Verify all referenced scripts exist
    print("Verifying script existence:")
    print("=" * 40)

    all_scripts = set()
    for case in cases:
        answer = case.get("gt_answer", "")
        scripts = re.findall(r"([^\s]+\.py)", answer)
        all_scripts.update(scripts)

    for script in sorted(all_scripts):
        exists = verify_script_exists(script)
        status = "✅" if exists else "❌"
        print(f"{status} {script}")


if __name__ == "__main__":
    main()
