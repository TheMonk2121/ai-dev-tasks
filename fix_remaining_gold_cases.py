#!/usr/bin/env python3
"""
Fix Remaining Gold Cases Script
Fixes the remaining script references that need special handling.
"""

import json
import os
import re
from pathlib import Path


def fix_remaining_cases():
    """Fix the remaining script references that need special handling."""
    gold_cases_file = Path("evals/data/gold/v1/gold_cases_121.jsonl")

    # Read all gold cases
    with open(gold_cases_file) as f:
        cases = [json.loads(line) for line in f]

    print("Fixing remaining script references...")

    updated_count = 0

    for case in cases:
        original_answer = case.get("gt_answer", "")
        updated_answer = original_answer

        # Fix test_mcp_for_codex.py -> scripts/utilities/test_mcp_server.py
        if "test_mcp_for_codex.py" in updated_answer:
            updated_answer = updated_answer.replace("test_mcp_for_codex.py", "scripts/utilities/test_mcp_server.py")
            updated_count += 1
            print(f"Updated {case['id']}: test_mcp_for_codex.py -> scripts/utilities/test_mcp_server.py")

        # Fix litellm_compatibility_shim.py - no longer needed
        if "litellm_compatibility_shim.py" in updated_answer:
            # Update the answer to reflect that no shim is needed
            updated_answer = updated_answer.replace(
                "litellm_compatibility_shim.py patches imports for DSPy 3.0.1; applied before DSPy imports in scripts",
                "DSPy 3.0.1 works directly with litellm 1.77.0 - no compatibility shim needed",
            )
            updated_count += 1
            print(f"Updated {case['id']}: litellm_compatibility_shim.py -> no shim needed")

        case["gt_answer"] = updated_answer

    # Write updated cases back to file
    with open(gold_cases_file, "w") as f:
        for case in cases:
            f.write(json.dumps(case) + "\n")

    print(f"Fixed {updated_count} additional cases")

    # Final verification
    print("\nFinal verification of all script references:")
    print("=" * 50)

    all_scripts = set()
    for case in cases:
        answer = case.get("gt_answer", "")
        scripts = re.findall(r"([^\s]+\.py)", answer)
        all_scripts.update(scripts)

    for script in sorted(all_scripts):
        exists = os.path.exists(script)
        status = "✅" if exists else "❌"
        print(f"{status} {script}")


if __name__ == "__main__":
    fix_remaining_cases()
