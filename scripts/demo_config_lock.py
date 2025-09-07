#!/usr/bin/env python3
"""
Demo Configuration Locking Workflow
- Lock the validated 450/0.10/J=0.8/prefix-A configuration
- Show how to use the production evaluation system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dspy_rag_system.src.utils.config_lock import (
    create_production_config,
    get_production_runbook,
    ConfigLockManager,
)


def main():
    print("🔒 Configuration Locking Demo")
    print("=" * 50)
    
    # Create and lock the validated configuration
    print("1. Creating locked configuration...")
    config = create_production_config(
        chunk_size=450,
        overlap_ratio=0.10,
        jaccard_threshold=0.8,
        prefix_policy="A",
        embedder_name="BAAI/bge-large-en-v1.5",
        baseline_metrics={
            "precision": 0.149,
            "recall": 0.099,
            "f1_score": 0.112,
            "faithfulness": "TBD"
        }
    )
    
    print(f"✅ Configuration locked: {config.chunk_version}")
    print(f"   Config hash: {config.get_config_hash()}")
    
    # Show the production runbook
    print("\n2. Production Evaluation Runbook:")
    print("=" * 50)
    runbook = get_production_runbook()
    print(runbook)
    
    # Show how to promote to production
    print("\n3. Promoting to production...")
    manager = ConfigLockManager()
    manager.promote_to_production(config)
    
    print("\n4. Next steps:")
    print("   - Run: python scripts/production_evaluation.py")
    print("   - Monitor: python scripts/production_health_monitor.py")
    print("   - Check: config/locked_configs/active_config.json")
    
    print(f"\n🎯 Your locked configuration is ready for production!")
    print(f"   Version: {config.chunk_version}")
    print(f"   Shadow table: {config.shadow_table}")


if __name__ == "__main__":
    main()
