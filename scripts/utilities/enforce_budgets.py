from __future__ import annotations

import pathlib
import subprocess
import sys
from pathlib import Path

import yaml

#!/usr/bin/env python3
"""
Enforce test suite budgets to prevent bloat.

Fails if PR exceeds test count limits or adds too many new tests.
"""

BUDGETS = pathlib.Path("tests/budgets.yml")

def count_tests(glob="tests/**/*.py"):
    """Count total test files"""
    return len(list(pathlib.Path("tests").glob("**/*.py")))

def count_tests_in(path):
    """Count test files in specific path"""
    p = pathlib.Path(path)
    return len(list(p.glob("**/*.py"))) if p.exists() else 0

def changed_test_files(base_ref):
    """Get list of changed and added test files in PR"""
    # list of added/modified test files in PR
    res = subprocess.run(
        ["bash", "-lc", f"git diff --name-status origin/{base_ref}...HEAD | grep '^A\\|^M' | awk '{{print $2}}'"],
        text=True,
        capture_output=True,
    )
    files = [l.strip() for l in res.stdout.splitlines() if l.strip().startswith("tests/") and l.strip().endswith(".py")]

    # count only added as "new tests"
    resA = subprocess.run(
        ["bash", "-lc", f"git diff --name-status origin/{base_ref}...HEAD | grep '^A' | awk '{{print $2}}'"],
        text=True,
        capture_output=True,
    )
    added = [
        l.strip() for l in resA.stdout.splitlines() if l.strip().startswith("tests/") and l.strip().endswith(".py")
    ]

    return files, added

def main():
    cfg = yaml.safe_load(BUDGETS.read_text())
    suite_cap = cfg["suite_max_tests"]
    new_cap = cfg["new_tests_added_max"]
    folders = cfg.get("folders", [])

    base_ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    changed, added = changed_test_files(base_ref)

    total = count_tests()
    if total > suite_cap:
        print(f"❌ Suite has {total} tests > cap {suite_cap}")
        sys.exit(1)

    if len(added) > new_cap:
        print(f"❌ PR adds {len(added)} new tests > cap {new_cap}")
        for f in added:
            print("  +", f)
        sys.exit(1)

    for f in folders:
        n = count_tests_in(f["path"])
        if n > f["max"]:
            print(f"❌ Folder {f['path']} has {n} tests > cap {f['max']}")
            sys.exit(1)

    print(f"✅ Budgets OK. total={total}, new_added={len(added)}")

if __name__ == "__main__":
    main()
