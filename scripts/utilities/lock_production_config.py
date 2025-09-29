from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from src.utils.config_lock import (
    AgentMemoryManager,
    DatasetTrapManager,
    DeterminismManager,
    LockedConfig,
    ObservabilityManager,
    ToolTrapManager,
)

#!/usr/bin/env python3
"""
Production Configuration Locking Script
- Lock the validated 450/0.10/J=0.8/prefix-A configuration
- Create shadow indexing setup
- Generate evaluation runbook
"""

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Add dspy-rag-system to path
dspy_rag_path = project_root / "dspy-rag-system"
sys.path.insert(0, str(dspy_rag_path))

# Import additional modules from dspy-rag-system
try:
    from src.utils.config_lock import (
        ConfigLockManager,
        create_production_config,
        get_production_runbook,
    )
except ImportError:
    # These modules may not be available in all environments
    ConfigLockManager = None
    create_production_config = None
    get_production_runbook = None

def main():
    parser = argparse.ArgumentParser(description="Lock production chunking configuration")
    parser.add_argument("--chunk-size", type=int, default=450, help="Chunk size")
    parser.add_argument("--overlap-ratio", type=float, default=0.10, help="Overlap ratio")
    parser.add_argument("--jaccard-threshold", type=float, default=0.8, help="Jaccard threshold")
    parser.add_argument("--prefix-policy", choices=["A", "B"], default="A", help="Prefix policy")
    parser.add_argument("--embedder", default="BAAI/bge-large-en-v1.5", help="Embedder name")
    parser.add_argument("--baseline-metrics", help="Path to baseline metrics JSON file")
    parser.add_argument("--generate-runbook", action="store_true", help="Generate evaluation runbook")
    parser.add_argument("--promote", action="store_true", help="Promote to production")

    args = parser.parse_args()

    # Load baseline metrics if provided
    baseline_metrics = {}
    if args.baseline_metrics and Path(args.baseline_metrics).exists():
        with open(args.baseline_metrics) as f:
            baseline_metrics = json.load(f)

    print("🔒 Locking Production Configuration")
    print("=" * 50)
    print(f"Chunk size: {args.chunk_size}")
    print(f"Overlap ratio: {args.overlap_ratio}")
    print(f"Jaccard threshold: {args.jaccard_threshold}")
    print(f"Prefix policy: {args.prefix_policy}")
    print(f"Embedder: {args.embedder}")
    print()

    # Create and lock configuration
    config = create_production_config(  # type: ignore
        chunk_size=args.chunk_size,
        overlap_ratio=args.overlap_ratio,
        jaccard_threshold=args.jaccard_threshold,
        prefix_policy=args.prefix_policy,
        embedder_name=args.embedder,
        baseline_metrics=baseline_metrics,
    )

    # Promote to production if requested
    if args.promote:
        manager = ConfigLockManager()  # type: ignore
        manager.promote_to_production(config)

    # Generate runbook if requested
    if args.generate_runbook:
        print("\n" + "=" * 60)
        print("PRODUCTION EVALUATION RUNBOOK")
        print("=" * 60)
        runbook = get_production_runbook()  # type: ignore
        print(runbook)

        # Save runbook to file
        runbook_file = Path("production_evaluation_runbook.sh")
        with open(runbook_file, "w") as f:
            f.write("#!/bin/bash\n")
            f.write("# Production Evaluation Runbook\n")
            f.write(f"# Generated: {config.locked_at}\n")
            f.write(f"# Config: {config.chunk_version}\n\n")
            f.write(runbook)

        runbook_file.chmod(0o755)
        print(f"\n📝 Runbook saved to: {runbook_file}")

    print(f"\n✅ Configuration locked: {config.chunk_version}")
    print(f"   Config hash: {config.get_config_hash()}")
    print("   Lock file: config/locked_configs/active_config.json")

if __name__ == "__main__":
    main()