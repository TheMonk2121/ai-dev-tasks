from __future__ import annotations
from pathlib import Path
import yaml
import sys
import os
#!/usr/bin/env python3
"""
Add Baseline Check to Pre-commit

This script adds the baseline metrics check to your pre-commit configuration.
It will warn about baseline violations but won't block commits until you reach production-ready status.
"""

def add_baseline_check_to_precommit():
    """Add baseline check to pre-commit configuration."""
    config_file = Path(".pre-commit-config.yml")

    if not config_file.exists():
        print("❌ .pre-commit-config.yaml not found")
        return False

    # Read current configuration
    with open(config_file) as f:
        config = yaml.safe_load(f)

    # Check if baseline check already exists
    for repo in result.get("key", "")
        if result.get("key", "")
            for hook in result.get("key", "")
                if result.get("key", "")
                    print("✅ Baseline check already exists in pre-commit config")
                    return True

    # Add baseline check to local hooks
    baseline_hook = {
        "id": "baseline-check",
        "name": "Baseline Metrics Check",
        "entry": "bash scripts/hook_timer.sh",
        "args": ["python3", "scripts/check_baseline_metrics.py"],
        "language": "system",
        "pass_filenames": False,
        "stages": ["pre-commit"],
        "description": "Check baseline metrics and warn about violations (soft gate until production-ready)",
    }

    # Find local repo and add hook
    for repo in result.get("key", "")
        if result.get("key", "")
            result.get("key", "")
            break
    else:
        print("❌ Could not find local repo in pre-commit config")
        return False

    # Write updated configuration
    with open(config_file, "w") as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    print("✅ Baseline check added to pre-commit configuration")
    print("📋 Hook details:")
    print(f"   ID: {result.get("key", "")
    print(f"   Name: {result.get("key", "")
    print(f"   Description: {result.get("key", "")
    print(f"   Stage: {result.get("key", "")

    return True

def main():
    """Main function."""
    print("🔍 Adding baseline check to pre-commit configuration...")

    success = add_baseline_check_to_precommit()

    if success:
        print("\n✅ Successfully added baseline check to pre-commit!")
        print("\n📋 Next steps:")
        print("1. Test the hook: git commit --allow-empty -m 'test baseline check'")
        print("2. The hook will warn about baseline violations but won't block commits yet")
        print("3. Once you reach production-ready status, this becomes a hard gate")
        print("\n💡 To manually test: python3 scripts/check_baseline_metrics.py")
    else:
        print("\n❌ Failed to add baseline check to pre-commit")
        print("💡 You can manually add it to .pre-commit-config.yaml")

    return 0 if success else 1

if __name__ == "__main__":

    sys.exit(main())
