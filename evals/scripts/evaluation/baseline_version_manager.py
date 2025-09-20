from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

#!/usr/bin/env python3
"""
Baseline Version Manager for Canonical Evaluation System
Manages versioned baselines and audit trails for regression tracking
"""


def get_git_commit_hash() -> Any:
    """Get current git commit hash for provenance tracking."""
    try:
        result: Any = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True)
        return result.stdout.strip()[:8]  # Short hash
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def create_baseline_version() -> Any:
    """Create a new versioned baseline from current stable configuration."""
    timestamp = datetime.now().strftime("%Y%m%d")
    stable_file = Path("configs/stable_bedrock.env")
    versioned_file = Path(f"configs/stable_bedrock_{timestamp}.env")

    if not stable_file.exists():
        print(f"❌ Stable config not found: {stable_file}")
        return False

    # Copy stable config to versioned file
    shutil.copy2(stable_file, versioned_file)
    print(f"✅ Created versioned baseline: {versioned_file}")

    # Update the versioned file with metadata
    with open(versioned_file, "a") as f:
        f.write(f"\n# Version: {timestamp}\n")
        f.write(f"# Git commit: {get_git_commit_hash()}\n")
        f.write(f"# Created: {datetime.now().isoformat()}\n")

    return versioned_file


def create_baseline_milestone() -> Any:
    """Create a new baseline milestone document."""
    timestamp = datetime.now().strftime("%Y%m%d")
    milestone_file = Path(f"metrics/baseline_evaluations/NEW_BASELINE_MILESTONE_{timestamp}.md")

    # Get current environment settings
    bedrock_model: Any = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region: Any = os.getenv("AWS_REGION", "us-east-1")
    max_rps: Any = os.getenv("BEDROCK_MAX_RPS", "0.15")

    milestone_content = f"""# 🎯 NEW BASELINE MILESTONE: {timestamp}

## 📋 **Milestone Overview**

**Date Established**: {datetime.now().strftime("%B %d, %Y")}
**Status**: 🎯 **NEW TARGET BASELINE** - Industry Standard Production Metrics
**Priority**: 🔥 **HIGHEST** - Transform from Development Phase to Production Ready

## 🔧 **Configuration Provenance**

**Git Commit**: `{get_git_commit_hash()}`
**Model**: `{bedrock_model}`
**Region**: `{aws_region}`
**Rate Limit**: `{max_rps} RPS`

## 📊 **Baseline Metrics**

### **🔍 Retrieval Quality Targets**
| **Metric** | **Target** | **Current** | **Gap** | **Priority** |
|------------|------------|-------------|---------|--------------|
| **Recall@20** | ≥ 0.65-0.75 | TBD | TBD | 🔥 **CRITICAL** |
| **Precision@k** | ≥ 0.20-0.35 | TBD | TBD | ⚠️ **HIGH** |
| **Reranker Lift** | +10-20% | TBD | TBD | 🔥 **CRITICAL** |

### **📝 Answer Quality Targets**
| **Metric** | **Target** | **Current** | **Gap** | **Priority** |
|------------|------------|-------------|---------|--------------|
| **Faithfulness** | ≥ 0.60-0.75 | TBD | TBD | ⚠️ **HIGH** |
| **Unsupported Claims** | ≤ 10-15% | TBD | TBD | 🔥 **CRITICAL** |
| **Context Utilization** | ≥ 60% | TBD | TBD | ✅ **ON TRACK** |

## 🚨 **RED LINE ENFORCEMENT**

**Status**: 🔴 **RED LINE BASELINE** - Absolute Performance Floor
**Rule**: **NO NEW FEATURES** until metrics are restored above baseline
**Priority**: 🔥 **HIGHEST** - Prevents performance degradation from feature creep

## 📝 **Usage**

**Run stable evaluation:**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

**Verify configuration:**
- Banner should show: `ASYNC_MAX_CONCURRENCY=1, BEDROCK_MAX_RPS={max_rps}, MODEL_ID={bedrock_model}`
- Environment locked: `🔒 Loaded env from configs/stable_bedrock.env … lock=True`

---
**Generated**: {datetime.now().isoformat()}
**Status**: 🎯 **NEW BASELINE MILESTONE ESTABLISHED**
"""

    milestone_file.write_text(milestone_content)
    print(f"✅ Created baseline milestone: {milestone_file}")
    return milestone_file


def create_baseline_locked() -> Any:
    """Create baseline locked document for current version."""
    timestamp = datetime.now().strftime("%Y%m%d")
    locked_file = Path(f"metrics/baseline_evaluations/BASELINE_LOCKED_{timestamp}.md")

    bedrock_model: Any = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
    aws_region: Any = os.getenv("AWS_REGION", "us-east-1")
    max_rps: Any = os.getenv("BEDROCK_MAX_RPS", "0.15")

    locked_content = f"""# 🔒 BASELINE LOCKED: {timestamp}

## 📋 **Lock Status**

**Date Locked**: {datetime.now().strftime("%B %d, %Y")}
**Status**: 🔒 **LOCKED** - Regression Tracking Baseline
**Git Commit**: `{get_git_commit_hash()}`

## 🔧 **Locked Configuration**

**Model**: `{bedrock_model}`
**Region**: `{aws_region}`
**Rate Limit**: `{max_rps} RPS`
**Concurrency**: `1`
**Cooldown**: `{os.getenv('BEDROCK_COOLDOWN_SEC', '30')}s`

## 📊 **Baseline Results**

**Results File**: `metrics/baseline_evaluations/ragchecker_official_evaluation_*.json`
**Evaluation Date**: {datetime.now().isoformat()}

## 🚨 **Enforcement Rules**

1. **No new features** until metrics exceed baseline
2. **All evaluations** must use this locked configuration
3. **Regression detection** against these exact settings
4. **Version bump required** for any configuration changes

## 📝 **Usage**

**Run locked evaluation:**
```bash
source throttle_free_eval.sh
python3 scripts/ragchecker_official_evaluation.py --use-bedrock --bypass-cli --stable
```

---
**Generated**: {datetime.now().isoformat()}
**Status**: 🔒 **BASELINE LOCKED**
"""

    locked_file.write_text(locked_content)
    print(f"✅ Created baseline locked: {locked_file}")
    return locked_file


def main() -> Any:
    """Main function for baseline version management."""

    parser: Any = argparse.ArgumentParser(description="Baseline Version Manager")
    parser.add_argument("--create-version", action="store_true", help="Create new versioned baseline")
    parser.add_argument("--create-milestone", action="store_true", help="Create new baseline milestone")
    parser.add_argument("--create-locked", action="store_true", help="Create baseline locked document")
    parser.add_argument("--full-setup", action="store_true", help="Create version, milestone, and locked documents")

    args: Any = parser.parse_args()

    if args.full_setup:
        print("🔒 Setting up complete baseline versioning...")
        create_baseline_version()
        create_baseline_milestone()
        create_baseline_locked()
        print("✅ Complete baseline versioning setup complete")
    elif args.create_version:
        create_baseline_version()
    elif args.create_milestone:
        create_baseline_milestone()
    elif args.create_locked:
        create_baseline_locked()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
