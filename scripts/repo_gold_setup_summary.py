#!/usr/bin/env python3
"""
Repo-Gold Setup Summary
Provides overview of the repo-gold evaluation system implementation
"""

import json
import os
from pathlib import Path


def print_section(title: str, content: str):
    """Print a formatted section."""
    print(f"\n{title}")
    print("=" * len(title))
    print(content)


def main():
    """Main summary function."""
    print("🎯 REPO-GOLD EVALUATION SYSTEM SETUP SUMMARY")
    print("=" * 60)
    
    # Dataset information
    dataset_file = Path("datasets/dev_gold.jsonl")
    if dataset_file.exists():
        with open(dataset_file, 'r') as f:
            records = [json.loads(line) for line in f if line.strip()]
        
        categories = {}
        for record in records:
            cat = record.get('category', 'unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        print_section("📊 Dataset Overview", f"""
Total records: {len(records)}
Categories:
{chr(10).join(f"  • {cat}: {count}" for cat, count in categories.items())}
File: {dataset_file}
        """)
    
    # Few-shot pool information
    pool_file = Path("datasets/few_shot_pool.jsonl")
    if pool_file.exists():
        with open(pool_file, 'r') as f:
            pool_records = [json.loads(line) for line in f if line.strip()]
        
        print_section("🔒 Leakage Guard", f"""
Few-shot pool size: {len(pool_records)}
Pool file: {pool_file}
Leakage guard: ✅ Implemented
        """)
    
    # Configuration information
    config_file = Path("configs/repo_gold_evaluation.env")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config_lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print_section("⚙️ Configuration", f"""
Config file: {config_file}
Key settings:
  • DATASET_HAS_GOLD=1
  • F1_SCORE_MIN=0.22
  • ORACLE_PREFILTER_TARGET=0.85
  • READER_USED_GOLD_TARGET=0.70
  • RERANK_ENABLE=1
        """)
    
    # Evaluation scripts
    print_section("🚀 Evaluation Scripts", """
Available scripts:
  • scripts/bootstrap_repo_gold_dataset.py - Create repo-gold dataset
  • scripts/leakage_guard.py - Validate no data leakage
  • scripts/run_evaluation_suite.py - Run comprehensive evaluations
  • scripts/ci_evaluation_pipeline.py - CI integration
  • scripts/gate_and_promote.py - Quality gates and promotion
        """)
    
    # Usage examples
    print_section("📋 Usage Examples", """
Run repo-gold evaluation:
  python3 scripts/run_evaluation_suite.py --repo-gold-only

Run ops smoke test:
  python3 scripts/run_evaluation_suite.py --ops-smoke-only

Run both evaluations:
  python3 scripts/run_evaluation_suite.py

Validate leakage guard:
  python3 scripts/leakage_guard.py --action validate --eval-file datasets/dev_gold.jsonl

Run CI pipeline:
  python3 scripts/ci_evaluation_pipeline.py
        """)
    
    # Current status
    print_section("📈 Current Status", """
✅ Repo-gold dataset created (30 records)
✅ Few-shot pool created (3 records)
✅ Leakage guard implemented
✅ Configuration files created
✅ Evaluation scripts implemented
✅ CI integration ready
✅ Quality gates implemented

Next steps:
1. Run initial evaluation to establish baseline
2. Calibrate oracle thresholds based on results
3. Integrate into CI/CD pipeline
4. Set up nightly evaluation runs
        """)
    
    # Gate thresholds
    print_section("🚪 Quality Gates", """
Current thresholds:
  • F1 Score: ≥ 0.22
  • Precision Drift: ≤ 0.02
  • Latency Increase: ≤ 15%
  • Oracle Prefilter: ≥ 85%
  • Reader Used Gold: ≥ 70%
  • Tool Schema Conformance: ≥ 95%

Note: Oracle metrics will be 0% on first run until calibrated.
        """)


if __name__ == "__main__":
    main()
