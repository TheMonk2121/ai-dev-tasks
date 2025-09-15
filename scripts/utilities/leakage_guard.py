from __future__ import annotations

import argparse
import json
import os
import random
from typing import Any, Optional, Union

#!/usr/bin/env python3
"""
Leakage Guard for Few-Shot ID Exclusion
Prevents few-shot examples from appearing in evaluation sets
"""


class LeakageGuard:
    """Guard against data leakage between few-shot and evaluation sets."""

    def __init__(self, few_shot_pool_file: str = "300_evals/datasets/few_shot_pool.jsonl"):
        self.few_shot_pool_file = few_shot_pool_file
        self.few_shot_ids: set[str] = set()
        self.eval_ids: set[str] = set()
        self._load_few_shot_pool()

    def _load_few_shot_pool(self):
        """Load few-shot pool IDs to exclude from evaluation."""
        if os.path.exists(self.few_shot_pool_file):
            with open(self.few_shot_pool_file) as f:
                for line in f:
                    if line.strip():
                        record = json.loads(line)
                        if "id" in record:
                            self.few_shot_ids.add(record["id"])
            print(f"🔒 Loaded {len(self.few_shot_ids)} few-shot IDs for leakage guard")
        else:
            print(f"⚠️ Few-shot pool file not found: {self.few_shot_pool_file}")

    def validate_evaluation_set(self, eval_file: str) -> dict[str, Any]:
        """Validate evaluation set for leakage."""
        eval_ids = set()
        leakage_found = []

        with open(eval_file) as f:
            for line_num, line in enumerate(f, 1):
                if line.strip():
                    record = json.loads(line)
                    if "id" in record:
                        eval_id = record["id"]
                        eval_ids.add(eval_id)

                        if eval_id in self.few_shot_ids:
                            leakage_found.append(
                                {"line": line_num, "id": eval_id, "query": record.get("query", "")[:50] + "..."}
                            )

        self.eval_ids = eval_ids

        result = {
            "total_eval_records": len(eval_ids),
            "total_few_shot_ids": len(self.few_shot_ids),
            "leakage_count": len(leakage_found),
            "leakage_found": leakage_found,
            "leakage_percentage": (len(leakage_found) / len(eval_ids) * 100) if eval_ids else 0,
            "is_clean": len(leakage_found) == 0,
        }

        return result

    def assert_no_leakage(self, eval_file: str):
        """Assert that evaluation set has no leakage from few-shot pool."""
        validation = self.validate_evaluation_set(eval_file)

        if not validation["is_clean"]:
            print(f"❌ LEAKAGE DETECTED: {validation['leakage_count']} records found in both few-shot and eval sets")
            print("Leaked records:")
            for leak in validation["leakage_found"]:
                print(f"  • Line {leak['line']}: {leak['id']} - {leak['query']}")
            raise RuntimeError(
                f"Data leakage detected: {validation['leakage_count']} records overlap between few-shot and evaluation sets"
            )

        print(
            f"✅ No leakage detected: {validation['total_eval_records']} eval records, {validation['total_few_shot_ids']} few-shot IDs"
        )

    def create_few_shot_pool(self, source_file: str, pool_size: int = 50):
        """Create few-shot pool from source dataset."""
        records = []

        with open(source_file) as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    records.append(record)

        # Sample records for few-shot pool

        random.seed(42)  # Reproducible sampling
        few_shot_records = random.sample(records, min(pool_size, len(records)))

        # Add IDs to records
        for i, record in enumerate(few_shot_records):
            record["id"] = f"few_shot_{i:03d}"

        # Save few-shot pool
        os.makedirs(os.path.dirname(self.few_shot_pool_file), exist_ok=True)
        with open(self.few_shot_pool_file, "w") as f:
            for record in few_shot_records:
                f.write(json.dumps(record) + "\n")

        print(f"💾 Created few-shot pool: {len(few_shot_records)} records in {self.few_shot_pool_file}")

        # Update internal state
        self.few_shot_ids = {record["id"] for record in few_shot_records}

        return few_shot_records

    def get_few_shot_ids(self) -> list[str]:
        """Get list of few-shot IDs for exclusion."""
        return list(self.few_shot_ids)

    def get_eval_ids(self) -> list[str]:
        """Get list of evaluation IDs."""
        return list(self.eval_ids)


def main():
    """Main entry point for leakage guard."""

    parser = argparse.ArgumentParser(description="Leakage guard for few-shot exclusion")
    parser.add_argument("--action", choices=["validate", "create-pool", "assert-clean"], required=True)
    parser.add_argument("--eval-file", help="Evaluation file to validate")
    parser.add_argument("--source-file", help="Source file for creating few-shot pool")
    parser.add_argument("--pool-size", type=int, default=50, help="Size of few-shot pool")
    parser.add_argument("--pool-file", default="300_evals/datasets/few_shot_pool.jsonl", help="Few-shot pool file")

    args = parser.parse_args()

    guard = LeakageGuard(args.pool_file)

    if args.action == "validate":
        if not args.eval_file:
            print("❌ --eval-file required for validate action")
            return

        validation = guard.validate_evaluation_set(args.eval_file)
        print("📊 Validation Results:")
        print(f"  • Total eval records: {validation['total_eval_records']}")
        print(f"  • Total few-shot IDs: {validation['total_few_shot_ids']}")
        print(f"  • Leakage count: {validation['leakage_count']}")
        print(f"  • Leakage percentage: {validation['leakage_percentage']:.1f}%")
        print(f"  • Is clean: {validation['is_clean']}")

        if validation["leakage_found"]:
            print("\n🚨 Leaked records:")
            for leak in validation["leakage_found"]:
                print(f"  • Line {leak['line']}: {leak['id']} - {leak['query']}")

    elif args.action == "create-pool":
        if not args.source_file:
            print("❌ --source-file required for create-pool action")
            return

        guard.create_few_shot_pool(args.source_file, args.pool_size)

    elif args.action == "assert-clean":
        if not args.eval_file:
            print("❌ --eval-file required for assert-clean action")
            return

        guard.assert_no_leakage(args.eval_file)


if __name__ == "__main__":
    main()
